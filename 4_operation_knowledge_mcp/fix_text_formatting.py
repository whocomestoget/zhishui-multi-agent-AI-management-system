#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复PDF文本提取中的格式问题
解决字符间多余换行符导致的显示乱码问题
"""

import sqlite3
import re
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_extracted_text(text):
    """
    清理PDF提取的文本格式问题
    
    Args:
        text (str): 原始提取的文本
        
    Returns:
        str: 清理后的文本
    """
    if not text:
        return text
    
    # 1. 移除字符间的多余换行符（保留段落间的换行）
    # 将单个字符后跟换行符的模式替换为连续文本
    cleaned = re.sub(r'([\u4e00-\u9fff\w])\s*\n\s*([\u4e00-\u9fff\w])', r'\1\2', text)
    
    # 2. 处理标点符号后的换行
    cleaned = re.sub(r'([，。、；：！？])\s*\n\s*', r'\1', cleaned)
    
    # 3. 处理数字和字母间的换行
    cleaned = re.sub(r'([0-9a-zA-Z])\s*\n\s*([0-9a-zA-Z])', r'\1\2', cleaned)
    
    # 4. 保留有意义的段落分隔（连续的换行符）
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    # 5. 清理多余的空格
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    
    # 6. 清理行首行尾空格
    lines = cleaned.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    
    return '\n'.join(lines)

def fix_database_text_formatting():
    """
    修复数据库中所有文档的文本格式问题
    """
    db_path = Path("knowledge_base/metadata.db")
    
    if not db_path.exists():
        logger.error(f"数据库文件不存在: {db_path}")
        return
    
    logger.info("开始修复数据库中的文本格式...")
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # 获取所有文档块
            cursor = conn.execute("SELECT chunk_id, content FROM document_chunks")
            chunks = cursor.fetchall()
            
            logger.info(f"找到 {len(chunks)} 个文档块需要处理")
            
            fixed_count = 0
            for chunk in chunks:
                chunk_id = chunk['chunk_id']
                original_content = chunk['content']
                
                # 清理文本格式
                cleaned_content = clean_extracted_text(original_content)
                
                # 检查是否有改变
                if cleaned_content != original_content:
                    # 更新数据库
                    conn.execute(
                        "UPDATE document_chunks SET content = ? WHERE chunk_id = ?",
                        (cleaned_content, chunk_id)
                    )
                    fixed_count += 1
                    
                    logger.info(f"修复文档块 {chunk_id}")
                    logger.debug(f"原始内容: {original_content[:100]}...")
                    logger.debug(f"修复后: {cleaned_content[:100]}...")
            
            conn.commit()
            logger.info(f"文本格式修复完成！共修复 {fixed_count} 个文档块")
            
    except Exception as e:
        logger.error(f"修复过程中出错: {e}")
        raise

def test_text_cleaning():
    """
    测试文本清理功能
    """
    test_text = "变 \n电 \n站 \n运 \n维 \n方 \n案 \n \n \n目  录 \n \n一、 总则  \n二、 工程概况"
    
    print("原始文本:")
    print(repr(test_text))
    print("\n显示效果:")
    print(test_text)
    
    cleaned = clean_extracted_text(test_text)
    
    print("\n清理后文本:")
    print(repr(cleaned))
    print("\n显示效果:")
    print(cleaned)

if __name__ == "__main__":
    print("=== PDF文本格式修复工具 ===")
    print("1. 测试文本清理功能")
    print("2. 修复数据库中的文本格式")
    
    choice = input("请选择操作 (1/2): ").strip()
    
    if choice == "1":
        test_text_cleaning()
    elif choice == "2":
        fix_database_text_formatting()
    else:
        print("无效选择")