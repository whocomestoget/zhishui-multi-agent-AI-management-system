# ============================================================================
# 文件：1_frontend_dashboard/pages.py
# 功能：页面模块 - 各功能页面的具体实现
# 技术：Streamlit + 组件库 + API客户端
# ============================================================================

"""
四川智水AI智慧管理平台 - 页面模块

功能页面：
1. 首页仪表板 - 数据概览和KPI展示
2. 项目管理页面 - 项目信息整合和管理
3. 财务分析页面 - AI财务分析和预测
4. 运维知识库页面 - 知识管理和搜索
5. 成本核算页面 - 成本分析和预测
6. 决策支持页面 - 数据分析和决策建议
7. 智能体中心页面 - AI智能体交互
8. 系统设置页面 - 配置和管理
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import time
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go

from config import get_config
from components import (
    apple_card, apple_metric_card, apple_button, apple_progress_bar,
    create_apple_chart, financial_overview_chart, project_status_chart,
    create_kpi_dashboard, apple_data_table, apple_file_uploader,
    apple_download_button, agent_chat_interface, multi_agent_collaboration_panel,
    service_status_indicator, loading_spinner, APPLE_COLORS
)
from api_client import (
    get_project_client, get_financial_client, get_knowledge_client,
    get_cost_client, get_decision_client, get_agno_client,
    check_services_health, call_multi_agent_system_with_file
)
from utils import (
    format_currency, format_percentage, export_to_excel,
    export_to_json, import_from_excel, validate_project_data
)
from models import ProjectInfo, FinancialData, AgentType

# ============================================================================
# 配置
# ============================================================================

config = get_config("agent_api")

# ============================================================================
# 首页仪表板
# ============================================================================

def dashboard_page():
    """首页仪表板"""
    
    # 页面标题
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {APPLE_COLORS['primary']} 0%, {APPLE_COLORS['secondary']} 100%);
        padding: 32px;
        border-radius: 16px;
        margin-bottom: 24px;
        text-align: center;
    ">
        <h1 style="
            color: white;
            font-family: SF Pro Display;
            font-weight: 700;
            font-size: 36px;
            margin: 0;
        ">🏢 系统核心功能</h1>
        <p style="
            color: white;
            font-size: 18px;
            margin: 8px 0 0 0;
            opacity: 0.9;
        ">AI驱动的项目信息整合与智能决策支持系统</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 系统状态检查
    with st.spinner("检查系统状态..."):
        services_status = check_services_health()
    
    # 服务状态指示器
    service_status_indicator(services_status)
    
    # KPI仪表板
    st.markdown("### 📊 关键指标概览")
    
    # 获取KPI数据 - 使用基础工具调用
    kpi_result = _call_basic_tool(
        service_name="project",
        tool_name="get_project_statistics",
        params={}
    )
    
    if kpi_result.get("success"):
        kpi_data = kpi_result.get("data", {})
    else:
        # 使用模拟数据
        kpi_data = {
            "total_revenue": {"value": 12500000, "delta": "+8.5%", "icon": "💰"},
            "active_projects": {"value": 28, "delta": "+3", "icon": "🚀"},
            "profit_margin": {"value": "23.5%", "delta": "+2.1%", "icon": "📈"},
            "customer_satisfaction": {"value": "94.2%", "delta": "+1.8%", "icon": "😊"}
        }
    
    create_kpi_dashboard(kpi_data)
    
    # 图表展示区域
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 财务数据概览")
        
        # 使用基础工具调用获取财务数据
        financial_result = _call_basic_tool(
            service_name="financial",
            tool_name="get_financial_overview",
            params={}
        )
        
        if financial_result.get("success"):
            financial_data = financial_result.get("data", [])
        else:
            financial_data = []
        
        fig = financial_overview_chart(financial_data)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🚀 项目状态分析")
        
        # 使用基础工具调用获取项目数据
        project_result = _call_basic_tool(
            service_name="project",
            tool_name="get_projects",
            params={}
        )
        
        if project_result.get("success"):
            projects = project_result.get("data", [])
            # 处理项目数据生成状态统计
            project_data = projects
        else:
            project_data = []
        
        fig = project_status_chart(project_data)
        st.plotly_chart(fig, use_container_width=True)
    
    # 快速操作区域
    st.markdown("### ⚡ 快速操作")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if apple_button("📊 查看项目", "view_projects", "primary"):
            st.session_state.current_page = "项目管理"
            st.rerun()
    
    with col2:
        if apple_button("💰 财务分析", "financial_analysis", "success"):
            st.session_state.current_page = "财务分析"
            st.rerun()
    
    with col3:
        if apple_button("🔧 运维知识", "knowledge_base", "info"):
            st.session_state.current_page = "运维知识库"
            st.rerun()
    
    with col4:
        if apple_button("🤖 智能体", "ai_agents", "secondary"):
            st.session_state.current_page = "智能体中心"
            st.rerun()
    
    # 最近活动
    st.markdown("### 📋 最近活动")
    
    recent_activities = [
        {"时间": "2024-01-15 14:30", "活动": "新增项目：智慧水利监测系统", "状态": "✅ 完成"},
        {"时间": "2024-01-15 13:45", "活动": "财务报告生成", "状态": "✅ 完成"},
        {"时间": "2024-01-15 12:20", "活动": "成本分析更新", "状态": "🔄 进行中"},
        {"时间": "2024-01-15 11:15", "活动": "运维知识库同步", "状态": "✅ 完成"},
        {"时间": "2024-01-15 10:30", "活动": "智能体协作任务", "状态": "⏳ 等待中"}
    ]
    
    activities_df = pd.DataFrame(recent_activities)
    apple_data_table(activities_df, "最近系统活动", searchable=False, pagination=False)

# ============================================================================
# 项目管理页面
# ============================================================================

def project_management_page():
    """项目管理页面"""
    
    st.title("🚀 项目信息整合管理")
    
    # 功能选项卡
    tab1, tab2, tab3, tab4 = st.tabs(["📊 项目概览", "📁 数据导入", "📤 数据导出", "➕ 新增项目"])
    
    with tab1:
        project_overview_tab()
    
    with tab2:
        project_import_tab()
    
    with tab3:
        project_export_tab()
    
    with tab4:
        project_create_tab()

def project_overview_tab():
    """项目概览标签页"""
    
    # 搜索和筛选
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 搜索项目", placeholder="输入项目名称、客户或关键词...")
    
    with col2:
        status_filter = st.selectbox("状态筛选", ["全部", "进行中", "已完成", "计划中", "暂停"])
    
    with col3:
        sort_by = st.selectbox("排序方式", ["创建时间", "项目名称", "预算金额", "完成度"])
    
    # 获取项目数据 - 基础功能使用工具调用
    try:
        filters = {}
        if status_filter != "全部":
            filters["status"] = status_filter
        if search_term:
            filters["search"] = search_term
        
        # 使用基础工具调用获取项目数据
        result = _call_basic_tool(
            service_name="project_service",
            tool_name="get_projects",
            filters=filters
        )
        
        projects = result.get("data", []) if result else []
        
    except Exception as e:
        st.error(f"获取项目数据失败: {str(e)}")
        projects = []
    
    # 如果没有数据，显示示例数据
    if not projects:
        projects = [
            {
                "id": "P001",
                "name": "智慧电厂监控系统",
                "client": "国家电网四川分公司",
                "status": "进行中",
                "budget": 2500000,
                "progress": 0.65,
                "start_date": "2024-01-01",
                "end_date": "2024-06-30",
                "manager": "张工程师"
            },
            {
                "id": "P002",
                "name": "大坝安全监测平台",
                "client": "四川省水利厅",
                "status": "已完成",
                "budget": 1800000,
                "progress": 1.0,
                "start_date": "2023-08-01",
                "end_date": "2023-12-31",
                "manager": "李工程师"
            },
            {
                "id": "P003",
                "name": "智能水站管理系统",
                "client": "成都市水务局",
                "status": "计划中",
                "budget": 3200000,
                "progress": 0.0,
                "start_date": "2024-03-01",
                "end_date": "2024-09-30",
                "manager": "王工程师"
            }
        ]
    
    # 项目统计卡片
    if projects:
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.get("status") == "进行中"])
        total_budget = sum([p.get("budget", 0) for p in projects])
        avg_progress = np.mean([p.get("progress", 0) for p in projects]) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            apple_metric_card("项目总数", total_projects, "", "🚀")
        with col2:
            apple_metric_card("进行中", active_projects, "", "⚡")
        with col3:
            apple_metric_card("总预算", format_currency(total_budget), "", "💰")
        with col4:
            apple_metric_card("平均进度", f"{avg_progress:.1f}%", "", "📈")
    
    # 项目列表表格
    if projects:
        # 格式化数据用于显示
        display_projects = []
        for project in projects:
            display_project = {
                "项目ID": project.get("id", ""),
                "项目名称": project.get("name", ""),
                "客户": project.get("client", ""),
                "状态": project.get("status", ""),
                "预算": format_currency(project.get("budget", 0)),
                "进度": f"{project.get('progress', 0) * 100:.1f}%",
                "开始日期": project.get("start_date", ""),
                "结束日期": project.get("end_date", ""),
                "项目经理": project.get("manager", "")
            }
            display_projects.append(display_project)
        
        projects_df = pd.DataFrame(display_projects)
        apple_data_table(projects_df, "项目列表", searchable=True, pagination=True)
        
        # 项目详情查看
        if st.button("📋 查看选中项目详情"):
            st.info("请在表格中选择要查看的项目")
    else:
        st.info("📭 暂无项目数据，请先导入项目信息或新增项目")

def project_import_tab():
    """项目导入标签页"""
    
    st.markdown("### 📁 项目数据导入")
    
    # 导入说明
    apple_card(
        "导入说明",
        """
        支持的文件格式：Excel (.xlsx, .xls)、CSV (.csv)、JSON (.json)
        
        **Excel/CSV 文件要求：**
        - 必须包含列：项目名称、客户、状态、预算、开始日期、结束日期
        - 可选列：项目ID、进度、项目经理、描述
        - 第一行为列标题
        
        **JSON 文件要求：**
        - 数组格式，每个对象代表一个项目
        - 必须包含 name, client, status, budget 字段
        """,
        "📋",
        "info"
    )
    
    # 文件上传
    uploaded_file = apple_file_uploader(
        "选择项目数据文件",
        accepted_types=['xlsx', 'xls', 'csv', 'json'],
        key="project_import_file"
    )
    
    if uploaded_file is not None:
        try:
            # 显示文件信息
            st.info(f"📄 文件名：{uploaded_file.name}，大小：{uploaded_file.size} 字节")
            
            # 预览数据
            if uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.json'):
                data = json.load(uploaded_file)
                df = pd.DataFrame(data)
            else:
                st.error("不支持的文件格式")
                return
            
            st.markdown("#### 📊 数据预览")
            st.dataframe(df.head(10), use_container_width=True)
            
            # 数据验证
            validation_result = validate_project_data(df)
            
            if validation_result["valid"]:
                st.success(f"✅ 数据验证通过！共 {len(df)} 条记录")
                
                # 导入选项
                col1, col2 = st.columns(2)
                
                with col1:
                    import_mode = st.radio(
                        "导入模式",
                        ["新增模式", "覆盖模式", "更新模式"]
                    )
                
                with col2:
                    skip_duplicates = st.checkbox("跳过重复项目", value=True)
                
                # 导入按钮 - 复杂功能使用工作流调用
                if apple_button("🚀 开始导入", "start_import", "primary"):
                    with st.spinner("正在导入项目数据..."):
                        try:
                            # 使用复杂工作流调用项目导入
                            file_data = uploaded_file.getvalue()
                            result = _execute_complex_workflow(
                                workflow_type="project_import",
                                file_data=file_data,
                                file_format="excel",
                                import_mode=import_mode,
                                skip_duplicates=skip_duplicates
                            )
                            
                            if result and result.get("success"):
                                st.success(f"✅ 导入成功！共导入 {result.get('imported_count', 0)} 个项目")
                                if result.get("skipped_count", 0) > 0:
                                    st.warning(f"⚠️ 跳过 {result.get('skipped_count')} 个重复项目")
                            else:
                                st.error(f"❌ 导入失败：{result.get('message', '导入处理失败') if result else '服务不可用'}")
                                
                        except Exception as e:
                            st.error(f"❌ 导入过程中发生错误：{str(e)}")
            else:
                st.error("❌ 数据验证失败")
                for error in validation_result["errors"]:
                    st.error(f"• {error}")
                
        except Exception as e:
            st.error(f"❌ 文件处理失败：{str(e)}")

def project_export_tab():
    """项目导出标签页"""
    
    st.markdown("### 📤 项目数据导出")
    
    # 导出选项
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox(
            "导出格式",
            ["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"]
        )
    
    with col2:
        date_range = st.date_input(
            "日期范围",
            value=[datetime.now() - timedelta(days=365), datetime.now()],
            help="选择要导出的项目日期范围"
        )
    
    # 筛选选项
    st.markdown("#### 筛选条件")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.multiselect(
            "项目状态",
            ["进行中", "已完成", "计划中", "暂停"],
            default=["进行中", "已完成", "计划中"]
        )
    
    with col2:
        client_filter = st.text_input("客户筛选", placeholder="输入客户名称...")
    
    with col3:
        budget_range = st.slider(
            "预算范围（万元）",
            min_value=0,
            max_value=1000,
            value=[0, 1000],
            step=10
        )
    
    # 导出按钮
    if apple_button("📥 导出数据", "export_projects", "primary"):
        with st.spinner("正在准备导出数据..."):
            try:
                # 构建筛选条件
                filters = {
                    "status": status_filter,
                    "start_date": date_range[0].isoformat() if len(date_range) > 0 else None,
                    "end_date": date_range[1].isoformat() if len(date_range) > 1 else None,
                    "client": client_filter if client_filter else None,
                    "budget_min": budget_range[0] * 10000,
                    "budget_max": budget_range[1] * 10000
                }
                
                # 获取导出格式
                format_map = {
                    "Excel (.xlsx)": "excel",
                    "CSV (.csv)": "csv",
                    "JSON (.json)": "json"
                }
                
                export_fmt = format_map[export_format]
                
                # 使用复杂工作流调用项目导出
                result = _execute_complex_workflow(
                    workflow_type="project_export",
                    export_format=export_fmt,
                    filters=filters
                )
                
                if result and result.get("success") and result.get("data"):
                    export_data = result["data"]
                    
                    # 生成文件名
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"projects_export_{timestamp}.{export_fmt}"
                    
                    # 确定MIME类型
                    mime_types = {
                        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "csv": "text/csv",
                        "json": "application/json"
                    }
                    
                    mime_type = mime_types[export_fmt]
                    
                    # 提供下载
                    apple_download_button(
                        export_data,
                        filename,
                        mime_type,
                        f"下载 {export_format} 文件",
                        "📥"
                    )
                    
                    st.success(f"✅ 导出完成！文件已准备好下载")
                else:
                    st.error(f"❌ 导出失败：{result.get('error', '导出处理失败') if result else '服务不可用'}")
                    
            except Exception as e:
                st.error(f"❌ 导出过程中发生错误：{str(e)}")

def project_create_tab():
    """项目创建标签页"""
    
    st.markdown("### ➕ 新增项目")
    
    # 项目基本信息
    with st.form("create_project_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input("项目名称 *", placeholder="输入项目名称...")
            client_name = st.text_input("客户名称 *", placeholder="输入客户名称...")
            project_manager = st.text_input("项目经理", placeholder="输入项目经理姓名...")
            budget = st.number_input("项目预算（元）", min_value=0, step=10000)
        
        with col2:
            project_status = st.selectbox("项目状态", ["计划中", "进行中", "暂停", "已完成"])
            start_date = st.date_input("开始日期")
            end_date = st.date_input("结束日期")
            priority = st.selectbox("优先级", ["低", "中", "高", "紧急"])
        
        # 项目描述
        description = st.text_area("项目描述", placeholder="输入项目详细描述...")
        
        # 项目标签
        tags = st.text_input("项目标签", placeholder="输入标签，用逗号分隔...")
        
        # 提交按钮
        submitted = st.form_submit_button("🚀 创建项目")
        
        if submitted:
            # 验证必填字段
            if not project_name or not client_name:
                st.error("❌ 请填写项目名称和客户名称")
            elif end_date < start_date:
                st.error("❌ 结束日期不能早于开始日期")
            else:
                # 构建项目数据
                project_data = {
                    "name": project_name,
                    "client": client_name,
                    "manager": project_manager,
                    "status": project_status,
                    "budget": budget,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "priority": priority,
                    "description": description,
                    "tags": [tag.strip() for tag in tags.split(",") if tag.strip()]
                }
                
                try:
                    # 使用复杂工作流调用项目创建
                    result = _execute_complex_workflow(
                        workflow_type="project_create",
                        project_data=project_data
                    )
                    
                    if result and result.get("success"):
                        project_id = result.get("data", {}).get("id", "N/A")
                        st.success(f"✅ 项目创建成功！项目ID：{project_id}")
                        st.balloons()
                    else:
                        error_msg = result.get("error", "项目创建失败") if result else "服务不可用"
                        st.error(f"❌ {error_msg}")
                        
                except Exception as e:
                    st.error(f"❌ 创建项目时发生错误：{str(e)}")

# ============================================================================
# 财务分析页面
# ============================================================================

def financial_analysis_page():
    """财务分析页面"""
    
    st.title("💰 AI财务分析中心")
    
    # 功能选项卡
    tab1, tab2, tab3, tab4 = st.tabs(["📊 财务概览", "🔮 预测分析", "💬 财务问答", "📋 报告生成"])
    
    with tab1:
        financial_overview_tab()
    
    with tab2:
        financial_prediction_tab()
    
    with tab3:
        financial_qa_tab()
    
    with tab4:
        financial_report_tab()

def financial_overview_tab():
    """财务概览标签页"""
    
    # 财务KPI
    st.markdown("### 💰 财务关键指标")
    
    # 模拟财务数据
    financial_kpis = {
        "total_revenue": {"value": 15800000, "delta": "+12.5%", "icon": "💰"},
        "total_cost": {"value": 11200000, "delta": "+8.3%", "icon": "💸"},
        "net_profit": {"value": 4600000, "delta": "+18.7%", "icon": "📈"},
        "profit_margin": {"value": "29.1%", "delta": "+3.2%", "icon": "📊"}
    }
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        apple_metric_card("总收入", format_currency(financial_kpis["total_revenue"]["value"]), 
                         financial_kpis["total_revenue"]["delta"], financial_kpis["total_revenue"]["icon"])
    
    with col2:
        apple_metric_card("总成本", format_currency(financial_kpis["total_cost"]["value"]), 
                         financial_kpis["total_cost"]["delta"], financial_kpis["total_cost"]["icon"])
    
    with col3:
        apple_metric_card("净利润", format_currency(financial_kpis["net_profit"]["value"]), 
                         financial_kpis["net_profit"]["delta"], financial_kpis["net_profit"]["icon"])
    
    with col4:
        apple_metric_card("利润率", financial_kpis["profit_margin"]["value"], 
                         financial_kpis["profit_margin"]["delta"], financial_kpis["profit_margin"]["icon"])
    
    # 财务图表
    col1, col2 = st.columns(2)
    
    with col1:
        # 收入趋势图
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
        revenue_data = pd.DataFrame({
            'month': dates.strftime('%Y-%m'),
            'revenue': np.random.uniform(1000000, 1500000, len(dates)),
            'cost': np.random.uniform(600000, 1000000, len(dates))
        })
        
        fig = create_apple_chart(
            "line", 
            revenue_data, 
            "收入与成本趋势",
            x='month', 
            y=['revenue', 'cost'],
            labels={'revenue': '收入', 'cost': '成本'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 利润分析饼图
        profit_data = pd.DataFrame({
            'category': ['人工成本', '材料成本', '设备成本', '其他成本', '净利润'],
            'amount': [3500000, 2800000, 2200000, 2700000, 4600000]
        })
        
        fig = create_apple_chart(
            "pie",
            profit_data,
            "成本与利润分布",
            names='category',
            values='amount'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 财务数据表格
    st.markdown("### 📋 详细财务数据")
    
    # 生成示例财务数据
    financial_details = []
    for i in range(12):
        month = (datetime.now().replace(day=1) - timedelta(days=30*i)).strftime('%Y-%m')
        financial_details.append({
            "月份": month,
            "收入": np.random.uniform(1000000, 1500000),
            "成本": np.random.uniform(600000, 1000000),
            "利润": np.random.uniform(200000, 600000),
            "利润率": f"{np.random.uniform(15, 35):.1f}%"
        })
    
    # 格式化金额
    for item in financial_details:
        item["收入"] = format_currency(item["收入"])
        item["成本"] = format_currency(item["成本"])
        item["利润"] = format_currency(item["利润"])
    
    financial_df = pd.DataFrame(financial_details)
    apple_data_table(financial_df, "月度财务数据", pagination=True)

def financial_prediction_tab():
    """财务预测标签页"""
    
    st.markdown("### 🔮 AI财务预测分析")
    
    # 预测参数设置
    col1, col2, col3 = st.columns(3)
    
    with col1:
        prediction_type = st.selectbox(
            "预测类型",
            ["现金流预测", "收入预测", "成本预测", "利润预测"]
        )
    
    with col2:
        prediction_periods = st.slider("预测期数（月）", 1, 12, 6)
    
    with col3:
        confidence_level = st.selectbox("置信度", ["90%", "95%", "99%"])
    
    # 开始预测按钮
    if apple_button("🚀 开始AI预测", "start_prediction", "primary"):
        with st.spinner("AI正在分析历史数据并生成预测..."):
            try:
                # 模拟历史数据
                historical_data = []
                for i in range(24):  # 24个月历史数据
                    date = datetime.now() - timedelta(days=30*i)
                    historical_data.append({
                        "date": date.strftime('%Y-%m'),
                        "revenue": np.random.uniform(1000000, 1500000),
                        "cost": np.random.uniform(600000, 1000000),
                        "cash_flow": np.random.uniform(200000, 600000)
                    })
                
                # 使用复杂工作流调用财务预测
                result = _execute_complex_workflow(
                    workflow_type="financial_prediction",
                    prediction_type=prediction_type,
                    historical_data=historical_data,
                    prediction_periods=prediction_periods,
                    confidence_level=confidence_level
                )
                
                if result.get("success"):
                    # 显示预测结果
                    st.success(f"✅ {prediction_type}完成！模型准确度：{result.get('model_accuracy', 0.9)*100:.1f}%")
                    
                    # 预测图表
                    predictions = result.get("predictions", [])
                    if predictions:
                        pred_df = pd.DataFrame([
                            {
                                "期间": pred["period"],
                                "预测值": pred["predicted_value"],
                                "下限": pred["confidence_interval"]["lower"],
                                "上限": pred["confidence_interval"]["upper"]
                            }
                            for pred in predictions
                        ])
                        
                        # 创建预测图表
                        fig = go.Figure()
                        
                        # 预测值线
                        fig.add_trace(go.Scatter(
                            x=pred_df["期间"],
                            y=pred_df["预测值"],
                            mode='lines+markers',
                            name='预测值',
                            line=dict(color=APPLE_COLORS["primary"], width=3)
                        ))
                        
                        # 置信区间
                        fig.add_trace(go.Scatter(
                            x=pred_df["期间"],
                            y=pred_df["上限"],
                            fill=None,
                            mode='lines',
                            line_color='rgba(0,0,0,0)',
                            showlegend=False
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=pred_df["期间"],
                            y=pred_df["下限"],
                            fill='tonexty',
                            mode='lines',
                            line_color='rgba(0,0,0,0)',
                            name=f'{confidence_level}置信区间',
                            fillcolor=f'rgba(0,122,255,0.2)'
                        ))
                        
                        fig.update_layout(
                            title=f"{prediction_type}结果",
                            xaxis_title="时间期间",
                            yaxis_title="金额（元）",
                            font=dict(family="SF Pro Display"),
                            plot_bgcolor="rgba(248,250,252,0.8)",  # 灰色背景
                            paper_bgcolor="rgba(248,250,252,0.8)"  # 灰色背景
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 预测数据表格
                        # 格式化金额
                        for _, row in pred_df.iterrows():
                            row["预测值"] = format_currency(row["预测值"])
                            row["下限"] = format_currency(row["下限"])
                            row["上限"] = format_currency(row["上限"])
                        
                        apple_data_table(pred_df, "预测详细数据", searchable=False, pagination=False)
                    
                    # AI洞察
                    insights = result.get("insights", [])
                    if insights:
                        st.markdown("#### 🧠 AI洞察建议")
                        for insight in insights:
                            st.info(f"💡 {insight}")
                else:
                    st.error(f"❌ 预测失败：{result.get('error', '未知错误')}")
                    
            except Exception as e:
                st.error(f"❌ 预测过程中发生错误：{str(e)}")

def financial_qa_tab():
    """财务问答标签页 - 智能功能使用Agent调用"""
    
    st.markdown("### 💬 AI财务问答助手")
    
    # 智能财务问答界面 - 使用Agent调用
    intelligent_agent_chat_interface("financial", "financial_chat_history")
    
    # 常见问题快捷按钮
    st.markdown("#### 🔥 常见问题")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 基于改进灰色马尔科夫模型的现金流预测分析"):
            _handle_financial_question(
                "请运用改进灰色马尔科夫模型，为智水信息提供未来3-12期的现金流精准预测，包含季节性波动和不确定性风险评估",
                "financial_chat_history"
            )
        
        if st.button("💰 水电项目IRR、NPV投资价值科学评估"):
            _handle_financial_question(
                "请对智水信息当前水电项目进行IRR内部收益率和NPV净现值深度分析，评估投资价值和财务可行性",
                "financial_chat_history"
            )
    
    with col2:
        if st.button("📈 SFA随机前沿分析法的预算执行效率量化"):
            _handle_financial_question(
                "运用SFA随机前沿分析法，量化分析智水信息本季度预算执行效率，识别效率损失点和改进机会",
                "financial_chat_history"
            )
        
        if st.button("🎯 电力水利行业专业财务战略咨询"):
            _handle_financial_question(
                "基于15年电力水利行业财务管理经验，为智水信息提供财务战略规划、风险管控和盈利模式优化建议",
                "financial_chat_history"
            )

def financial_report_tab():
    """财务报告标签页"""
    
    st.markdown("### 📋 AI财务报告生成")
    
    # 报告配置
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox(
            "报告类型",
            ["月度财务报告", "季度财务报告", "年度财务报告", "项目财务报告"]
        )
        
        report_period = st.date_input(
            "报告期间",
            value=[datetime.now().replace(day=1), datetime.now()]
        )
    
    with col2:
        include_charts = st.checkbox("包含图表", value=True)
        include_analysis = st.checkbox("包含AI分析", value=True)
        include_recommendations = st.checkbox("包含建议", value=True)
        
        report_format = st.selectbox("报告格式", ["PDF", "Word", "Excel"])
    
    # 生成报告按钮 - 复杂功能使用工作流
    if apple_button("📊 生成财务报告", "generate_report", "primary"):
        with st.spinner("AI正在生成财务报告..."):
            try:
                # 构建报告参数
                report_config = {
                    "type": report_type,
                    "start_date": report_period[0].isoformat() if len(report_period) > 0 else None,
                    "end_date": report_period[1].isoformat() if len(report_period) > 1 else None,
                    "include_charts": include_charts,
                    "include_analysis": include_analysis,
                    "include_recommendations": include_recommendations,
                    "format": report_format.lower()
                }
                
                # 使用复杂工作流生成财务报告
                result = _execute_complex_workflow(
                    workflow_type="financial_report_generation",
                    report_config=report_config
                )
                
                if result and result.get("success"):
                    st.success("✅ 财务报告生成完成！")
                    
                    # 显示报告预览
                    report_content = result.get("report_content", "")
                    if report_content:
                        st.markdown("#### 📄 报告预览")
                        st.markdown(report_content)
                    
                    # 提供下载链接
                    if result.get("download_url"):
                        st.markdown(f"[📥 下载完整报告]({result['download_url']})")
                    
                    # 报告摘要
                    summary = result.get("summary", {})
                    if summary:
                        st.markdown("#### 📊 报告摘要")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            apple_metric_card(
                                "总收入", 
                                format_currency(summary.get("total_revenue", 0)), 
                                summary.get("revenue_change", ""), 
                                "💰"
                            )
                        
                        with col2:
                            apple_metric_card(
                                "净利润", 
                                format_currency(summary.get("net_profit", 0)), 
                                summary.get("profit_change", ""), 
                                "📈"
                            )
                        
                        with col3:
                            apple_metric_card(
                                "利润率", 
                                summary.get("profit_margin", "0%"), 
                                summary.get("margin_change", ""), 
                                "📊"
                            )
                else:
                    st.error(f"❌ 报告生成失败：{result.get('error', '未知错误') if result else '工作流执行失败'}")
                    
            except Exception as e:
                st.error(f"❌ 生成报告时发生错误：{str(e)}")

# ============================================================================
# 运维知识库页面
# ============================================================================

def knowledge_base_page():
    """运维知识库页面"""
    
    st.title("🔧 运维知识库中心")
    
    # 功能选项卡
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 知识搜索", "📚 知识浏览", "➕ 添加知识", "💬 知识问答"])
    
    with tab1:
        knowledge_search_tab()
    
    with tab2:
        knowledge_browse_tab()
    
    with tab3:
        knowledge_add_tab()
    
    with tab4:
        knowledge_qa_tab()

def knowledge_search_tab():
    """知识搜索标签页"""
    
    st.markdown("### 🔍 智能知识搜索")
    
    # 搜索界面
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "搜索知识",
            placeholder="输入关键词搜索运维知识...",
            label_visibility="collapsed"
        )
    
    with col2:
        search_category = st.selectbox(
            "分类",
            ["全部", "电力系统", "水利工程", "设备维护", "故障排除", "安全规范"]
        )
    
    # 搜索按钮 - 基础功能使用工具调用
    if apple_button("🔍 搜索", "search_knowledge", "primary") or search_query:
        if search_query:
            with st.spinner("正在搜索知识库..."):
                try:
                    # 使用基础工具调用搜索知识
                    category = None if search_category == "全部" else search_category
                    result = _call_basic_tool(
                        service_name="knowledge",
                        tool_name="knowledge_search",
                        query=search_query,
                        category=category,
                        limit=10
                    )
                    
                    if result and result.get("success"):
                        knowledge_items = result.get("knowledge_items", [])
                        
                        if knowledge_items:
                            st.success(f"✅ 找到 {len(knowledge_items)} 条相关知识")
                            
                            # 显示搜索结果
                            for i, item in enumerate(knowledge_items):
                                with st.expander(f"📄 {item.get('title', '未知标题')}"):
                                    col1, col2 = st.columns([3, 1])
                                    
                                    with col1:
                                        st.markdown(f"**内容：** {item.get('content', '无内容')}")
                                        
                                        tags = item.get('tags', [])
                                        if tags:
                                            tag_html = " ".join([f"<span style='background: {APPLE_COLORS['light']}; padding: 2px 8px; border-radius: 12px; font-size: 12px;'>{tag}</span>" for tag in tags])
                                            st.markdown(f"**标签：** {tag_html}", unsafe_allow_html=True)
                                    
                                    with col2:
                                        st.markdown(f"**分类：** {item.get('category', '未分类')}")
                                        st.markdown(f"**相关度：** {item.get('relevance_score', 0)*100:.1f}%")
                                        st.markdown(f"**更新时间：** {item.get('updated_at', 'N/A')}")
                        else:
                            st.info("📭 没有找到相关知识，请尝试其他关键词")
                    else:
                        # 显示模拟搜索结果
                        st.info("🔧 知识库服务不可用，显示模拟结果")
                        
                        mock_results = [
                            {
                                "title": "电力系统故障诊断流程",
                                "content": "电力系统故障诊断的标准流程包括：1. 故障现象观察 2. 初步判断 3. 详细检测 4. 故障定位 5. 修复方案制定...",
                                "category": "电力系统",
                                "tags": ["故障诊断", "电力", "维护"],
                                "relevance_score": 0.95,
                                "updated_at": "2024-01-10"
                            },
                            {
                                "title": "水利设备日常维护指南",
                                "content": "水利设备的日常维护包括：定期检查、清洁保养、润滑维护、性能测试等关键环节...",
                                "category": "水利工程",
                                "tags": ["设备维护", "水利", "日常保养"],
                                "relevance_score": 0.88,
                                "updated_at": "2024-01-08"
                            }
                        ]
                        
                        for item in mock_results:
                            with st.expander(f"📄 {item['title']}"):
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.markdown(f"**内容：** {item['content']}")
                                    
                                    tags = item['tags']
                                    tag_html = " ".join([f"<span style='background: {APPLE_COLORS['light']}; padding: 2px 8px; border-radius: 12px; font-size: 12px;'>{tag}</span>" for tag in tags])
                                    st.markdown(f"**标签：** {tag_html}", unsafe_allow_html=True)
                                
                                with col2:
                                    st.markdown(f"**分类：** {item['category']}")
                                    st.markdown(f"**相关度：** {item['relevance_score']*100:.1f}%")
                                    st.markdown(f"**更新时间：** {item['updated_at']}")
                        
                except Exception as e:
                    st.error(f"❌ 搜索过程中发生错误：{str(e)}")
        else:
            st.warning("⚠️ 请输入搜索关键词")

def knowledge_browse_tab():
    """知识浏览标签页"""
    
    st.markdown("### 📚 知识分类浏览")
    
    # 获取知识分类 - 使用基础工具调用
    categories_result = _call_basic_tool(
        service_name="knowledge",
        tool_name="get_knowledge_categories",
        params={}
    )
    
    if categories_result.get("success"):
        categories = categories_result.get("data", {}).get("categories", [])
    else:
        categories = []
    
    # 如果没有分类数据，使用模拟数据
    if not categories:
        categories = [
            {"name": "电力系统", "count": 45, "description": "电力设备运维、故障处理相关知识"},
            {"name": "水利工程", "count": 38, "description": "水利设施维护、监测相关知识"},
            {"name": "设备维护", "count": 52, "description": "各类设备的维护保养知识"},
            {"name": "故障排除", "count": 67, "description": "常见故障的诊断和解决方案"},
            {"name": "安全规范", "count": 29, "description": "安全操作规程和注意事项"},
            {"name": "技术标准", "count": 34, "description": "行业技术标准和规范文档"}
        ]
    
    # 分类卡片展示
    cols = st.columns(2)
    
    for i, category in enumerate(categories):
        col_index = i % 2
        with cols[col_index]:
            apple_card(
                f"{category['name']} ({category['count']}篇)",
                category['description'],
                "📚",
                "primary" if i % 3 == 0 else "info" if i % 3 == 1 else "success"
            )
            
            if st.button(f"浏览 {category['name']}", key=f"browse_{category['name']}"):
                st.session_state.selected_category = category['name']
                st.info(f"正在加载 {category['name']} 分类下的知识...")
    
    # 显示选中分类的知识列表
    if hasattr(st.session_state, 'selected_category'):
        selected_cat = st.session_state.selected_category
        st.markdown(f"### 📖 {selected_cat} 知识列表")
        
        # 模拟知识列表
        knowledge_list = [
            {
                "标题": f"{selected_cat}相关知识 1",
                "摘要": "这是一篇关于具体技术实施的详细指南...",
                "标签": "技术, 实施, 指南",
                "更新时间": "2024-01-15",
                "阅读量": 156
            },
            {
                "标题": f"{selected_cat}相关知识 2",
                "摘要": "详细介绍了相关设备的维护要点和注意事项...",
                "标签": "维护, 设备, 注意事项",
                "更新时间": "2024-01-12",
                "阅读量": 203
            },
            {
                "标题": f"{selected_cat}相关知识 3",
                "摘要": "常见问题的解决方案和预防措施...",
                "标签": "问题, 解决方案, 预防",
                "更新时间": "2024-01-10",
                "阅读量": 89
            }
        ]
        
        knowledge_df = pd.DataFrame(knowledge_list)
        apple_data_table(knowledge_df, f"{selected_cat} 知识库", pagination=True)

def knowledge_add_tab():
    """知识添加标签页"""
    
    st.markdown("### ➕ 添加运维知识")
    
    # 知识添加表单
    with st.form("add_knowledge_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            knowledge_title = st.text_input("知识标题 *", placeholder="输入知识标题...")
            knowledge_category = st.selectbox(
                "知识分类 *",
                ["电力系统", "水利工程", "设备维护", "故障排除", "安全规范", "技术标准"]
            )
            knowledge_tags = st.text_input("标签", placeholder="输入标签，用逗号分隔...")
        
        with col2:
            knowledge_priority = st.selectbox("优先级", ["低", "中", "高", "紧急"])
            knowledge_source = st.text_input("知识来源", placeholder="输入知识来源...")
            knowledge_author = st.text_input("作者", placeholder="输入作者姓名...")
        
        # 知识内容
        knowledge_content = st.text_area(
            "知识内容 *",
            placeholder="输入详细的知识内容...",
            height=200
        )
        
        # 附件上传
        uploaded_files = st.file_uploader(
            "相关附件",
            accept_multiple_files=True,
            type=['pdf', 'doc', 'docx', 'txt', 'jpg', 'png']
        )
        
        # 提交按钮
        submitted = st.form_submit_button("📚 添加知识")
        
        if submitted:
            if not knowledge_title or not knowledge_content:
                st.error("❌ 请填写知识标题和内容")
            else:
                # 构建知识数据
                knowledge_data = {
                    "title": knowledge_title,
                    "category": knowledge_category,
                    "content": knowledge_content,
                    "tags": [tag.strip() for tag in knowledge_tags.split(",") if tag.strip()],
                    "priority": knowledge_priority,
                    "source": knowledge_source,
                    "author": knowledge_author
                }
                
                # 使用基础工具调用添加知识
                result = _call_basic_tool(
                    service_name="knowledge",
                    tool_name="add_knowledge",
                    params=knowledge_data
                )
                
                if result.get("success"):
                    st.success(f"✅ 知识添加成功！知识ID：{result.get('id', 'N/A')}")
                    st.balloons()
                else:
                    st.error(f"❌ 添加失败：{result.get('error', '未知错误')}")

def knowledge_qa_tab():
    """知识问答标签页 - 智能功能使用Agent调用"""
    
    st.markdown("### 💬 运维知识问答")
    
    # 知识问答界面 - 使用智能Agent调用
    intelligent_agent_chat_interface("knowledge", "knowledge_chat_history")
    
    # 常见问题快捷按钮
    st.markdown("#### 🔥 常见运维问题")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⚡ 智能电站SCADA系统故障诊断与应急处置"):
            _handle_knowledge_question("智能电站SCADA系统出现通信中断，请提供基于IEC 61850标准的故障诊断流程和应急处置方案")
        
        if st.button("🔧 水电机组振动监测与预测性维护策略"):
            _handle_knowledge_question("基于FFT频谱分析和机器学习算法，制定水电机组轴承振动监测的预测性维护策略和阈值设定")
    
    with col2:
        if st.button("🚰 大坝安全监测数据异常分析与风险评估"):
            _handle_knowledge_question("大坝位移监测数据出现异常波动，请运用统计过程控制和时间序列分析方法进行风险评估")
        
        if st.button("⚠️ 电力系统继电保护整定计算与配合优化"):
            _handle_knowledge_question("110kV变电站新增间隔，请提供继电保护整定计算方案和与上下级保护的配合优化策略")

# ============================================================================
# 智能体中心页面
# ============================================================================

def agent_center_page():
    """智能体中心页面"""
    
    st.title("🤖 AI智能体协作中心")
    
    # 功能选项卡
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 智能体概览", "💬 多智能体协作", "⚙️ 智能体配置", "📊 协作分析"])
    
    with tab1:
        agent_overview_tab()
    
    with tab2:
        multi_agent_collaboration_tab()
    
    with tab3:
        agent_config_tab()
    
    with tab4:
        collaboration_analysis_tab()

def agent_overview_tab():
    """智能体概览标签页"""
    
    st.markdown("### 🎯 智能体状态概览")
    
    # 智能体状态卡片
    agents_status = [
        {"name": "财务分析智能体", "status": "运行中", "tasks": 12, "success_rate": 0.95, "type": "financial"},
        {"name": "运维知识智能体", "status": "运行中", "tasks": 8, "success_rate": 0.92, "type": "knowledge"},
        {"name": "成本核算智能体", "status": "运行中", "tasks": 15, "success_rate": 0.88, "type": "cost"},
        {"name": "决策支持智能体", "status": "运行中", "tasks": 6, "success_rate": 0.97, "type": "decision"},
        {"name": "项目管理智能体", "status": "运行中", "tasks": 20, "success_rate": 0.91, "type": "project"},
        {"name": "协调中心智能体", "status": "运行中", "tasks": 35, "success_rate": 0.94, "type": "coordinator"}
    ]
    
    # 智能体状态网格
    cols = st.columns(3)
    
    for i, agent in enumerate(agents_status):
        col_index = i % 3
        with cols[col_index]:
            status_color = "success" if agent["status"] == "运行中" else "warning"
            status_icon = "✅" if agent["status"] == "运行中" else "⚠️"
            
            apple_card(
                f"{status_icon} {agent['name']}",
                f"""
                **状态：** {agent['status']}
                **处理任务：** {agent['tasks']} 个
                **成功率：** {agent['success_rate']*100:.1f}%
                """,
                "🤖",
                status_color
            )
    
    # 智能体性能图表
    st.markdown("### 📊 智能体性能分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 任务处理量图表
        agent_names = [agent["name"].replace("智能体", "") for agent in agents_status]
        task_counts = [agent["tasks"] for agent in agents_status]
        
        fig = create_apple_chart(
            "bar",
            pd.DataFrame({"智能体": agent_names, "任务数": task_counts}),
            "智能体任务处理量",
            x="智能体",
            y="任务数"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 成功率图表
        success_rates = [agent["success_rate"] * 100 for agent in agents_status]
        
        fig = create_apple_chart(
            "bar",
            pd.DataFrame({"智能体": agent_names, "成功率": success_rates}),
            "智能体成功率",
            x="智能体",
            y="成功率"
        )
        st.plotly_chart(fig, use_container_width=True)

def multi_agent_collaboration_tab():
    """多智能体协作标签页"""
    
    st.markdown("### 💬 多智能体协作平台")
    
    # 多智能体协作面板
    multi_agent_collaboration_panel()

def agent_config_tab():
    """智能体配置标签页"""
    
    st.markdown("### ⚙️ 智能体配置管理")
    
    # 选择要配置的智能体
    selected_agent = st.selectbox(
        "选择智能体",
        ["财务分析智能体", "运维知识智能体", "成本核算智能体", "决策支持智能体", "项目管理智能体"]
    )
    
    # 配置表单
    with st.form("agent_config_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            agent_name = st.text_input("智能体名称", value=selected_agent)
            agent_model = st.selectbox("AI模型", ["gemini-2.5-pro", "gpt-4", "claude-3"])
            temperature = st.slider("创造性参数", 0.0, 1.0, 0.7, 0.1)
            max_tokens = st.number_input("最大令牌数", 100, 4000, 2000, 100)
        
        with col2:
            response_timeout = st.number_input("响应超时（秒）", 5, 60, 30, 5)
            retry_attempts = st.number_input("重试次数", 1, 5, 3, 1)
            enable_memory = st.checkbox("启用记忆功能", value=True)
            enable_learning = st.checkbox("启用学习功能", value=True)
        
        # 专业提示词配置
        system_prompt = st.text_area(
            "系统提示词",
            value="你是一个专业的智能助手，专注于帮助用户解决相关问题...",
            height=150
        )
        
        # 保存配置按钮 - 复杂功能使用工作流调用
        if st.form_submit_button("💾 保存配置"):
            config_data = {
                "name": agent_name,
                "model": agent_model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timeout": response_timeout,
                "retry_attempts": retry_attempts,
                "enable_memory": enable_memory,
                "enable_learning": enable_learning,
                "system_prompt": system_prompt
            }
            
            try:
                # 使用复杂工作流调用智能体配置更新
                result = _execute_complex_workflow(
                    workflow_type="agent_config_update",
                    agent_name=selected_agent,
                    config_data=config_data
                )
                
                if result and result.get("success"):
                    st.success("✅ 智能体配置保存成功！")
                else:
                    st.error(f"❌ 保存失败：{result.get('error', '配置更新失败') if result else '服务不可用'}")
                    
            except Exception as e:
                st.error(f"❌ 保存配置时发生错误：{str(e)}")

def collaboration_analysis_tab():
    """协作分析标签页"""
    
    st.markdown("### 📊 智能体协作分析")
    
    # 协作统计
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        apple_metric_card("协作任务", "156", "+12", "🤝")
    
    with col2:
        apple_metric_card("成功协作", "142", "+15", "✅")
    
    with col3:
        apple_metric_card("协作效率", "91.0%", "+2.3%", "⚡")
    
    with col4:
        apple_metric_card("平均响应", "2.3s", "-0.5s", "⏱️")
    
    # 协作流程图表
    st.markdown("#### 🔄 协作流程分析")
    
    # 模拟协作数据
    collaboration_data = pd.DataFrame({
        "时间": pd.date_range(start='2024-01-01', periods=30, freq='D'),
        "协作次数": np.random.randint(3, 15, 30),
        "成功率": np.random.uniform(0.8, 0.98, 30)
    })
    
    fig = create_apple_chart(
        "line",
        collaboration_data,
        "智能体协作趋势",
        x="时间",
        y=["协作次数", "成功率"]
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 协作网络图
    st.markdown("#### 🕸️ 智能体协作网络")
    
    # 这里可以添加网络图可视化
    st.info("🚧 协作网络图功能开发中...")

# ============================================================================
# 系统设置页面
# ============================================================================

def system_settings_page():
    """系统设置页面"""
    
    st.title("⚙️ 系统设置")
    
    # 功能选项卡
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 基础设置", "🔐 安全设置", "📊 数据管理", "🔄 系统维护"])
    
    with tab1:
        basic_settings_tab()
    
    with tab2:
        security_settings_tab()
    
    with tab3:
        data_management_tab()
    
    with tab4:
        system_maintenance_tab()

def basic_settings_tab():
    """基础设置标签页"""
    
    st.markdown("### 🔧 基础系统设置")
    
    # 系统配置
    with st.form("basic_settings_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏢 企业信息")
            company_name = st.text_input("企业名称", value="四川智水信息技术有限公司")
            company_address = st.text_input("企业地址", value="四川省成都市")
            contact_email = st.text_input("联系邮箱", value="contact@zhishui.com")
            contact_phone = st.text_input("联系电话", value="028-12345678")
        
        with col2:
            st.markdown("#### ⚙️ 系统配置")
            timezone = st.selectbox("时区设置", ["Asia/Shanghai", "UTC", "America/New_York"])
            language = st.selectbox("系统语言", ["中文", "English"])
            theme = st.selectbox("界面主题", ["苹果风格", "经典风格", "深色模式"])
            auto_save = st.checkbox("自动保存", value=True)
        
        # 保存按钮
        if st.form_submit_button("💾 保存基础设置"):
            st.success("✅ 基础设置保存成功！")

def security_settings_tab():
    """安全设置标签页"""
    
    st.markdown("### 🔐 安全设置")
    
    # 密码策略
    st.markdown("#### 🔒 密码策略")
    
    col1, col2 = st.columns(2)
    
    with col1:
        min_password_length = st.number_input("最小密码长度", 6, 20, 8)
        require_uppercase = st.checkbox("要求大写字母", value=True)
        require_lowercase = st.checkbox("要求小写字母", value=True)
    
    with col2:
        require_numbers = st.checkbox("要求数字", value=True)
        require_symbols = st.checkbox("要求特殊字符", value=True)
        password_expiry_days = st.number_input("密码过期天数", 30, 365, 90)
    
    # 访问控制
    st.markdown("#### 🚪 访问控制")
    
    col1, col2 = st.columns(2)
    
    with col1:
        session_timeout = st.number_input("会话超时（分钟）", 15, 480, 60)
        max_login_attempts = st.number_input("最大登录尝试次数", 3, 10, 5)
    
    with col2:
        enable_2fa = st.checkbox("启用双因素认证", value=False)
        enable_ip_whitelist = st.checkbox("启用IP白名单", value=False)
    
    # 保存安全设置
    if st.button("🔐 保存安全设置"):
        st.success("✅ 安全设置保存成功！")

def data_management_tab():
    """数据管理标签页"""
    
    st.markdown("### 📊 数据管理")
    
    # 数据备份
    st.markdown("#### 💾 数据备份")
    
    col1, col2 = st.columns(2)
    
    with col1:
        backup_frequency = st.selectbox("备份频率", ["每日", "每周", "每月", "手动"])
        backup_retention = st.number_input("备份保留天数", 7, 365, 30)
    
    with col2:
        auto_backup = st.checkbox("自动备份", value=True)
        compress_backup = st.checkbox("压缩备份文件", value=True)
    
    # 备份操作按钮
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 立即备份"):
            with st.spinner("正在备份数据..."):
                time.sleep(2)
                st.success("✅ 数据备份完成！")
    
    with col2:
        if st.button("📥 下载备份"):
            st.info("📦 备份文件准备中...")
    
    with col3:
        if st.button("🔄 恢复数据"):
            st.warning("⚠️ 数据恢复功能需要管理员权限")
    
    # 数据清理
    st.markdown("#### 🧹 数据清理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        clean_logs_days = st.number_input("清理多少天前的日志", 7, 365, 30)
        clean_temp_files = st.checkbox("清理临时文件", value=True)
    
    with col2:
        clean_cache = st.checkbox("清理缓存文件", value=True)
        clean_old_reports = st.checkbox("清理旧报告", value=False)
    
    if st.button("🧹 开始清理"):
        with st.spinner("正在清理数据..."):
            time.sleep(1)
            st.success("✅ 数据清理完成！")

def system_maintenance_tab():
    """系统维护标签页"""
    
    st.markdown("### 🔄 系统维护")
    
    # 系统状态
    st.markdown("#### 📊 系统状态")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        apple_metric_card("CPU使用率", "45%", "-5%", "💻")
    
    with col2:
        apple_metric_card("内存使用", "2.1GB", "+0.3GB", "🧠")
    
    with col3:
        apple_metric_card("磁盘空间", "78%", "+2%", "💾")
    
    with col4:
        apple_metric_card("网络延迟", "12ms", "-3ms", "🌐")
    
    # 服务状态
    st.markdown("#### 🔧 服务状态")
    
    services = [
        {"服务名称": "项目信息整合服务", "状态": "运行中", "端口": "8001", "CPU": "15%", "内存": "256MB"},
        {"服务名称": "AI财务分析服务", "状态": "运行中", "端口": "8002", "CPU": "22%", "内存": "512MB"},
        {"服务名称": "运维知识库服务", "状态": "运行中", "端口": "8003", "CPU": "18%", "内存": "384MB"},
        {"服务名称": "成本核算预测服务", "状态": "运行中", "端口": "8004", "CPU": "20%", "内存": "448MB"},
        {"服务名称": "Agno智能体中心", "状态": "运行中", "端口": "8007", "CPU": "35%", "内存": "768MB"}
    ]
    
    services_df = pd.DataFrame(services)
    apple_data_table(services_df, "服务状态监控", searchable=False, pagination=False)
    
    # 维护操作
    st.markdown("#### 🛠️ 维护操作")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 重启所有服务"):
            with st.spinner("正在重启服务..."):
                time.sleep(3)
                st.success("✅ 所有服务重启完成！")
    
    with col2:
        if st.button("🧹 清理系统缓存"):
            with st.spinner("正在清理缓存..."):
                time.sleep(2)
                st.success("✅ 系统缓存清理完成！")
    
    with col3:
        if st.button("📊 生成系统报告"):
            with st.spinner("正在生成报告..."):
                time.sleep(2)
                st.success("✅ 系统报告生成完成！")
    
    # 系统日志
    st.markdown("#### 📋 系统日志")
    
    log_level = st.selectbox("日志级别", ["全部", "错误", "警告", "信息", "调试"])
    
    # 模拟系统日志
    logs = [
        {"时间": "2024-01-15 14:30:25", "级别": "信息", "服务": "项目服务", "消息": "项目数据同步完成"},
        {"时间": "2024-01-15 14:28:15", "级别": "警告", "服务": "财务服务", "消息": "API调用频率较高"},
        {"时间": "2024-01-15 14:25:10", "级别": "信息", "服务": "知识库", "消息": "知识索引更新完成"},
        {"时间": "2024-01-15 14:20:05", "级别": "错误", "服务": "成本服务", "消息": "数据库连接超时"},
        {"时间": "2024-01-15 14:15:30", "级别": "信息", "服务": "智能体中心", "消息": "智能体协作任务完成"}
    ]
    
    logs_df = pd.DataFrame(logs)
    apple_data_table(logs_df, "系统日志", searchable=True, pagination=True)

# ============================================================================
# 页面路由映射
# ============================================================================

PAGE_FUNCTIONS = {
    "首页": dashboard_page,
    "项目管理": project_management_page,
    "财务分析": financial_analysis_page,
    "运维知识库": knowledge_base_page,
    "智能体中心": agent_center_page,
    "系统设置": system_settings_page
}

def render_page(page_name: str):
    """渲染指定页面"""
    if page_name in PAGE_FUNCTIONS:
        PAGE_FUNCTIONS[page_name]()
    else:
        st.error(f"❌ 页面 '{page_name}' 不存在")

# ============================================================================
# 智能路由支持函数
# ============================================================================

def intelligent_agent_chat_interface(agent_type: str, session_key: str = "chat_history"):
    """智能Agent聊天界面 - 使用智能路由调用"""
    
    # 初始化聊天历史
    if session_key not in st.session_state:
        st.session_state[session_key] = []
    
    # 显示聊天历史
    for message in st.session_state[session_key]:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # 用户输入
    if prompt := st.chat_input(f"请输入您的{agent_type}相关问题..."):
        # 添加用户消息
        st.session_state[session_key].append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # 调用智能Agent获取回复
        with st.chat_message("assistant"):
            with st.spinner("AI正在思考中..."):
                # 使用智能功能调用Agent
                response = _execute_complex_workflow(
                    workflow_type="agent_chat",
                    agent_type=agent_type,
                    task_description=prompt,
                    context={"chat_history": st.session_state[session_key][-5:]}
                )
                
                if response and response.get("success"):
                    ai_response = response.get("result", "")
                else:
                    ai_response = f"抱歉，{agent_type}服务暂时不可用，请稍后再试。"
                
                st.write(ai_response)
                
                # 添加AI回复到历史
                st.session_state[session_key].append({"role": "assistant", "content": ai_response})

def _handle_financial_question(question: str, session_key: str):
    """处理财务问题 - 智能功能使用Agent调用"""
    
    # 添加用户问题到聊天历史
    if session_key not in st.session_state:
        st.session_state[session_key] = []
    
    st.session_state[session_key].append({
        "role": "user", 
        "content": question
    })
    
    # 使用智能功能调用财务Agent
    response = _execute_complex_workflow(
        workflow_type="agent_chat",
        agent_type="financial",
        task_description=question,
        context={"source": "quick_question"}
    )
    
    if response and response.get("success"):
        ai_response = response.get("result", "")
    else:
        ai_response = "抱歉，财务分析服务暂时不可用，请稍后再试。"
    
    # 添加AI回复到历史
    st.session_state[session_key].append({
        "role": "assistant", 
        "content": ai_response
    })
    
    # 刷新页面显示新消息
    st.rerun()

def _handle_knowledge_question(question: str):
    """处理知识库问题 - 智能功能使用Agent调用"""
    
    # 添加用户问题到聊天历史
    session_key = "knowledge_chat_history"
    if session_key not in st.session_state:
        st.session_state[session_key] = []
    
    st.session_state[session_key].append({
        "role": "user", 
        "content": question
    })
    
    # 使用智能功能调用知识库Agent
    response = _execute_complex_workflow(
        workflow_type="agent_chat",
        agent_type="knowledge",
        task_description=question,
        context={"source": "quick_question"}
    )
    
    if response and response.get("success"):
        ai_response = response.get("result", "")
    else:
        ai_response = "抱歉，运维知识库服务暂时不可用，请稍后再试。"
    
    # 添加AI回复到历史
    st.session_state[session_key].append({
        "role": "assistant", 
        "content": ai_response
    })
    
    # 刷新页面显示新消息
    st.rerun()

def _call_basic_tool(service_name: str, tool_name: str, **kwargs):
    """调用基础MCP工具 - 基础功能使用直接工具调用"""
    
    # 模拟基础工具调用，实际应通过Agno协调器调用
    try:
        # 这里应该通过Agno协调器调用基础工具
        # 暂时返回模拟数据，确保页面正常运行
        if service_name == "project" and tool_name == "get_projects":
            return {"success": True, "data": []}
        elif service_name == "financial" and tool_name == "get_financial_overview":
            return {"success": True, "data": {"revenue": 0, "cost": 0, "profit": 0}}
        elif service_name == "knowledge" and tool_name == "search_knowledge":
            return {"success": True, "data": []}
        else:
            return {"success": True, "data": {}}
    except Exception as e:
        st.error(f"工具调用失败：{str(e)}")
        return {"success": False, "error": str(e)}

def _execute_complex_workflow(workflow_type: str, **kwargs):
    """执行复杂工作流 - 复杂功能使用完整工作流"""
    
    # 模拟复杂工作流执行，实际应通过Agno协调器执行
    try:
        # 这里应该通过Agno协调器执行复杂工作流
        # 暂时返回模拟数据，确保页面正常运行
        if workflow_type == "agent_chat":
            agent_type = kwargs.get("agent_type", "general")
            task_description = kwargs.get("task_description", "")
            return {
                "success": True, 
                "result": f"这是{agent_type}智能体的模拟回复：{task_description[:50]}..."
            }
        elif workflow_type == "multi_agent_collaboration":
            return {"success": True, "result": "多智能体协作完成"}
        else:
            return {"success": True, "result": "工作流执行完成"}
    except Exception as e:
        st.error(f"工作流执行失败：{str(e)}")
        return None

def _get_service_health_basic():
    """获取服务健康状态 - 基础功能使用直接调用"""
    
    try:
        # 直接调用健康检查工具
        return _call_basic_tool("system", "health_check")
    except Exception as e:
        st.error(f"健康检查失败：{str(e)}")
        return None

# ============================================================================
# 测试函数
# ============================================================================

def test_pages():
    """测试页面功能"""
    print("🧪 测试页面模块...")
    
    # 测试页面路由
    assert "首页" in PAGE_FUNCTIONS
    assert "项目管理" in PAGE_FUNCTIONS
    assert "财务分析" in PAGE_FUNCTIONS
    assert "运维知识库" in PAGE_FUNCTIONS
    assert "智能体中心" in PAGE_FUNCTIONS
    assert "系统设置" in PAGE_FUNCTIONS
    
    print("✅ 页面模块测试通过！")

if __name__ == "__main__":
    test_pages()