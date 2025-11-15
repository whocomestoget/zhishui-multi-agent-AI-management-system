#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复数据库中的文本编码问题
直接修复SQLite数据库中存储的乱码文本
"""

import sqlite3
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_database_encoding():
    """修复数据库中的编码问题"""
    db_path = Path("knowledge_base/metadata.db")
    
    if not db_path.exists():
        logger.error(f"数据库文件不存在: {db_path}")
        return
    
    try:
        # 连接数据库
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 查询所有文档分块
        cursor.execute("SELECT chunk_id, content FROM document_chunks")
        chunks = cursor.fetchall()
        
        logger.info(f"找到 {len(chunks)} 个文档分块")
        
        fixed_count = 0
        for chunk in chunks:
            chunk_id = chunk['chunk_id']
            content = chunk['content']
            
            if content:
                try:
                    # 检查是否包含中文字符
                    if not any('\u4e00' <= char <= '\u9fff' for char in content[:100]):
                        # 尝试修复编码
                        try:
                            # 方法1: latin1 -> utf8
                            fixed_content = content.encode('latin1').decode('utf-8')
                            
                            # 验证修复后的内容
                            if any('\u4e00' <= char <= '\u9fff' for char in fixed_content[:100]):
                                # 更新数据库
                                cursor.execute(
                                    "UPDATE document_chunks SET content = ? WHERE chunk_id = ?",
                                    (fixed_content, chunk_id)
                                )
                                fixed_count += 1
                                logger.info(f"修复分块 {chunk_id}: {content[:50]} -> {fixed_content[:50]}")
                            else:
                                # 方法2: 尝试其他编码
                                try:
                                    fixed_content = content.encode('cp1252').decode('utf-8')
                                    if any('\u4e00' <= char <= '\u9fff' for char in fixed_content[:100]):
                                        cursor.execute(
                                            "UPDATE document_chunks SET content = ? WHERE chunk_id = ?",
                                            (fixed_content, chunk_id)
                                        )
                                        fixed_count += 1
                                        logger.info(f"修复分块 {chunk_id} (cp1252): {content[:50]} -> {fixed_content[:50]}")
                                except:
                                    logger.warning(f"无法修复分块 {chunk_id} 的编码")
                        except Exception as e:
                            logger.warning(f"修复分块 {chunk_id} 时出错: {e}")
                except Exception as e:
                    logger.error(f"处理分块 {chunk_id} 时出错: {e}")
        
        # 提交更改
        conn.commit()
        logger.info(f"成功修复 {fixed_count} 个文档分块的编码")
        
        # 验证修复结果
        cursor.execute("SELECT content FROM document_chunks LIMIT 3")
        samples = cursor.fetchall()
        
        logger.info("修复后的内容示例:")
        for i, sample in enumerate(samples, 1):
            content = sample['content'][:100]
            logger.info(f"示例 {i}: {content}")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"修复数据库编码时出错: {e}")

if __name__ == "__main__":
    logger.info("开始修复数据库编码...")
    fix_database_encoding()
    logger.info("数据库编码修复完成")
    logger.info("请重启MCP服务以使更改生效")