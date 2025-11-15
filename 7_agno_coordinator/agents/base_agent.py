#!/usr/bin/env python3
"""
智水信息Multi-Agent智能分析系统 - 基础Agent类
定义Agent系统的基础数据结构和抽象类

Author: 商海星辰队
Version: 1.0.0
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime

# ================================
# 1. 数据结构定义
# ================================

@dataclass
class AgentTask:
    """Agent任务数据结构"""
    task_id: str
    task_type: str
    input_data: Dict[str, Any]
    user_id: Optional[str] = None
    priority: str = "normal"  # low, normal, high
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """将AgentResult转换为可序列化的字典"""
        return {
            'task_id': self.task_id,
            'agent_id': self.agent_id,
            'status': self.status,
            'result_data': self.result_data,
            'confidence_score': self.confidence_score,
            'recommendations': self.recommendations,
            'error_message': self.error_message,
            'processing_time': self.processing_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class AgentResult:
    """Agent结果数据结构"""
    task_id: str
    agent_id: str
    status: str  # success, error, partial
    result_data: Dict[str, Any]
    confidence_score: float
    recommendations: List[str]
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

# ================================
# 2. 基础Agent抽象类
# ================================

class BaseAgent(ABC):
    """Agent基础抽象类"""
    
    def __init__(self, agent_id: str, agent_name: str):
        """初始化基础Agent"""
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"Agent.{agent_id}")
        
        # 配置日志
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        pass
    
    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """获取必需的输入字段"""
        pass
    
    @abstractmethod
    def validate_input_data(self, task: AgentTask) -> tuple[bool, List[str]]:
        """验证输入数据
        
        Returns:
            tuple: (是否有效, 错误信息列表)
        """
        pass
    
    @abstractmethod
    def perform_analysis(self, data: Dict[str, Any], task: AgentTask) -> Dict[str, Any]:
        """执行分析
        
        Args:
            data: 输入数据
            task: 任务对象
            
        Returns:
            Dict: 分析结果
        """
        pass
    
    @abstractmethod
    def calculate_confidence_score(self, result: Dict[str, Any]) -> float:
        """计算置信度分数
        
        Args:
            result: 分析结果
            
        Returns:
            float: 置信度分数 (0.0-1.0)
        """
        pass
    
    @abstractmethod
    def generate_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """生成建议
        
        Args:
            result: 分析结果
            
        Returns:
            List[str]: 建议列表
        """
        pass
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取Agent信息"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "required_fields": self.get_required_fields(),
            "capabilities": self.get_capabilities()
        }
    
    def get_capabilities(self) -> List[str]:
        """获取Agent能力列表"""
        return ["基础分析能力"]
    
    def format_error_result(self, task_id: str, error_message: str) -> AgentResult:
        """格式化错误结果"""
        return AgentResult(
            task_id=task_id,
            agent_id=self.agent_id,
            status="error",
            result_data={"error": error_message},
            confidence_score=0.0,
            recommendations=[],
            error_message=error_message
        )