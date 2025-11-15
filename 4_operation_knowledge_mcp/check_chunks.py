#!/usr/bin/env python3
"""
检查PDF文档分块情况的脚本
"""

import sqlite3
from pathlib import Path

def check_document_chunks():
    """检查文档分块情况"""
    # 尝试多个可能的数据库路径
    possible_paths = [
        Path('C:/MCP_Knowledge_Base/knowledge_base/metadata.db'),  # 配置的路径
        Path('./knowledge_base/metadata.db'),  # 本地路径
        Path('./data/knowledge.db')  # 备用路径
    ]
    
    db_path = None
    for path in possible_paths:
        if path.exists():
            db_path = path
            break
    
    if not db_path:
        print("未找到数据库文件，尝试的路径:")
        for path in possible_paths:
            print(f"  - {path}")
        return
    
    print(f"使用数据库: {db_path}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        
        # 查找最新的PDF文档
        cursor = conn.execute("""
            SELECT doc_id, title, original_filename, upload_time 
            FROM documents 
            WHERE status = 'active' 
            ORDER BY upload_time DESC 
            LIMIT 1
        """)
        latest_doc = cursor.fetchone()
        
        if not latest_doc:
            print("没有找到活跃的文档")
            return
        
        doc_id = latest_doc['doc_id']
        print(f"最新文档: {latest_doc['title']} ({latest_doc['original_filename']})")
        print(f"文档ID: {doc_id}")
        print(f"上传时间: {latest_doc['upload_time']}")
        
        # 查询该文档的分块信息
        cursor = conn.execute("""
            SELECT chunk_id, chunk_index, char_count, content
            FROM document_chunks 
            WHERE doc_id = ? 
            ORDER BY chunk_index
        """, (doc_id,))
        
        chunks = cursor.fetchall()
        print(f"\n📊 分块统计:")
        print(f"总分块数: {len(chunks)}")
        
        if len(chunks) == 0:
            print("❌ 没有找到任何分块！")
            return
        
        total_chars = 0
        for i, chunk in enumerate(chunks):
            char_count = chunk['char_count']
            total_chars += char_count
            content_preview = chunk['content'][:100].replace('\n', ' ') if chunk['content'] else ""
            print(f"  📝 块{chunk['chunk_index']}: {char_count}字符")
            print(f"     内容预览: {content_preview}...")
            print()
        
        print(f"📈 总字符数: {total_chars}")
        print(f"📏 平均每块字符数: {total_chars // len(chunks) if len(chunks) > 0 else 0}")
        
        # 检查分块配置是否合理
        if len(chunks) == 1 and total_chars > 1000:
            print("\n⚠️  警告: 文档只有1个分块，但内容较长，可能分块配置有问题")
            print("   建议检查分块配置参数")
        elif len(chunks) > 1:
            print(f"\n✅ 分块正常: 文档被合理分割为{len(chunks)}个块")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查分块时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_document_chunks()