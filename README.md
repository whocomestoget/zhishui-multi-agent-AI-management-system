# 智水AI智慧管理解决方案

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**🏢 企业级多智能体AI管理系统**

**💡 专为电力和水利行业打造的智慧管理解决方案**

[English](#english-version) | [中文](#项目简介)

</div>

---

## 📋 目录

- [项目简介](#项目简介)
- [系统架构](#系统架构)
- [核心功能](#核心功能)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [详细部署](#详细部署)
- [API文档](#api文档)
- [配置说明](#配置说明)
- [开发指南](#开发指南)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 项目简介

智水AI智慧管理解决方案是一个专为电力和水利行业设计的企业级多智能体AI管理系统。系统采用先进的MCP（Model Context Protocol）架构，通过多个专业化的AI智能体协同工作，为企业提供全方位的智能分析和决策支持。

### 🎯 项目特色

- **🏗️ 模块化架构**：基于MCP协议的多智能体协作架构
- **🔧 行业定制**：专门针对电力和水利行业的业务场景优化
- **📊 智能分析**：集成财务分析、成本预测、知识管理、效能评估等多维度AI能力
- **🎨 可视化界面**：现代化的Streamlit仪表板，支持拖拽式操作
- **⚡ 高性能**：采用异步处理和并行计算，确保系统响应速度
- **🔒 安全可靠**：企业级的安全设计和数据保护机制

---

## 系统架构

### 🏗️ 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    前端展示层                                │
│              ┌───────────────────────┐                       │
│              │   Streamlit仪表板     │                       │
│              │  • 数据可视化         │                       │
│              │  • 智能体交互         │                       │
│              │  • 报告生成           │                       │
│              └──────────┬────────────┘                       │
│                         │                                   │
└─────────────────────────┼───────────────────────────────────┘
                          │ HTTP/REST API
┌─────────────────────────┼───────────────────────────────────┐
│                    协调控制层                                │
│              ┌──────────┴────────────┐                       │
│              │   Agno协调中心        │                       │
│              │  • 任务调度           │                       │
│              │  • 智能体管理         │                       │
│              │  • 结果聚合           │                       │
│              └──────────┬────────────┘                       │
│                         │                                   │
└─────────────────────────┼───────────────────────────────────┘
                          │ MCP协议
┌─────────────────────────┼───────────────────────────────────┐
│                    智能体服务层                               │
│              ┌──────────┴────────────┐                       │
│              │   专业AI智能体集群    │                       │
│  ┌───────────┼───────────┬─────────┼───────────┐         │
│  │财务分析   │成本预测   │知识管理 │效能评估   │         │
│  │智能体     │智能体     │智能体   │智能体     │         │
│  └───────────┴───────────┴─────────┴───────────┘         │
│                         │                                   │
└─────────────────────────┼───────────────────────────────────┘
                          │ 数据访问
┌─────────────────────────┼───────────────────────────────────┐
│                    数据存储层                                │
│  ┌───────────┬───────────┬─────────┬───────────┐           │
│  │SQLite     │JSON文件   │Excel    │日志文件   │           │
│  │数据库     │          │数据     │          │           │
│  └───────────┴───────────┴─────────┴───────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### 📁 项目结构

```
智水AI智慧管理解决方案/
├── 1_frontend_dashboard/          # Streamlit前端仪表板
│   ├── main.py                   # 主应用入口
│   ├── pages.py                  # 页面路由和组件
│   ├── components.py            # UI组件库
│   ├── api_client.py             # API客户端
│   ├── config.py                 # 前端配置
│   ├── models.py                 # 数据模型
│   ├── utils.py                  # 工具函数
│   └── requirements.txt          # 前端依赖
│
├── 2_financial_ai_mcp/            # 财务AI MCP服务
│   ├── financial_mcp.py          # 财务分析智能体
│   ├── data/                     # 财务数据存储
│   └── requirements.txt          # 服务依赖
│
├── 3_cost_prediction_mcp/         # 成本预测MCP服务
│   ├── cost_prediction_mcp.py   # 成本预测智能体
│   ├── predict_cost.py           # 预测算法
│   ├── train_model.py            # 模型训练
│   ├── utils.py                  # 工具函数
│   ├── data_templates/           # 数据模板
│   ├── models/                   # 训练好的模型
│   └── requirements.txt          # 服务依赖
│
├── 4_operation_knowledge_mcp/     # 运营知识MCP服务
│   ├── knowledge_mcp.py          # 知识管理智能体
│   ├── knowledge_base/           # 知识库文件
│   └── requirements.txt          # 服务依赖
│
├── 5_hr_efficiency_mcp/          # 人力资源效能MCP服务
│   ├── zhishui_efficiency_mcp.py # 效能评估智能体
│   └── requirements.txt          # 服务依赖
│
├── 7_agno_coordinator/            # 智能体协调中心
│   ├── start_optimized.py        # 协调中心主程序
│   ├── main.py                   # FastAPI应用
│   ├── planner_agent.py          # 规划智能体
│   ├── agents/                   # 业务智能体基类
│   │   ├── base_agent.py         # 基础智能体类
│   │   ├── business_agent.py     # 业务智能体基类
│   │   ├── financial_agent.py    # 财务智能体
│   │   ├── cost_agent.py         # 成本智能体
│   │   ├── knowledge_agent.py    # 知识智能体
│   │   └── efficiency_agent.py   # 效能智能体
│   ├── config.py                 # 系统配置
│   ├── requirements.txt          # 协调中心依赖
│   └── docs/                     # 架构文档
│
├── .env.example                   # 环境变量示例
├── README.md                     # 项目说明文档
└── LICENSE                       # 许可证文件
```

---

## 核心功能

### 💰 财务AI分析
- **智能财务分析**：自动分析财务报表，识别异常和风险
- **关键指标计算**：ROE、ROA、流动比率、速动比率等
- **趋势预测**：基于历史数据预测未来财务表现
- **可视化报告**：生成专业的财务分析报告

### 📈 成本预测
- **成本模型训练**：基于历史数据训练预测模型
- **多维度预测**：支持按项目、部门、时间等维度预测
- **敏感性分析**：评估不同因素对成本的影响
- **预警机制**：成本超支自动预警

### 📚 知识管理
- **智能文档处理**：自动提取和分类技术文档
- **语义搜索**：基于语义的智能文档检索
- **知识图谱**：构建领域知识图谱
- **最佳实践推荐**：基于场景推荐最佳实践

### 👥 人力资源效能
- **员工效能评估**：多维度评估员工工作表现
- **个性化建议**：基于AI的个性化改进建议
- **团队分析**：团队效能趋势分析
- **培训推荐**：智能推荐培训课程

### 📊 可视化仪表板
- **实时监控**：关键指标实时展示
- **交互式图表**：支持钻取和筛选的图表
- **自定义报告**：用户可自定义报告模板
- **数据导出**：支持多种格式的数据导出

---

## 技术栈

### 🐍 后端技术
- **Python 3.10+**：主要开发语言
- **FastAPI**：高性能Web框架
- **Agno**：多智能体协调框架
- **Pandas**：数据处理和分析
- **NumPy**：数值计算
- **SQLite**：轻量级数据库
- **Joblib**：模型序列化

### 🎨 前端技术
- **Streamlit**：快速构建数据应用
- **Plotly**：交互式图表库
- **Pandas**：前端数据处理
- **Streamlit-Option-Menu**：导航组件

### 🤖 AI/ML技术
- **OpenAI API**：大语言模型集成
- **Scikit-learn**：机器学习算法
- **Matplotlib**：数据可视化
- **Requests**：HTTP客户端

### 🔧 开发工具
- **Python-dotenv**：环境变量管理
- **Logging**：日志系统
- **PyInstaller**：应用打包
- **Git**：版本控制

---

## 快速开始

### 📋 环境要求

- Python 3.10 或更高版本
- Windows 10/11 或 Linux Ubuntu 20.04+
- 8GB RAM（推荐16GB）
- 10GB 可用磁盘空间
- 网络连接（用于API调用）

### 🚀 一键安装

```bash
# 克隆项目
git clone https://github.com/your-username/zhishui-ai-management.git
cd zhishui-ai-management

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r 7_agno_coordinator/requirements.txt
pip install -r 1_frontend_dashboard/requirements.txt
```

### ⚙️ 配置环境

1. 复制环境变量示例文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的API密钥：
```env
# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# 系统配置
SYSTEM_ENV=development
LOG_LEVEL=INFO
```

3. 配置AI模型参数（编辑 `7_agno_coordinator/config.py`）：
```python
AI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY", ""),
    "api_base": os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
    "model": "gpt-4-turbo-preview",
    "temperature": 0.7,
    "max_tokens": 65000,
}
```

### 🏃‍♂️ 启动服务

```bash
# 1. 启动协调中心（终端1）
cd 7_agno_coordinator
python start_optimized.py

# 2. 启动前端应用（终端2）
cd 1_frontend_dashboard
streamlit run main.py --server.port 8501
```

### 🌐 访问应用

- **前端仪表板**：http://localhost:8501
- **API文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health

---

## 详细部署

### 📦 各服务启动顺序

#### 第一步：启动MCP专业服务

```bash
# 启动财务分析服务（终端1）
cd 2_financial_ai_mcp
python financial_mcp.py

# 启动成本预测服务（终端2）
cd 3_cost_prediction_mcp
python cost_prediction_mcp.py

# 启动知识管理服务（终端3）
cd 4_operation_knowledge_mcp
python knowledge_mcp.py

# 启动效能评估服务（终端4）
cd 5_hr_efficiency_mcp
python zhishui_efficiency_mcp.py
```

#### 第二步：启动协调中心

```bash
# 启动智能体协调中心（终端5）
cd 7_agno_coordinator
python start_optimized.py
```

#### 第三步：启动前端应用

```bash
# 启动Streamlit前端（终端6）
cd 1_frontend_dashboard
streamlit run main.py --server.port 8501
```

### 🔧 配置说明

#### 系统配置

编辑 `7_agno_coordinator/config.py` 文件：

```python
# 系统运行配置
@dataclass
class SystemConfig:
    system_name: str = "智水信息AI智慧管理系统"
    version: str = "1.0.0"
    environment: str = "development"  # development, production
    max_concurrent_workflows: int = 5
    max_agent_execution_time: int = 600  # 秒
    thread_pool_size: int = 4

# AI模型配置
AI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY", ""),
    "api_base": os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
    "model": "gpt-4-turbo-preview",
    "temperature": 0.7,
    "max_tokens": 65000,
}
```

#### 前端配置

编辑 `1_frontend_dashboard/config.py` 文件：

```python
# Streamlit配置
STREAMLIT_CONFIG = {
    "page_title": "智水AI智慧管理系统",
    "page_icon": "💧",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "theme": {
        "primaryColor": "#1f77b4",
        "backgroundColor": "#f0f2f6",
        "secondaryBackgroundColor": "#ffffff",
        "textColor": "#262730",
    }
}
```

---

## API文档

### 核心接口

#### 智能体协作接口

**POST** `/collaborate`

提交任务给多智能体系统进行处理。

**请求参数：**
```json
{
  "task_type": "financial_analysis",
  "task_data": {
    "company_name": "智水信息技术有限公司",
    "analysis_period": "2024",
    "focus_areas": ["profitability", "liquidity", "efficiency"]
  },
  "priority": "high",
  "timeout": 300
}
```

**响应示例：**
```json
{
  "task_id": "task_123456",
  "status": "completed",
  "results": {
    "financial_summary": {
      "current_ratio": 2.1,
      "roe": 0.15,
      "profit_margin": 0.12,
      "recommendations": [
        "建议优化应收账款管理",
        "考虑增加短期投资"
      ]
    }
  },
  "processing_time": 45.2,
  "confidence_score": 0.89
}
```

#### 健康检查接口

**GET** `/health`

检查系统健康状态。

**响应示例：**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "coordinator": "running",
    "financial_agent": "available",
    "cost_agent": "available", 
    "knowledge_agent": "available",
    "efficiency_agent": "available"
  },
  "version": "1.0.0"
}
```

---

## 开发指南

### 🛠️ 开发环境搭建

1. **创建开发分支：**
```bash
git checkout -b feature/your-feature-name
```

2. **安装开发依赖：**
```bash
pip install -r requirements-dev.txt
```

3. **运行测试：**
```bash
python -m pytest tests/ -v
```

### 📏 代码规范

- 遵循PEP 8 Python编码规范
- 使用类型提示（Type Hints）
- 编写单元测试和集成测试
- 添加详细的文档字符串
- 使用有意义的变量和函数命名

### 📝 提交规范

提交信息格式：
```
type(scope): description

[optional body]

[optional footer]
```

类型说明：
- `feat`: 新功能
- `fix`: 修复Bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 🔍 调试技巧

1. **启用详细日志：**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **使用断点调试：**
```python
import pdb
pdb.set_trace()
```

3. **性能分析：**
```python
import cProfile
cProfile.run('your_function()')
```

---

## 贡献指南

我们欢迎所有形式的贡献，包括：

- 🐛 **报告Bug**：提交Issue时请提供详细的复现步骤
- 💡 **新功能建议**：欢迎提出新的功能想法和改进建议
- 📝 **文档改进**：帮助我们完善项目文档
- 🔧 **代码贡献**：提交Pull Request参与代码开发

### 如何贡献

1. Fork 项目仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

---

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🆘 常见问题

### Q: 系统启动后前端无法连接到后端？
**A:** 请检查：
1. 协调中心是否成功启动（查看终端日志）
2. 防火墙是否阻止了8000端口
3. 前端配置中的API地址是否正确

### Q: API调用返回401错误？
**A:** 请检查：
1. `.env` 文件中的API密钥是否正确配置
2. 环境变量是否成功加载
3. API密钥是否有足够的权限

### Q: 模型预测结果不准确？
**A:** 建议：
1. 检查训练数据的质量和完整性
2. 调整模型参数和训练周期
3. 使用更多的历史数据进行训练

### Q: 如何处理大量数据？
**A:** 建议：
1. 使用数据分批处理
2. 启用系统的并行处理功能
3. 考虑升级硬件配置

---

## 📞 联系方式

- **项目维护者**：商海星辰队
- **邮箱**：contact@zhishui-ai.com
- **项目主页**：[https://github.com/your-username/zhishui-ai-management](https://github.com/your-username/zhishui-ai-management)
- **问题反馈**：[提交Issue](https://github.com/your-username/zhishui-ai-management/issues)

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个Star！** 

**💧 智水AI - 让管理更智能，让决策更精准！**

</div>

---

## English Version

### Project Overview

Zhishui AI Smart Management Solution is an enterprise-grade multi-agent AI management system designed specifically for the electric power and water conservancy industries. The system adopts advanced MCP (Model Context Protocol) architecture, providing comprehensive intelligent analysis and decision support for enterprises through the collaborative work of multiple specialized AI agents.

### Key Features

- **Modular Architecture**: Multi-agent collaborative architecture based on MCP protocol
- **Industry Customization**: Optimized for business scenarios in electric power and water conservancy industries
- **Intelligent Analysis**: Integrated multi-dimensional AI capabilities including financial analysis, cost prediction, knowledge management, and performance evaluation
- **Visual Interface**: Modern Streamlit dashboard with drag-and-drop operation
- **High Performance**: Asynchronous processing and parallel computing ensure system response speed
- **Safe and Reliable**: Enterprise-grade security design and data protection mechanisms

### Quick Start

```bash
# Clone the project
git clone https://github.com/your-username/zhishui-ai-management.git
cd zhishui-ai-management

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r 7_agno_coordinator/requirements.txt
pip install -r 1_frontend_dashboard/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env file with your API keys

# Start services
cd 7_agno_coordinator && python start_optimized.py  # Terminal 1
cd 1_frontend_dashboard && streamlit run main.py  # Terminal 2
```

Access the application:
- Frontend Dashboard: http://localhost:8501
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health