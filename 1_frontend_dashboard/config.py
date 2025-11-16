# ============================================================================
# 文件：1_frontend_dashboard/config.py
# 功能：前端界面配置文件
# 技术：Python配置管理
# ============================================================================

"""
四川智水AI智慧管理平台 - 前端配置文件

配置内容：
1. API接口配置
2. UI样式配置
3. 数据处理配置
4. 系统参数配置
"""

import os
from typing import Dict, List, Any
from pathlib import Path

# ============================================================================
# 基础配置
# ============================================================================

# 应用基本信息
APP_CONFIG = {
    "name": "系统核心功能",
    "version": "1.0.0",
    "description": "AI驱动的项目信息整合与智能决策支持系统",
    "company": "四川智水信息技术有限公司",
    "icon": "未命名的设计.png"
}

# 页面配置
PAGE_CONFIG = {
    "page_title": "系统核心功能",
    "page_icon": "未命名的设计.png",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "menu_items": {
        'Get Help': 'https://www.zhishui.com/help',
        'Report a bug': 'https://www.zhishui.com/bug',
        'About': '四川智水AI智慧管理解决方案 v1.0.0'
    }
}

# ============================================================================
# API配置
# ============================================================================

# Multi-Agent API配置
AGENT_API_CONFIG = {
    "base_url": "http://localhost:8000",
    "endpoints": {
        "query": "/api/agents/query",
        "status": "/api/agents/status",
        "health": "/api/health"
    },
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1
}

# 智能体配置
AGENT_CONFIG = {
    "financial_analyst": {
        "name": "💰 财务分析师",
        "description": "专业财务分析和投资建议",
        "capabilities": ["财务状况分析", "投资建议", "风险评估", "现金流预测"],
        "color": "#007aff"
    },
    "cost_analyst": {
        "name": "📊 成本分析师",
        "description": "项目成本分析和优化建议",
        "capabilities": ["成本结构分析", "预算控制", "成本优化", "ROI计算"],
        "color": "#34c759"
    },
    "knowledge_manager": {
        "name": "📚 知识管理员",
        "description": "运维知识库和最佳实践",
        "capabilities": ["文档查询", "最佳实践", "技术支持", "培训资料"],
        "color": "#ff9500"
    },
    "efficiency_evaluator": {
        "name": "⚡ 效能评估师",
        "description": "团队效能分析和改进建议",
        "capabilities": ["绩效分析", "效率提升", "团队协作", "流程优化"],
        "color": "#ff3b30"
    }
}

# ============================================================================
# UI样式配置
# ============================================================================

# 苹果风格配色方案 - 白蓝高级质感
COLOR_SCHEME = {
    "primary": "#1d4ed8",      # 深蓝 - 主色调
    "secondary": "#3b82f6",    # 标准蓝 - 辅助色
    "accent": "#60a5fa",       # 浅蓝 - 强调色
    "light": "#dbeafe",       # 极浅蓝 - 背景色
    "lighter": "#f0f9ff",     # 最浅蓝 - 卡片背景
    "white": "#ffffff",       # 纯白
    "gray": "#f8fafc",        # 浅灰
    "dark": "#0f172a",        # 深蓝黑 - 文字主色
    "darker": "#1e293b",      # 深灰 - 文字次要色
    "text_primary": "#0f172a", # 主要文字 - 深蓝黑
    "text_secondary": "#475569", # 次要文字 - 灰蓝
    "text_muted": "#94a3b8",   # 弱文字 - 浅灰蓝
    "border": "#e2e8f0",      # 边框 - 浅灰蓝
    "border_light": "#f1f5f9", # 浅色边框
    "shadow": "rgba(15, 23, 42, 0.08)", # 阴影色
    "shadow_blue": "rgba(59, 130, 246, 0.15)", # 蓝色阴影
    "success": "#10b981",     # 成功绿
    "warning": "#f59e0b",   # 警告橙
    "danger": "#ef4444",     # 危险红
    "info": "#3b82f6"        # 信息蓝
}

# 字体配置 - 苹果官网风格
FONT_CONFIG = {
    "family": "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', Helvetica, Arial, sans-serif",
    "sizes": {
        "hero": "4rem",           # 主标题
        "title": "3.5rem",        # 页面标题
        "subtitle": "1.5rem",     # 副标题
        "heading": "1.25rem",     # 小标题
        "body": "1rem",           # 正文
        "small": "0.875rem",      # 小字
        "caption": "0.75rem"      # 说明文字
    },
    "weights": {
        "light": 300,
        "normal": 400,
        "medium": 500,
        "semibold": 600,
        "bold": 700
    },
    "line_heights": {
        "tight": 1.2,
        "normal": 1.5,
        "relaxed": 1.75
    }
}

# 布局配置 - 苹果官网风格
LAYOUT_CONFIG = {
    "container_max_width": "1280px",
    "sidebar_width": "280px",
    "card_border_radius": "20px",
    "button_border_radius": "12px",
    "input_border_radius": "12px",
    "spacing": {
        "xs": "0.5rem",
        "sm": "0.75rem",
        "md": "1rem",
        "lg": "1.5rem",
        "xl": "2rem",
        "xxl": "3rem",
        "hero": "4rem"
    },
    "shadows": {
        "sm": "0 1px 3px rgba(15, 23, 42, 0.1)",
        "md": "0 4px 12px rgba(15, 23, 42, 0.15)",
        "lg": "0 8px 25px rgba(15, 23, 42, 0.2)",
        "blue": "0 4px 20px rgba(59, 130, 246, 0.25)"
    },
    "transitions": {
        "fast": "0.15s ease",
        "normal": "0.3s ease",
        "slow": "0.5s ease"
    }
}

# ============================================================================
# 数据配置
# ============================================================================

# 数据处理配置
DATA_CONFIG = {
    "max_upload_size": 200,  # MB
    "supported_formats": [".xlsx", ".xls", ".csv"],
    "date_format": "%Y-%m-%d",
    "datetime_format": "%Y-%m-%d %H:%M:%S",
    "decimal_places": 2,
    "cache_ttl": 3600,  # 缓存时间（秒）
    "pagination_size": 50  # 分页大小
}

# 图表配置 - 白蓝高级配色
CHART_CONFIG = {
    "default_height": 450,
    "default_width": 900,
    "color_palette": [
        "#1d4ed8",  # 深蓝
        "#3b82f6",  # 标准蓝
        "#60a5fa",  # 浅蓝
        "#93c5fd",  # 极浅蓝
        "#dbeafe",  # 蓝色背景
        "#0f172a",  # 深蓝黑
        "#475569",  # 灰蓝
        "#64748b"   # 浅灰蓝
    ],
    "template": "plotly_white",
    "font_family": "-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif",
    "animation_duration": 800,
    "background_color": "#ffffff",
    "grid_color": "#f1f5f9",
    "text_color": "#0f172a"
}

# ============================================================================
# 业务配置
# ============================================================================

# 项目状态配置
PROJECT_STATUS = {
    "进行中": {"color": "#007aff", "icon": "🔄"},
    "已完成": {"color": "#34c759", "icon": "✅"},
    "规划中": {"color": "#ff9500", "icon": "📋"},
    "暂停": {"color": "#ff3b30", "icon": "⏸️"},
    "取消": {"color": "#86868b", "icon": "❌"}
}

# 客户类型配置
CUSTOMER_TYPES = {
    "国企": {"color": "#007aff", "icon": "🏢"},
    "央企": {"color": "#34c759", "icon": "🏛️"},
    "政府": {"color": "#ff9500", "icon": "🏛️"},
    "民企": {"color": "#5856d6", "icon": "🏪"},
    "外企": {"color": "#af52de", "icon": "🌐"}
}

# 部门配置
DEPARTMENTS = {
    "技术部": {"color": "#007aff", "icon": "💻"},
    "项目部": {"color": "#34c759", "icon": "📊"},
    "财务部": {"color": "#ff9500", "icon": "💰"},
    "运维部": {"color": "#ff3b30", "icon": "🔧"},
    "销售部": {"color": "#5856d6", "icon": "📈"},
    "人事部": {"color": "#af52de", "icon": "👥"}
}

# ============================================================================
# 系统配置
# ============================================================================

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_path": "logs/frontend.log",
    "max_size": "10MB",
    "backup_count": 5
}

# 缓存配置
CACHE_CONFIG = {
    "enabled": True,
    "ttl": 3600,  # 默认缓存时间（秒）
    "max_entries": 1000,
    "clear_on_startup": False
}

# 安全配置
SECURITY_CONFIG = {
    "max_file_size": 200 * 1024 * 1024,  # 200MB
    "allowed_extensions": [".xlsx", ".xls", ".csv", ".json"],
    "session_timeout": 3600,  # 会话超时（秒）
    "rate_limit": {
        "requests_per_minute": 60,
        "requests_per_hour": 1000
    }
}

# ============================================================================
# 环境配置
# ============================================================================

# 开发环境配置
DEV_CONFIG = {
    "debug": True,
    "hot_reload": True,
    "show_errors": True,
    "log_level": "DEBUG"
}

# 生产环境配置
PROD_CONFIG = {
    "debug": False,
    "hot_reload": False,
    "show_errors": False,
    "log_level": "INFO"
}

# ============================================================================
# 配置获取函数
# ============================================================================

def get_config(config_name: str) -> Dict[str, Any]:
    """
    获取指定的配置
    
    Args:
        config_name: 配置名称
        
    Returns:
        Dict[str, Any]: 配置字典
    """
    config_map = {
        "app": APP_CONFIG,
        "page": PAGE_CONFIG,
        "agent_api": AGENT_API_CONFIG,
        "agent": AGENT_CONFIG,
        "color": COLOR_SCHEME,
        "font": FONT_CONFIG,
        "layout": LAYOUT_CONFIG,
        "data": DATA_CONFIG,
        "chart": CHART_CONFIG,
        "project_status": PROJECT_STATUS,
        "customer_types": CUSTOMER_TYPES,
        "departments": DEPARTMENTS,
        "logging": LOGGING_CONFIG,
        "cache": CACHE_CONFIG,
        "security": SECURITY_CONFIG,
        "dev": DEV_CONFIG,
        "prod": PROD_CONFIG
    }
    
    return config_map.get(config_name, {})

def get_environment() -> str:
    """
    获取当前运行环境
    
    Returns:
        str: 环境名称（dev/prod）
    """
    return os.getenv("ENVIRONMENT", "dev")

def get_env_config() -> Dict[str, Any]:
    """
    获取当前环境的配置
    
    Returns:
        Dict[str, Any]: 环境配置
    """
    env = get_environment()
    return get_config("dev" if env == "dev" else "prod")

def get_api_url(endpoint: str) -> str:
    """
    获取API完整URL
    
    Args:
        endpoint: API端点名称
        
    Returns:
        str: 完整的API URL
    """
    api_config = get_config("agent_api")
    base_url = api_config["base_url"]
    endpoint_path = api_config["endpoints"].get(endpoint, "")
    
    return f"{base_url}{endpoint_path}"

def get_agent_info(agent_name: str) -> Dict[str, Any]:
    """
    获取智能体信息
    
    Args:
        agent_name: 智能体名称
        
    Returns:
        Dict[str, Any]: 智能体信息
    """
    agent_config = get_config("agent")
    return agent_config.get(agent_name, {})

# ============================================================================
# 配置验证函数
# ============================================================================

def validate_config() -> bool:
    """
    验证配置的完整性和正确性
    
    Returns:
        bool: 配置是否有效
    """
    try:
        # 验证必要的配置项
        required_configs = ["app", "page", "agent_api", "color", "data"]
        
        for config_name in required_configs:
            config = get_config(config_name)
            if not config:
                print(f"缺少必要配置: {config_name}")
                return False
        
        # 验证API配置
        api_config = get_config("agent_api")
        if not api_config.get("base_url"):
            print("API base_url 未配置")
            return False
        
        # 验证颜色配置
        color_config = get_config("color")
        required_colors = ["primary", "secondary", "background"]
        for color in required_colors:
            if not color_config.get(color):
                print(f"缺少颜色配置: {color}")
                return False
        
        return True
        
    except Exception as e:
        print(f"配置验证失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 配置验证
    if validate_config():
        print("✅ 配置验证通过")
    else:
        print("❌ 配置验证失败")
    
    # 显示当前环境配置
    env = get_environment()
    env_config = get_env_config()
    print(f"当前环境: {env}")
    print(f"调试模式: {env_config.get('debug', False)}")

# ============================================================================
# 前端性能优化配置
# ============================================================================

# Streamlit性能配置
STREAMLIT_CONFIG = {
    "server.maxUploadSize": 200,
    "server.maxMessageSize": 200,
    "server.enableCORS": False,
    "server.enableXsrfProtection": False,
    "browser.gatherUsageStats": False,
    "client.caching": True,
    "client.displayEnabled": True
}

# 缓存配置
FRONTEND_CACHE_CONFIG = {
    "enable_data_cache": True,
    "cache_ttl": 300,  # 5分钟
    "max_cache_entries": 100,
    "enable_session_state": True
}

# 响应优化
RESPONSE_OPTIMIZATION = {
    "enable_compression": True,
    "lazy_loading": True,
    "batch_requests": True,
    "debounce_delay": 300  # 毫秒
}
