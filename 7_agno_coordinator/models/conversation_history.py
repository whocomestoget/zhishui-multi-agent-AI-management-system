#!/usr/bin/env python3
"""
对话历史数据模型
用于存储和管理用户与AI系统的对话记录

Author: 商海星辰队
Version: 1.0.0
"""

import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConversationMessage:
    """对话消息数据类"""
    id: str
    session_id: str
    user_message: str
    ai_response: Dict[str, Any]
    timestamp: str
    file_info: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class ConversationHistoryDB:
    """对话历史数据库管理器"""
    
    def __init__(self, db_path: str = "data/conversation_history.db"):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建对话历史表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversation_history (
                        id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        user_message TEXT NOT NULL,
                        ai_response TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        file_info TEXT,
                        created_at TEXT NOT NULL
                    )
                ''')
                
                # 创建索引
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_session_id 
                    ON conversation_history(session_id)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_created_at 
                    ON conversation_history(created_at)
                ''')
                
                # 创建会话信息表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        created_at TEXT NOT NULL,
                        last_activity TEXT NOT NULL,
                        message_count INTEGER DEFAULT 0
                    )
                ''')
                
                conn.commit()
                logger.info("对话历史数据库初始化完成")
                
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def save_message(self, message: ConversationMessage) -> bool:
        """
        保存对话消息
        
        Args:
            message: 对话消息对象
            
        Returns:
            bool: 保存是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 保存消息
                cursor.execute('''
                    INSERT OR REPLACE INTO conversation_history 
                    (id, session_id, user_message, ai_response, timestamp, file_info, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    message.id,
                    message.session_id,
                    message.user_message,
                    json.dumps(message.ai_response, ensure_ascii=False),
                    message.timestamp,
                    json.dumps(message.file_info, ensure_ascii=False) if message.file_info else None,
                    message.created_at
                ))
                
                # 更新会话信息
                cursor.execute('''
                    INSERT OR REPLACE INTO sessions 
                    (session_id, created_at, last_activity, message_count)
                    VALUES (?, 
                            COALESCE((SELECT created_at FROM sessions WHERE session_id = ?), ?),
                            ?,
                            COALESCE((SELECT message_count FROM sessions WHERE session_id = ?), 0) + 1)
                ''', (
                    message.session_id,
                    message.session_id,
                    message.created_at,
                    message.created_at,
                    message.session_id
                ))
                
                conn.commit()
                logger.debug(f"保存对话消息成功: {message.id}")
                return True
                
        except Exception as e:
            logger.error(f"保存对话消息失败: {e}")
            return False
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取指定会话的对话历史
        
        Args:
            session_id: 会话ID
            limit: 返回消息数量限制
            
        Returns:
            List[Dict]: 对话历史列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, session_id, user_message, ai_response, timestamp, file_info, created_at
                    FROM conversation_history 
                    WHERE session_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (session_id, limit))
                
                rows = cursor.fetchall()
                
                # 转换为字典格式并反转顺序（最新的在后面）
                history = []
                for row in reversed(rows):
                    try:
                        ai_response = json.loads(row[3]) if row[3] else {}
                        file_info = json.loads(row[5]) if row[5] else None
                        
                        history.append({
                            'id': row[0],
                            'session_id': row[1],
                            'user_message': row[2],
                            'ai_response': ai_response,
                            'timestamp': row[4],
                            'file_info': file_info,
                            'created_at': row[6]
                        })
                    except json.JSONDecodeError as e:
                        logger.warning(f"解析消息数据失败: {e}")
                        continue
                
                logger.debug(f"获取会话 {session_id} 的历史记录: {len(history)} 条")
                return history
                
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []
    
    def get_all_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取所有会话列表
        
        Args:
            limit: 返回会话数量限制
            
        Returns:
            List[Dict]: 会话列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT session_id, created_at, last_activity, message_count
                    FROM sessions 
                    ORDER BY last_activity DESC
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                
                sessions = []
                for row in rows:
                    sessions.append({
                        'session_id': row[0],
                        'created_at': row[1],
                        'last_activity': row[2],
                        'message_count': row[3]
                    })
                
                return sessions
                
        except Exception as e:
            logger.error(f"获取会话列表失败: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除指定会话的所有记录
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 删除对话记录
                cursor.execute('DELETE FROM conversation_history WHERE session_id = ?', (session_id,))
                
                # 删除会话信息
                cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
                
                conn.commit()
                logger.info(f"删除会话 {session_id} 成功")
                return True
                
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return False
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        清理指定天数之前的旧会话
        
        Args:
            days: 保留天数
            
        Returns:
            int: 清理的会话数量
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 获取要删除的会话ID
                cursor.execute('''
                    SELECT session_id FROM sessions 
                    WHERE last_activity < ?
                ''', (cutoff_str,))
                
                old_sessions = [row[0] for row in cursor.fetchall()]
                
                if old_sessions:
                    # 删除对话记录
                    placeholders = ','.join(['?'] * len(old_sessions))
                    cursor.execute(f'''
                        DELETE FROM conversation_history 
                        WHERE session_id IN ({placeholders})
                    ''', old_sessions)
                    
                    # 删除会话信息
                    cursor.execute(f'''
                        DELETE FROM sessions 
                        WHERE session_id IN ({placeholders})
                    ''', old_sessions)
                    
                    conn.commit()
                    logger.info(f"清理了 {len(old_sessions)} 个旧会话")
                    return len(old_sessions)
                
                return 0
                
        except Exception as e:
            logger.error(f"清理旧会话失败: {e}")
            return 0

# 全局数据库实例
conversation_db = ConversationHistoryDB()

def generate_session_id() -> str:
    """生成新的会话ID"""
    return str(uuid.uuid4())

def save_conversation_message(session_id: str, user_message: str, ai_response: Dict[str, Any], 
                            file_info: Optional[Dict[str, Any]] = None) -> bool:
    """
    保存对话消息的便捷函数
    
    Args:
        session_id: 会话ID
        user_message: 用户消息
        ai_response: AI回复
        file_info: 文件信息（可选）
        
    Returns:
        bool: 保存是否成功
    """
    message = ConversationMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        user_message=user_message,
        ai_response=ai_response,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        file_info=file_info
    )
    
    return conversation_db.save_message(message)

def get_conversation_history(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    获取对话历史的便捷函数
    
    Args:
        session_id: 会话ID
        limit: 返回消息数量限制
        
    Returns:
        List[Dict]: 对话历史列表
    """
    return conversation_db.get_conversation_history(session_id, limit)