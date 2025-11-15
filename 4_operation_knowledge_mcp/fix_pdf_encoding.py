#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复PDF文档编码问题
解决PyPDF2提取中文文本时的编码乱码问题
"""

import os
import sys
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List

try:
    import PyPDF2
    import pdfplumber  # 更好的PDF文本提取库
except ImportError as e:
    print(f"缺少依赖库: {e}")
    print("请安装: pip install PyPDF2 pdfplumber")
    sys.exit(1)

# 配置路径
DATA_DIR = Path("knowledge_base")
DOCUMENTS_DIR = DATA_DIR / "documents"
DB_PATH = DATA_DIR / "metadata.db"
LOGS_DIR = Path("logs")

# 确保目录存在
for dir_path in [LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'fix_encoding.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract_pdf_text_improved(pdf_path: str) -> str:
    """
    使用pdfplumber改进PDF文本提取
    
    Args:
        pdf_path: PDF文件路径
        
    Returns:
        str: 提取的文本内容
    """
    try:
        # 首先尝试使用pdfplumber（对中文支持更好）
        with pdfplumber.open(pdf_path) as pdf:
            text_content = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
            
            if text_content.strip():
                logger.info(f"使用pdfplumber成功提取文本: {len(text_content)}字符")
                return text_content.strip()
    
    except Exception as e:
        logger.warning(f"pdfplumber提取失败: {e}，尝试PyPDF2")
    
    # 如果pdfplumber失败，回退到PyPDF2
    try:
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text_content = ""
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
            
            if text_content.strip():
                logger.info(f"使用PyPDF2提取文本: {len(text_content)}字符")
                return text_content.strip()
    
    except Exception as e:
        logger.error(f"PyPDF2提取失败: {e}")
    
    return ""

def get_all_documents() -> List[Dict]:
    """
    获取所有文档信息
    
    Returns:
        List[Dict]: 文档列表
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT doc_id, original_filename, title, category, file_path
                FROM documents
                ORDER BY upload_time DESC
            """)
            
            documents = []
            for row in cursor.fetchall():
                documents.append({
                    'doc_id': row['doc_id'],
                    'filename': row['original_filename'],
                    'title': row['title'],
                    'category': row['category'],
                    'file_path': row['file_path']
                })
            
            return documents
    
    except Exception as e:
        logger.error(f"获取文档列表失败: {e}")
        return []

def update_document_chunks(doc_id: str, new_content: str) -> bool:
    """
    更新文档分块内容
    
    Args:
        doc_id: 文档ID
        new_content: 新的文本内容
        
    Returns:
        bool: 是否成功
    """
    try:
        # 简单分块（与原系统保持一致）
        chunk_size = 800
        overlap = 100
        chunks = []
        
        start = 0
        while start < len(new_content):
            end = start + chunk_size
            chunk = new_content[start:end]
            
            if chunk.strip():
                chunks.append(chunk.strip())
            
            start = end - overlap
            if start >= len(new_content):
                break
        
        # 更新数据库
        with sqlite3.connect(DB_PATH) as conn:
            # 删除旧的分块
            conn.execute("DELETE FROM document_chunks WHERE doc_id = ?", (doc_id,))
            
            # 插入新的分块
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                conn.execute("""
                    INSERT INTO document_chunks 
                    (chunk_id, doc_id, chunk_index, content, vector_id, char_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (chunk_id, doc_id, i, chunk, -1, len(chunk)))
            
            conn.commit()
            
        logger.info(f"文档{doc_id}更新了{len(chunks)}个分块")
        return True
    
    except Exception as e:
        logger.error(f"更新文档分块失败: {e}")
        return False

def fix_document_encoding(doc_info: Dict) -> bool:
    """
    修复单个文档的编码问题
    
    Args:
        doc_info: 文档信息
        
    Returns:
        bool: 是否成功修复
    """
    doc_id = doc_info['doc_id']
    file_path = doc_info['file_path']
    title = doc_info['title']
    
    logger.info(f"正在修复文档: {title} ({doc_id})")
    
    # 检查文件是否存在
    if not Path(file_path).exists():
        logger.error(f"文件不存在: {file_path}")
        return False
    
    # 重新提取文本
    new_content = extract_pdf_text_improved(file_path)
    
    if not new_content:
        logger.error(f"无法提取文本内容: {file_path}")
        return False
    
    # 检查内容是否有改善
    if len(new_content) < 50:  # 内容太短可能有问题
        logger.warning(f"提取的内容可能不完整: {len(new_content)}字符")
    
    # 显示提取的内容预览
    preview = new_content[:200] + "..." if len(new_content) > 200 else new_content
    logger.info(f"提取内容预览: {preview}")
    
    # 更新数据库
    success = update_document_chunks(doc_id, new_content)
    
    if success:
        logger.info(f"✅ 文档修复成功: {title}")
    else:
        logger.error(f"❌ 文档修复失败: {title}")
    
    return success

def main():
    """
    主函数：修复所有文档的编码问题
    """
    logger.info("开始修复PDF文档编码问题...")
    
    # 获取所有文档
    documents = get_all_documents()
    
    if not documents:
        logger.warning("没有找到任何文档")
        return
    
    logger.info(f"找到{len(documents)}个文档，开始修复...")
    
    success_count = 0
    failed_count = 0
    
    for doc_info in documents:
        try:
            if fix_document_encoding(doc_info):
                success_count += 1
            else:
                failed_count += 1
        except Exception as e:
            logger.error(f"修复文档时出错: {e}")
            failed_count += 1
        
        print("-" * 50)
    
    # 总结
    logger.info(f"修复完成！成功: {success_count}, 失败: {failed_count}")
    
    if success_count > 0:
        logger.info("建议重新启动MCP服务以重建向量索引")
        print("\n🔄 请重新启动MCP服务以重建向量索引:")
        print("python knowledge_mcp.py")

if __name__ == "__main__":
    main()