# ============================================================================
# 文件：1_frontend_dashboard/components.py
# 功能：UI组件库 - 可复用的前端界面组件
# 技术：Streamlit + Plotly + 自定义CSS
# ============================================================================

"""
四川智水AI智慧管理平台 - UI组件库

功能模块：
1. 数据展示组件（图表、表格、卡片）
2. 交互组件（按钮、表单、对话框）
3. 布局组件（容器、分栏、导航）
4. 智能体交互组件
5. 数据导入导出组件
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
import json
import base64
from io import BytesIO
import time

from config import get_config
from utils import format_currency, format_percentage, create_download_link
from models import ProjectInfo, FinancialData, AgentType

# ============================================================================
# 配置和样式
# ============================================================================

config = get_config("agent_api")

# 苹果风格配色方案
APPLE_COLORS = {
    "primary": "#007AFF",      # 苹果蓝
    "secondary": "#5856D6",    # 紫色
    "success": "#34C759",      # 绿色
    "warning": "#FF9500",      # 橙色
    "danger": "#FF3B30",       # 红色
    "info": "#5AC8FA",         # 浅蓝
    "light": "#F2F2F7",        # 浅灰
    "dark": "#1C1C1E",         # 深灰
    "white": "#FFFFFF",        # 白色
    "black": "#000000",        # 黑色
    "gray": "#8E8E93"          # 中灰
}

# 图表主题配置
CHART_THEME = {
    "layout": {
        "font": {"family": "SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif", "size": 12},
        "plot_bgcolor": "rgba(248,250,252,0.8)",  # 灰色背景
        "paper_bgcolor": "rgba(248,250,252,0.8)",  # 灰色背景
        "colorway": [APPLE_COLORS["primary"], APPLE_COLORS["success"], APPLE_COLORS["warning"], 
                     APPLE_COLORS["danger"], APPLE_COLORS["secondary"], APPLE_COLORS["info"]]
    }
}

# ============================================================================
# 基础组件
# ============================================================================

def apple_card(title: str, content: Any, icon: str = "📊", color: str = "primary") -> None:
    """苹果风格卡片组件"""
    card_color = APPLE_COLORS.get(color, APPLE_COLORS["primary"])
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {card_color}15 0%, {card_color}05 100%);
        border: 1px solid {card_color}30;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        backdrop-filter: blur(10px);
    ">
        <div style="
            display: flex;
            align-items: center;
            margin-bottom: 12px;
        ">
            <span style="font-size: 20px; margin-right: 10px;">{icon}</span>
            <h3 style="
                margin: 0;
                color: {card_color};
                font-weight: 600;
                font-size: 18px;
            ">{title}</h3>
        </div>
        <div style="color: #1C1C1E; font-size: 14px;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def apple_metric_card(title: str, value: Union[str, int, float], 
                     delta: Optional[str] = None, icon: str = "📈") -> None:
    """苹果风格指标卡片"""
    delta_color = APPLE_COLORS["success"] if delta and "+" in str(delta) else APPLE_COLORS["danger"]
    delta_html = f"<span style='color: {delta_color}; font-size: 12px;'>{delta}</span>" if delta else ""
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
        border: 1px solid #E5E5EA;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: transform 0.2s ease;
    " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="font-size: 24px; margin-bottom: 8px;">{icon}</div>
        <div style="color: #8E8E93; font-size: 12px; margin-bottom: 4px;">{title}</div>
        <div style="color: #1C1C1E; font-size: 28px; font-weight: 700; margin-bottom: 4px;">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def apple_button(label: str, key: str, color: str = "primary", 
                size: str = "medium", disabled: bool = False) -> bool:
    """苹果风格按钮组件"""
    button_color = APPLE_COLORS.get(color, APPLE_COLORS["primary"])
    
    # 根据尺寸设置样式
    size_styles = {
        "small": {"padding": "8px 16px", "font-size": "12px", "border-radius": "8px"},
        "medium": {"padding": "12px 24px", "font-size": "14px", "border-radius": "10px"},
        "large": {"padding": "16px 32px", "font-size": "16px", "border-radius": "12px"}
    }
    
    style = size_styles.get(size, size_styles["medium"])
    
    # 创建按钮HTML
    button_html = f"""
    <style>
    .apple-button-{key} {{
        background: {button_color};
        color: white;
        border: none;
        border-radius: {style['border-radius']};
        padding: {style['padding']};
        font-size: {style['font-size']};
        font-weight: 600;
        cursor: {'not-allowed' if disabled else 'pointer'};
        opacity: {'0.5' if disabled else '1'};
        transition: all 0.2s ease;
        font-family: SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    .apple-button-{key}:hover {{
        background: {button_color}DD;
        transform: {'none' if disabled else 'translateY(-1px)'};
        box-shadow: {'none' if disabled else '0 4px 12px rgba(0,0,0,0.15)'};
    }}
    </style>
    """
    
    st.markdown(button_html, unsafe_allow_html=True)
    
    return st.button(label, key=key, disabled=disabled, 
                    help=None if not disabled else "按钮已禁用")

def apple_progress_bar(progress: float, label: str = "", color: str = "primary") -> None:
    """苹果风格进度条"""
    progress_color = APPLE_COLORS.get(color, APPLE_COLORS["primary"])
    progress_percent = min(max(progress, 0), 1) * 100
    
    st.markdown(f"""
    <div style="margin: 16px 0;">
        {f'<div style="color: #1C1C1E; font-size: 14px; margin-bottom: 8px;">{label}</div>' if label else ''}
        <div style="
            background: #F2F2F7;
            border-radius: 8px;
            height: 8px;
            overflow: hidden;
        ">
            <div style="
                background: linear-gradient(90deg, {progress_color} 0%, {progress_color}CC 100%);
                height: 100%;
                width: {progress_percent}%;
                border-radius: 8px;
                transition: width 0.3s ease;
            "></div>
        </div>
        <div style="color: #8E8E93; font-size: 12px; margin-top: 4px; text-align: right;">
            {progress_percent:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# 数据展示组件
# ============================================================================

def create_apple_chart(chart_type: str, data: pd.DataFrame, 
                      title: str, **kwargs) -> go.Figure:
    """创建苹果风格图表"""
    
    # 基础配置
    fig_config = {
        "layout": {
            "title": {
                "text": title,
                "font": {"size": 18, "color": APPLE_COLORS["dark"], "family": "SF Pro Display"},
                "x": 0.5,
                "xanchor": "center"
            },
            "font": {"family": "SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif"},
            "plot_bgcolor": "rgba(248,250,252,0.8)",  # 灰色背景
            "paper_bgcolor": "rgba(248,250,252,0.8)",  # 灰色背景
            "margin": {"l": 40, "r": 40, "t": 60, "b": 40},
            "showlegend": True,
            "legend": {
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1
            }
        }
    }
    
    # 根据图表类型创建图表
    if chart_type == "line":
        fig = px.line(data, **kwargs)
    elif chart_type == "bar":
        fig = px.bar(data, **kwargs)
    elif chart_type == "pie":
        fig = px.pie(data, **kwargs)
    elif chart_type == "scatter":
        fig = px.scatter(data, **kwargs)
    elif chart_type == "area":
        fig = px.area(data, **kwargs)
    else:
        fig = px.bar(data, **kwargs)  # 默认柱状图
    
    # 应用苹果风格
    fig.update_layout(**fig_config["layout"])
    fig.update_layout(colorway=CHART_THEME["layout"]["colorway"])
    
    # 网格线样式
    fig.update_xaxes(gridcolor="#F2F2F7", gridwidth=1)
    fig.update_yaxes(gridcolor="#F2F2F7", gridwidth=1)
    
    return fig

def financial_overview_chart(financial_data: List[Dict]) -> go.Figure:
    """财务概览图表"""
    if not financial_data:
        # 创建示例数据
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
        financial_data = [
            {
                "date": date.strftime('%Y-%m'),
                "revenue": np.random.uniform(800000, 1200000),
                "cost": np.random.uniform(500000, 800000),
                "profit": np.random.uniform(100000, 400000)
            }
            for date in dates
        ]
    
    df = pd.DataFrame(financial_data)
    
    # 创建子图
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('收入趋势', '成本分析', '利润率', '现金流'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 收入趋势
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['revenue'], name='收入', 
                  line=dict(color=APPLE_COLORS["primary"], width=3)),
        row=1, col=1
    )
    
    # 成本分析
    fig.add_trace(
        go.Bar(x=df['date'], y=df['cost'], name='成本',
               marker_color=APPLE_COLORS["warning"]),
        row=1, col=2
    )
    
    # 利润率
    profit_margin = (df['profit'] / df['revenue'] * 100).fillna(0)
    fig.add_trace(
        go.Scatter(x=df['date'], y=profit_margin, name='利润率(%)',
                  line=dict(color=APPLE_COLORS["success"], width=3),
                  fill='tonexty'),
        row=2, col=1
    )
    
    # 现金流
    cash_flow = df['revenue'] - df['cost']
    fig.add_trace(
        go.Bar(x=df['date'], y=cash_flow, name='现金流',
               marker_color=APPLE_COLORS["info"]),
        row=2, col=2
    )
    
    # 更新布局
    fig.update_layout(
        height=600,
        title_text="财务数据概览",
        title_x=0.5,
        showlegend=False,
        font=dict(family="SF Pro Display", size=12),
        plot_bgcolor="rgba(248,250,252,0.8)",  # 灰色背景
        paper_bgcolor="rgba(248,250,252,0.8)"  # 灰色背景
    )
    
    return fig

def project_status_chart(project_data: List[Dict]) -> go.Figure:
    """项目状态图表"""
    if not project_data:
        # 创建示例数据
        project_data = [
            {"status": "进行中", "count": 15, "budget": 5000000},
            {"status": "已完成", "count": 8, "budget": 3200000},
            {"status": "计划中", "count": 12, "budget": 4800000},
            {"status": "暂停", "count": 3, "budget": 800000}
        ]
    
    df = pd.DataFrame(project_data)
    
    # 创建双轴图表
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('项目数量分布', '预算分布'),
        specs=[[{"type": "pie"}, {"type": "bar"}]]
    )
    
    # 项目数量饼图
    colors = [APPLE_COLORS["primary"], APPLE_COLORS["success"], 
              APPLE_COLORS["warning"], APPLE_COLORS["danger"]]
    
    fig.add_trace(
        go.Pie(labels=df['status'], values=df['count'], 
               marker_colors=colors, hole=0.4),
        row=1, col=1
    )
    
    # 预算柱状图
    fig.add_trace(
        go.Bar(x=df['status'], y=df['budget'], 
               marker_color=colors, name='预算'),
        row=1, col=2
    )
    
    fig.update_layout(
        height=400,
        title_text="项目状态分析",
        title_x=0.5,
        font=dict(family="SF Pro Display", size=12),
        plot_bgcolor="rgba(248,250,252,0.8)",  # 灰色背景
        paper_bgcolor="rgba(248,250,252,0.8)"  # 灰色背景
    )
    
    return fig

def create_kpi_dashboard(kpi_data: Dict) -> None:
    """创建KPI仪表板"""
    if not kpi_data:
        # 示例KPI数据
        kpi_data = {
            "total_revenue": {"value": 12500000, "delta": "+8.5%", "icon": "💰"},
            "active_projects": {"value": 28, "delta": "+3", "icon": "🚀"},
            "profit_margin": {"value": "23.5%", "delta": "+2.1%", "icon": "📈"},
            "customer_satisfaction": {"value": "94.2%", "delta": "+1.8%", "icon": "😊"}
        }
    
    # 创建4列布局
    cols = st.columns(4)
    
    kpi_configs = [
        ("总收入", kpi_data.get("total_revenue", {})),
        ("活跃项目", kpi_data.get("active_projects", {})),
        ("利润率", kpi_data.get("profit_margin", {})),
        ("客户满意度", kpi_data.get("customer_satisfaction", {}))
    ]
    
    for i, (title, data) in enumerate(kpi_configs):
        with cols[i]:
            value = data.get("value", "N/A")
            delta = data.get("delta", "")
            icon = data.get("icon", "📊")
            
            # 格式化数值
            if isinstance(value, (int, float)) and "revenue" in title.lower():
                value = format_currency(value)
            
            apple_metric_card(title, value, delta, icon)

# ============================================================================
# 数据表格组件
# ============================================================================

def apple_data_table(data: pd.DataFrame, title: str = "", 
                    searchable: bool = True, sortable: bool = True,
                    pagination: bool = True, page_size: int = 10) -> pd.DataFrame:
    """苹果风格数据表格"""
    
    if title:
        st.markdown(f"""
        <h3 style="
            color: {APPLE_COLORS['dark']};
            font-family: SF Pro Display;
            font-weight: 600;
            margin-bottom: 16px;
        ">{title}</h3>
        """, unsafe_allow_html=True)
    
    # 搜索功能
    filtered_data = data.copy()
    if searchable and not data.empty:
        search_term = st.text_input("🔍 搜索", placeholder="输入关键词搜索...")
        if search_term:
            # 在所有文本列中搜索
            text_columns = data.select_dtypes(include=['object']).columns
            mask = data[text_columns].astype(str).apply(
                lambda x: x.str.contains(search_term, case=False, na=False)
            ).any(axis=1)
            filtered_data = data[mask]
    
    # 分页功能
    if pagination and len(filtered_data) > page_size:
        total_pages = (len(filtered_data) - 1) // page_size + 1
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.selectbox(
                "页码",
                range(1, total_pages + 1),
                format_func=lambda x: f"第 {x} 页 (共 {total_pages} 页)"
            )
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        filtered_data = filtered_data.iloc[start_idx:end_idx]
    
    # 显示表格
    if not filtered_data.empty:
        # 自定义表格样式
        st.markdown("""
        <style>
        .stDataFrame {
            border: 1px solid #E5E5EA;
            border-radius: 12px;
            overflow: hidden;
        }
        .stDataFrame > div {
            border-radius: 12px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.dataframe(
            filtered_data,
            use_container_width=True,
            hide_index=True
        )
        
        # 显示统计信息
        st.caption(f"显示 {len(filtered_data)} 条记录，共 {len(data)} 条")
    else:
        st.info("📭 没有找到匹配的数据")
    
    return filtered_data

# ============================================================================
# 文件上传下载组件
# ============================================================================

def apple_file_uploader(label: str, accepted_types: List[str] = None, 
                       multiple: bool = False, key: str = None) -> Any:
    """苹果风格文件上传组件"""
    
    if accepted_types is None:
        accepted_types = ['xlsx', 'xls', 'csv', 'json']
    
    st.markdown(f"""
    <div style="
        border: 2px dashed {APPLE_COLORS['primary']};
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        background: linear-gradient(135deg, {APPLE_COLORS['primary']}08 0%, {APPLE_COLORS['primary']}03 100%);
        margin: 16px 0;
    ">
        <div style="font-size: 32px; margin-bottom: 12px;">📁</div>
        <div style="color: {APPLE_COLORS['dark']}; font-weight: 600; margin-bottom: 8px;">{label}</div>
        <div style="color: {APPLE_COLORS['gray']}; font-size: 14px;">
            支持格式: {', '.join(accepted_types)}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    return st.file_uploader(
        "",
        type=accepted_types,
        accept_multiple_files=multiple,
        key=key,
        label_visibility="collapsed"
    )

def apple_download_button(data: Union[str, bytes], filename: str, 
                         mime_type: str, label: str = "下载", 
                         icon: str = "⬇️") -> None:
    """苹果风格下载按钮"""
    
    # 创建下载链接
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    b64_data = base64.b64encode(data).decode()
    
    download_html = f"""
    <style>
    .apple-download-btn {{
        display: inline-flex;
        align-items: center;
        background: {APPLE_COLORS['primary']};
        color: white;
        padding: 12px 24px;
        border-radius: 10px;
        text-decoration: none;
        font-family: SF Pro Display;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.2s ease;
        margin: 8px 0;
    }}
    .apple-download-btn:hover {{
        background: {APPLE_COLORS['primary']}DD;
        transform: translateY(-1px);
        text-decoration: none;
        color: white;
    }}
    </style>
    <a href="data:{mime_type};base64,{b64_data}" download="{filename}" class="apple-download-btn">
        <span style="margin-right: 8px;">{icon}</span>
        {label}
    </a>
    """
    
    st.markdown(download_html, unsafe_allow_html=True)

# ============================================================================
# 智能体交互组件
# ============================================================================

def agent_chat_interface(agent_type: str, session_key: str = "chat_history") -> None:
    """智能体聊天界面"""
    
    # 智能体配置
    agent_configs = {
        "financial": {"name": "财务分析师", "icon": "💰", "color": "success"},
        "knowledge": {"name": "运维专家", "icon": "🔧", "color": "info"},
        "cost": {"name": "成本分析师", "icon": "📊", "color": "warning"},
        "decision": {"name": "决策顾问", "icon": "🎯", "color": "primary"}
    }
    
    config = agent_configs.get(agent_type, {"name": "AI助手", "icon": "🤖", "color": "primary"})
    
    # 聊天标题
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        padding: 16px;
        background: linear-gradient(135deg, {APPLE_COLORS[config['color']]}15 0%, {APPLE_COLORS[config['color']]}05 100%);
        border-radius: 12px;
        margin-bottom: 16px;
    ">
        <span style="font-size: 24px; margin-right: 12px;">{config['icon']}</span>
        <h3 style="margin: 0; color: {APPLE_COLORS[config['color']]}; font-family: SF Pro Display;">
            {config['name']}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 初始化聊天历史
    if session_key not in st.session_state:
        st.session_state[session_key] = []
    
    # 显示聊天历史
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state[session_key]):
            is_user = message["role"] == "user"
            
            # 消息气泡样式
            bubble_style = f"""
            background: {'linear-gradient(135deg, ' + APPLE_COLORS['primary'] + ' 0%, ' + APPLE_COLORS['primary'] + 'CC 100%)' if is_user else '#F2F2F7'};
            color: {'white' if is_user else APPLE_COLORS['dark']};
            padding: 12px 16px;
            border-radius: {'18px 18px 4px 18px' if is_user else '18px 18px 18px 4px'};
            margin: {'0 0 8px 20%' if is_user else '0 20% 8px 0'};
            max-width: 80%;
            word-wrap: break-word;
            font-family: SF Pro Display;
            """
            
            st.markdown(f"""
            <div style="{bubble_style}">
                {message['content']}
            </div>
            """, unsafe_allow_html=True)
    
    # 输入框
    user_input = st.chat_input(f"向{config['name']}提问...")
    
    if user_input:
        # 添加用户消息
        st.session_state[session_key].append({"role": "user", "content": user_input})
        
        # 这里应该调用实际的智能体API
        # 暂时使用模拟响应
        with st.spinner(f"{config['name']}正在思考..."):
            time.sleep(1)  # 模拟处理时间
            
            # 模拟AI响应
            ai_response = f"感谢您的问题：'{user_input}'。作为{config['name']}，我正在为您分析相关信息..."
            
            # 添加AI响应
            st.session_state[session_key].append({"role": "assistant", "content": ai_response})
        
        # 重新运行以显示新消息
        st.rerun()

def multi_agent_collaboration_panel() -> None:
    """多智能体协作面板"""
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {APPLE_COLORS['primary']}10 0%, {APPLE_COLORS['secondary']}10 100%);
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
    ">
        <h3 style="
            color: {APPLE_COLORS['dark']};
            font-family: SF Pro Display;
            margin-bottom: 16px;
            text-align: center;
        ">🤝 多智能体协作中心</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 智能体选择
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("选择协作智能体")
        agents = st.multiselect(
            "智能体",
            ["财务分析师", "运维专家", "成本分析师", "决策顾问"],
            default=["财务分析师", "决策顾问"],
            label_visibility="collapsed"
        )
    
    with col2:
        st.subheader("协作任务")
        task = st.text_area(
            "任务描述",
            placeholder="例如：请财务分析师运用改进灰色马尔科夫模型预测现金流，成本分析师进行AHP层次分析法风险评估，运维专家提供设备维护策略，决策顾问综合制定Q4季度经营优化方案...",
            height=100,
            label_visibility="collapsed"
        )
    
    if apple_button("🚀 开始协作", "start_collaboration", "primary"):
        if agents and task:
            with st.spinner("智能体们正在协作中..."):
                # 模拟多智能体协作，实际应通过Agno协调器调用
                try:
                    # 模拟协作结果
                    st.success(f"✅ 协作任务完成！参与智能体：{', '.join(agents)}")
                    
                    # 显示模拟协作结果
                    st.markdown("### 📋 协作结果")
                    st.markdown(f"多智能体协作完成任务：{task[:100]}...")
                    
                    # 显示协作进度
                    progress_container = st.container()
                    with progress_container:
                        for i, agent in enumerate(agents):
                            apple_progress_bar(1.0, f"{agent} 分析完成")
                            
                except Exception as e:
                    st.error(f"❌ 协作执行失败：{str(e)}")
                    
        else:
            st.warning("⚠️ 请选择智能体并输入任务描述")

# ============================================================================
# 状态指示器组件
# ============================================================================

def service_status_indicator(services_status: Dict[str, bool]) -> None:
    """服务状态指示器"""
    
    st.markdown("### 🔧 系统服务状态")
    
    # 创建状态网格
    cols = st.columns(3)
    
    service_names = {
        "project": "项目服务",
        "financial": "财务分析",
        "knowledge": "知识库",
        "cost": "成本核算",
        "decision": "决策分析",
        "agno": "智能体协调"
    }
    
    for i, (service_key, service_name) in enumerate(service_names.items()):
        col_index = i % 3
        with cols[col_index]:
            is_healthy = services_status.get(service_key, False)
            status_color = APPLE_COLORS["success"] if is_healthy else APPLE_COLORS["danger"]
            status_icon = "🟢" if is_healthy else "🔴"
            status_text = "正常" if is_healthy else "异常"
            
            st.markdown(f"""
            <div style="
                background: {status_color}15;
                border: 1px solid {status_color}30;
                border-radius: 8px;
                padding: 12px;
                margin: 4px 0;
                text-align: center;
            ">
                <div style="font-size: 16px; margin-bottom: 4px;">{status_icon}</div>
                <div style="font-weight: 600; color: {APPLE_COLORS['dark']}; font-size: 12px;">{service_name}</div>
                <div style="color: {status_color}; font-size: 10px;">{status_text}</div>
            </div>
            """, unsafe_allow_html=True)

def loading_spinner(text: str = "加载中...") -> None:
    """苹果风格加载动画"""
    
    st.markdown(f"""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px;
        text-align: center;
    ">
        <div style="
            width: 40px;
            height: 40px;
            border: 3px solid {APPLE_COLORS['light']};
            border-top: 3px solid {APPLE_COLORS['primary']};
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 16px;
        "></div>
        <div style="
            color: {APPLE_COLORS['gray']};
            font-family: SF Pro Display;
            font-size: 14px;
        ">{text}</div>
    </div>
    
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# 测试函数
# ============================================================================

def test_components():
    """测试组件库"""
    st.title("🧪 组件库测试")
    
    # 测试卡片组件
    st.subheader("卡片组件")
    apple_card("测试卡片", "这是一个测试卡片的内容", "🧪", "primary")
    
    # 测试指标卡片
    st.subheader("指标卡片")
    cols = st.columns(4)
    with cols[0]:
        apple_metric_card("总收入", "¥1,250万", "+8.5%", "💰")
    with cols[1]:
        apple_metric_card("活跃项目", "28", "+3", "🚀")
    with cols[2]:
        apple_metric_card("利润率", "23.5%", "+2.1%", "📈")
    with cols[3]:
        apple_metric_card("客户满意度", "94.2%", "+1.8%", "😊")
    
    # 测试按钮
    st.subheader("按钮组件")
    col1, col2, col3 = st.columns(3)
    with col1:
        apple_button("主要按钮", "btn1", "primary")
    with col2:
        apple_button("成功按钮", "btn2", "success")
    with col3:
        apple_button("警告按钮", "btn3", "warning")
    
    # 测试进度条
    st.subheader("进度条组件")
    apple_progress_bar(0.75, "项目完成度", "success")
    
    # 测试图表
    st.subheader("图表组件")
    sample_data = pd.DataFrame({
        'x': range(10),
        'y': np.random.randn(10).cumsum()
    })
    fig = create_apple_chart("line", sample_data, "测试图表", x='x', y='y')
    st.plotly_chart(fig, use_container_width=True)
    
    st.success("✅ 所有组件测试完成！")

if __name__ == "__main__":
    test_components()