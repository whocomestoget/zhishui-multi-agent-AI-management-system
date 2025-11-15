#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重建向量索引脚本
用于在修复文本格式后重新构建FAISS向量索引
"""

import sqlite3
import numpy as np
import faiss
import json
import os
from pathlib import Path
import requests
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "qwen3-embedding"
EMBEDDING_DIM = None  # 动态检测维度

def get_embedding(text):
    """获取文本的向量表示"""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={
                "model": EMBEDDING_MODEL,
                "prompt": text
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            embedding = np.array(result['embedding'], dtype=np.float32)
            # 归一化向量
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            return embedding
        else:
            logger.error(f"获取向量失败: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"获取向量时出错: {e}")
        return None

def rebuild_vector_index():
    """重建向量索引"""
    logger.info("开始重建向量索引...")
    
    # 连接数据库
    db_path = "knowledge_base/metadata.db"
    if not os.path.exists(db_path):
        logger.error(f"数据库文件不存在: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # 获取所有文档块
        cursor = conn.execute("""
            SELECT chunk_id, content 
            FROM document_chunks 
            ORDER BY chunk_id
        """)
        
        chunks = cursor.fetchall()
        logger.info(f"找到 {len(chunks)} 个文档块")
        
        if not chunks:
            logger.warning("没有找到文档块")
            return False
        
        # 创建FAISS索引（动态检测维度）
        index = None
        chunk_mapping = {}
        
        # 处理每个文档块
        for i, chunk in enumerate(chunks):
            chunk_id = chunk['chunk_id']
            content = chunk['content']
            
            if not content or not content.strip():
                logger.warning(f"跳过空内容的块: {chunk_id}")
                continue
            
            # 获取向量
            embedding = get_embedding(content)
            if embedding is None:
                logger.warning(f"无法获取块 {chunk_id} 的向量")
                continue
            
            # 第一次获取向量时初始化索引
            if index is None:
                embedding_dim = len(embedding)
                logger.info(f"检测到向量维度: {embedding_dim}")
                index = faiss.IndexFlatIP(embedding_dim)
            
            # 添加到索引
            index.add(embedding.reshape(1, -1))
            chunk_mapping[index.ntotal - 1] = chunk_id
            
            if (i + 1) % 10 == 0:
                logger.info(f"已处理 {i + 1}/{len(chunks)} 个文档块")
        
        # 保存索引
        vectors_dir = Path("knowledge_base/vectors")
        vectors_dir.mkdir(exist_ok=True)
        
        index_file = vectors_dir / "faiss.index"
        mapping_file = vectors_dir / "chunk_mapping.json"
        
        # 保存FAISS索引
        faiss.write_index(index, str(index_file))
        
        # 保存映射关系
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(chunk_mapping, f, ensure_ascii=False, indent=2)
        
        logger.info(f"向量索引重建完成！")
        logger.info(f"- 索引文件: {index_file}")
        logger.info(f"- 映射文件: {mapping_file}")
        logger.info(f"- 总向量数: {index.ntotal}")
        
        return True
        
    except Exception as e:
        import traceback
        logger.error(f"重建索引时出错: {e}")
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== 向量索引重建工具 ===")
    print("此工具将使用修复后的文本内容重新构建向量索引")
    print()
    
    # 检查Ollama服务
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama服务不可用，请确保Ollama正在运行")
            exit(1)
    except:
        print("❌ 无法连接到Ollama服务，请确保Ollama正在运行")
        exit(1)
    
    print("✅ Ollama服务正常")
    
    # 开始重建
    success = rebuild_vector_index()
    
    if success:
        print("\n🎉 向量索引重建成功！")
        print("现在可以测试搜索功能了")
    else:
        print("\n❌ 向量索引重建失败")
        exit(1)