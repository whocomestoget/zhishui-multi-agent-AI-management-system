#!/usr/bin/env python3
"""
重置文档记录，以便重新处理应用新的分块逻辑
"""

import sqlite3
import shutil
from pathlib import Path

def reset_documents():
    """清理现有文档记录和向量索引"""
    
    # 数据库路径
    db_path = Path('C:/MCP_Knowledge_Base/knowledge_base/metadata.db')
    
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        return
    
    try:
        # 连接数据库
        conn = sqlite3.connect(str(db_path))
        
        # 查看当前文档
        cursor = conn.execute("SELECT doc_id, original_filename, status FROM documents")
        docs = cursor.fetchall()
        print(f"当前数据库中的文档:")
        for doc in docs:
            print(f"  {doc[0]} - {doc[1]} - {doc[2]}")
        
        # 清理文档记录
        print("\n清理文档记录...")
        conn.execute("DELETE FROM document_chunks")
        conn.execute("DELETE FROM documents")
        conn.commit()
        
        print("文档记录已清理")
        
        # 清理向量索引文件
        vectors_dir = Path('C:/MCP_Knowledge_Base/knowledge_base/vectors')
        if vectors_dir.exists():
            print("清理向量索引文件...")
            for file in vectors_dir.glob('*'):
                if file.is_file():
                    file.unlink()
                    print(f"  删除: {file.name}")
        
        # 清理本地向量文件
        local_vectors_dir = Path('./knowledge_base/vectors')
        if local_vectors_dir.exists():
            print("清理本地向量索引文件...")
            for file in local_vectors_dir.glob('*'):
                if file.is_file():
                    file.unlink()
                    print(f"  删除: {file.name}")
        
        conn.close()
        print("\n重置完成！重启服务后将重新处理PDF文档。")
        
    except Exception as e:
        print(f"重置时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reset_documents()