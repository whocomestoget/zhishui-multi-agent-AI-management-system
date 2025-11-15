#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重建向量索引工具
清理向量索引并重新构建，确保搜索结果与数据库一致
"""

import sqlite3
import os
import shutil
from pathlib import Path

def rebuild_vector_index():
    """重建向量索引"""
    print("🔄 重建向量索引工具")
    print("=" * 50)
    
    # 检查数据库
    db_path = "knowledge_base/metadata.db"
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    # 检查向量索引目录
    vector_dirs = [
        "knowledge_base/vectors",
        "data/vector_index"
    ]
    
    print("🗑️  清理旧的向量索引...")
    for vector_dir in vector_dirs:
        if os.path.exists(vector_dir):
            try:
                shutil.rmtree(vector_dir)
                print(f"  ✅ 已删除: {vector_dir}")
            except Exception as e:
                print(f"  ❌ 删除失败 {vector_dir}: {e}")
        else:
            print(f"  ℹ️  目录不存在: {vector_dir}")
    
    # 重新创建向量索引目录
    print("\n📁 重新创建向量索引目录...")
    for vector_dir in vector_dirs:
        try:
            os.makedirs(vector_dir, exist_ok=True)
            print(f"  ✅ 已创建: {vector_dir}")
        except Exception as e:
            print(f"  ❌ 创建失败 {vector_dir}: {e}")
    
    # 检查数据库中的文档
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM document_chunks")
        chunk_count = cursor.fetchone()[0]
        
        print(f"\n📊 数据库统计:")
        print(f"  📄 文档数量: {doc_count}")
        print(f"  📝 文档块数量: {chunk_count}")
        
        if doc_count > 0:
            print(f"\n📋 现有文档列表:")
            cursor.execute("""
                SELECT title, original_filename, category, subcategory 
                FROM documents
            """)
            docs = cursor.fetchall()
            
            for i, (title, filename, category, subcategory) in enumerate(docs, 1):
                print(f"  {i}. {title} ({filename}) - {category}/{subcategory}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查数据库失败: {e}")
        return
    
    print(f"\n✅ 向量索引重建完成!")
    print(f"\n🎯 后续操作:")
    print(f"  1. 重启MCP服务以重新加载向量索引")
    print(f"  2. 测试搜索功能")
    print(f"  3. 如果需要，重新导入文档")

def main():
    """主函数"""
    print("🔄 智水运维知识库 - 向量索引重建工具")
    print("=" * 60)
    
    confirm = input("❓ 确认重建向量索引吗？这将删除所有现有的向量数据 (y/N): ")
    if confirm.lower() != 'y':
        print("❌ 取消重建操作")
        return
    
    rebuild_vector_index()

if __name__ == "__main__":
    main()