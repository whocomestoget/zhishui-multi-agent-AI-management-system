#!/usr/bin/env python3
"""
智水信息Multi-Agent系统 - 系统配置文件
统一管理所有系统配置参数

功能职责：
1. AI模型配置管理
2. 系统运行参数配置
3. Agent行为参数配置
4. 日志和监控配置
5. 工作流模板配置

Author: 商海星辰队
Version: 1.0.0
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass

# ================================
# 1. AI模型配置
# ================================

# 统一AI配置 - 所有模块使用
AI_CONFIG = {
    "api_key": "", 
    "api_base": "http://38.246.251.165:3002/v1",
    "model": "gemini-2.5-flash-preview-05-20",
    "temperature": 0.7,
    "max_tokens": 65000,
}

# ================================
# 2. 系统运行配置
# ================================

@dataclass
class SystemConfig:
    """系统运行配置"""
    
    # 基础配置
    system_name: str = "智水信息AI智慧管理系统"
    version: str = "1.0.0"
    environment: str = "development"  # development, production
    
    # 性能配置
    max_concurrent_workflows: int = 5
    max_agent_execution_time: int = 600  # 秒
    thread_pool_size: int = 4
    
    # 缓存配置
    enable_caching: bool = True
    cache_ttl: int = 3600  # 秒
    max_cache_size: int = 1000
    
    # 安全配置
    enable_input_validation: bool = True
    max_input_length: int = 10000
    allowed_file_types: List[str] = None
    
    def __post_init__(self):
        if self.allowed_file_types is None:
            self.allowed_file_types = ['.txt', '.csv', '.xlsx', '.json', '.pdf']

# ================================
# 3. Agent配置
# ================================

@dataclass
class AgentConfig:
    """Agent通用配置"""
    
    # 执行配置
    default_timeout: int = 600  # 秒
    max_retry_attempts: int = 2
    confidence_threshold: float = 0.6
    
    # 输出配置
    max_output_length: int = 5000
    include_reasoning: bool = True
    include_confidence: bool = True
    
    # 专业Agent特定配置
    financial_agent_config: Dict[str, Any] = None
    cost_agent_config: Dict[str, Any] = None
    knowledge_agent_config: Dict[str, Any] = None
    efficiency_agent_config: Dict[str, Any] = None
    report_agent_config: Dict[str, Any] = None
    
    def __post_init__(self):
        # 财务分析Agent配置
        if self.financial_agent_config is None:
            self.financial_agent_config = {
                "analysis_depth": "comprehensive",  # basic, standard, comprehensive
                "include_forecasting": True,
                "risk_assessment_level": "detailed",
                "benchmark_comparison": True,
                "industry_context": "电力水利行业"
            }
        
        # 成本分析Agent配置
        if self.cost_agent_config is None:
            self.cost_agent_config = {
                "cost_breakdown_level": "detailed",
                "profitability_analysis": True,
                "cost_optimization_suggestions": True,
                "budget_variance_analysis": True,
                "project_cost_tracking": True
            }
        
        # 知识管理Agent配置
        if self.knowledge_agent_config is None:
            self.knowledge_agent_config = {
                "knowledge_depth": "expert",
                "solution_complexity": "comprehensive",
                "best_practices_inclusion": True,
                "case_study_examples": True,
                "technical_documentation": True
            }
        
        # 效能分析Agent配置
        if self.efficiency_agent_config is None:
            self.efficiency_agent_config = {
                "efficiency_metrics": "comprehensive",
                "performance_benchmarking": True,
                "optimization_recommendations": True,
                "resource_utilization_analysis": True,
                "productivity_insights": True
            }
        
        # 报告生成Agent配置
        if self.report_agent_config is None:
            self.report_agent_config = {
                "report_format": "html",
                "include_charts": True,
                "include_tables": True,
                "include_executive_summary": True,
                "include_recommendations": True,
                "visual_theme": "professional",
                "chart_library": "plotly"
            }

# ================================
# 4. 日志配置
# ================================

@dataclass
class LoggingConfig:
    """日志配置"""
    
    # 基础配置
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 文件配置
    enable_file_logging: bool = True
    log_file_path: str = "logs/agno_system.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    
    # 控制台配置
    enable_console_logging: bool = True
    console_log_level: str = "INFO"
    
    # 特殊日志
    enable_performance_logging: bool = True
    performance_log_file: str = "logs/performance.log"
    
    enable_audit_logging: bool = True
    audit_log_file: str = "logs/audit.log"

# ================================
# 5. 工作流配置
# ================================

@dataclass
class WorkflowConfig:
    """工作流配置"""
    
    # 默认工作流类型
    default_workflow_type: str = "comprehensive_analysis"
    
    # 阶段超时配置（秒）
    planning_stage_timeout: int = 180
    analysis_stage_timeout: int = 900
    report_stage_timeout: int = 600
    
    # 重试配置
    max_stage_retries: int = 2
    retry_delay: float = 2.0
    
    # 并行执行配置
    enable_parallel_execution: bool = True
    max_parallel_agents: int = 4
    
    # 结果保存配置
    save_intermediate_results: bool = True
    results_retention_days: int = 30

# ================================
# 6. 监控配置
# ================================

@dataclass
class MonitoringConfig:
    """监控配置"""
    
    # 性能监控
    enable_performance_monitoring: bool = True
    performance_metrics_interval: int = 60  # 秒
    
    # 健康检查
    enable_health_checks: bool = True
    health_check_interval: int = 30  # 秒
    
    # 告警配置
    enable_alerts: bool = True
    alert_thresholds: Dict[str, float] = None
    
    # 指标收集
    collect_detailed_metrics: bool = True
    metrics_retention_hours: int = 24
    
    def __post_init__(self):
        if self.alert_thresholds is None:
            self.alert_thresholds = {
                "max_execution_time": 600.0,  # 秒
                "min_success_rate": 0.8,
                "max_error_rate": 0.2,
                "max_memory_usage": 0.8,  # 80%
                "max_cpu_usage": 0.9  # 90%
            }

# ================================
# 7. 业务配置
# ================================

@dataclass
class BusinessConfig:
    """业务相关配置"""
    
    # 公司信息
    company_name: str = "四川智水信息技术有限公司"
    industry: str = "电力水利行业解决方案"
    business_focus: List[str] = None
    
    # 分析重点
    key_business_areas: List[str] = None
    priority_metrics: List[str] = None
    
    # 报告配置
    default_report_language: str = "中文"
    report_branding: Dict[str, str] = None
    
    def __post_init__(self):
        if self.business_focus is None:
            self.business_focus = [
                "智慧电厂解决方案",
                "智能电站管理", 
                "智慧水利系统",
                "大坝监测技术",
                "项目成本管控",
                "运维知识管理"
            ]
        
        if self.key_business_areas is None:
            self.key_business_areas = [
                "项目管理",
                "财务分析", 
                "成本控制",
                "运维效率",
                "知识管理",
                "人员效能"
            ]
        
        if self.priority_metrics is None:
            self.priority_metrics = [
                "项目盈利率",
                "成本控制率",
                "客户满意度",
                "运维效率",
                "人员利用率",
                "知识复用率"
            ]
        
        if self.report_branding is None:
            self.report_branding = {
                "company_logo": "",
                "primary_color": "#1f77b4",
                "secondary_color": "#ff7f0e",
                "font_family": "Microsoft YaHei, Arial, sans-serif"
            }

# ================================
# 8. 配置管理器
# ================================

class ConfigManager:
    """配置管理器
    
    统一管理所有系统配置
    """
    
    def __init__(self):
        """初始化配置管理器"""
        self.system_config = SystemConfig()
        self.agent_config = AgentConfig()
        self.logging_config = LoggingConfig()
        self.workflow_config = WorkflowConfig()
        self.monitoring_config = MonitoringConfig()
        self.business_config = BusinessConfig()
        
        # 确保日志目录存在
        self._ensure_log_directories()
    
    def _ensure_log_directories(self):
        """确保日志目录存在"""
        log_dirs = [
            os.path.dirname(self.logging_config.log_file_path),
            os.path.dirname(self.logging_config.performance_log_file),
            os.path.dirname(self.logging_config.audit_log_file)
        ]
        
        for log_dir in log_dirs:
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
    
    def get_ai_config(self) -> Dict[str, Any]:
        """获取AI配置"""
        return AI_CONFIG.copy()
    
    def get_agent_config(self, agent_type: str = None) -> Dict[str, Any]:
        """获取Agent配置"""
        base_config = {
            "timeout": self.agent_config.default_timeout,
            "max_retry_attempts": self.agent_config.max_retry_attempts,
            "confidence_threshold": self.agent_config.confidence_threshold,
            "max_output_length": self.agent_config.max_output_length,
            "include_reasoning": self.agent_config.include_reasoning,
            "include_confidence": self.agent_config.include_confidence
        }
        
        # 添加特定Agent配置
        if agent_type:
            specific_config_key = f"{agent_type}_agent_config"
            if hasattr(self.agent_config, specific_config_key):
                specific_config = getattr(self.agent_config, specific_config_key)
                base_config.update(specific_config)
        
        return base_config
    
    def get_workflow_config(self) -> Dict[str, Any]:
        """获取工作流配置"""
        return {
            "default_workflow_type": self.workflow_config.default_workflow_type,
            "stage_timeouts": {
                "planning": self.workflow_config.planning_stage_timeout,
                "analysis": self.workflow_config.analysis_stage_timeout,
                "report": self.workflow_config.report_stage_timeout
            },
            "retry_config": {
                "max_retries": self.workflow_config.max_stage_retries,
                "retry_delay": self.workflow_config.retry_delay
            },
            "parallel_config": {
                "enable_parallel": self.workflow_config.enable_parallel_execution,
                "max_parallel_agents": self.workflow_config.max_parallel_agents
            },
            "storage_config": {
                "save_intermediate": self.workflow_config.save_intermediate_results,
                "retention_days": self.workflow_config.results_retention_days
            }
        }
    
    def get_business_context(self) -> Dict[str, Any]:
        """获取业务上下文"""
        return {
            "company_info": {
                "name": self.business_config.company_name,
                "industry": self.business_config.industry,
                "business_focus": self.business_config.business_focus
            },
            "analysis_context": {
                "key_areas": self.business_config.key_business_areas,
                "priority_metrics": self.business_config.priority_metrics,
                "report_language": self.business_config.default_report_language
            },
            "branding": self.business_config.report_branding
        }
    
    def update_config(self, config_type: str, updates: Dict[str, Any]):
        """更新配置"""
        config_map = {
            "system": self.system_config,
            "agent": self.agent_config,
            "logging": self.logging_config,
            "workflow": self.workflow_config,
            "monitoring": self.monitoring_config,
            "business": self.business_config
        }
        
        if config_type in config_map:
            config_obj = config_map[config_type]
            for key, value in updates.items():
                if hasattr(config_obj, key):
                    setattr(config_obj, key, value)
    
    def export_config(self) -> Dict[str, Any]:
        """导出所有配置"""
        return {
            "ai_config": self.get_ai_config(),
            "system_config": self.system_config.__dict__,
            "agent_config": self.agent_config.__dict__,
            "logging_config": self.logging_config.__dict__,
            "workflow_config": self.workflow_config.__dict__,
            "monitoring_config": self.monitoring_config.__dict__,
            "business_config": self.business_config.__dict__
        }

# ================================
# 9. 全局配置实例
# ================================

# 创建全局配置管理器实例
config_manager = ConfigManager()

# 便捷访问函数
def get_ai_config() -> Dict[str, Any]:
    """获取AI配置"""
    return config_manager.get_ai_config()

def get_agent_config(agent_type: str = None) -> Dict[str, Any]:
    """获取Agent配置"""
    return config_manager.get_agent_config(agent_type)

def get_workflow_config() -> Dict[str, Any]:
    """获取工作流配置"""
    return config_manager.get_workflow_config()

def get_business_context() -> Dict[str, Any]:
    """获取业务上下文"""
    return config_manager.get_business_context()

# ================================
# 10. 模块导出
# ================================

__all__ = [
    'AI_CONFIG',
    'SystemConfig',
    'AgentConfig', 
    'LoggingConfig',
    'WorkflowConfig',
    'MonitoringConfig',
    'BusinessConfig',
    'ConfigManager',
    'config_manager',
    'get_ai_config',
    'get_agent_config',
    'get_workflow_config',
    'get_business_context'
]

# 性能优化配置
PERFORMANCE_CONFIG = {
    "agent_timeout": 30,  # 智能体超时时间（秒）
    "max_concurrent_agents": 3,  # 最大并发智能体数
    "response_cache_ttl": 300,  # 响应缓存时间（秒）
    "enable_fast_mode": True,  # 启用快速模式
    "max_response_length": 2000  # 最大响应长度
}


# ============================================================================
# 性能优化配置
# ============================================================================

# 响应缓存配置
RESPONSE_CACHE_CONFIG = {
    "enabled": True,
    "cache_size": 1000,
    "cache_ttl": 300,  # 5分钟缓存
    "cache_key_prefix": "agno_response_"
}

# 并发处理配置
CONCURRENCY_CONFIG = {
    "max_workers": 4,
    "request_timeout": 30,
    "connection_pool_size": 20,
    "enable_async": True
}

# 智能体响应优化
AGENT_OPTIMIZATION = {
    "response_streaming": True,
    "batch_processing": True,
    "lazy_loading": True,
    "memory_optimization": True
}

# 数据库连接优化
DATABASE_OPTIMIZATION = {
    "connection_pooling": True,
    "query_cache": True,
    "batch_operations": True,
    "index_optimization": True
}
