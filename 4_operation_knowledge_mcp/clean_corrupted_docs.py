#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理乱码文档工具
删除knowledge_base/metadata.db中的乱码文档，保留正常的中文文档
"""

import sqlite3
import re
import os
from pathlib import Path

def is_corrupted_text(text):
    """判断文本是否为乱码"""
    if not text:
        return False
    
    # 检查是否包含大量的特殊字符模式
    corrupted_patterns = [
        r'\(cid:\d+\)',  # (cid:xxx) 模式
        r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]',  # 控制字符
        r'Ł[•fl]',  # 特定乱码模式
        r'[\u00A0-\u00FF]{3,}',  # 连续的扩展ASCII字符
    ]
    
    corrupted_count = 0
    total_chars = len(text)
    
    for pattern in corrupted_patterns:
        matches = re.findall(pattern, text)
        corrupted_count += sum(len(match) for match in matches)
    
    # 如果乱码字符超过总字符数的30%，认为是乱码
    corruption_ratio = corrupted_count / total_chars if total_chars > 0 else 0
    return corruption_ratio > 0.3

def clean_corrupted_documents():
    """清理乱码文档"""
    db_path = "knowledge_base/metadata.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    print("🧹 开始清理乱码文档...")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有文档块
        cursor.execute("""
            SELECT chunk_id, doc_id, chunk_index, content 
            FROM document_chunks
        """)
        chunks = cursor.fetchall()
        
        corrupted_chunks = []
        corrupted_docs = set()
        
        print(f"📊 总共检查 {len(chunks)} 个文档块")
        
        # 检查每个块是否为乱码
        for chunk_id, doc_id, chunk_index, content in chunks:
            if is_corrupted_text(content):
                corrupted_chunks.append(chunk_id)
                corrupted_docs.add(doc_id)
                print(f"🔍 发现乱码块: {chunk_id[:20]}... (doc: {doc_id[:8]}...)")
        
        print(f"\n📋 统计结果:")
        print(f"  🗑️  乱码文档块: {len(corrupted_chunks)} 个")
        print(f"  📄 涉及文档: {len(corrupted_docs)} 个")
        
        if not corrupted_chunks:
            print("✅ 没有发现乱码文档，无需清理")
            return
        
        # 显示将要删除的文档信息
        if corrupted_docs:
            print(f"\n📋 将要删除的文档:")
            for doc_id in corrupted_docs:
                cursor.execute("""
                    SELECT title, original_filename, category 
                    FROM documents WHERE doc_id = ?
                """, (doc_id,))
                doc_info = cursor.fetchone()
                if doc_info:
                    title, filename, category = doc_info
                    print(f"  📄 {title} ({filename}) - {category}")
        
        # 确认删除
        confirm = input(f"\n❓ 确认删除这 {len(corrupted_docs)} 个乱码文档吗？(y/N): ")
        if confirm.lower() != 'y':
            print("❌ 取消删除操作")
            return
        
        # 删除乱码文档块
        print("\n🗑️  删除乱码文档块...")
        for chunk_id in corrupted_chunks:
            cursor.execute("DELETE FROM document_chunks WHERE chunk_id = ?", (chunk_id,))
        
        # 删除乱码文档记录
        print("🗑️  删除乱码文档记录...")
        for doc_id in corrupted_docs:
            cursor.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
        
        # 提交更改
        conn.commit()
        
        print(f"\n✅ 清理完成!")
        print(f"  🗑️  已删除 {len(corrupted_chunks)} 个乱码文档块")
        print(f"  🗑️  已删除 {len(corrupted_docs)} 个乱码文档")
        
        # 显示剩余文档
        cursor.execute("SELECT COUNT(*) FROM documents")
        remaining_docs = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM document_chunks")
        remaining_chunks = cursor.fetchone()[0]
        
        print(f"\n📊 清理后统计:")
        print(f"  📄 剩余文档: {remaining_docs} 个")
        print(f"  📝 剩余文档块: {remaining_chunks} 个")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 清理过程中出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("🧹 智水运维知识库 - 乱码文档清理工具")
    print("=" * 60)
    
    clean_corrupted_documents()
    
    print("\n🎯 建议后续操作:")
    print("  1. 重新导入正确的PDF文档")
    print("  2. 使用修复后的文本提取工具")
    print("  3. 验证搜索功能是否正常")

if __name__ == "__main__":
    main()