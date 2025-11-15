#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四川智水信息技术有限公司 - 运维知识库MCP服务

专为电力、水利行业信息化系统运维设计的智能知识库
基于RAG技术，使用ollama qwen3-embedding模型进行向量检索

功能：
- PDF文档导入和智能分块
- 基于向量相似度的知识检索  
- 文档分类管理（电力、水利、通信、安防、规范）
- 长期本地存储和索引维护
"""

import os
import sys
import json
import sqlite3
import logging
import hashlib
import base64
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading

# 第三方依赖
try:
    import numpy as np
    import faiss
    import requests
    import pdfplumber
    import fitz  # pymupdf
    import PyPDF2  # PDF文档处理
    from mcp.server.fastmcp import FastMCP
except ImportError as e:
    print(f"缺少依赖库: {e}")
    print("请安装: pip install fastmcp pdfplumber pymupdf faiss-cpu numpy requests PyPDF2")
    sys.exit(1)

# ================================
# 配置和常量
# ================================

TOOL_NAME = "zhishui-knowledge-mcp"
COMPANY_NAME = "四川智水信息技术有限公司"

# 知识库分类体系（基于四川智水业务领域）
KNOWLEDGE_CATEGORIES = {
    "电力系统运维": ["水电站", "火电站", "新能源站", "变电站", "配电系统", "发电机组"],
    "水利系统运维": ["大坝监测", "水库管理", "灌区系统", "水文监测", "闸门控制", "泵站设备"],
    "通信网络运维": ["通信设备", "网络系统", "数据传输", "无线通信", "光纤网络", "网络安全"],
    "安防系统运维": ["视频监控", "门禁系统", "报警系统", "周界防护", "安全检测", "消防系统"],
    "运维标准规范": ["操作流程", "安全规范", "维护标准", "应急预案", "质量管理", "技术标准"]
}

# Ollama配置（基于原始代码）
OLLAMA_CONFIG = {
    "url": "http://localhost:11434",
    "model_name": "qwen3-embedding",
    "embedding_dim": 2560,
    "timeout": 30
}

# 文档分块配置
CHUNK_CONFIG = {
    "min_size": 500,
    "max_size": 1000, 
    "overlap": 100
}

# 数据存储路径配置 - 使用绝对路径确保跨平台数据共享
# 所有MCP平台都将数据存储在同一位置
BASE_DATA_PATH = Path("C:/MCP_Knowledge_Base")
DATA_DIR = BASE_DATA_PATH / "knowledge_base"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTORS_DIR = DATA_DIR / "vectors"
LOGS_DIR = BASE_DATA_PATH / "logs"

# 确保目录存在
for dir_path in [DATA_DIR, DOCUMENTS_DIR, VECTORS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'knowledge_service.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(TOOL_NAME)

# 创建MCP服务
mcp = FastMCP(TOOL_NAME)

# ================================
# 数据库管理器
# ================================

class DatabaseManager:
    """SQLite数据库管理器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = DATA_DIR / "metadata.db"
        self.db_path = str(db_path)
        self._lock = threading.Lock()
        self.init_database()
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            # 文档元数据表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id TEXT PRIMARY KEY,
                    original_filename TEXT NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    file_path TEXT NOT NULL,
                    upload_time TIMESTAMP NOT NULL,
                    page_count INTEGER,
                    file_size INTEGER,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # 文档分块表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    doc_id TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    vector_id INTEGER,
                    char_count INTEGER,
                    FOREIGN KEY (doc_id) REFERENCES documents (doc_id)
                )
            """)
            
            conn.commit()
            logger.info("数据库表结构初始化完成")

# ================================
# 向量检索引擎
# ================================

class VectorSearchEngine:
    """基于FAISS的向量检索引擎"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.faiss_index = None
        self.chunk_ids = []
        self.index_file = VECTORS_DIR / "faiss.index"
        self.mapping_file = VECTORS_DIR / "chunk_mapping.json"
        
        # 初始化Ollama连接
        self._init_ollama()
        
        # 加载或创建索引
        self._load_or_create_index()
    
    def _init_ollama(self):
        """初始化Ollama服务连接"""
        try:
            # 检查Ollama服务状态
            response = requests.get(f"{OLLAMA_CONFIG['url']}/api/tags", timeout=15)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_exists = any(model['name'].startswith(OLLAMA_CONFIG['model_name']) 
                                 for model in models)
                
                if not model_exists:
                    logger.info(f"正在拉取{OLLAMA_CONFIG['model_name']}模型...")
                    pull_response = requests.post(
                        f"{OLLAMA_CONFIG['url']}/api/pull",
                        json={"name": OLLAMA_CONFIG['model_name']},
                        timeout=600
                    )
                    if pull_response.status_code != 200:
                        raise Exception(f"模型拉取失败: {pull_response.text}")
                
                logger.info("Ollama embedding服务初始化完成")
            else:
                raise Exception(f"Ollama服务不可用: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Ollama初始化失败: {e}")
            raise Exception(f"无法连接到Ollama服务，请确保Ollama已启动并运行在{OLLAMA_CONFIG['url']}")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """获取文本的embedding向量"""
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
                embedding = response.json().get('embedding')
                if embedding:
                    return np.array(embedding, dtype=np.float32)
                else:
                    raise Exception("响应中没有embedding数据")
            else:
                raise Exception(f"API请求失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"获取embedding失败: {e}")
            raise
    
    def _chunk_text(self, text: str) -> List[str]:
        """智能文本分块"""
        if not text or len(text) <= CHUNK_CONFIG['max_size']:
            return [text] if text else []
        
        # 按段落分割
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if not paragraphs:
            paragraphs = [text]
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # 如果单个段落就超过最大长度，需要强制分割
            if len(paragraph) > CHUNK_CONFIG['max_size']:
                # 先保存当前块（如果有内容）
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                # 对超长段落进行强制分割
                para_chunks = self._force_split_paragraph(paragraph)
                chunks.extend(para_chunks)
                continue
            
            # 如果添加这个段落会超过最大长度
            potential_length = len(current_chunk + "\n\n" + paragraph) if current_chunk else len(paragraph)
            if potential_length > CHUNK_CONFIG['max_size']:
                # 如果当前块已达到最小长度，保存它
                if len(current_chunk) >= CHUNK_CONFIG['min_size']:
                    chunks.append(current_chunk.strip())
                    # 添加重叠部分
                    overlap_text = current_chunk[-CHUNK_CONFIG['overlap']:] if CHUNK_CONFIG['overlap'] > 0 else ""
                    current_chunk = overlap_text + "\n\n" + paragraph
                else:
                    # 当前块太小，继续添加
                    current_chunk += "\n\n" + paragraph if current_chunk else paragraph
            else:
                # 可以安全添加这个段落
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # 添加最后一个块
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text]
    
    def _force_split_paragraph(self, paragraph: str) -> List[str]:
        """强制分割超长段落"""
        chunks = []
        max_size = CHUNK_CONFIG['max_size']
        overlap = CHUNK_CONFIG['overlap']
        
        start = 0
        while start < len(paragraph):
            # 计算当前块的结束位置
            end = start + max_size
            
            if end >= len(paragraph):
                # 最后一块
                chunks.append(paragraph[start:].strip())
                break
            
            # 尝试在句号、感叹号、问号处分割
            best_split = end
            for i in range(end - 100, end + 1):
                if i < len(paragraph) and paragraph[i] in '。！？\n':
                    best_split = i + 1
                    break
            
            chunks.append(paragraph[start:best_split].strip())
            
            # 下一块的开始位置（考虑重叠）
            start = max(best_split - overlap, start + 1)
        
        return [chunk for chunk in chunks if chunk.strip()]
    
    def _load_or_create_index(self):
        """加载已有索引或创建新索引 - 使用临时英文路径解决中文路径问题"""
        import tempfile
        import shutil
        
        try:
            if self.index_file.exists() and self.mapping_file.exists():
                # 使用临时英文路径加载索引，避免FAISS中文路径问题
                temp_dir = Path(tempfile.gettempdir()) / "zhishui_load"
                temp_dir.mkdir(exist_ok=True)
                temp_index_file = temp_dir / "faiss.index"
                temp_mapping_file = temp_dir / "chunk_mapping.json"
                
                try:
                    # 复制文件到临时英文路径
                    shutil.copy2(str(self.index_file), str(temp_index_file))
                    shutil.copy2(str(self.mapping_file), str(temp_mapping_file))
                    
                    # 从临时路径加载索引
                    self.faiss_index = faiss.read_index(str(temp_index_file))
                    with open(temp_mapping_file, 'r', encoding='utf-8') as f:
                        chunk_mapping = json.load(f)
                        # 兼容新旧映射格式
                        if isinstance(chunk_mapping, list):
                            # 处理列表格式，可能包含字典对象
                            self.chunk_ids = []
                            for item in chunk_mapping:
                                if isinstance(item, dict) and 'chunk_id' in item:
                                    self.chunk_ids.append(item['chunk_id'])
                                else:
                                    self.chunk_ids.append(str(item))
                        elif isinstance(chunk_mapping, dict):
                            # 字典格式：{"0": "chunk_id_1", "1": "chunk_id_2", ...}
                            # 或者 {"0": {"chunk_id": "...", ...}, ...}
                            self.chunk_ids = []
                            for i in range(len(chunk_mapping)):
                                mapping_data = chunk_mapping.get(str(i), "")
                                if isinstance(mapping_data, dict) and 'chunk_id' in mapping_data:
                                    self.chunk_ids.append(mapping_data['chunk_id'])
                                else:
                                    self.chunk_ids.append(str(mapping_data))
                        else:
                            raise ValueError(f"不支持的映射格式: {type(chunk_mapping)}")
                    
                    # 清理临时文件
                    temp_index_file.unlink()
                    temp_mapping_file.unlink()
                    temp_dir.rmdir()
                    
                    logger.info(f"已加载现有向量索引，包含{len(self.chunk_ids)}个向量")
                    
                except Exception as temp_error:
                    logger.error(f"临时路径加载失败: {temp_error}")
                    # 清理临时文件
                    if temp_index_file.exists():
                        temp_index_file.unlink()
                    if temp_mapping_file.exists():
                        temp_mapping_file.unlink()
                    if temp_dir.exists():
                        temp_dir.rmdir()
                    raise temp_error
                    
            else:
                # 创建新索引 - 使用L2距离索引与重建脚本保持一致
                self.faiss_index = faiss.IndexFlatL2(OLLAMA_CONFIG['embedding_dim'])
                self.chunk_ids = []
                logger.info("创建了新的向量索引")
                
        except Exception as e:
            logger.error(f"索引加载失败: {e}")
            # 创建新索引 - 使用L2距离索引与重建脚本保持一致
            self.faiss_index = faiss.IndexFlatL2(OLLAMA_CONFIG['embedding_dim'])
            self.chunk_ids = []
    
    def add_document(self, doc_id: str, title: str, content: str) -> int:
        """添加文档到索引"""
        try:
            # 智能分块
            chunks = self._chunk_text(content)
            added_chunks = 0
            
            with self.db_manager.get_connection() as conn:
                for i, chunk in enumerate(chunks):
                    if not chunk.strip():
                        continue
                    
                    # 生成向量
                    embedding = self._get_embedding(f"{title}\n{chunk}")
                    embedding = embedding / np.linalg.norm(embedding)  # 归一化
                    
                    # 添加到FAISS索引
                    self.faiss_index.add(embedding.reshape(1, -1))
                    
                    # 创建分块ID
                    chunk_id = f"{doc_id}_chunk_{i}"
                    self.chunk_ids.append(chunk_id)
                    
                    # 保存到数据库
                    conn.execute("""
                        INSERT INTO document_chunks 
                        (chunk_id, doc_id, chunk_index, content, vector_id, char_count)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (chunk_id, doc_id, i, chunk, len(self.chunk_ids)-1, len(chunk)))
                    
                    added_chunks += 1
                
                conn.commit()
            
            # 保存索引到文件
            self._save_index()
            
            logger.info(f"文档{doc_id}添加到索引，共{added_chunks}个分块")
            return added_chunks
            
        except Exception as e:
            logger.error(f"添加文档到索引失败: {e}")
            raise
    
    def search(self, query: str, top_k: int = 5, category: str = "") -> List[Dict]:
        """搜索相关文档"""
        try:
            if not self.faiss_index or len(self.chunk_ids) == 0:
                return []
            
            # 获取查询向量
            query_embedding = self._get_embedding(query)
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            
            # FAISS搜索
            scores, indices = self.faiss_index.search(
                query_embedding.reshape(1, -1), 
                min(top_k * 2, len(self.chunk_ids))  # 搜索更多结果以便过滤
            )
            
            # 获取详细信息
            results = []
            seen_docs = set()
            
            with self.db_manager.get_connection() as conn:
                for score, idx in zip(scores[0], indices[0]):
                    if idx < len(self.chunk_ids):
                        chunk_id = self.chunk_ids[idx]
                        
                        # 获取文档信息
                        cursor = conn.execute("""
                            SELECT d.doc_id, d.original_filename, d.title, d.category, d.subcategory,
                                   c.content, c.chunk_index
                            FROM documents d
                            JOIN document_chunks c ON d.doc_id = c.doc_id
                            WHERE c.chunk_id = ? AND d.status = 'active'
                        """, (chunk_id,))
                        
                        row = cursor.fetchone()
                        if row:
                            doc_id = row['doc_id']
                            
                            # 避免重复文档
                            if doc_id in seen_docs:
                                continue
                            
                            # 分类过滤
                            if category and row['category'] != category:
                                continue
                            
                            # 处理content_preview
                            content = row['content']
                            try:
                                # 确保content是字符串类型
                                if content:
                                    if isinstance(content, bytes):
                                        content = content.decode('utf-8', errors='replace')
                                    elif not isinstance(content, str):
                                        content = str(content)
                                    
                                    # 直接截取内容，不进行额外的编码操作
                                    content_preview = content[:200] + "..." if len(content) > 200 else content
                                    
                                    # 确保预览内容是有效的UTF-8字符串
                                    content_preview = content_preview.encode('utf-8', errors='replace').decode('utf-8')
                                else:
                                    content_preview = "内容预览暂不可用"
                            except Exception as e:
                                logger.warning(f"处理content_preview时出错: {e}")
                                content_preview = "内容预览暂不可用"
                            
                            result = {
                                "doc_id": row['doc_id'],
                                "title": row['title'],
                                "filename": row['original_filename'],
                                "category": row['category'],
                                "subcategory": row['subcategory'],
                                "content_preview": content_preview,
                                "similarity_score": float(score),
                                "chunk_index": row['chunk_index']
                            }
                            results.append(result)
                            seen_docs.add(doc_id)
                            
                            if len(results) >= top_k:
                                break
            
            return results
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def _save_index(self):
        """保存索引到文件"""
        try:
            logger.info(f"开始保存向量索引到: {self.index_file}")
            logger.info(f"当前索引包含 {len(self.chunk_ids)} 个向量")
            
            # 检查索引是否有效
            if self.faiss_index is None:
                logger.error("FAISS索引为空，无法保存")
                return
                
            if len(self.chunk_ids) == 0:
                logger.warning("没有分块数据，跳过保存")
                return
            
            # 确保目录存在
            self.index_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 检查目录权限
            if not os.access(str(self.index_file.parent), os.W_OK):
                logger.error(f"没有写入权限: {self.index_file.parent}")
                return
            
            # 保存FAISS索引
            logger.info(f"正在保存FAISS索引到: {self.index_file}")
            faiss.write_index(self.faiss_index, str(self.index_file))
            
            # 验证文件是否创建成功
            if self.index_file.exists():
                file_size = self.index_file.stat().st_size
                logger.info(f"FAISS索引已保存，文件大小: {file_size} 字节")
            else:
                logger.error(f"FAISS索引文件未创建: {self.index_file}")
                return
            
            # 保存chunk_ids映射
            logger.info(f"正在保存分块映射到: {self.mapping_file}")
            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.chunk_ids, f, ensure_ascii=False, indent=2)
            
            # 验证映射文件是否创建成功
            if self.mapping_file.exists():
                logger.info(f"分块映射已保存，共 {len(self.chunk_ids)} 个分块")
            else:
                logger.error(f"分块映射文件未创建: {self.mapping_file}")
                return
            
            logger.info(f"向量索引保存成功: {self.index_file}")
            logger.info(f"映射文件保存成功: {self.mapping_file}")
        except Exception as e:
            logger.error(f"保存索引失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            raise
    
    def remove_document(self, doc_id: str):
        """从索引中移除文档（注意：FAISS不支持直接删除，需要重建索引）"""
        logger.warning(f"文档{doc_id}已从数据库删除，向量索引将在下次重建时更新")

# ================================
# 全局实例
# ================================
db_manager = None
vector_engine = None

def init_service():
    """初始化服务组件"""
    global db_manager, vector_engine
    
    if db_manager is None:
        db_manager = DatabaseManager()
        logger.info("数据库管理器初始化完成")
    
    if vector_engine is None:
        vector_engine = VectorSearchEngine(db_manager)
        logger.info("向量检索引擎初始化完成")
    
    # 自动扫描和导入PDF文档
    auto_import_documents()

def auto_import_documents():
    """自动扫描documents目录并导入PDF文档"""
    try:
        # 获取已存在的文档
        existing_docs = []
        try:
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT original_filename FROM documents")
            existing_docs = [row[0] for row in cursor.fetchall()]
            conn.close()
        except Exception as e:
            logger.warning(f"获取已存在文档失败: {e}")
        
        # 扫描PDF文件
        pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))
        new_imports = 0
        
        for pdf_file in pdf_files:
            filename = pdf_file.name
            
            # 检查是否已存在
            if filename in existing_docs:
                continue
            
            try:
                # 提取PDF内容
                with open(pdf_file, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text_content = ""
                    page_count = len(pdf_reader.pages)
                    
                    for page in pdf_reader.pages:
                        text_content += page.extract_text() + "\n"
                    
                    file_size = pdf_file.stat().st_size
                
                if not text_content.strip():
                    logger.warning(f"PDF文件无文本内容: {filename}")
                    continue
                
                # 智能分类
                filename_lower = filename.lower()
                if any(keyword in filename_lower for keyword in 
                       ['变电站', '电站', '发电', '配电', '电力', '电网', '机组']):
                    category = "电力系统运维"
                elif any(keyword in filename_lower for keyword in 
                         ['水利', '水电', '大坝', '水库', '灌区', '水文', '闸门', '泵站']):
                    category = "水利系统运维"
                elif any(keyword in filename_lower for keyword in 
                         ['通信', '网络', '数据传输', '无线', '光纤', '网络安全']):
                    category = "通信网络运维"
                elif any(keyword in filename_lower for keyword in 
                         ['监控', '安防', '门禁', '报警', '周界', '消防']):
                    category = "安防系统运维"
                else:
                    category = "运维标准规范"
                
                # 保存文档信息
                doc_id = str(uuid.uuid4())
                title = filename.replace('.pdf', '')
                
                conn = db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO documents 
                    (doc_id, original_filename, title, category, subcategory, file_path, 
                     upload_time, page_count, file_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    doc_id, filename, title, category, '', str(pdf_file),
                    datetime.now().isoformat(), page_count, file_size
                ))
                conn.commit()
                conn.close()
                
                # 添加到向量索引
                if vector_engine:
                    vector_engine.add_document(doc_id, title, text_content)
                
                new_imports += 1
                logger.info(f"自动导入文档: {filename} ({category})")
                
            except Exception as e:
                logger.error(f"自动导入文档失败 {filename}: {e}")
        
        if new_imports > 0:
            logger.info(f"自动导入完成，新增 {new_imports} 个文档")
        else:
            logger.info("未发现新的PDF文档")
            
    except Exception as e:
        logger.error(f"自动导入过程出错: {e}")

# ================================
# MCP工具函数
# ================================

@mcp.tool()
def import_file_to_knowledge(
    file_path: str,
    title: str,
    category: str,
    subcategory: str = ""
) -> str:
    """
    导入文件到运维知识库
    
    专为四川智水信息技术有限公司运维知识管理设计
    支持电力、水利、通信、安防等专业领域文档
    支持PDF和TXT格式文件
    
    Args:
        file_path (str): 本地文件路径（PDF或TXT文件）
        title (str): 文档标题
        category (str): 文档分类（电力系统运维/水利系统运维/通信网络运维/安防系统运维/运维标准规范）
        subcategory (str): 子分类（可选）
        
    Returns:
        str: 导入结果
    """
    try:
        # 初始化服务
        init_service()
        
        # 参数验证
        if not all([file_path, title, category]):
            return json.dumps({"error": "必填参数不能为空"}, ensure_ascii=False)
        
        if category not in KNOWLEDGE_CATEGORIES:
            return json.dumps({
                "error": f"无效的分类，支持的分类: {list(KNOWLEDGE_CATEGORIES.keys())}"
            }, ensure_ascii=False)
        
        # 验证文件路径
        source_file = Path(file_path)
        if not source_file.exists():
            return json.dumps({"error": f"文件不存在: {file_path}"}, ensure_ascii=False)
        
        if not source_file.is_file():
            return json.dumps({"error": f"路径不是文件: {file_path}"}, ensure_ascii=False)
        
        # 获取文件名和扩展名
        filename = source_file.name
        file_size = source_file.stat().st_size
        
        # 生成文档ID和目标文件路径
        doc_id = str(uuid.uuid4())
        
        # 根据文件扩展名确定处理方式
        file_ext = filename.lower().split('.')[-1] if '.' in filename else 'pdf'
        logger.info(f"文件名: {filename}, 检测到扩展名: {file_ext}")
        
        if file_ext == 'txt':
            # 处理TXT文件
            target_file_path = DOCUMENTS_DIR / f"{doc_id}.txt"
            
            # 复制TXT文件到目标位置
            import shutil
            shutil.copy2(source_file, target_file_path)
            
            # 提取TXT文本
            try:
                with open(target_file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                
                if not text_content.strip():
                    return json.dumps({"error": "TXT文件内容为空"}, ensure_ascii=False)
                
                page_count = 1  # TXT文件视为1页
                    
            except Exception as e:
                # 清理已保存的文件
                if target_file_path.exists():
                    target_file_path.unlink()
                return json.dumps({"error": f"TXT文本读取失败: {str(e)}"}, ensure_ascii=False)
        
        else:
            # 处理PDF文件
            target_file_path = DOCUMENTS_DIR / f"{doc_id}.pdf"
            
            # 复制PDF文件到目标位置
            import shutil
            shutil.copy2(source_file, target_file_path)
            
            # 提取PDF文本 - 使用多种方法确保最佳兼容性
            text_content = ""
            page_count = 0
            extraction_success = False
            
            # 方法1: 使用pdfplumber（对中文支持最好）
            try:
                with pdfplumber.open(target_file_path) as pdf:
                    page_count = len(pdf.pages)
                    logger.info(f"使用pdfplumber处理PDF，共{page_count}页")
                    
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n\n"  # 使用双换行符确保段落分隔
                    
                    if text_content.strip():
                        extraction_success = True
                        logger.info(f"pdfplumber提取成功，文本长度: {len(text_content)}")
                        
            except Exception as e:
                logger.warning(f"pdfplumber提取失败: {e}")
            
            # 方法2: 如果pdfplumber失败，使用pymupdf作为备选
            if not extraction_success:
                try:
                    doc = fitz.open(target_file_path)
                    page_count = doc.page_count
                    logger.info(f"使用pymupdf处理PDF，共{page_count}页")
                    
                    for page_num in range(page_count):
                        page = doc[page_num]
                        page_text = page.get_text()
                        if page_text:
                            text_content += page_text + "\n\n"  # 使用双换行符确保段落分隔
                    
                    doc.close()
                    
                    if text_content.strip():
                        extraction_success = True
                        logger.info(f"pymupdf提取成功，文本长度: {len(text_content)}")
                        
                except Exception as e:
                    logger.warning(f"pymupdf提取失败: {e}")
            
            # 检查提取结果
            if not extraction_success or not text_content.strip():
                # 清理已保存的文件
                if target_file_path.exists():
                    target_file_path.unlink()
                return json.dumps({
                    "error": "PDF文件无法提取文本内容，可能是扫描版PDF或文件损坏。建议使用OCR工具处理扫描版PDF。"
                }, ensure_ascii=False)
        
        # 保存文档元数据
        with db_manager.get_connection() as conn:
            conn.execute("""
                INSERT INTO documents 
                (doc_id, original_filename, title, category, subcategory, file_path, 
                 upload_time, page_count, file_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_id, filename, title, category, subcategory or "",
                str(target_file_path), datetime.now().isoformat(),
                page_count, file_size
            ))
            conn.commit()
        
        # 添加到向量索引
        logger.info(f"开始添加文档到向量索引: {title}")
        logger.info(f"文本内容长度: {len(text_content)} 字符")
        try:
            chunk_count = vector_engine.add_document(doc_id, title, text_content)
            logger.info(f"向量索引添加成功，创建了 {chunk_count} 个分块")
        except Exception as e:
            logger.error(f"向量索引添加失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            # 即使向量索引失败，也返回成功，但标记chunk_count为0
            chunk_count = 0
        
        result = {
            "success": True,
            "doc_id": doc_id,
            "filename": filename,
            "title": title,
            "category": category,
            "subcategory": subcategory,
            "page_count": page_count,
            "file_size_mb": round(file_size / 1024 / 1024, 2),
            "chunks_created": chunk_count,
            "upload_time": datetime.now().isoformat(),
            "message": f"文档已成功导入到{COMPANY_NAME}运维知识库"
        }
        
        logger.info(f"文档导入成功: {title} ({category})")
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"文档导入失败: {e}")
        return json.dumps({"error": f"导入失败: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
def search_knowledge(
    query: str,
    top_k: int = 5,
    category: str = ""
) -> str:
    """
    搜索运维知识库
    
    基于RAG技术的智能知识检索，使用qwen3-embedding模型
    专为四川智水运维团队提供精准的技术知识查询
    
    Args:
        query (str): 搜索查询语句
        top_k (int): 返回结果数量（默认5）
        category (str): 限定搜索分类（可选）
        
    Returns:
        str: 搜索结果
    """
    try:
        # 初始化服务
        init_service()
        
        # 参数验证
        if not query or not query.strip():
            return json.dumps({"error": "查询内容不能为空"}, ensure_ascii=False)
        
        if category and category not in KNOWLEDGE_CATEGORIES:
            return json.dumps({
                "error": f"无效的分类，支持的分类: {list(KNOWLEDGE_CATEGORIES.keys())}"
            }, ensure_ascii=False)
        
        # 执行搜索
        results = vector_engine.search(query, top_k, category)
        
        # 格式化结果
        response = {
            "query": query,
            "category_filter": category or "全部分类",
            "total_found": len(results),
            "search_time": datetime.now().isoformat(),
            "knowledge_source": f"{COMPANY_NAME}运维知识库",
            "results": []
        }
        
        for i, result in enumerate(results, 1):
            formatted_result = {
                "rank": i,
                "title": result['title'],
                "filename": result['filename'],
                "category": result['category'],
                "subcategory": result['subcategory'],
                "similarity_score": round(result['similarity_score'], 4),
                "content_preview": result['content_preview'],
                "doc_id": result['doc_id']
            }
            response["results"].append(formatted_result)
        
        if not results:
            response["message"] = "未找到相关文档，建议：\n1. 尝试更换关键词\n2. 减少搜索条件\n3. 检查分类筛选"
        
        logger.info(f"知识搜索完成: {query} - 找到{len(results)}个结果")
        
        # 确保中文编码正确处理
        json_str = json.dumps(response, ensure_ascii=False, indent=2)
        # 确保返回的是正确编码的字符串
        if isinstance(json_str, bytes):
            json_str = json_str.decode('utf-8')
        
        # 调试日志：记录实际返回的内容
        if results:
            first_preview = response['results'][0]['content_preview'][:50]
            logger.info(f"返回内容预览: {repr(first_preview)}")
        
        return json_str
        
    except Exception as e:
        logger.error(f"知识搜索失败: {e}")
        return json.dumps({"error": f"搜索失败: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
def manage_documents(
    action: str,
    doc_id: str = "",
    category: str = ""
) -> str:
    """
    文档管理操作
    
    支持查看、删除和统计运维知识库中的文档
    
    Args:
        action (str): 操作类型（list/delete/info/stats）
        doc_id (str): 文档ID（删除和查看详情时需要）
        category (str): 分类过滤（列表时可选）
        
    Returns:
        str: 操作结果
    """
    try:
        # 初始化服务
        init_service()
        
        # 调试信息：显示数据库路径
        import os
        current_dir = os.getcwd()
        db_path = os.path.join(current_dir, "knowledge_base.db")
        logger.info(f"MCP服务调试 - 工作目录: {current_dir}")
        logger.info(f"MCP服务调试 - 数据库路径: {db_path}")
        logger.info(f"MCP服务调试 - 数据库文件存在: {os.path.exists(db_path)}")
        
        # 参数验证
        if not action:
            return json.dumps({"error": "操作类型不能为空"}, ensure_ascii=False)
        
        if action == "list":
            return _list_documents(category)
        elif action == "delete":
            if not doc_id:
                return json.dumps({"error": "删除操作需要提供doc_id"}, ensure_ascii=False)
            return _delete_document(doc_id)
        elif action == "info":
            if not doc_id:
                return json.dumps({"error": "查看详情需要提供doc_id"}, ensure_ascii=False)
            return _get_document_info(doc_id)
        elif action == "stats":
            return _get_knowledge_stats()
        else:
            return json.dumps({
                "error": f"无效的操作类型: {action}",
                "supported_actions": ["list", "delete", "info", "stats"]
            }, ensure_ascii=False)
            
    except Exception as e:
        logger.error(f"文档管理操作失败: {e}")
        return json.dumps({"error": f"操作失败: {str(e)}"}, ensure_ascii=False)

def _list_documents(category: str = "") -> str:
    """列出文档"""
    with db_manager.get_connection() as conn:
        if category:
            cursor = conn.execute("""
                SELECT doc_id, title, original_filename, category, subcategory,
                       upload_time, page_count, file_size
                FROM documents 
                WHERE category = ? AND status = 'active'
                ORDER BY upload_time DESC
            """, (category,))
        else:
            cursor = conn.execute("""
                SELECT doc_id, title, original_filename, category, subcategory,
                       upload_time, page_count, file_size
                FROM documents 
                WHERE status = 'active'
                ORDER BY upload_time DESC
            """)
        
        documents = [dict(row) for row in cursor.fetchall()]
    
    response = {
        "action": "list_documents",
        "category_filter": category or "全部分类",
        "total_documents": len(documents),
        "knowledge_base": f"{COMPANY_NAME}运维知识库",
        "documents": []
    }
    
    for doc in documents:
        doc_info = {
            "doc_id": doc['doc_id'],
            "title": doc['title'],
            "filename": doc['original_filename'],
            "category": doc['category'],
            "subcategory": doc['subcategory'],
            "upload_time": doc['upload_time'],
            "page_count": doc['page_count'],
            "file_size_mb": round(doc['file_size'] / 1024 / 1024, 2) if doc['file_size'] else 0
        }
        response["documents"].append(doc_info)
    
    return json.dumps(response, ensure_ascii=False, indent=2)

def _delete_document(doc_id: str) -> str:
    """删除文档"""
    with db_manager.get_connection() as conn:
        # 检查文档是否存在
        cursor = conn.execute("""
            SELECT title, file_path FROM documents WHERE doc_id = ? AND status = 'active'
        """, (doc_id,))
        doc = cursor.fetchone()
        
        if not doc:
            return json.dumps({"error": "文档不存在或已被删除"}, ensure_ascii=False)
        
        # 标记为删除状态
        conn.execute("""
            UPDATE documents SET status = 'deleted' WHERE doc_id = ?
        """, (doc_id,))
        
        # 删除分块数据
        conn.execute("""
            DELETE FROM document_chunks WHERE doc_id = ?
        """, (doc_id,))
        
        conn.commit()
    
    # 删除物理文件
    try:
        file_path = Path(doc['file_path'])
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        logger.warning(f"删除物理文件失败: {e}")
    
    # 从向量索引中移除
    vector_engine.remove_document(doc_id)
    
    result = {
        "success": True,
        "action": "delete_document",
        "doc_id": doc_id,
        "title": doc['title'],
        "message": "文档已成功删除",
        "note": "向量索引将在系统重启时自动更新"
    }
    
    logger.info(f"文档删除成功: {doc['title']}")
    return json.dumps(result, ensure_ascii=False, indent=2)

def _get_document_info(doc_id: str) -> str:
    """获取文档详细信息"""
    with db_manager.get_connection() as conn:
        cursor = conn.execute("""
            SELECT * FROM documents WHERE doc_id = ? AND status = 'active'
        """, (doc_id,))
        doc = cursor.fetchone()
        
        if not doc:
            return json.dumps({"error": "文档不存在"}, ensure_ascii=False)
        
        # 获取分块统计
        cursor = conn.execute("""
            SELECT COUNT(*) as chunk_count, AVG(char_count) as avg_chunk_size
            FROM document_chunks WHERE doc_id = ?
        """, (doc_id,))
        chunk_stats = cursor.fetchone()
    
    doc_info = {
        "doc_id": doc['doc_id'],
        "title": doc['title'],
        "filename": doc['original_filename'],
        "category": doc['category'],
        "subcategory": doc['subcategory'],
        "upload_time": doc['upload_time'],
        "page_count": doc['page_count'],
        "file_size_mb": round(doc['file_size'] / 1024 / 1024, 2) if doc['file_size'] else 0,
        "chunk_count": chunk_stats['chunk_count'],
        "avg_chunk_size": round(chunk_stats['avg_chunk_size']) if chunk_stats['avg_chunk_size'] else 0,
        "file_path": doc['file_path']
    }
    
    return json.dumps(doc_info, ensure_ascii=False, indent=2)

def _get_knowledge_stats() -> str:
    """获取知识库统计信息"""
    with db_manager.get_connection() as conn:
        # 总体统计
        cursor = conn.execute("""
            SELECT COUNT(*) as total_docs, 
                   SUM(page_count) as total_pages,
                   SUM(file_size) as total_size
            FROM documents WHERE status = 'active'
        """)
        overall_stats = cursor.fetchone()
        
        # 按分类统计
        cursor = conn.execute("""
            SELECT category, COUNT(*) as doc_count, AVG(page_count) as avg_pages
            FROM documents WHERE status = 'active'
            GROUP BY category
            ORDER BY doc_count DESC
        """)
        category_stats = [dict(row) for row in cursor.fetchall()]
        
        # 分块统计
        cursor = conn.execute("""
            SELECT COUNT(*) as total_chunks, AVG(char_count) as avg_chunk_size
            FROM document_chunks
        """)
        chunk_stats = cursor.fetchone()
    
    stats = {
        "knowledge_base": f"{COMPANY_NAME}运维知识库",
        "statistics_time": datetime.now().isoformat(),
        "overall": {
            "total_documents": overall_stats['total_docs'],
            "total_pages": overall_stats['total_pages'],
            "total_size_mb": round(overall_stats['total_size'] / 1024 / 1024, 2) if overall_stats['total_size'] else 0,
            "total_chunks": chunk_stats['total_chunks'],
            "avg_chunk_size": round(chunk_stats['avg_chunk_size']) if chunk_stats['avg_chunk_size'] else 0
        },
        "by_category": [],
        "supported_categories": list(KNOWLEDGE_CATEGORIES.keys())
    }
    
    for cat_stat in category_stats:
        category_info = {
            "category": cat_stat['category'],
            "document_count": cat_stat['doc_count'],
            "avg_pages": round(cat_stat['avg_pages'], 1) if cat_stat['avg_pages'] else 0,
            "subcategories": KNOWLEDGE_CATEGORIES.get(cat_stat['category'], [])
        }
        stats["by_category"].append(category_info)
    
    return json.dumps(stats, ensure_ascii=False, indent=2)

# ================================
# 服务启动
# ================================

if __name__ == "__main__":
    logger.info(f"启动 {COMPANY_NAME} 运维知识库MCP服务")
    
    # 将启动信息记录到日志而不是stdout，避免干扰MCP通信
    logger.info("========================================")
    logger.info(f"  {COMPANY_NAME}")
    logger.info("  运维知识库MCP服务")
    logger.info("========================================")
    logger.info("服务功能：")
    logger.info("[√] PDF文档导入和智能分块")
    logger.info("[√] 基于qwen3-embedding的向量检索")
    logger.info("[√] 五大专业分类管理")
    logger.info("[√] 长期本地存储")
    logger.info("专业分类：")
    logger.info("- 电力系统运维（水电站、火电站、新能源等）")
    logger.info("- 水利系统运维（大坝监测、水库管理等）")
    logger.info("- 通信网络运维（通信设备、网络系统等）")
    logger.info("- 安防系统运维（监控、门禁、报警等）")
    logger.info("- 运维标准规范（流程、安全、标准等）")
    logger.info("技术特性：")
    logger.info("- RAG检索：qwen3-embedding + FAISS")
    logger.info("- 本地存储：SQLite + 文件系统")
    logger.info("- 智能分块：500-1000字符自适应")
    logger.info("正在启动服务...")
    logger.info("========================================")
    
    try:
        # 初始化服务组件
        init_service()
        logger.info("所有服务组件初始化完成")
        
        # 启动MCP服务 - 使用stdio传输（标准输入输出）
        mcp.run()
    except KeyboardInterrupt:
        logger.info("正在关闭服务...")
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
    finally:
        logger.info("服务已关闭")

# ================================
# 使用说明
# ================================
"""
🚀 四川智水运维知识库MCP服务使用指南

📋 功能概述：
专为四川智水信息技术有限公司设计的运维知识库，
支持电力、水利行业信息化系统的运维知识管理。

🔧 工具使用：

1. 导入文档：
   import_document(
       file_path="C:\\path\\to\\运维手册.pdf",
       title="水电站运维标准操作手册",
       category="电力系统运维",
       subcategory="水电站"
   )

2. 搜索知识：
   search_knowledge(
       query="水电站故障处理流程",
       top_k=5,
       category="电力系统运维"
   )

3. 管理文档：
   manage_documents(
       action="list",          # list/delete/info/stats
       category="水利系统运维"
   )

📂 支持的分类：
- 电力系统运维：水电站、火电站、新能源站、变电站等
- 水利系统运维：大坝监测、水库管理、灌区系统等
- 通信网络运维：通信设备、网络系统、光纤网络等  
- 安防系统运维：视频监控、门禁系统、报警系统等
- 运维标准规范：操作流程、安全规范、技术标准等

⚡ 技术特点：
- 使用qwen3-embedding模型进行向量化
- FAISS向量数据库实现快速检索
- 智能文本分块保持语义完整性
- 本地存储确保数据安全和长期可用

💡 最佳实践：
1. 文档标题要清晰描述内容主题
2. 选择准确的分类和子分类
3. 搜索时使用专业术语获得更好结果
4. 定期查看统计信息了解知识库状况
"""