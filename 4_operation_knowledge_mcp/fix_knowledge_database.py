#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
文件：fix_knowledge_database.py
功能：修复知识库中的乱码文档，清理和重建索引
技术：数据库清理 + 向量索引重建 + 文档重新导入
============================================================================

解决方案：
1. 识别和删除乱码文档
2. 清理向量索引
3. 提供重新导入功能
4. 验证修复效果
"""

import json
import logging
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import re

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KnowledgeDatabaseFixer:
    """知识库修复工具"""
    
    def __init__(self, db_path: str = "data/knowledge.db"):
        self.db_path = Path(db_path)
        self.vector_index_dir = Path("data/vector_index")
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"数据库文件不存在: {self.db_path}")
    
    def analyze_documents(self) -> Dict:
        """分析文档质量，识别乱码文档"""
        logger.info("开始分析文档质量...")
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            
            # 获取所有文档
            cursor = conn.execute("""
                SELECT doc_id, title, original_filename, category, subcategory, 
                       upload_time, page_count, file_size
                FROM documents 
                WHERE status = 'active'
                ORDER BY upload_time DESC
            """)
            
            documents = cursor.fetchall()
            
            analysis_result = {
                "total_documents": len(documents),
                "clean_documents": [],
                "garbled_documents": [],
                "suspicious_documents": []
            }
            
            for doc in documents:
                doc_id = doc['doc_id']
                title = doc['title']
                filename = doc['original_filename']
                
                # 获取文档的内容预览
                chunk_cursor = conn.execute("""
                    SELECT content FROM document_chunks 
                    WHERE doc_id = ? 
                    LIMIT 3
                """, (doc_id,))
                
                chunks = chunk_cursor.fetchall()
                
                if not chunks:
                    analysis_result["suspicious_documents"].append({
                        "doc_id": doc_id,
                        "title": title,
                        "filename": filename,
                        "issue": "无内容分块",
                        "category": doc['category']
                    })
                    continue
                
                # 检查内容质量
                sample_content = " ".join([chunk['content'] for chunk in chunks])
                quality_score = self._assess_content_quality(sample_content)
                
                doc_info = {
                    "doc_id": doc_id,
                    "title": title,
                    "filename": filename,
                    "category": doc['category'],
                    "subcategory": doc['subcategory'],
                    "upload_time": doc['upload_time'],
                    "quality_score": quality_score,
                    "content_preview": sample_content[:200]
                }
                
                if quality_score < 0.3:
                    analysis_result["garbled_documents"].append(doc_info)
                elif quality_score < 0.7:
                    analysis_result["suspicious_documents"].append(doc_info)
                else:
                    analysis_result["clean_documents"].append(doc_info)
            
            logger.info(f"分析完成: 总计{analysis_result['total_documents']}个文档")
            logger.info(f"  - 正常文档: {len(analysis_result['clean_documents'])}个")
            logger.info(f"  - 可疑文档: {len(analysis_result['suspicious_documents'])}个")
            logger.info(f"  - 乱码文档: {len(analysis_result['garbled_documents'])}个")
            
            return analysis_result
    
    def _assess_content_quality(self, content: str) -> float:
        """评估内容质量（0-1分，1为最好）"""
        if not content or len(content.strip()) < 10:
            return 0.0
        
        total_chars = len(content)
        
        # 检查乱码字符
        garbled_patterns = [
            r'\(cid:\d+\)',  # PDF乱码
            r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]',  # 控制字符
            r'Ł',  # 常见乱码字符
            r'fl',  # 连字符乱码
            r'[¡-¿]',  # 拉丁扩展字符
            r'â€™|â€œ|â€|Â',  # UTF-8编码错误
        ]
        
        garbled_count = 0
        for pattern in garbled_patterns:
            garbled_count += len(re.findall(pattern, content))
        
        # 检查可读字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
        english_chars = len(re.findall(r'[a-zA-Z]', content))
        numbers = len(re.findall(r'[0-9]', content))
        
        readable_chars = chinese_chars + english_chars + numbers
        
        # 计算质量分数
        if total_chars == 0:
            return 0.0
        
        garbled_ratio = garbled_count / total_chars
        readable_ratio = readable_chars / total_chars
        
        # 质量分数 = 可读比例 - 乱码比例
        quality_score = readable_ratio - garbled_ratio * 2
        
        return max(0.0, min(1.0, quality_score))
    
    def remove_garbled_documents(self, doc_ids: List[str]) -> Dict:
        """删除乱码文档"""
        logger.info(f"开始删除{len(doc_ids)}个乱码文档...")
        
        removed_count = 0
        failed_count = 0
        
        with sqlite3.connect(str(self.db_path)) as conn:
            for doc_id in doc_ids:
                try:
                    # 删除文档分块
                    conn.execute("DELETE FROM document_chunks WHERE doc_id = ?", (doc_id,))
                    
                    # 删除文档记录
                    cursor = conn.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
                    
                    if cursor.rowcount > 0:
                        removed_count += 1
                        logger.info(f"✅ 已删除文档: {doc_id}")
                    else:
                        logger.warning(f"❌ 文档不存在: {doc_id}")
                        failed_count += 1
                        
                except Exception as e:
                    logger.error(f"❌ 删除文档失败 {doc_id}: {e}")
                    failed_count += 1
            
            conn.commit()
        
        result = {
            "removed_count": removed_count,
            "failed_count": failed_count,
            "success": failed_count == 0
        }
        
        logger.info(f"删除完成: 成功{removed_count}个，失败{failed_count}个")
        return result
    
    def rebuild_vector_index(self) -> Dict:
        """重建向量索引"""
        logger.info("开始重建向量索引...")
        
        try:
            # 备份现有索引
            if self.vector_index_dir.exists():
                backup_dir = Path(f"data/vector_index_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                shutil.move(str(self.vector_index_dir), str(backup_dir))
                logger.info(f"已备份现有索引到: {backup_dir}")
            
            # 创建新的索引目录
            self.vector_index_dir.mkdir(exist_ok=True)
            
            logger.info("✅ 向量索引已重置，需要重新启动MCP服务以重建索引")
            
            return {
                "success": True,
                "message": "向量索引已重置，请重新启动MCP服务"
            }
            
        except Exception as e:
            logger.error(f"❌ 重建向量索引失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_report(self, analysis_result: Dict, output_file: str = "knowledge_analysis_report.json"):
        """生成分析报告"""
        report = {
            "analysis_time": datetime.now().isoformat(),
            "database_path": str(self.db_path),
            "summary": {
                "total_documents": analysis_result["total_documents"],
                "clean_documents": len(analysis_result["clean_documents"]),
                "suspicious_documents": len(analysis_result["suspicious_documents"]),
                "garbled_documents": len(analysis_result["garbled_documents"])
            },
            "details": analysis_result
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"分析报告已保存到: {output_file}")
        return report
    
    def clean_database(self, auto_remove_garbled: bool = False) -> Dict:
        """清理数据库"""
        logger.info("开始清理知识库...")
        
        # 1. 分析文档质量
        analysis = self.analyze_documents()
        
        # 2. 生成报告
        report = self.generate_report(analysis)
        
        # 3. 自动删除乱码文档（如果启用）
        removal_result = None
        if auto_remove_garbled and analysis["garbled_documents"]:
            garbled_ids = [doc["doc_id"] for doc in analysis["garbled_documents"]]
            removal_result = self.remove_garbled_documents(garbled_ids)
        
        # 4. 重建向量索引
        index_result = self.rebuild_vector_index()
        
        return {
            "analysis": analysis,
            "report_file": "knowledge_analysis_report.json",
            "removal_result": removal_result,
            "index_rebuild": index_result,
            "recommendations": self._generate_recommendations(analysis)
        }
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """生成修复建议"""
        recommendations = []
        
        if analysis["garbled_documents"]:
            recommendations.append(f"发现{len(analysis['garbled_documents'])}个乱码文档，建议删除并重新导入")
        
        if analysis["suspicious_documents"]:
            recommendations.append(f"发现{len(analysis['suspicious_documents'])}个可疑文档，建议人工检查")
        
        if analysis["total_documents"] == 0:
            recommendations.append("知识库为空，建议导入文档")
        
        recommendations.extend([
            "重新启动MCP服务以重建向量索引",
            "使用TXT格式文档可以避免PDF编码问题",
            "定期备份知识库数据"
        ])
        
        return recommendations

def main():
    """主函数"""
    import sys
    
    fixer = KnowledgeDatabaseFixer()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "analyze":
            # 仅分析，不修改
            analysis = fixer.analyze_documents()
            fixer.generate_report(analysis)
            
        elif command == "clean":
            # 清理数据库（不自动删除）
            result = fixer.clean_database(auto_remove_garbled=False)
            print("\n=== 清理结果 ===")
            print(f"分析报告: {result['report_file']}")
            print("建议操作:")
            for rec in result['recommendations']:
                print(f"  - {rec}")
                
        elif command == "clean-auto":
            # 自动清理（删除乱码文档）
            result = fixer.clean_database(auto_remove_garbled=True)
            print("\n=== 自动清理完成 ===")
            print(f"分析报告: {result['report_file']}")
            if result['removal_result']:
                print(f"删除文档: {result['removal_result']['removed_count']}个")
            print("请重新启动MCP服务以完成修复")
            
        elif command == "rebuild-index":
            # 仅重建索引
            result = fixer.rebuild_vector_index()
            print(f"索引重建结果: {result}")
            
        else:
            print("未知命令")
            print_usage()
    else:
        print_usage()

def print_usage():
    """打印使用说明"""
    print("知识库修复工具")
    print("用法:")
    print("  python fix_knowledge_database.py analyze      # 分析文档质量")
    print("  python fix_knowledge_database.py clean        # 清理数据库（手动确认）")
    print("  python fix_knowledge_database.py clean-auto   # 自动清理乱码文档")
    print("  python fix_knowledge_database.py rebuild-index # 重建向量索引")

if __name__ == "__main__":
    main()