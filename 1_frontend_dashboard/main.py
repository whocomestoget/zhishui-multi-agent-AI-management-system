# ============================================================================
# 文件：1_frontend_dashboard/main.py
# 功能：四川智水AI智慧管理解决方案 - 前端交互界面
# 技术：Streamlit + Plotly + Pandas
# ============================================================================

"""
四川智水AI智慧管理解决方案 - 前端界面

核心功能：
1. 企业数据汇总展示
2. Excel表格导入数据
3. JSON格式导出数据
4. Multi-Agent智能体系统交互
5. 实时数据可视化

解决痛点：
- 数据分散：统一数据管理平台
- 成本不透明：可视化成本分析
- 财务能力不足：AI财务助手
- 运维知识分散：智能知识库
- 系统割裂：一体化管理界面

设计特色：
- 移除侧边栏交互逻辑
- 采用顶部导航栏设计
- 优化用户体验
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import requests
from datetime import datetime, timedelta
import io
import base64
from typing import Dict, List, Any
import os
import time
from pathlib import Path

def format_ai_response_for_display(ai_response_content: str) -> str:
    """
    将AI回复内容格式化为自然语言显示，移除思考过程和非自然语言内容
    
    Args:
        ai_response_content: 原始AI回复内容（可能是JSON格式）
        
    Returns:
        str: 格式化后的自然语言显示内容
    """
    try:
        # 如果是JSON格式，尝试解析并格式化
        import json
        import re
        
        # 清理可能的markdown代码块标记和思考过程标记
        content = ai_response_content.strip()
        
        # 移除常见的思考过程标记
        thinking_patterns = [
            r'```json.*?```',  # JSON代码块
            r'```.*?```',      # 其他代码块
            r'\[思考\].*?\[/思考\]',  # 思考标记
            r'\[分析\].*?\[/分析\]',  # 分析标记
            r'让我.*?[。！]',   # "让我..."开头的思考
            r'我需要.*?[。！]',  # "我需要..."开头的思考
            r'首先.*?然后.*?[。！]',  # 步骤性思考
            r'根据.*?我认为.*?[。！]',  # 推理过程
        ]
        
        for pattern in thinking_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # 清理markdown标记
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        # 尝试解析JSON
        try:
            data = json.loads(content)
            
            # 如果是字典格式，进行智能格式化
            if isinstance(data, dict):
                formatted_parts = []
                
                # 处理summary_content字段（主要内容）
                if 'summary_content' in data:
                    summary_content = data['summary_content']
                    if summary_content and summary_content.strip():
                        # 清理转义字符
                        summary_content = re.sub(r'\\n', '\n', summary_content)
                        summary_content = re.sub(r'\\"', '"', summary_content)
                        formatted_parts.append(f"📋 **智水信息技术有限公司分析报告**\n\n{summary_content}")
                
                # 处理agent_name和generated_at信息
                if 'agent_name' in data and 'generated_at' in data:
                    agent_name = data['agent_name']
                    generated_at = data['generated_at']
                    formatted_parts.append(f"---\n📋 **分析来源：** {agent_name}  \n🕐 **生成时间：** {generated_at}")
                
                # 处理summary字段（兼容旧格式）
                elif 'summary' in data and 'content' in data['summary']:
                    summary_content = data['summary']['content']
                    formatted_parts.append(f"📋 **智水信息技术有限公司分析报告**\n\n{summary_content}")
                
                # 处理core_findings
                if 'core_findings' in data:
                    findings = data['core_findings']
                    if isinstance(findings, list) and findings:
                        formatted_parts.append("🔍 **核心发现：**")
                        for i, finding in enumerate(findings, 1):
                            formatted_parts.append(f"{i}. {finding}")
                
                # 处理key_recommendations  
                if 'key_recommendations' in data:
                    recommendations = data['key_recommendations']
                    if isinstance(recommendations, list) and recommendations:
                        formatted_parts.append("💡 **关键建议：**")
                        for i, rec in enumerate(recommendations, 1):
                            formatted_parts.append(f"{i}. {rec}")
                
                # 处理risk_warnings
                if 'risk_warnings' in data:
                    risks = data['risk_warnings']
                    if isinstance(risks, list) and risks:
                        formatted_parts.append("⚠️ **风险提醒：**")
                        for i, risk in enumerate(risks, 1):
                            formatted_parts.append(f"{i}. {risk}")
                
                # 处理confidence
                if 'confidence' in data:
                    confidence = data['confidence']
                    confidence_percent = int(float(confidence) * 100) if isinstance(confidence, (int, float)) else "未知"
                    formatted_parts.append(f"📊 **分析置信度：** {confidence_percent}%")
                
                # 处理agents_used
                if 'agents_used' in data:
                    agents = data['agents_used']
                    if isinstance(agents, list) and agents:
                        agent_names = []
                        for agent in agents:
                            if isinstance(agent, dict) and 'name' in agent:
                                agent_names.append(agent['name'])
                            elif isinstance(agent, str):
                                agent_names.append(agent)
                        if agent_names:
                            formatted_parts.append(f"🤖 **参与智能体：** {', '.join(agent_names)}")
                
                # 如果有格式化内容，返回格式化结果
                if formatted_parts:
                    return "\n\n".join(formatted_parts)
            
            # 如果是其他格式的JSON，尝试提取主要内容
            elif isinstance(data, str):
                return data
                
        except json.JSONDecodeError:
            # 不是JSON格式，直接返回原内容
            pass
        
        # 如果包含特定的结构化标记，进行简单格式化
        if "summary" in content.lower() or "content" in content.lower():
            # 移除多余的引号和转义字符
            content = re.sub(r'\\n', '\n', content)
            content = re.sub(r'\\"', '"', content)
            content = re.sub(r'^"', '', content)
            content = re.sub(r'"$', '', content)
        
        return content
        
    except Exception as e:
        # 如果格式化失败，返回原内容
        print(f"格式化AI回复时出错: {e}")
        return ai_response_content

# 导入API客户端函数
try:
    from api_client import call_multi_agent_system_with_file
except ImportError:
    # 如果导入失败，显示错误信息
    st.error("⚠️ API客户端导入失败，请检查api_client.py文件")

# ============================================================================
# 页面配置 - 苹果风格设计
# ============================================================================

def load_logo_base64():
    """
    加载企业logo并转换为base64格式
    """
    try:
        logo_path = Path(__file__).parent / "未命名的设计.png"
        if logo_path.exists():
            with open(logo_path, "rb") as f:
                logo_data = f.read()
            return base64.b64encode(logo_data).decode()
        else:
            return None
    except Exception as e:
        st.error(f"加载logo失败: {e}")
        return None

st.set_page_config(
    page_title="系统核心功能",
    page_icon="未命名的设计.png",
    layout="wide",
    initial_sidebar_state="collapsed"  # 默认隐藏侧边栏
)

# ============================================================================
# 自定义CSS样式 - 苹果官网风格（重新设计版）
# ============================================================================

def load_custom_css():
    """
    加载自定义CSS样式，实现苹果官网风格
    - 黑白蓝配色方案
    - 简洁现代的设计
    - 顶部导航栏设计
    - 移除侧边栏相关样式
    """
    st.markdown("""
    <style>
    /* 全局背景 - 蓝+黑高级质感 */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"], .main, .stApp {
        background: linear-gradient(135deg,
            #0b1220 0%,
            #0f1b3d 40%,
            #0a0f1e 100%) !important;
        background-size: 300% 300% !important;
        animation: gradientShift 20s ease infinite !important;
        min-height: 100vh !important;
        color: #ffffff !important;
    }
    
    /* 确保所有容器都使用绿色背景 */
    .block-container, [data-testid="block-container"] {
        background: transparent !important;
        padding-top: 1rem !important;
    }
    
    /* 主容器样式 */
    .main {
        padding: 0rem 1rem;
        position: relative;
    }
    
    /* Apple风格玻璃态背景层 */
    .main::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(ellipse at center,
            rgba(37, 99, 235, 0.12) 0%,
            rgba(2, 8, 23, 0.1) 50%,
            transparent 75%);
        pointer-events: none;
        z-index: -2;
    }
    
    /* Apple风格几何背景图案 */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image:
            radial-gradient(circle at 20% 20%, rgba(37, 99, 235, 0.12) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(34, 211, 238, 0.08) 0%, transparent 50%),
            linear-gradient(45deg, rgba(3, 15, 30, 0.35) 25%, transparent 25%),
            linear-gradient(-45deg, rgba(3, 15, 30, 0.25) 25%, transparent 25%);
        background-size: 250px 250px, 350px 350px, 80px 80px, 80px 80px;
        background-position: 0 0, 150px 150px, 0 0, 40px 40px;
        pointer-events: none;
        z-index: -1;
    }
    
    /* 背景动画 */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* 隐藏侧边栏 */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* 隐藏侧边栏相关按钮 */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* 苹果风格标题 */
    .apple-title {
        font-size: 3.5rem;
        font-weight: 600;
        color: #22d3ee;
        text-align: center;
        margin: 2rem 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* 副标题 */
    .apple-subtitle {
        font-size: 1.5rem;
        font-weight: 400;
        color: #ffffff;
        text-align: center;
        margin-bottom: 3rem;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* 顶部导航栏 - Apple风格玻璃态 */
    .top-navigation {
        background: linear-gradient(135deg,
            rgba(2, 8, 23, 0.85) 0%,
            rgba(15, 27, 61, 0.9) 40%,
            rgba(37, 99, 235, 0.8) 100%);
        backdrop-filter: blur(25px);
        padding: 1.5rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        box-shadow: 
            0 12px 40px rgba(37, 99, 235, 0.25),
            0 4px 12px rgba(2, 8, 23, 0.25),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .top-navigation::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(255, 255, 255, 0.1), 
            transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .nav-title {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-align: center;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .nav-buttons {
        display: flex;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    .nav-button {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        text-decoration: none;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-shadow: 0 4px 20px rgba(29, 78, 216, 0.2);
    }
    
    .nav-button:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(29, 78, 216, 0.3);
    }
    
    .nav-button.active {
        background: rgba(255, 255, 255, 0.98);
        color: #1d4ed8;
        font-weight: 600;
        box-shadow: 0 6px 25px rgba(29, 78, 216, 0.35);
    }
    
    /* Apple风格卡片 - 白蓝高级配色 */
    .apple-card {
        background: linear-gradient(145deg,
            rgba(11, 18, 32, 0.95) 0%,
            rgba(15, 27, 61, 0.92) 60%,
            rgba(11, 18, 32, 0.90) 100%);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 
            0 12px 40px rgba(37, 99, 235, 0.18),
            0 4px 12px rgba(2, 8, 23, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.95),
            inset 0 -1px 0 rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(37, 99, 235, 0.25);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .apple-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(29, 78, 216, 0.4), transparent);
    }
    
    .apple-card:hover {
        box-shadow: 
            0 20px 60px rgba(37, 99, 235, 0.3),
            0 6px 20px rgba(37, 99, 235, 0.15),
            inset 0 1px 0 rgba(37, 99, 235, 0.4),
            inset 0 -1px 0 rgba(37, 99, 235, 0.2);
        transform: translateY(-8px) scale(1.02);
        background: linear-gradient(145deg,
            rgba(11, 18, 32, 0.98) 0%,
            rgba(15, 27, 61, 0.95) 60%,
            rgba(11, 18, 32, 0.92) 100%);
        border-color: rgba(37, 99, 235, 0.4);
    }
    
    /* Apple蓝色强调色 */
    .apple-blue {
        color: #22d3ee;
        font-weight: 600;
    }
    
    /* Apple风格按钮 */
    .stButton > button {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6);
        color: white;
        border: none;
        border-radius: 16px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-shadow: 0 4px 20px rgba(29, 78, 216, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1e40af, #2563eb);
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(29, 78, 216, 0.4);
    }
    
    /* Apple风格指标卡片 */
    .metric-card {
        background: linear-gradient(135deg, 
            #1d4ed8 0%, 
            #3b82f6 25%, 
            #60a5fa 50%, 
            #93c5fd 75%, 
            #bfdbfe 100%);
        background-size: 200% 200%;
        animation: gradientFlow 8s ease infinite;
        color: white;
        padding: 2rem 1.5rem;
        border-radius: 24px;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 
            0 12px 40px rgba(29, 78, 216, 0.35),
            0 4px 12px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.15);
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 50% 0%, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
        pointer-events: none;
    }
    
    .metric-card:hover {
        transform: translateY(-4px) scale(1.03);
        box-shadow: 
            0 16px 50px rgba(29, 78, 216, 0.45),
            0 6px 16px rgba(0, 0, 0, 0.12),
            inset 0 1px 0 rgba(255, 255, 255, 0.4);
    }
    
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Apple风格数据表格 */
    .dataframe {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(37, 99, 235, 0.25);
        background: rgba(11, 18, 32, 0.9);
        backdrop-filter: blur(15px);
        box-shadow: 0 8px 32px rgba(37, 99, 235, 0.15);
        color: #ffffff;
    }
    
    /* Apple风格Streamlit组件 */
    .stSelectbox > div > div {
        background: linear-gradient(145deg, 
            rgba(255, 255, 255, 0.98) 0%, 
            rgba(240, 249, 255, 0.95) 100%);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(224, 242, 254, 0.7);
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(29, 78, 216, 0.15);
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div {
        background: linear-gradient(145deg, 
            rgba(255, 255, 255, 0.95) 0%, 
            rgba(240, 249, 255, 0.92) 100%);
        backdrop-filter: blur(15px);
        border: 2px dashed rgba(147, 197, 253, 0.6);
        border-radius: 20px;
        padding: 2rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stFileUploader > div:hover {
        border-color: rgba(37, 99, 235, 0.6);
        background: linear-gradient(145deg, 
            rgba(11, 18, 32, 0.98) 0%, 
            rgba(15, 27, 61, 0.95) 100%);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.3);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(145deg, 
            rgba(11, 18, 32, 0.9) 0%, 
            rgba(15, 27, 61, 0.85) 100%);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 0.5rem;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.25);
        border: 1px solid rgba(37, 99, 235, 0.4);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        color: #ffffff !important;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
        color: white !important;
        font-weight: 600;
        box-shadow: 0 4px 16px rgba(29, 78, 216, 0.3) !important;
    }
    
    /* Apple风格文本输入框 */
    .stTextInput > div > div > input {
        background: linear-gradient(145deg, 
            rgba(255, 255, 255, 0.98) 0%, 
            rgba(240, 249, 255, 0.95) 100%);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(224, 242, 254, 0.7);
        border-radius: 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: inset 0 1px 3px rgba(29, 78, 216, 0.1);
        color: #1e293b;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1d4ed8;
        box-shadow: 
            0 0 0 4px rgba(29, 78, 216, 0.2),
            inset 0 1px 3px rgba(29, 78, 216, 0.1);
        background: linear-gradient(145deg, 
            rgba(255, 255, 255, 0.99) 0%, 
            rgba(240, 249, 255, 0.98) 100%);
    }
    
    /* Apple风格选项卡 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(145deg, rgba(255,255,255,0.9), rgba(240,249,255,0.85));
        border-radius: 20px;
        padding: 6px;
        box-shadow: 0 4px 16px rgba(29, 78, 216, 0.1);
        border: 1px solid rgba(224, 242, 254, 0.6);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 16px;
        color: #64748b;
        font-weight: 500;
        padding: 12px 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
        color: white !important;
        font-weight: 600;
        box-shadow: 0 4px 20px rgba(29, 78, 216, 0.3) !important;
        border: none !important;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Apple风格响应式设计 */
    @media (max-width: 768px) {
        .apple-title {
            font-size: 2.5rem;
        }
        .apple-card {
            padding: 1.5rem;
            border-radius: 20px;
        }
        .nav-buttons {
            flex-direction: column;
            align-items: center;
            gap: 0.75rem;
        }
        .nav-button {
            width: 220px;
            text-align: center;
            border-radius: 14px;
        }
        .metric-card {
            padding: 1.5rem 1rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            flex-direction: column;
            gap: 6px;
        }
        .stTabs [data-baseweb="tab"] {
            width: 100%;
            text-align: center;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# 数据处理函数
# ============================================================================

def load_sample_data() -> Dict[str, pd.DataFrame]:
    """
    加载示例数据，模拟智水信息的真实业务数据
    专为各MCP服务工具提供所需的数据格式
    
    Returns:
        Dict[str, pd.DataFrame]: 包含各类业务数据的字典
    """
    # 财务数据 - 专为财务MCP工具优化的数据格式
    financial_data = {
        '月份': ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06'],
        '营业收入(万元)': [320, 280, 450, 380, 520, 410],
        '项目成本(万元)': [240, 210, 340, 290, 390, 310],
        '毛利润(万元)': [80, 70, 110, 90, 130, 100],
        '毛利率(%)': [25.0, 25.0, 24.4, 23.7, 25.0, 24.4],
        '运营费用(万元)': [45, 42, 48, 46, 52, 49],
        '净利润(万元)': [35, 28, 62, 44, 78, 51],
        # 新增：现金流数据（用于灰色马尔科夫模型预测）
        '现金流入(万元)': [350, 310, 480, 410, 550, 440],
        '现金流出(万元)': [285, 252, 388, 336, 442, 359],
        '净现金流(万元)': [65, 58, 92, 74, 108, 81],
        # 新增：财务比率分析数据
        '资产负债率(%)': [45.2, 43.8, 46.1, 44.5, 42.9, 43.7],
        '流动比率': [1.85, 1.92, 1.78, 1.88, 1.95, 1.83],
        '速动比率': [1.42, 1.48, 1.35, 1.45, 1.52, 1.39],
        # 新增：项目投资数据（用于IRR/NPV计算）
        '项目投资(万元)': [180, 150, 220, 190, 280, 210],
        '投资回报率(%)': [19.4, 18.7, 28.2, 23.2, 27.9, 24.3]
    }
    
    # 成本预测数据 - 为成本预测MCP工具提供水利工程项目数据
    cost_prediction_data = {
        '项目名称': ['白鹤滩水电站扩建', '锦屏一级水电站改造', '溪洛渡水电站维护', '向家坝水电站升级', '糯扎渡水电站优化'],
        '装机容量(MW)': [1600, 3600, 1386, 640, 585],
        '项目类型': ['水电站', '水电站', '水电站', '水电站', '水电站'],
        '坝高(m)': [289, 305, 285.5, 162, 261.5],
        '库容(亿m³)': [206.27, 77.6, 129.1, 51.63, 237.03],
        '地质条件': ['复杂', '极复杂', '中等', '简单', '复杂'],
        '施工难度': ['高', '极高', '中', '低', '高'],
        '预估成本(亿元)': [450, 680, 320, 180, 420],
        # 新增：建设周期数据（修复报表分析图表错误）
        '建设周期(月)': [72, 96, 48, 36, 60],
        '项目状态': ['规划中', '建设中', '运维中', '升级中', '优化中'],
        '完成进度(%)': [15, 45, 85, 60, 30]
    }
    
    # 知识库文档数据 - 为知识库MCP工具提供运维文档信息
    knowledge_docs_data = {
        '文档标题': ['水电站运维手册V2.1', '大坝安全监测规程', '电力设备维护指南', '应急预案操作手册', '智能监控系统说明书'],
        '文档类型': ['技术规范', '安全规程', '操作手册', '故障处理', '最佳实践'],
        '分类': ['运维管理', '安全监测', '设备维护', '应急处理', '系统操作'],
        '文档大小(KB)': [2048, 1536, 3072, 1024, 2560],
        '上传日期': ['2024-01-15', '2024-02-20', '2024-03-10', '2024-04-05', '2024-05-12'],
        '访问次数': [156, 89, 234, 67, 123],
        '文档状态': ['已索引', '已索引', '已索引', '处理中', '已索引']
    }
    
    # 员工效能评估数据 - 为人员效能MCP工具提供员工评估信息
    employee_efficiency_data = {
        '员工姓名': ['张明华', '李建国', '王小红', '赵志强', '陈美丽'],
        '部门': ['运维部', '技术部', '项目部', '运维部', '财务部'],
        '职位': ['生产运维', '技术研发', '管理岗位', '生产运维', '客户服务'],
        '工作年限': [8, 5, 12, 6, 4],
        '经济价值创造(分)': [85, 92, 88, 78, 82],
        '客户服务贡献(分)': [88, 75, 90, 85, 95],
        '流程治理表现(分)': [82, 88, 92, 80, 88],
        '学习成长能力(分)': [75, 95, 85, 70, 80],
        '综合评分': [82.5, 87.5, 88.8, 78.3, 86.3]
    }
    
    return {
        'financial': pd.DataFrame(financial_data),
        'cost_prediction': pd.DataFrame(cost_prediction_data),
        'knowledge_docs': pd.DataFrame(knowledge_docs_data),
        'employee_efficiency': pd.DataFrame(employee_efficiency_data)
    }

def process_uploaded_excel(uploaded_file) -> pd.DataFrame:
    """
    处理上传的Excel文件
    
    Args:
        uploaded_file: Streamlit上传的文件对象
        
    Returns:
        pd.DataFrame: 处理后的数据框
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(uploaded_file)
        
        # 数据清洗
        df = df.dropna(how='all')  # 删除全空行
        df.columns = df.columns.astype(str)  # 确保列名为字符串
        
        return df
    except Exception as e:
        st.error(f"Excel文件处理失败: {str(e)}")
        return pd.DataFrame()

def export_to_json(data: Dict[str, Any]) -> str:
    """
    将数据导出为JSON格式 - 符合Agno协调中心要求
    专为各MCP服务工具提供所需的数据格式
    
    Args:
        data: 要导出的数据字典
        
    Returns:
        str: JSON格式的字符串
    """
    try:
        # 转换为Agno协调中心要求的格式
        export_data = {
            "task_type": "comprehensive_analysis",
            "analysis_requirements": {
                "focus_areas": ["financial", "cost_prediction", "knowledge", "employee_efficiency"],
                "output_format": "comprehensive_report",
                "include_recommendations": True
            },
            "project_data": {
                "company_info": {
                    "name": "四川智水信息技术有限公司",
                    "industry": "电力水利信息技术",
                    "established_year": 2011,
                    "employee_count": 80
                },
                "financial_data": {
                    "revenue_data": data["financial"].to_dict("records") if "financial" in data and isinstance(data["financial"], pd.DataFrame) else [],
                    "cash_flow_data": {
                        "cash_inflows": data["financial"]["现金流入(万元)"].tolist() if "financial" in data and isinstance(data["financial"], pd.DataFrame) else [],
                        "cash_outflows": data["financial"]["现金流出(万元)"].tolist() if "financial" in data and isinstance(data["financial"], pd.DataFrame) else [],
                        "net_cash_flows": data["financial"]["净现金流(万元)"].tolist() if "financial" in data and isinstance(data["financial"], pd.DataFrame) else [],
                        "periods": data["financial"]["月份"].tolist() if "financial" in data and isinstance(data["financial"], pd.DataFrame) else []
                    },
                    "investment_data": {
                        "project_investments": data["financial"]["项目投资(万元)"].tolist() if "financial" in data and isinstance(data["financial"], pd.DataFrame) else [],
                        "investment_returns": data["financial"]["投资回报率(%)"].tolist() if "financial" in data and isinstance(data["financial"], pd.DataFrame) else [],
                        "discount_rate": 8.5  # 假设折现率为8.5%
                    },
                    "financial_ratios": {
                        "debt_to_asset_ratio": data["financial"]["资产负债率(%)"].tolist() if "financial" in data and isinstance(data["financial"], pd.DataFrame) else [],
                        "current_ratio": data["financial"]["流动比率"].tolist() if "financial" in data and isinstance(data["financial"], pd.DataFrame) else [],
                        "quick_ratio": data["financial"]["速动比率"].tolist() if "financial" in data and isinstance(data["financial"], pd.DataFrame) else []
                    },
                    "cost_structure": {
                        "total_revenue": float(data["financial"]["营业收入(万元)"].sum()) if "financial" in data and isinstance(data["financial"], pd.DataFrame) else 0.0,
                        "total_cost": float(data["financial"]["项目成本(万元)"].sum()) if "financial" in data and isinstance(data["financial"], pd.DataFrame) else 0.0,
                        "profit_margin": float(data["financial"]["毛利率(%)"].mean()) if "financial" in data and isinstance(data["financial"], pd.DataFrame) else 0.0
                    }
                },
                "cost_prediction_data": {
                    "hydropower_projects": data["cost_prediction"].to_dict("records") if "cost_prediction" in data and isinstance(data["cost_prediction"], pd.DataFrame) else [],
                    "prediction_features": {
                        "total_capacity": float(data["cost_prediction"]["装机容量(MW)"].sum()) if "cost_prediction" in data and isinstance(data["cost_prediction"], pd.DataFrame) else 0.0,
                        "average_cost": float(data["cost_prediction"]["预估成本(亿元)"].mean()) if "cost_prediction" in data and isinstance(data["cost_prediction"], pd.DataFrame) else 0.0,
                        "project_count": len(data["cost_prediction"]) if "cost_prediction" in data and isinstance(data["cost_prediction"], pd.DataFrame) else 0,
                        "average_construction_period": float(data["cost_prediction"]["建设周期(月)"].mean()) if "cost_prediction" in data and isinstance(data["cost_prediction"], pd.DataFrame) else 0.0,
                        "completion_progress": float(data["cost_prediction"]["完成进度(%)"].mean()) if "cost_prediction" in data and isinstance(data["cost_prediction"], pd.DataFrame) else 0.0
                    }
                },
                "knowledge_data": {
                    "document_library": data["knowledge_docs"].to_dict("records") if "knowledge_docs" in data and isinstance(data["knowledge_docs"], pd.DataFrame) else [],
                    "knowledge_metrics": {
                        "total_documents": len(data["knowledge_docs"]) if "knowledge_docs" in data and isinstance(data["knowledge_docs"], pd.DataFrame) else 0,
                        "indexed_documents": len(data["knowledge_docs"][data["knowledge_docs"]["文档状态"] == "已索引"]) if "knowledge_docs" in data and isinstance(data["knowledge_docs"], pd.DataFrame) else 0,
                        "total_access_count": int(data["knowledge_docs"]["访问次数"].sum()) if "knowledge_docs" in data and isinstance(data["knowledge_docs"], pd.DataFrame) else 0
                    }
                },
                "employee_efficiency_data": {
                    "employee_evaluations": data["employee_efficiency"].to_dict("records") if "employee_efficiency" in data and isinstance(data["employee_efficiency"], pd.DataFrame) else [],
                    "efficiency_metrics": {
                        "average_score": float(data["employee_efficiency"]["综合评分"].mean()) if "employee_efficiency" in data and isinstance(data["employee_efficiency"], pd.DataFrame) else 0.0,
                        "top_performer_score": float(data["employee_efficiency"]["综合评分"].max()) if "employee_efficiency" in data and isinstance(data["employee_efficiency"], pd.DataFrame) else 0.0,
                        "employee_count": len(data["employee_efficiency"]) if "employee_efficiency" in data and isinstance(data["employee_efficiency"], pd.DataFrame) else 0
                    }
                },
                "metadata": {
                    "export_timestamp": datetime.now().isoformat(),
                    "data_source": "智水信息管理平台",
                    "data_types": ["financial", "cost_prediction", "knowledge_docs", "employee_efficiency"],
                    "data_quality_score": 0.85
                }
            }
        }
        
        return json.dumps(export_data, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"JSON导出失败: {str(e)}")
        return "{}"

# ============================================================================
# Multi-Agent交互函数
# ============================================================================

# 注意：call_multi_agent_system 和 call_agent_api 函数已移至 api_client.py 中

# ============================================================================
# 导航栏函数
# ============================================================================

def render_navigation():
    """
    渲染顶部导航栏
    """
    st.markdown("""
    <div class="top-navigation">
        <div class="nav-title">🧭 系统核心功能</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建导航按钮
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        dashboard_btn = st.button("📊 数据仪表板", key="nav_dashboard", use_container_width=True)
    with col2:
        data_mgmt_btn = st.button("📁 数据管理", key="nav_data", use_container_width=True)
    with col3:
        ai_assistant_btn = st.button("🤖 AI智能体", key="nav_ai", use_container_width=True)
    with col4:
        history_btn = st.button("📜 历史会话", key="nav_history", use_container_width=True)
    with col5:
        reports_btn = st.button("📈 报表分析", key="nav_reports", use_container_width=True)
    with col6:
        about_btn = st.button("ℹ️ 关于系统", key="nav_about", use_container_width=True)
    
    # 根据按钮点击设置页面状态
    if dashboard_btn:
        st.session_state.current_page = "dashboard"
    elif data_mgmt_btn:
        st.session_state.current_page = "data_management"
    elif ai_assistant_btn:
        st.session_state.current_page = "agent_interaction"
    elif history_btn:
        st.session_state.current_page = "conversation_history"
    elif reports_btn:
        st.session_state.current_page = "reports"
    elif about_btn:
        st.session_state.current_page = "about"
    
    # 初始化页面状态
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    return st.session_state.current_page

# ============================================================================
# 主界面函数
# ============================================================================

def render_apple_header():
    """
    渲染页面头部 - 苹果风格
    """
    logo_base64 = load_logo_base64()
    if logo_base64:
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" style="width: 56px; height: 56px; vertical-align: text-bottom; margin-right: 15px;"/>'
    else:
        logo_html = '💧'  # 如果logo加载失败，回退到水滴emoji
    
    st.markdown(f"""
    <div class="apple-title">{logo_html} 智水信息AI智慧信息系统</div>
    <div class="apple-subtitle">AI驱动的项目信息整合与智能决策支持系统</div>
    <div style="text-align: center; margin-top: 10px; color: #ffffff; font-size: 14px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">2025 Designed by 商海星辰</div>
    """, unsafe_allow_html=True)

def render_metrics_dashboard(data: Dict[str, pd.DataFrame]):
    """
    渲染关键指标仪表板
    
    Args:
        data: 业务数据字典
    """
    st.markdown("### 📊 关键业务指标")
    
    # 计算关键指标 - 使用占位符代替真实数据，员工总数为已知数据
    total_projects = "**"
    active_projects = "**"
    total_revenue = "**"
    avg_profit_margin = "**"
    total_staff = 80
    
    # 创建指标卡片
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_projects}</div>
            <div class="metric-label">总项目数</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{active_projects}</div>
            <div class="metric-label">进行中项目</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_revenue}</div>
            <div class="metric-label">总营收(万元)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_profit_margin}</div>
            <div class="metric-label">平均毛利率</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_staff}</div>
            <div class="metric-label">员工总数</div>
        </div>
        """, unsafe_allow_html=True)

def render_data_visualization(data: Dict[str, pd.DataFrame]):
    """
    渲染数据可视化图表
    
    Args:
        data: 业务数据字典
    """
    st.markdown("### 📈 数据可视化分析")
    
    # 创建图表列
    col1, col2 = st.columns(2)
    
    with col1:
        # 财务趋势图 - 彩色配色方案
        fig_financial = go.Figure()
        fig_financial.add_trace(go.Scatter(
            x=data['financial']['月份'],
            y=data['financial']['营业收入(万元)'],
            mode='lines+markers',
            name='营业收入',
            line=dict(color='#22d3ee', width=3),  # 青色
            marker=dict(size=8, color='#22d3ee')
        ))
        fig_financial.add_trace(go.Scatter(
            x=data['financial']['月份'],
            y=data['financial']['净利润(万元)'],
            mode='lines+markers',
            name='净利润',
            line=dict(color='#a78bfa', width=3),  # 紫色
            marker=dict(size=8, color='#a78bfa')
        ))
        fig_financial.add_trace(go.Scatter(
            x=data['financial']['月份'],
            y=data['financial']['净现金流(万元)'],
            mode='lines+markers',
            name='净现金流',
            line=dict(color='#10b981', width=3),  # 绿色
            marker=dict(size=8, color='#10b981')
        ))
        
        fig_financial.update_layout(
            title="财务趋势分析",
            xaxis_title="月份",
            yaxis_title="金额(万元)",
            template="plotly_dark",
            plot_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
            paper_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
            height=400,
            font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#ffffff'),
            title_font=dict(size=18, color='#60a5fa'),
            xaxis=dict(gridcolor='rgba(37, 99, 235, 0.3)', linecolor='#2563eb', title_font=dict(color='#ffffff')),
            yaxis=dict(gridcolor='rgba(37, 99, 235, 0.3)', linecolor='#2563eb', title_font=dict(color='#ffffff')),
            legend=dict(bgcolor='rgba(15, 27, 61, 0.9)', bordercolor='#2563eb', borderwidth=1, font=dict(color='#ffffff'))
        )
        
        st.plotly_chart(fig_financial, use_container_width=True)
    
    with col2:
        # 成本预测分析
        if 'cost_prediction' in data and not data['cost_prediction'].empty:
            # 按项目类型分组的成本分析
            cost_by_type = data['cost_prediction'].groupby('项目类型')['预估成本(亿元)'].sum()
            
            fig_cost = go.Figure(data=[go.Pie(
                labels=cost_by_type.index,
                values=cost_by_type.values,
                hole=0.4,
                marker_colors=['#22d3ee', '#a78bfa', '#10b981', '#f59e0b', '#ef4444', '#ec4899']  # 彩色配色
            )])
            
            fig_cost.update_layout(
                title="项目类型成本分布",
                template="plotly_dark",
                plot_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
                paper_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
                height=400,
                font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#ffffff'),
                title_font=dict(size=18, color='#22d3ee'),
                legend=dict(bgcolor='rgba(15, 27, 61, 0.9)', bordercolor='#2563eb', borderwidth=1, font=dict(color='#ffffff'))
            )
            
            st.plotly_chart(fig_cost, use_container_width=True)
        else:
            # 显示占位符图表
            fig_placeholder = go.Figure(data=[go.Pie(
                labels=['水电站', '风电场', '光伏电站'],
                values=[45, 30, 25],
                hole=0.4,
                marker_colors=['#22d3ee', '#a78bfa', '#10b981']  # 彩色配色
            )])
            
            fig_placeholder.update_layout(
                title="项目类型成本分布（示例）",
                template="plotly_dark",
                plot_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
                paper_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
                height=400,
                font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#ffffff'),
                title_font=dict(size=18, color='#22d3ee'),
                legend=dict(bgcolor='rgba(15, 27, 61, 0.9)', bordercolor='#2563eb', borderwidth=1, font=dict(color='#ffffff'))
            )
            
            st.plotly_chart(fig_placeholder, use_container_width=True)

def render_data_management():
    """
    渲染数据管理功能区
    """
    st.markdown("### 📁 数据管理")
    
    # 创建功能选项卡
    tab1, tab2 = st.tabs(["📤 数据导入", "📥 数据导出"])
    
    with tab1:
        # 添加自定义CSS优化数据导入区域的可读性
        st.markdown("""
        <style>
        /* 文件上传组件：提升文字可读性 */
        div[data-testid="stFileUploader"] * {
            color: #ffffff !important;
        }
        
        /* 拖拽/浏览区域的提示与按钮文字 */
        div[data-testid="stFileUploaderDropzone"] *,
        div[data-testid="stFileUploaderDropzone"] button {
            color: #e5e7eb !important;
            font-weight: 500 !important;
        }
        
        /* 已上传文件项：文件名与细节 */
        div[data-testid="stUploadedFile"] * {
            color: #ffffff !important;
        }
        div[data-testid="stUploadedFile"] strong,
        div[data-testid="stUploadedFileName"] {
            color: #ffffff !important; /* 文件名更亮 */
            font-weight: 600 !important;
        }
        div[data-testid="stUploadedFileDetails"],
        div[data-testid="stUploadedFile"] small {
            color: #cbd5e1 !important; /* 大小/类型信息 */
        }
        
        /* 删除按钮（红色强调） */
        div[data-testid="stUploadedFile"] button {
            color: #ef4444 !important;
            font-weight: 500 !important;
        }
        div[data-testid="stUploadedFile"] button:hover {
            color: #ffffff !important;
            background: rgba(239, 68, 68, 0.15) !important;
        }
        
        /* 文件上传标签优化 */
        div[data-testid="stFileUploader"] label {
            color: #ffffff !important;
            font-weight: 500 !important;
        }
        
        /* Metric容器文本颜色优化 */
        div[data-testid="metric-container"] * {
            color: #e5e7eb !important;
        }
        /* Metric 数值（更亮，白色） */
        div[data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-weight: 600 !important;
        }
        /* Metric 标签（浅灰） */
        div[data-testid="stMetricLabel"] {
            color: #e5e7eb !important;
        }
        /* Metric 增减颜色 */
        div[data-testid="stMetricDelta"] {
            color: #10b981 !important;
        }
        div[data-testid="stMetricDelta"] svg path[fill="#ff2e2e"] {
            fill: #ef4444 !important;
        }
        
        /* 选项卡文字优化 */
        .stTabs [data-baseweb="tab"] {
            color: #cbd5e1 !important;
        }
        .stTabs [aria-selected="true"] {
            color: #ffffff !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 📊 数据导入")
        
        # 创建四个数据导入模块
        col1, col2 = st.columns(2)
        
        with col1:
            # 财务分析数据导入
            st.markdown("##### 💰 财务分析数据")
            st.markdown("用于财务AI分析服务的现金流预测")
            
            financial_file = st.file_uploader(
                "选择财务分析Excel文件",
                type=['xlsx', 'xls'],
                key="financial_upload",
                help="包含现金流、收入支出等财务数据",
                label_visibility="collapsed"
            )
            
            if financial_file is not None:
                df_financial = process_uploaded_excel(financial_file)
                if not df_financial.empty:
                    st.success(f"✅ 财务数据导入成功：{len(df_financial)} 行")
                    st.dataframe(df_financial.head(3), use_container_width=True)
                    st.session_state['financial_data'] = df_financial
            
            # 成本预测数据导入
            st.markdown("##### 📈 成本预测数据")
            st.markdown("用于成本预测MCP服务的项目分析")
            
            cost_file = st.file_uploader(
                "选择成本预测Excel文件",
                type=['xlsx', 'xls'],
                key="cost_upload",
                help="包含项目成本、工期、风险等数据",
                label_visibility="collapsed"
            )
            
            if cost_file is not None:
                df_cost = process_uploaded_excel(cost_file)
                if not df_cost.empty:
                    st.success(f"✅ 成本数据导入成功：{len(df_cost)} 行")
                    st.dataframe(df_cost.head(3), use_container_width=True)
                    st.session_state['cost_data'] = df_cost
        
        with col2:
            # 员工效能数据导入
            st.markdown("##### 👤 员工效能数据")
            st.markdown("用于人员效能MCP服务的评估分析")
            
            hr_file = st.file_uploader(
                "选择员工效能Excel文件",
                type=['xlsx', 'xls'],
                key="hr_upload",
                help="包含员工绩效、技能、项目贡献等数据",
                label_visibility="collapsed"
            )
            
            if hr_file is not None:
                df_hr = process_uploaded_excel(hr_file)
                if not df_hr.empty:
                    st.success(f"✅ 效能数据导入成功：{len(df_hr)} 行")
                    st.dataframe(df_hr.head(3), use_container_width=True)
                    st.session_state['hr_data'] = df_hr
            
            # 财务报表数据导入
            st.markdown("##### 📋 财务报表数据")
            st.markdown("用于财务报表分析和合规检查")
            
            report_file = st.file_uploader(
                "选择财务报表Excel文件",
                type=['xlsx', 'xls'],
                key="report_upload",
                help="包含资产负债表、利润表、现金流量表等",
                label_visibility="collapsed"
            )
            
            if report_file is not None:
                df_report = process_uploaded_excel(report_file)
                if not df_report.empty:
                    st.success(f"✅ 报表数据导入成功：{len(df_report)} 行")
                    st.dataframe(df_report.head(3), use_container_width=True)
                    st.session_state['report_data'] = df_report
        
        # 数据导入状态总览
        st.markdown("---")
        st.markdown("#### 📊 数据导入状态")
        
        status_col1, status_col2, status_col3, status_col4 = st.columns(4)
        
        with status_col1:
            if 'financial_data' in st.session_state:
                st.metric("财务分析数据", f"{len(st.session_state['financial_data'])} 行", "✅ 已导入")
            else:
                st.metric("财务分析数据", "0 行", "⏳ 待导入")
        
        with status_col2:
            if 'cost_data' in st.session_state:
                st.metric("成本预测数据", f"{len(st.session_state['cost_data'])} 行", "✅ 已导入")
            else:
                st.metric("成本预测数据", "0 行", "⏳ 待导入")
        
        with status_col3:
            if 'hr_data' in st.session_state:
                st.metric("员工效能数据", f"{len(st.session_state['hr_data'])} 行", "✅ 已导入")
            else:
                st.metric("员工效能数据", "0 行", "⏳ 待导入")
        
        with status_col4:
            if 'report_data' in st.session_state:
                st.metric("财务报表数据", f"{len(st.session_state['report_data'])} 行", "✅ 已导入")
            else:
                st.metric("财务报表数据", "0 行", "⏳ 待导入")
    
    with tab2:
        # 数据导出区域也应用相同的字体颜色优化
        st.markdown("""
        <style>
        /* 确保数据导出区域的文字也清晰可见 */
        .stButton > button {
            color: #ffffff !important;
            font-weight: 500 !important;
        }
        /* 导出区域的说明文字 */
        .stMarkdown p, .stMarkdown li {
            color: #ffffff !important;
        }
        /* 文件下载链接 */
        a[download] {
            color: #22d3ee !important;
            font-weight: 500 !important;
        }
        a[download]:hover {
            color: #60a5fa !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 📤 数据导出")
        st.markdown("为智水信息Multi-Agent智能体导出专门格式数据")
        
        # 创建三列布局
        col1, col2, col3 = st.columns(3)
        
        # 财务数据导出
        with col1:
            st.markdown("##### 💰 财务分析数据")
            st.markdown("用于财务AI分析服务的现金流预测")
            
            if st.button("📊 导出财务数据", key="export_financial", use_container_width=True):
                # 从financial_data.json文件加载完整的财务MCP服务测试数据
                try:
                    with open("../financial_data.json", "r", encoding="utf-8") as f:
                        financial_data = json.load(f)
                except FileNotFoundError:
                    # 如果文件不存在，使用备用数据
                    financial_data = {
                        "description": "四川智水信息技术有限公司 - 财务MCP服务完整测试数据集",
                        "version": "1.0",
                        "created_date": "2024-01-15",
                        "company": "四川智水信息技术有限公司",
                        "industry": "电力水利信息技术",
                        "cash_flow_prediction": {
                            "description": "现金流预测工具测试数据",
                            "test_cases": [
                                {
                                    "case_name": "智慧电厂项目现金流预测",
                                    "data": {
                                        "project_name": "某电力公司智慧电厂管理系统",
                                        "project_type": "智慧电厂",
                                        "contract_amount": 2800000,
                                        "start_date": "2024-02-01",
                                        "end_date": "2024-12-31",
                                        "payment_schedule": [
                                            {"date": "2024-02-15", "amount": 840000, "type": "预付款", "percentage": 30},
                                            {"date": "2024-06-30", "amount": 1120000, "type": "进度款", "percentage": 40},
                                            {"date": "2024-10-31", "amount": 560000, "type": "验收款", "percentage": 20},
                                            {"date": "2025-01-31", "amount": 280000, "type": "质保金", "percentage": 10}
                                        ],
                                        "cost_breakdown": {
                                            "人工成本": 1400000,
                                            "硬件采购": 700000,
                                            "软件许可": 350000,
                                            "差旅费用": 140000,
                                            "其他费用": 210000
                                        }
                                    }
                                }
                            ]
                        },
                        "financial_qa": {
                            "description": "财务问答工具测试数据",
                            "test_cases": [
                                {
                                    "case_name": "电力行业财务分析",
                                    "questions": [
                                        "智水信息在电力行业项目的平均毛利率是多少？",
                                        "电力项目的回款周期通常多长？"
                                    ]
                                }
                            ]
                        },
                        "irr_calculation": {
                            "description": "IRR内部收益率计算工具测试数据",
                            "test_cases": [
                                {
                                    "case_name": "智慧电厂项目IRR计算",
                                    "data": {
                                        "project_name": "某电力公司智慧电厂管理系统",
                                        "initial_investment": -500000,
                                        "cash_flows": [
                                            {"period": 1, "amount": 200000, "description": "第1季度净现金流"},
                                            {"period": 2, "amount": 250000, "description": "第2季度净现金流"}
                                        ]
                                    }
                                }
                            ]
                        },
                        "budget_monitoring": {
                            "description": "预算监控工具测试数据",
                            "test_cases": [
                                {
                                    "case_name": "智慧电厂项目预算监控",
                                    "data": {
                                        "project_name": "某电力公司智慧电厂管理系统",
                                        "budget_period": "2024年度",
                                        "total_budget": 2800000
                                    }
                                }
                            ]
                        }
                    }
                
                # 转换为JSON
                json_data = json.dumps(financial_data, ensure_ascii=False, indent=2)
                
                # 创建下载链接
                b64 = base64.b64encode(json_data.encode()).decode()
                href = f'<a href="data:application/json;base64,{b64}" download="财务数据_MCP_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json">📥 下载财务数据</a>'
                st.markdown(href, unsafe_allow_html=True)
                
                # 预览数据
                with st.expander("📄 预览财务数据"):
                    st.json(financial_data)
        
        # 成本预测数据导出
        with col2:
            st.markdown("##### 💸 成本预测数据")
            st.markdown("用于成本预测MCP服务的项目分析")
            
            if st.button("📈 导出成本数据", key="export_cost", use_container_width=True):
                # 从成本预测MCP测试数据文件加载完整数据
                try:
                    # 修复路径问题：使用当前文件的绝对路径来构建正确的相对路径
                    current_file = Path(__file__).resolve()
                    project_root = current_file.parent.parent
                    cost_data_file_path = project_root / "3_cost_prediction_mcp" / "cost_prediction_data.json"
                    
                    if cost_data_file_path.exists():
                        with open(cost_data_file_path, 'r', encoding='utf-8') as f:
                            cost_data = json.load(f)
                    else:
                        # 备用数据 - 如果文件不存在
                        cost_data = {
                            "description": "四川智水信息技术有限公司 - 成本预测MCP服务测试数据集",
                            "version": "1.0.0",
                            "created_date": datetime.now().strftime("%Y-%m-%d"),
                            "purpose": "为成本预测MCP服务的三个核心工具提供完整的测试数据",
                            "tools_covered": [
                                "predict_hydropower_cost - 智慧水电成本预测器",
                                "assess_project_risk - 智能项目风险评估器",
                                "generate_analysis_data - 成本分析数据生成器"
                            ],
                            "note": "备用数据 - 原始测试数据文件未找到"
                        }
                        st.warning("⚠️ 使用备用数据 - 原始测试数据文件未找到")
                        
                except Exception as e:
                    st.error(f"❌ 加载数据失败: {e}")
                    cost_data = {"error": f"数据加载失败: {str(e)}"}
                
                # 转换为JSON
                json_data = json.dumps(cost_data, ensure_ascii=False, indent=2)
                
                # 创建下载链接
                b64 = base64.b64encode(json_data.encode()).decode()
                href = f'<a href="data:application/json;base64,{b64}" download="成本预测MCP测试数据_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json">📥 下载成本预测测试数据</a>'
                st.markdown(href, unsafe_allow_html=True)
                
                # 预览数据
                with st.expander("📄 预览成本预测测试数据"):
                    st.json(cost_data)
        
        # 员工效能数据导出
        with col3:
            st.markdown("##### 👥 员工效能数据")
            st.markdown("用于人员效能MCP服务的评估分析")
            
            if st.button("👤 导出效能数据", key="export_hr", use_container_width=True):
                # 从人员效能MCP数据文件加载完整数据
                try:
                    # 修复路径问题：使用当前文件的绝对路径来构建正确的相对路径
                    current_file = Path(__file__).resolve()
                    project_root = current_file.parent.parent
                    hr_data_file_path = project_root / "5_hr_efficiency_mcp" / "hr_efficiency_data.json"
                    
                    if hr_data_file_path.exists():
                        with open(hr_data_file_path, 'r', encoding='utf-8') as f:
                            hr_data = json.load(f)
                    else:
                        # 如果文件不存在，使用默认数据
                        hr_data = {
                            "description": "智水人员效能管理MCP服务完整数据demo",
                            "version": "1.0",
                            "created_date": "2024-12-19",
                            "tools_supported": [
                                "evaluate_employee_efficiency",
                                "generate_efficiency_report"
                            ],
                            "employee_data_demo": {
                                "name": "张伟",
                                "employee_id": "ZS2024001",
                                "department": "技术研发部",
                                "position": "高级软件工程师",
                                "evaluation_period": "2024年第四季度",
                                "hire_date": "2022-03-15",
                                "education": "本科",
                                "work_experience": "5年"
                            },
                            "metrics_data_demo": {
                                "economic_value": {
                                    "cost_optimization": {
                                        "cost_reduction_amount": 150000,
                                        "cost_reduction_percentage": 12.5,
                                        "optimization_projects_count": 3,
                                        "roi_improvement": 8.2
                                    },
                                    "digital_efficiency": {
                                        "automation_hours_saved": 240,
                                        "process_improvement_count": 5,
                                        "system_uptime_percentage": 99.2,
                                        "digital_tools_adoption_rate": 85
                                    }
                                },
                                "customer_social": {
                                    "service_reliability": {
                                        "system_availability": 99.5,
                                        "incident_response_time_minutes": 15,
                                        "customer_satisfaction_score": 4.6,
                                        "sla_compliance_rate": 98.5
                                    },
                                    "customer_service": {
                                        "customer_feedback_score": 4.7,
                                        "service_improvement_initiatives": 4,
                                        "customer_retention_contribution": 92,
                                        "social_responsibility_hours": 16
                                    }
                                },
                                "internal_process": {
                                    "process_efficiency": {
                                        "task_completion_rate": 96,
                                        "deadline_adherence_rate": 94,
                                        "process_optimization_suggestions": 8,
                                        "cross_department_collaboration_score": 4.3
                                    },
                                    "risk_compliance": {
                                        "compliance_training_completion": 100,
                                        "security_incident_count": 0,
                                        "audit_findings_resolved": 5,
                                        "risk_assessment_participation": 12
                                    }
                                },
                                "learning_growth": {
                                    "skill_development": {
                                        "new_certifications_count": 2,
                                        "training_hours_completed": 72,
                                        "skill_assessment_score": 88
                                    },
                                    "innovation_sharing": {
                                        "innovation_proposals_submitted": 3,
                                        "innovation_proposals_adopted": 2,
                                        "knowledge_sharing_contributions": 8
                                    },
                                    "environmental_practice": {
                                        "green_behavior_score": 4.2,
                                        "environmental_improvement_proposals": 1,
                                        "environmental_training_hours": 6
                                    }
                                }
                            },
                            "position_types": [
                                "生产运维",
                                "客户服务", 
                                "技术研发",
                                "管理岗位"
                            ],
                            "additional_test_employees": [
                                {
                                    "name": "李娜",
                                    "employee_id": "ZS2024002",
                                    "department": "客户服务部",
                                    "position": "客户服务经理",
                                    "position_type": "客户服务",
                                    "evaluation_period": "2024年第四季度"
                                },
                                {
                                    "name": "王强",
                                    "employee_id": "ZS2024003", 
                                    "department": "运维部",
                                    "position": "运维工程师",
                                    "position_type": "生产运维",
                                    "evaluation_period": "2024年第四季度"
                                },
                                {
                                    "name": "陈明",
                                    "employee_id": "ZS2024004",
                                    "department": "管理层",
                                    "position": "技术总监",
                                    "position_type": "管理岗位",
                                    "evaluation_period": "2024年第四季度"
                                }
                            ]
                        }
                        
                except Exception as e:
                    st.error(f"加载人员效能数据失败: {str(e)}")
                    hr_data = {"error": "数据加载失败"}
                
                # 转换为JSON
                json_data = json.dumps(hr_data, ensure_ascii=False, indent=2)
                
                # 创建下载链接
                b64 = base64.b64encode(json_data.encode()).decode()
                href = f'<a href="data:application/json;base64,{b64}" download="员工效能数据_MCP_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json">📥 下载效能数据</a>'
                st.markdown(href, unsafe_allow_html=True)
                
                # 预览数据
                with st.expander("📄 预览效能数据"):
                    st.json(hr_data)
        
        # 使用说明
        st.markdown("---")
        st.markdown("##### 📋 使用说明")
        st.info("""
        **数据导出说明：**
        
        1. **财务数据** - 包含历史现金流、项目收入、成本结构等，可直接用于财务AI分析服务的现金流预测
        2. **成本预测数据** - 包含项目信息、历史成本、风险因素等，可直接用于成本预测MCP服务的分析
        3. **员工效能数据** - 包含员工信息和四大维度评估指标，可直接用于人员效能MCP服务的评估
        
        导出的JSON格式数据可以用于智水信息Multi-Agent智能体的分析。
        """)
    


def render_agent_interaction():
    """
    渲染智水Multi-Agent系统交互界面 - Gemini风格聊天界面
    """
    st.markdown("### 🤖 智水Multi-Agent智能体系统")
    
    # 系统状态显示
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("**🔗 连接状态：** 🟢 智水Multi-Agent系统已连接")
    with col2:
        st.markdown("**🧠 智能体：** 6个专业智能体")
    with col3:
        if st.button("🔄 刷新连接", key="refresh_connection"):
            st.rerun()
    
    st.markdown("---")
    
    # 初始化会话状态
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_input' not in st.session_state:
        st.session_state.current_input = ""
    if 'session_id' not in st.session_state:
        # 创建新的会话ID
        from api_client import get_agno_client
        agno_client = get_agno_client()
        session_id = agno_client.create_session()
        if session_id:
            st.session_state.session_id = session_id
            # 尝试从后端恢复对话历史
            try:
                history = agno_client.get_conversation_history(session_id)
                if history:
                    # 转换后端历史格式为前端格式
                    converted_history = []
                    user_msg = None
                    for msg in history:
                        if msg['message_type'] == 'user':
                            user_msg = msg['content']
                        elif msg['message_type'] == 'assistant' and user_msg:
                            try:
                                ai_response = json.loads(msg['content']) if isinstance(msg['content'], str) else msg['content']
                            except:
                                ai_response = {'status': 'success', 'response': msg['content']}
                            
                            converted_history.append({
                                'user_message': user_msg,
                                'ai_response': ai_response,
                                'timestamp': msg['timestamp']
                            })
                            user_msg = None
                    
                    st.session_state.chat_history = converted_history
            except Exception as e:
                st.warning(f"恢复对话历史失败: {str(e)}")
        else:
            # 如果无法创建会话ID，使用本地UUID
            import uuid
            st.session_state.session_id = str(uuid.uuid4())
    
    # 对话历史显示区域（现在在上方，大框）
    st.markdown("#### 💬 对话历史")
    
    # 创建对话历史显示容器（大框，无高度限制）
    chat_history_container = st.container()
    
    with chat_history_container:
        if len(st.session_state.chat_history) > 0:
            # 显示完整聊天历史
            for i, chat in enumerate(st.session_state.chat_history):
                # 用户消息
                st.markdown(f"""
                <div style="
                    background-color: #f0f0f0;
                    padding: 15px;
                    border-radius: 15px;
                    margin: 10px 0;
                    margin-left: 50px;
                    border-left: 4px solid #007aff;
                ">
                    <strong>🙋‍♂️ 您：</strong><br>
                    {chat['user_message']}
                </div>
                """, unsafe_allow_html=True)
                
                # AI回复
                # 确保ai_response包含status字段，如果没有则设置默认值
                ai_response = chat['ai_response']
                if not isinstance(ai_response, dict):
                    ai_response = {'status': 'error', 'response': str(ai_response)}
                elif 'status' not in ai_response:
                    ai_response['status'] = 'success'  # 默认为成功状态
                
                if ai_response['status'] in ['success', 'simulation']:
                    status_icon = "🤖" if ai_response['status'] == 'success' else "⚠️"
                    status_text = "智水Multi-Agent系统" if ai_response['status'] == 'success' else "模拟模式"
                    
                    # 格式化AI回复内容
                    response_content = ai_response.get('response', '响应内容缺失')
                    # 如果response是字典且包含summary_content，直接传递
                    if isinstance(response_content, dict) and 'summary_content' in response_content:
                        formatted_response = format_ai_response_for_display(json.dumps(response_content))
                    else:
                        formatted_response = format_ai_response_for_display(response_content)
                    
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
                        padding: 15px;
                        border-radius: 15px;
                        margin: 10px 0;
                        margin-right: 50px;
                        border-left: 4px solid #ffffff;
                        box-shadow: 0 2px 10px rgba(100, 116, 139, 0.2);
                    ">
                        <strong>{status_icon} {status_text}：</strong><br><br>
                        {formatted_response}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # 格式化错误信息
                    error_content = ai_response.get('response', '错误信息缺失')
                    if isinstance(error_content, dict) and 'summary_content' in error_content:
                        formatted_error = format_ai_response_for_display(json.dumps(error_content))
                    else:
                        formatted_error = format_ai_response_for_display(error_content)
                    
                    st.markdown(f"""
                    <div style="
                        background-color: #ffe6e6;
                        padding: 15px;
                        border-radius: 15px;
                        margin: 10px 0;
                        margin-right: 50px;
                        border-left: 4px solid #ff3b30;
                    ">
                        <strong>❌ 系统错误：</strong><br><br>
                        {formatted_error}
                    </div>
                    """, unsafe_allow_html=True)
                
                # 分隔线
                if i < len(st.session_state.chat_history) - 1:
                    st.markdown("---")
        # 如果没有对话历史，不显示任何内容
        pass
    
    # Multi-Agent回复显示区域（现在在下方，小框）
    st.markdown("#### 🤖 智水信息Multi-Agent智能体回复")
    
    # 创建Multi-Agent回复显示容器（小框，限制高度）
    ai_response_container = st.container(height=300)
    
    with ai_response_container:
        if st.session_state.chat_history:
            # 显示最新的AI回复
            latest_chat = st.session_state.chat_history[-1]
            
            # 确保latest_chat的ai_response包含status字段
            latest_ai_response = latest_chat['ai_response']
            if not isinstance(latest_ai_response, dict):
                latest_ai_response = {'status': 'error', 'response': str(latest_ai_response)}
            elif 'status' not in latest_ai_response:
                latest_ai_response['status'] = 'success'  # 默认为成功状态
            
            if latest_ai_response['status'] in ['success', 'simulation']:
                status_icon = "🤖" if latest_ai_response['status'] == 'success' else "⚠️"
                status_text = "智水Multi-Agent系统" if latest_ai_response['status'] == 'success' else "模拟模式"
                
                # 格式化最新AI回复内容
                latest_response_content = latest_ai_response.get('response', '响应内容缺失')
                if isinstance(latest_response_content, dict) and 'summary_content' in latest_response_content:
                    formatted_latest_response = format_ai_response_for_display(json.dumps(latest_response_content))
                else:
                    formatted_latest_response = format_ai_response_for_display(latest_response_content)
                
                st.markdown(f"""
                <div style="
                    padding: 15px;
                    border-radius: 15px;
                    margin: 5px 0;
                    border: 2px solid #e0e0e0;
                    font-size: 16px;
                    line-height: 1.6;
                ">
                    <strong style="font-size: 16px;">{status_icon} {status_text}：</strong><br><br>
                    <div style="margin-top: 10px;">
                        {formatted_latest_response}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # 格式化最新错误信息
                latest_error_content = latest_ai_response.get('response', '错误信息缺失')
                if isinstance(latest_error_content, dict) and 'summary_content' in latest_error_content:
                    formatted_latest_error = format_ai_response_for_display(json.dumps(latest_error_content))
                else:
                    formatted_latest_error = format_ai_response_for_display(latest_error_content)
                
                st.markdown(f"""
                <div style="
                    padding: 15px;
                    border-radius: 15px;
                    margin: 5px 0;
                    border: 2px solid #ff3b30;
                    font-size: 16px;
                    line-height: 1.6;
                    color: #ff3b30;
                ">
                    <strong style="font-size: 16px;">❌ 系统错误：</strong><br><br>
                    <div style="margin-top: 10px;">
                        {formatted_latest_error}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # 当没有对话历史时显示空的回复框
            st.markdown("智水信息AI智慧信息系统随时准备为您服务")
    
    # 这部分已经移动到上面了
    
    # 底部输入区域
    st.markdown("#### 💭 向智水信息Multi-Agent智能体提问")
    
    # 文件上传区域 - 增强用户体验
    st.markdown("##### 📎 文件上传（可选）")
    
    # 文件上传提示信息
    with st.expander("📋 支持的文件格式和说明", expanded=False):
        st.markdown("""
        **支持的文件格式：**
        - 📄 **文本文件**：.txt（纯文本文档）
        - 📊 **Excel文件**：.xlsx（数据表格）
        - 📈 **CSV文件**：.csv（逗号分隔值）
        - 🔧 **JSON文件**：.json（结构化数据）
        - 📝 **Word文档**：.docx（文档内容）
        - 📋 **PDF文件**：.pdf（便携式文档）
        
        **文件大小限制**：最大200MB
        
        **使用建议**：
        - 上传项目数据表格可获得更精准的分析
        - 财务报表文件有助于成本分析
        - 技术文档可用于运维知识查询
        """)
    
    uploaded_file = st.file_uploader(
        "选择文件",
        type=['txt', 'pdf', 'docx', 'xlsx', 'csv', 'json'],
        help="拖拽文件到此处或点击选择文件",
        label_visibility="collapsed"
    )
    
    # 文件上传状态显示
    if uploaded_file is not None:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        
        # 文件信息展示
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(224, 242, 254, 0.95), rgba(191, 219, 254, 0.9));
            padding: 20px;
            border-radius: 16px;
            margin: 12px 0;
            border-left: 4px solid #1d4ed8;
            box-shadow: 0 4px 20px rgba(29, 78, 216, 0.15);
            backdrop-filter: blur(10px);
        ">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 24px; margin-right: 12px; color: #1d4ed8;">📁</span>
                <strong style="color: #1d4ed8; font-size: 16px;">文件已选择</strong>
            </div>
            <div style="font-size: 14px; color: #334155; margin-left: 36px; line-height: 1.6;">
                <strong>文件名：</strong>{uploaded_file.name}<br>
                <strong>文件类型：</strong>{uploaded_file.type}<br>
                <strong>文件大小：</strong>{file_size_mb:.2f} MB
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 文件大小警告
        if file_size_mb > 50:
            st.warning("⚠️ 文件较大，处理时间可能较长，请耐心等待...")
        elif file_size_mb > 100:
            st.error("❌ 文件过大（超过100MB），建议压缩后重新上传")
    else:
        # 显示拖拽提示
        st.markdown("""
        <div style="
            border: 2px dashed #d1d5db;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            color: #9ca3af;
            margin: 10px 0;
        ">
            <div style="font-size: 24px; margin-bottom: 10px;">📁</div>
            <div>拖拽文件到此处或点击上方按钮选择文件</div>
            <div style="font-size: 12px; margin-top: 5px;">支持多种格式，最大200MB</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 输入框和发送按钮 - 增强用户体验
    input_col, send_col = st.columns([4, 1])
    
    with input_col:
        user_input = st.text_area(
            "请输入您的问题：",
            value=st.session_state.current_input,
            height=100,
            placeholder="例如：请分析我们公司的财务状况，包括盈利能力和成本控制...\n\n💡 提示：按Ctrl+Enter快速发送",
            key="user_input_area",
            help="支持多行输入，可以详细描述您的需求"
        )
        
        # 输入验证和字符计数
        if user_input:
            char_count = len(user_input.strip())
            if char_count > 2000:
                st.warning(f"⚠️ 输入内容过长（{char_count}/2000字符），建议精简描述")
            elif char_count > 1500:
                st.info(f"📝 当前输入：{char_count}/2000字符")
            else:
                st.caption(f"📝 当前输入：{char_count}字符")
    
    with send_col:
        st.markdown("<br>", unsafe_allow_html=True)  # 添加间距
        
        # 检查是否正在处理中
        is_processing = st.session_state.get('is_processing', False)
        
        # 发送按钮状态控制
        has_content = (user_input and len(user_input.strip()) >= 3) or uploaded_file is not None
        button_disabled = not has_content or is_processing
        
        send_button = st.button(
            "处理中..." if is_processing else ("发送" if has_content else "请输入内容"),
            type="primary" if has_content and not is_processing else "secondary",
            use_container_width=True,
            disabled=button_disabled,
            key="send_message",
            help="AI正在处理中，请稍候..." if is_processing else ("发送消息给AI智能体" if has_content else "请输入至少3个字符或上传文件")
        )
        
        # 快捷操作按钮
        if st.button("示例", use_container_width=True, help="查看常用问题示例"):
            st.session_state.show_examples = not st.session_state.get('show_examples', False)
    
    # 示例问题展示
    if st.session_state.get('show_examples', False):
        with st.expander("常用问题示例", expanded=True):
            example_questions = [
                "📊 基于改进灰色马尔科夫模型预测Q4季度现金流和IRR投资回报率",
                "💰 分析200MW抽水蓄能电站工程成本并进行AHP风险评估",
                "🔧 查询大坝安全监测系统数据异常处理的标准操作流程和应急预案",
                "📈 运用SFA随机前沿分析法评估当前预算执行效率和优化建议",
                "👥 基于改进型平衡计分卡评估生产运维团队四维度效能和协作效率",
                "🏗️ 生成智水信息Q3季度财务、成本、运维、人效四维综合经营报告"
            ]
            
            cols = st.columns(2)
            for i, question in enumerate(example_questions):
                with cols[i % 2]:
                    if st.button(question, key=f"example_{i}", use_container_width=True):
                        st.session_state.current_input = question.replace("📊 ", "").replace("💰 ", "").replace("🔧 ", "").replace("📈 ", "").replace("👥 ", "").replace("🏗️ ", "")
                        st.rerun()
    
    # 键盘快捷键支持
    if user_input and "\n" in user_input and user_input.endswith("\n"):
        # 检测Ctrl+Enter（在文本区域中表现为换行符结尾）
        if len(user_input.strip()) >= 3:
            # 模拟发送按钮点击
            send_button = True
            # 清理输入中的额外换行符
            user_input = user_input.strip()
    
    # 处理发送消息
    if send_button and (user_input.strip() or uploaded_file):
        # 构建数据上下文 - 只基于用户上传的真实数据，不使用预设数据
        data_context = {
            "message": "用户请求智能分析",
            "has_uploaded_file": uploaded_file is not None,
            "analysis_mode": "real_data_only"  # 标记只使用真实数据
        }
        
        # 处理上传的文件
        file_content = None
        file_info = None
        if uploaded_file is not None:
            file_info = {
                "name": uploaded_file.name,
                "type": uploaded_file.type,
                "size": uploaded_file.size
            }
            
            # 读取文件内容 - 增强错误处理
            file_processing_placeholder = st.empty()
            
            try:
                # 显示文件处理状态
                with file_processing_placeholder.container():
                    st.info("📄 正在处理文件，请稍候...")
                
                # 重置文件指针
                uploaded_file.seek(0)
                
                if uploaded_file.type == "text/plain":
                    file_content = str(uploaded_file.read(), "utf-8")
                    st.success(f"✅ 文本文件处理完成，共{len(file_content)}个字符")
                    
                elif uploaded_file.type == "application/json":
                    file_content = json.loads(uploaded_file.read())
                    st.success(f"✅ JSON文件处理完成，包含{len(file_content) if isinstance(file_content, (list, dict)) else 1}个数据项")
                    
                elif uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                    file_content = df.to_dict('records')
                    st.success(f"✅ CSV文件处理完成，共{len(df)}行{len(df.columns)}列数据")
                    
                elif uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                    file_content = df.to_dict('records')
                    st.success(f"✅ Excel文件处理完成，共{len(df)}行{len(df.columns)}列数据")
                    
                elif uploaded_file.name.endswith('.docx'):
                    # 对于Word文档，转换为base64
                    file_content = base64.b64encode(uploaded_file.read()).decode('utf-8')
                    st.success("✅ Word文档已编码，将作为附件发送给AI分析")
                    
                elif uploaded_file.name.endswith('.pdf'):
                    # 对于PDF文件，转换为base64
                    file_content = base64.b64encode(uploaded_file.read()).decode('utf-8')
                    st.success("✅ PDF文档已编码，将作为附件发送给AI分析")
                    
                else:
                    # 对于其他文件类型，转换为base64
                    file_content = base64.b64encode(uploaded_file.read()).decode('utf-8')
                    st.warning(f"⚠️ 未知文件类型{uploaded_file.type}，已编码为附件")
                
                # 清除处理状态
                time.sleep(1)
                file_processing_placeholder.empty()
                
            except UnicodeDecodeError as e:
                file_processing_placeholder.empty()
                st.error("❌ 文件编码错误：文件可能不是UTF-8编码，请转换后重新上传")
                st.info("💡 建议：使用记事本打开文件，另存为UTF-8编码格式")
                file_content = None
                
            except pd.errors.EmptyDataError:
                file_processing_placeholder.empty()
                st.error("❌ 文件为空：上传的CSV/Excel文件没有数据")
                st.info("💡 建议：检查文件是否包含有效数据")
                file_content = None
                
            except pd.errors.ParserError as e:
                file_processing_placeholder.empty()
                st.error(f"❌ 文件格式错误：{str(e)}")
                st.info("💡 建议：检查CSV文件的分隔符和格式是否正确")
                file_content = None
                
            except json.JSONDecodeError as e:
                file_processing_placeholder.empty()
                st.error(f"❌ JSON格式错误：{str(e)}")
                st.info("💡 建议：使用JSON验证工具检查文件格式")
                file_content = None
                
            except MemoryError:
                file_processing_placeholder.empty()
                st.error("❌ 内存不足：文件过大，无法处理")
                st.info("💡 建议：压缩文件或分割成较小的文件")
                file_content = None
                
            except Exception as e:
                file_processing_placeholder.empty()
                st.error(f"❌ 文件处理失败：{str(e)}")
                st.info("💡 建议：检查文件是否损坏或格式是否正确")
                file_content = None
        
        # 构建完整的请求消息
        full_message = user_input
        if file_info:
            full_message += f"\n\n[上传文件：{file_info['name']}，类型：{file_info['type']}，大小：{file_info['size']} bytes]"
        
        # 设置处理状态，防止重复提交
        st.session_state.is_processing = True
        
        # 调用智水Multi-Agent系统API - 增强用户体验
        # 创建进度指示器
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        try:
            # 显示详细的加载状态
            with progress_placeholder.container():
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, rgba(224, 242, 254, 0.95), rgba(191, 219, 254, 0.9));
                    padding: 24px;
                    border-radius: 20px;
                    margin: 12px 0;
                    border-left: 4px solid #1d4ed8;
                    box-shadow: 0 6px 25px rgba(29, 78, 216, 0.2);
                    backdrop-filter: blur(12px);
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 12px;">
                        <div style="
                            width: 24px;
                            height: 24px;
                            border: 3px solid #1d4ed8;
                            border-top: 3px solid transparent;
                            border-radius: 50%;
                            animation: spin 1s linear infinite;
                            margin-right: 12px;
                        "></div>
                        <strong style="color: #1d4ed8; font-size: 16px;">🤖 智水AI系统正在分析中...</strong>
                    </div>
                    <div style="font-size: 14px; color: #334155; margin-left: 36px; line-height: 1.6;">
                        正在调用Multi-Agent智能体系统，请稍候...
                    </div>
                </div>
                <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                </style>
                """, unsafe_allow_html=True)
            
            # 调用API
            response = call_multi_agent_system_with_file(full_message, data_context, file_content, file_info)
            
            # 清除加载状态
            progress_placeholder.empty()
            
            # 显示成功状态
            if response.get('success', False):
                with status_placeholder.container():
                    st.success("✅ AI分析完成！智能体系统已成功处理您的请求。")
                    time.sleep(1)  # 显示1秒成功消息
                    status_placeholder.empty()
            else:
                with status_placeholder.container():
                    error_msg = response.get('response', '未知错误')
                    st.error(f"❌ 处理失败：{error_msg}")
                    time.sleep(2)  # 显示2秒错误消息
                    status_placeholder.empty()
                    
        except Exception as e:
            # 清除加载状态和处理状态
            progress_placeholder.empty()
            st.session_state.is_processing = False
            
            # 显示详细错误信息
            with status_placeholder.container():
                st.error(f"❌ 系统错误：{str(e)}")
                st.warning("💡 建议：请检查网络连接或稍后重试")
                time.sleep(3)  # 显示3秒错误消息
                status_placeholder.empty()
            
            # 创建错误响应
            response = {
                "success": False,
                "status": "error",
                "response": f"系统连接失败：{str(e)}",
                "error": "CONNECTION_ERROR",
                "timestamp": datetime.now().isoformat()
            }
        
        # 添加到聊天历史
        st.session_state.chat_history.append({
            'user_message': full_message,
            'ai_response': response,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'file_info': file_info
        })
        
        # 同步保存到后端
        try:
            from api_client import get_agno_client
            agno_client = get_agno_client()
            session_id = st.session_state.get('session_id')
            if session_id:
                agno_client.save_conversation(
                    session_id=session_id,
                    user_message=full_message,
                    ai_response=response,
                    file_info=file_info
                )
        except Exception as e:
            # 保存失败不影响用户体验，只记录警告
            st.warning(f"保存对话到后端失败: {str(e)}")
        
        # 清空输入框和处理状态
        st.session_state.current_input = ""
        st.session_state.is_processing = False
        
        # 重新运行以更新界面
        st.rerun()
    
    # 清空聊天历史按钮
    if st.session_state.chat_history:
        if st.button("🗑️ 清空对话历史", key="clear_history"):
            # 清空前端历史
            st.session_state.chat_history = []
            
            # 同时清空后端历史
            try:
                from api_client import get_agno_client
                agno_client = get_agno_client()
                session_id = st.session_state.get('session_id')
                if session_id:
                    agno_client.delete_conversation(session_id)
            except Exception as e:
                st.warning(f"清空后端对话历史失败: {str(e)}")
            
            st.rerun()

def render_reports():
    """
    渲染报表分析页面
    """
    st.markdown("### 📈 报表分析")
    
    data = load_sample_data()
    
    # 创建报表选项卡
    tab1, tab2, tab3, tab4 = st.tabs(["💰 财务报表", "🔧 成本预测报表", "📚 知识库报表", "👥 效能评估报表"])
    
    with tab1:
        st.markdown("#### 财务数据详细报表")
        st.dataframe(data['financial'], use_container_width=True)
        
        # 收入成本对比 - 彩色配色
        fig_finance = go.Figure()
        fig_finance.add_trace(go.Bar(
            x=data['financial']['月份'],
            y=data['financial']['营业收入(万元)'],
            name='营业收入',
            marker_color='#22d3ee'  # 青色
        ))
        fig_finance.add_trace(go.Bar(
            x=data['financial']['月份'],
            y=data['financial']['项目成本(万元)'],
            name='项目成本',
            marker_color='#a78bfa'  # 紫色
        ))
        
        fig_finance.update_layout(
            title="收入成本对比分析",
            xaxis_title="月份",
            yaxis_title="金额(万元)",
            template="plotly_dark",
            plot_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
            paper_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
            height=400,
            font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#ffffff'),
            title_font=dict(size=18, color='#22d3ee'),
            xaxis=dict(gridcolor='rgba(37, 99, 235, 0.3)', linecolor='#2563eb', title_font=dict(color='#ffffff')),
            yaxis=dict(gridcolor='rgba(37, 99, 235, 0.3)', linecolor='#2563eb', title_font=dict(color='#ffffff')),
            legend=dict(bgcolor='rgba(15, 27, 61, 0.9)', bordercolor='#2563eb', borderwidth=1, font=dict(color='#ffffff'))
        )
        st.plotly_chart(fig_finance, use_container_width=True)
    
    with tab2:
        st.markdown("#### 成本预测详细报表")
        st.dataframe(data['cost_prediction'], use_container_width=True)
        
        # 成本预测分析 - 彩色配色方案
        fig_cost = px.scatter(
            data['cost_prediction'], 
            x='装机容量(MW)', 
            y='预估成本(亿元)',
            color='项目状态',  # 修复：使用正确的字段名
            size='坝高(m)',  # 修复：使用存在的字段作为size参数
            hover_data=['项目名称', '地质条件', '建设周期(月)', '完成进度(%)'],
            title="装机容量与成本关系分析",
            color_discrete_map={
                '规划中': '#22d3ee',    # 青色
                '建设中': '#a78bfa',    # 紫色
                '运维中': '#10b981',    # 绿色
                '升级中': '#f59e0b',    # 橙色
                '优化中': '#ef4444'     # 红色
            }
        )
        fig_cost.update_layout(
            height=400,
            template="plotly_dark",
            plot_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
            paper_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
            font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#ffffff'),
            title_font=dict(size=18, color='#22d3ee'),
            xaxis=dict(gridcolor='rgba(37, 99, 235, 0.3)', title_font=dict(color='#94a3b8')),
            yaxis=dict(gridcolor='rgba(37, 99, 235, 0.3)', title_font=dict(color='#94a3b8'))
        )
        st.plotly_chart(fig_cost, use_container_width=True)
        
        # 新增：项目建设进度条形图 - 彩色配色
        fig_progress = px.bar(
            data['cost_prediction'],
            x='项目名称',
            y='完成进度(%)',
            color='项目状态',
            title="项目建设进度分析",
            text='完成进度(%)',
            color_discrete_map={
                '规划中': '#22d3ee',    # 青色
                '建设中': '#a78bfa',    # 紫色
                '运维中': '#10b981',    # 绿色
                '升级中': '#f59e0b',    # 橙色
                '优化中': '#ef4444'     # 红色
            }
        )
        fig_progress.update_layout(
            height=600,
            xaxis_tickangle=-45,
            template="plotly_dark",
            plot_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
            paper_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
            margin=dict(t=120, b=80, l=80, r=80),
            yaxis=dict(showticklabels=False, title=''),
            font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#ffffff'),
            title_font=dict(size=18, color='#22d3ee'),
            legend=dict(bgcolor='rgba(15, 27, 61, 0.9)', bordercolor='#2563eb', borderwidth=1, font=dict(color='#ffffff'))
        )
        fig_progress.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(fig_progress, use_container_width=True)
    
    with tab3:
        st.markdown("#### 知识库管理报表")
        st.dataframe(data['knowledge_docs'], use_container_width=True)
        
        # 知识库访问分析 - 彩色配色
        fig_knowledge = px.bar(
            data['knowledge_docs'], 
            x='文档标题', 
            y='访问次数',
            color='文档类型',
            title="知识库文档访问统计",
            color_discrete_map={
                '技术规范': '#22d3ee',    # 青色
                '安全规程': '#a78bfa',    # 紫色
                '操作手册': '#10b981',    # 绿色
                '故障处理': '#f59e0b',    # 橙色
                '最佳实践': '#ef4444'     # 红色
            }
        )
        fig_knowledge.update_layout(
            height=400,
            xaxis_tickangle=-45,
            template="plotly_dark",
            plot_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
            paper_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
            font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#ffffff'),
            title_font=dict(size=18, color='#22d3ee'),
            legend=dict(bgcolor='rgba(15, 27, 61, 0.9)', bordercolor='#2563eb', borderwidth=1, font=dict(color='#ffffff'))
        )
        st.plotly_chart(fig_knowledge, use_container_width=True)
        
        # 新增：文档状态分布饼图 - 彩色配色
        fig_status = px.pie(
            data['knowledge_docs'],
            names='文档状态',
            title="文档处理状态分布",
            color_discrete_map={
                '已索引': '#22d3ee',    # 青色
                '处理中': '#a78bfa',    # 紫色
                '待处理': '#10b981'     # 绿色
            }
        )
        fig_status.update_layout(
            height=400,
            template="plotly_dark",
            plot_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
            paper_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
            font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#ffffff'),
            title_font=dict(size=18, color='#22d3ee'),
            legend=dict(bgcolor='rgba(15, 27, 61, 0.9)', bordercolor='#2563eb', borderwidth=1, font=dict(color='#ffffff'))
        )
        st.plotly_chart(fig_status, use_container_width=True)
        
    with tab4:
        st.markdown("#### 员工效能评估报表")
        st.dataframe(data['employee_efficiency'], use_container_width=True)
        
        # 员工效能分析 - 彩色配色
        fig_efficiency = px.bar(
            data['employee_efficiency'], 
            x='员工姓名', 
            y='综合评分',
            color='部门',
            title="员工综合评分分析",
            color_discrete_map={
                '技术部': '#22d3ee',    # 青色
                '项目部': '#a78bfa',    # 紫色
                '运维部': '#10b981',    # 绿色
                '财务部': '#f59e0b'     # 橙色
            }
        )
        fig_efficiency.update_layout(
            height=400,
            xaxis_tickangle=-45,
            template="plotly_dark",
            plot_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
            paper_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
            font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#ffffff'),
            title_font=dict(size=18, color='#22d3ee'),
            legend=dict(bgcolor='rgba(15, 27, 61, 0.9)', bordercolor='#2563eb', borderwidth=1, font=dict(color='#ffffff'))
        )
        st.plotly_chart(fig_efficiency, use_container_width=True)
        
        # 新增：部门效能对比饼图 - 彩色配色
        dept_efficiency = data['employee_efficiency'].groupby('部门')['综合评分'].mean().reset_index()
        fig_dept_pie = px.pie(
            dept_efficiency,
            names='部门',
            values='综合评分',
            title="各部门平均综合评分对比",
            color_discrete_map={
                '技术部': '#22d3ee',    # 青色
                '项目部': '#a78bfa',    # 紫色
                '运维部': '#10b981',    # 绿色
                '财务部': '#f59e0b'     # 橙色
            }
        )
        fig_dept_pie.update_layout(
            height=400,
            template="plotly_dark",
            plot_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
            paper_bgcolor="rgba(11, 18, 32, 0.8)",  # 蓝黑背景
            font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#ffffff'),
            title_font=dict(size=18, color='#22d3ee'),
            legend=dict(bgcolor='rgba(15, 27, 61, 0.9)', bordercolor='#2563eb', borderwidth=1, font=dict(color='#ffffff'))
        )
        st.plotly_chart(fig_dept_pie, use_container_width=True)

def render_conversation_history():
    """
    渲染历史会话页面
    """
    st.markdown("### 📜 历史会话")
    
    # 获取API客户端
    from api_client import api_manager
    agno_client = api_manager.get_client("agno")
    
    # 页面控制
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("**查看和管理您的历史对话记录**")
    with col2:
        # 显示数量选择器
        limit = st.selectbox("显示数量", [10, 20, 50, 100], index=1, key="history_limit")
    with col3:
        # 刷新按钮
        if st.button("🔄 刷新", key="refresh_history"):
            st.rerun()
    
    st.markdown("---")
    
    try:
        # 获取会话列表
        with st.spinner("正在加载历史会话..."):
            response = agno_client.get_all_conversations(limit=limit, offset=0)
        
        if response.get("success", False):
            conversations = response.get("conversations", [])
            total_count = response.get("total_count", 0)
            
            if conversations:
                st.markdown(f"**📊 共找到 {total_count} 个会话，显示前 {len(conversations)} 个**")
                st.markdown("---")
                
                # 显示会话列表
                for i, conv in enumerate(conversations):
                    with st.container():
                        # 会话卡片
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            # 会话标题和最后消息
                            st.markdown(f"**🗨️ {conv.get('title', '未命名会话')}**")
                            st.markdown(f"*最后消息：* {conv.get('last_user_message', '无消息')}")
                        
                        with col2:
                            # 会话信息
                            st.markdown(f"**消息数：** {conv.get('message_count', 0)}")
                            st.markdown(f"**最后活动：** {conv.get('last_message_time', '未知')}")
                        
                        with col3:
                            # 操作按钮
                            session_id = conv.get('session_id', '')
                            
                            # 查看详情按钮
                            if st.button("查看", key=f"view_{session_id}_{i}"):
                                st.session_state.selected_conversation = session_id
                                st.rerun()
                            
                            # 删除按钮
                            if st.button("删除", key=f"delete_{session_id}_{i}"):
                                if agno_client.delete_conversation(session_id):
                                    st.success(f"✅ 会话 {session_id[:8]}... 已删除")
                                    st.rerun()
                                else:
                                    st.error("❌ 删除失败")
                        
                        st.markdown("---")
                
                # 显示选中的会话详情
                if hasattr(st.session_state, 'selected_conversation') and st.session_state.selected_conversation:
                    st.markdown("### 📖 会话详情")
                    
                    # 获取会话历史
                    with st.spinner("正在加载会话详情..."):
                        history = agno_client.get_conversation_history(st.session_state.selected_conversation)
                    
                    if history:
                        st.markdown(f"**会话ID：** `{st.session_state.selected_conversation}`")
                        st.markdown("---")
                        
                        # 显示对话历史
                        for j, msg in enumerate(history):
                            # 用户消息
                            if msg.get('user_message'):
                                st.markdown("**👤 用户：**")
                                st.markdown(f"> {msg['user_message']}")
                            
                            # AI回复
                            if msg.get('ai_response'):
                                st.markdown("**🤖 AI智能体：**")
                                ai_response = msg['ai_response']
                                if isinstance(ai_response, dict):
                                    # 格式化AI回复
                                    if 'final_result' in ai_response:
                                        final_result = ai_response['final_result']
                                        if isinstance(final_result, dict) and 'content' in final_result:
                                            content = final_result['content']
                                            # 使用格式化函数处理AI回复
                                            formatted_content = format_ai_response_for_display(content)
                                            st.markdown(formatted_content)
                                        else:
                                            st.json(final_result)
                                    else:
                                        st.json(ai_response)
                                else:
                                    st.markdown(str(ai_response))
                            
                            # 时间戳
                            if msg.get('timestamp'):
                                st.markdown(f"*时间：{msg['timestamp']}*")
                            
                            st.markdown("---")
                        
                        # 关闭详情按钮
                        if st.button("❌ 关闭详情", key="close_details"):
                            if hasattr(st.session_state, 'selected_conversation'):
                                delattr(st.session_state, 'selected_conversation')
                            st.rerun()
                    else:
                        st.warning("⚠️ 该会话暂无历史记录")
            else:
                st.info("📭 暂无历史会话记录")
                st.markdown("您可以通过 **🤖 AI智能体** 页面开始新的对话。")
        else:
            error_msg = response.get("error", "未知错误")
            st.error(f"❌ 获取会话列表失败: {error_msg}")
            st.info("💡 请检查后端服务是否正常运行")
    
    except Exception as e:
        st.error(f"❌ 获取会话列表失败: {str(e)}")
        st.info("💡 请检查网络连接和后端服务状态")

def render_about():
    """
    渲染关于系统页面
    """
    st.markdown("### ℹ️ 关于系统核心功能")
    
    st.markdown("""
    <div class="apple-card">
    <h4>🎯 系统目标</h4>
    <p>由商海星辰团队为四川智水信息技术有限公司打造的AI驱动的智慧信息平台demo版本，解决数据分散、成本不透明、财务能力不足、运维知识分散、系统割裂等核心痛点。</p>
    
    <h4>🔧 核心功能</h4>
    <ul>
    <li><strong>数据整合：</strong>统一管理项目、财务、人员等各类数据</li>
    <li><strong>智能分析：</strong>AI驱动的财务分析和成本预测</li>
    <li><strong>知识管理：</strong>运维知识库和最优操作方案分享</li>
    <li><strong>决策支持：</strong>数据可视化和智能决策建议</li>
    </ul>
    
    <h4>🏗️ 技术架构</h4>
    <ul>
    <li><strong>前端：</strong>Streamlit + Plotly（现代化Web界面）</li>
    <li><strong>后端：</strong>FastAPI + MCP框架（微服务架构）</li>
    <li><strong>AI引擎：</strong>Agno协调中心（Multi-Agent智能体系统）</li>
    <li><strong>数据处理：</strong>Pandas + SQLite</li>
    <li><strong>API通信：</strong>RESTful API + JSON数据格式</li>
    </ul>
    
    <h4>🤖 Agno协调中心集成</h4>
    <ul>
    <li><strong>API地址：</strong>http://localhost:8000</li>
    <li><strong>工作流类型：</strong>agent_specific_analysis</li>
    <li><strong>支持智能体：</strong>规划专家、财务分析师、成本分析师、知识管理员、效能评估师、报告生成专家</li>
    <li><strong>容错机制：</strong>连接失败时自动切换到模拟模式</li>
    </ul>
    
    <h4>🎨 设计理念</h4>
    <p>界面设计参考苹果官网风格，采用黑白蓝配色方案，注重用户体验和视觉美感。新版本采用顶部导航栏设计，移除了侧边栏的打开/隐藏交互逻辑，提供更简洁直观的用户体验。</p>
    
    <h4>✨ 新版本特色</h4>
    <ul>
    <li><strong>简化交互：</strong>移除侧边栏切换功能，采用顶部导航设计</li>
    <li><strong>响应式布局：</strong>适配不同屏幕尺寸，优化移动端体验</li>
    <li><strong>一致性设计：</strong>保持原有的苹果风格和配色方案</li>
    <li><strong>功能完整：</strong>保留所有核心功能，提升使用便利性</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# 主程序入口
# ============================================================================

def main():
    """
    主程序入口
    """
    # 加载自定义样式
    load_custom_css()
    
    # 渲染页面头部
    render_apple_header()
    
    # 渲染导航栏并获取当前页面
    current_page = render_navigation()
    
    # 加载业务数据
    data = load_sample_data()
    
    # 添加系统状态信息
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("**📈 系统状态：** 🟢 运行正常")
    with col2:
        st.markdown(f"**🕐 最后更新：** {datetime.now().strftime('%H:%M:%S')}")
    with col3:
        if st.button("🔄 刷新数据", key="refresh_data"):
            st.rerun()
    
    st.markdown("---")
    
    # 根据当前页面渲染内容
    if current_page == "dashboard":
        render_metrics_dashboard(data)
        st.markdown("---")
        render_data_visualization(data)
        
    elif current_page == "data_management":
        render_data_management()
        
    elif current_page == "agent_interaction":
        render_agent_interaction()
        
    elif current_page == "conversation_history":
        render_conversation_history()
        
    elif current_page == "reports":
        render_reports()
        
    elif current_page == "about":
        render_about()
    
    # 页脚
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #ffffff; padding: 2rem;'>" +
        "2025 Designed by 商海星辰" +
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()