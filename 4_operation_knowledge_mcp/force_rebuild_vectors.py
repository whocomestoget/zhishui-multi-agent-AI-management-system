#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制重建向量索引脚本
从数据库重新读取所有文档内容并重建向量索引
"""

import os
import sys
import sqlite3
import json
import numpy as np
import faiss
import requests
from pathlib import Path

# 配置
DB_PATH = "knowledge_base/metadata.db"
VECTORS_DIR = Path("knowledge_base/vectors")
INDEX_FILE = VECTORS_DIR / "faiss_index.bin"
MAPPING_FILE = VECTORS_DIR / "chunk_mapping.json"

# Ollama配置
OLLAMA_CONFIG = {
    "url": "http://localhost:11434",
    "model_name": "qwen3-embedding",
    "embedding_dim": 2560,
    "timeout": 30
}

def get_embedding(text: str) -> np.ndarray:
    """获取文本的向量表示"""
    try:
        response = requests.post(
            f"{OLLAMA_CONFIG['url']}/api/embeddings",
            json={
                "model": OLLAMA_CONFIG['model_name'],
                "prompt": text
            },
            timeout=OLLAMA_CONFIG['timeout']
        )
        
        if response.status_code == 200:
            embedding = response.json()['embedding']
            return np.array(embedding, dtype=np.float32)
        else:
            print(f"Embedding API错误: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"获取embedding失败: {e}")
        return None

def force_rebuild_vectors():
    """
    强制重建向量索引
    """
    print("开始强制重建向量索引...")
    
    try:
        # 1. 删除现有索引文件
        if INDEX_FILE.exists():
            INDEX_FILE.unlink()
            print(f"已删除索引文件: {INDEX_FILE}")
        
        if MAPPING_FILE.exists():
            MAPPING_FILE.unlink()
            print(f"已删除映射文件: {MAPPING_FILE}")
        
        # 2. 从数据库读取所有文档分块
        print("从数据库读取文档分块...")
        
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT c.chunk_id, c.content, d.title, d.category
                FROM document_chunks c
                JOIN documents d ON c.doc_id = d.doc_id
                WHERE d.status = 'active'
                ORDER BY c.chunk_id
            """)
            
            chunks = cursor.fetchall()
            print(f"找到 {len(chunks)} 个文档分块")
        
        if not chunks:
            print("没有找到任何文档分块")
            return False
        
        # 3. 检查修复后的内容示例
        print("\n检查修复后的内容示例:")
        for i, chunk in enumerate(chunks[:3]):
            content_preview = chunk['content'][:100]
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in content_preview)
            print(f"分块 {i+1}: {chunk['title']} - 包含中文: {has_chinese}")
            print(f"内容预览: {content_preview}")
            print()
        
        # 4. 生成向量
        print("开始生成向量...")
        embeddings = []
        chunk_ids = []
        
        for i, chunk in enumerate(chunks):
            print(f"处理分块 {i+1}/{len(chunks)}: {chunk['chunk_id']}")
            
            # 获取向量
            embedding = get_embedding(chunk['content'])
            if embedding is not None:
                embeddings.append(embedding)
                chunk_ids.append(chunk['chunk_id'])
            else:
                print(f"跳过分块 {chunk['chunk_id']} (向量生成失败)")
        
        if not embeddings:
            print("没有成功生成任何向量")
            return False
        
        print(f"成功生成 {len(embeddings)} 个向量")
        
        # 5. 构建FAISS索引
        print("构建FAISS索引...")
        embeddings_matrix = np.vstack(embeddings)
        
        # 归一化向量
        norms = np.linalg.norm(embeddings_matrix, axis=1, keepdims=True)
        embeddings_matrix = embeddings_matrix / norms
        
        # 创建FAISS索引
        index = faiss.IndexFlatIP(OLLAMA_CONFIG['embedding_dim'])
        index.add(embeddings_matrix)
        
        # 6. 保存索引和映射
        VECTORS_DIR.mkdir(parents=True, exist_ok=True)
        
        faiss.write_index(index, str(INDEX_FILE))
        print(f"索引已保存到: {INDEX_FILE}")
        
        with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
            json.dump(chunk_ids, f, ensure_ascii=False, indent=2)
        print(f"映射已保存到: {MAPPING_FILE}")
        
        print(f"\n✅ 向量索引重建完成")
        print(f"- 索引包含 {len(embeddings)} 个向量")
        print(f"- 向量维度: {OLLAMA_CONFIG['embedding_dim']}")
        
        return True
        
    except Exception as e:
        print(f"重建向量索引失败: {e}")
        return False

if __name__ == "__main__":
    success = force_rebuild_vectors()
    if success:
        print("\n请重新启动MCP服务以加载新的向量索引")
    else:
        print("\n❌ 向量索引重建失败")
        sys.exit(1)