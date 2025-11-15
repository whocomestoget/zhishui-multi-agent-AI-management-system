#!/usr/bin/env python3
"""
智水信息Multi-Agent智能分析系统 - Agents包初始化
统一导入和配置所有Agent类

Author: 商海星辰队
Version: 1.0.0
"""

# 导入基础类
from .base_agent import BaseAgent, AgentTask, AgentResult
from .business_agent import BusinessAgent, MCP_SERVICES_CONFIG, AI_CONFIG

# 导入具体Agent实现
from .financial_agent import FinancialAgent
from .cost_agent import CostAgent
from .knowledge_agent import KnowledgeAgent
from .efficiency_agent import EfficiencyAgent

# 定义包的公共接口
__all__ = [
    # 基础类
    'BaseAgent',
    'BusinessAgent', 
    'AgentTask',
    'AgentResult',
    
    # 具体Agent实现
    'FinancialAgent',
    'CostAgent', 
    'KnowledgeAgent',
    'EfficiencyAgent',
    
    # 配置
    'AI_CONFIG',
    'MCP_SERVICES_CONFIG',
    
    # 工厂函数
    'create_agent',
    'get_available_agents'
]

# Agent注册表 - 与workflow_templates.py和start_optimized.py中的配置完全匹配
AGENT_REGISTRY = {
    'planner_agent': {
        'class': None,  # 待实现：PlannerAgent类
        'name': '任务规划智能体',
        'description': '专注于需求分析、任务规划、执行策略制定',
        'mcp_service': None  # 规划功能暂不依赖MCP服务
    },
    'financial_agent': {
        'class': FinancialAgent,
        'name': '财务分析智能体',
        'description': '专注于财务分析、现金流预测、投资回报评估',
        'mcp_service': 'financial'
    },
    'cost_agent': {
        'class': CostAgent,
        'name': '成本分析智能体', 
        'description': '专注于工程成本预测、投资风险评估',
        'mcp_service': 'cost_prediction'
    },
    'efficiency_agent': {
        'class': EfficiencyAgent,
        'name': '效率分析智能体',
        'description': '专注于员工效能评估、团队分析、组织优化',
        'mcp_service': 'efficiency'
    },
    'knowledge_agent': {
        'class': KnowledgeAgent,
        'name': '知识管理智能体',
        'description': '专注于知识检索、文档管理、最佳实践分享',
        'mcp_service': 'knowledge'
    },
    'report_generator_agent': {
        'class': None,  # 待实现：ReportGeneratorAgent类
        'name': '报告生成智能体',
        'description': '专注于综合分析结果整合、可视化报告生成',
        'mcp_service': None  # 报告生成功能暂不依赖MCP服务
    }
}

def create_agent(agent_id: str) -> BaseAgent:
    """
    Agent工厂函数 - 根据ID创建对应的Agent实例
    
    Args:
        agent_id (str): Agent标识符
        
    Returns:
        BaseAgent: Agent实例
        
    Raises:
        ValueError: 如果agent_id不存在或未实现
    """
    if agent_id not in AGENT_REGISTRY:
        available_agents = list(AGENT_REGISTRY.keys())
        raise ValueError(f"未知的Agent ID: {agent_id}。可用的Agent: {available_agents}")
    
    agent_config = AGENT_REGISTRY[agent_id]
    agent_class = agent_config['class']
    
    # 检查Agent类是否已实现
    if agent_class is None:
        # 对于未实现的Agent，尝试从根目录导入
        if agent_id == 'planner_agent':
            try:
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.dirname(__file__)))
                from planner_agent import PlannerAgent
                return PlannerAgent()
            except ImportError:
                raise ValueError(f"Agent {agent_id} 的实现类尚未完成，请检查 planner_agent.py 文件")
        elif agent_id == 'report_generator_agent':
            # 报告生成智能体暂时使用基础BusinessAgent
            return BusinessAgent()
        else:
            raise ValueError(f"Agent {agent_id} 的实现类尚未完成")
    
    return agent_class()

def get_available_agents() -> dict:
    """
    获取所有可用的Agent信息
    
    Returns:
        dict: Agent信息字典
    """
    return {
        agent_id: {
            'name': config['name'],
            'description': config['description'],
            'mcp_service': config['mcp_service']
        }
        for agent_id, config in AGENT_REGISTRY.items()
    }

def validate_agent_dependencies() -> dict:
    """
    验证Agent依赖是否满足
    
    Returns:
        dict: 验证结果
    """
    import requests
    
    validation_results = {
        'mcp_services': {},
        'overall_status': True
    }
    
    # 检查MCP服务可用性
    for agent_id, config in AGENT_REGISTRY.items():
        mcp_service = config['mcp_service']
        service_config = MCP_SERVICES_CONFIG.get(mcp_service)
        
        if service_config:
            service_url = service_config['url']
            try:
                response = requests.get(f"{service_url}/health", timeout=5)
                service_available = response.status_code == 200
            except:
                service_available = False
                
            validation_results['mcp_services'][mcp_service] = {
                'url': service_url,
                'available': service_available,
                'agent': agent_id
            }
            
            if not service_available:
                validation_results['overall_status'] = False
        else:
            validation_results['mcp_services'][mcp_service] = {
                'url': 'unknown',
                'available': False,
                'agent': agent_id,
                'error': 'Service config not found'
            }
            validation_results['overall_status'] = False
    
    return validation_results

# 版本信息
__version__ = '1.0.0'
__author__ = '商海星辰队'
__email__ = 'tech@zhishui.com'
