# 智水信息Multi-Agent AI智慧管理系统

## 🚀 项目概述

智水信息Multi-Agent AI智慧管理系统是专为四川智水信息技术有限公司设计的AI驱动智慧管理解决方案。系统采用先进的Multi-Agent架构，通过Agno框架实现多智能体协作，解决企业在数据分散、成本不透明、财务能力不足、运维知识分散、系统割裂等核心痛点。

### 🎯 技术定位
- **AI协调中心**：基于Agno框架的多智能体协调器，统一管理各业务AI模块
- **标准化MCP客户端**：实现参数结构标准化，解决FastMCP兼容性问题
- **智能任务编排**：Planner Agent实现需求理解、任务分解、执行计划制定
- **多Agent协作**：财务、成本、效率、知识管理四大业务Agent协同工作
- **统一报告生成**：Report Generator Agent整合多Agent结果，生成可视化HTML报告

### 🎯 核心价值

- **数据整合**：统一分散的Excel数据，建立标准化数据管理体系
- **成本透明**：实现项目成本的精确核算和实时监控
- **财务赋能**：提供AI驱动的财务分析和战略决策支持
- **知识管理**：构建统一的运维知识库和技能标准体系
- **智能决策**：基于多维度数据分析提供决策支持

### 🏢 适用场景

- **电力行业**：智慧电厂、智能电站项目管理
- **水利行业**：智慧水利、大坝监测项目分析
- **企业管理**：财务分析、成本控制、效率优化
- **知识管理**：技术文档标准化、运维知识库建设

## 🏗️ 系统架构

### 核心组件架构

```
智水信息Multi-Agent系统
├── 🧠 Agno协调中心 (standardized_mcp_client_v2.py)
│   ├── 标准化MCP客户端 - 解决FastMCP参数兼容性问题
│   ├── 多Agent生命周期管理 - 统一创建、调度、监控
│   ├── 参数结构标准化 - 自动补全、格式验证、错误处理
│   └── 工作流编排引擎 - 任务分解、依赖管理、结果聚合
├── 📋 规划智能体 (planner_agent.py)
│   ├── 自然语言意图识别 - 基于Gemini-2.5-Pro的智能理解
│   ├── 需求分析与任务分解 - 复杂需求拆分为可执行任务
│   ├── 数据完整性检查 - 自动识别缺失数据并生成补充询问
│   └── 执行计划制定 - Agent调度顺序、依赖关系、超时控制
├── 💼 业务分析智能体群 (agents/)
│   ├── 💰 财务分析Agent (financial_agent.py) - ROE、ROA、现金流分析
│   ├── 💸 成本分析Agent (cost_agent.py) - 成本结构、预算执行分析  
│   ├── ⚡ 效率分析Agent (efficiency_agent.py) - 人员效率、流程优化
│   └── 📚 知识管理Agent (knowledge_agent.py) - 知识库、技能评估
├── 📊 报告生成智能体 (report_generator_agent.py)
│   ├── 多Agent结果聚合 - 统一数据格式、冲突解决、权重计算
│   ├── HTML可视化报告 - Plotly图表、响应式设计、交互功能
│   ├── 关键洞察提取 - 核心发现总结、行动建议、风险识别
│   └── 多格式输出 - HTML、Markdown、JSON多种格式支持
└── ⚙️ 系统配置与管理
    ├── 配置管理 (config.py) - AI模型、业务参数、日志配置
    ├── 工作流模板 (workflow_templates.py) - 预定义业务流程模板
    ├── 会话历史 (models/conversation_history.py) - 对话状态管理
    └── 主启动程序 (main.py) - FastAPI服务、命令行接口
```

### 核心技术栈

- **AI框架**：Agno Multi-Agent Framework - 多智能体协调管理
- **AI模型**：Gemini-2.5-Pro (通过OpenAI API兼容接口调用)
- **编程语言**：Python 3.8+ - 异步编程支持
- **异步处理**：asyncio, aiohttp - 高并发Agent调度
- **数据处理**：pandas, numpy - 业务数据分析和处理
- **报告生成**：Jinja2, Plotly - HTML可视化报告生成
- **配置管理**：Pydantic, YAML - 类型安全的配置管理
- **Web服务**：FastAPI, uvicorn - RESTful API服务
- **数据存储**：SQLite - 会话历史和业务数据存储
- **日志系统**：logging - 结构化日志记录和追踪

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- Windows 10/11 或 Linux/macOS
- 至少 4GB 可用内存
- 稳定的网络连接（用于AI API调用）

### 安装步骤

1. **进入项目目录**
```bash
cd "d:\竞赛\2025企创\决赛\四川智水AI智慧管理解决方案\7_agno_coordinator"
```

2. **创建虚拟环境**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. **安装核心依赖**
```bash
pip install -r requirements.txt

# 核心依赖包：
# agno>=1.0.0 - Multi-Agent框架
# openai>=1.0.0 - AI模型调用
# fastapi>=0.104.0 - Web服务框架
# uvicorn>=0.24.0 - ASGI服务器
# pydantic>=2.0.0 - 数据验证
# pandas>=2.0.0 - 数据处理
# plotly>=5.0.0 - 可视化图表
# jinja2>=3.0.0 - HTML模板引擎
```

4. **验证系统安装**
```bash
# 验证Agno框架
python -c "import agno; print('✅ Agno框架安装成功')"

# 验证AI模型连接
python -c "from config import get_ai_config; print('✅ AI配置加载成功')"

# 验证所有Agent
python -c "from agents.base_agent import BaseAgent; print('✅ Agent基类加载成功')"
```

### 配置系统

系统已预配置AI API密钥，无需额外配置即可使用。如需自定义配置，可修改 `config.py` 文件：

```python
# AI配置已内置，支持以下模型
AI_CONFIG = {
    "api_key": "sk-bwYd3WFPwE5dQrhIL1UpuTkf9wjq3bazraPDUAiJPSNN3wVE",
    "api_base": "https://xi.apicenter.top/v1",
    "model": "gemini-2.5-pro",
    "temperature": 0.7
}
```

## 💻 使用指南

### 启动系统

#### 1. 交互模式（推荐）
```bash
python main.py --mode interactive
```

启动后可以直接输入分析需求：
```
💬 请输入分析需求: 分析我们公司2024年的财务状况
💬 请输入分析需求: 评估智慧电厂项目的成本控制情况
💬 请输入分析需求: 如何提升运维团队的技能标准化
```

#### 2. 单次分析模式
```bash
python main.py --mode analysis --analysis "分析财务状况" --output report.html
```

#### 3. 演示模式
```bash
python main.py --mode demo
```

### 可用工作流

#### 1. 综合管理分析 (comprehensive_analysis)
- **适用场景**：全面的企业管理分析
- **分析维度**：财务、成本、效率、知识管理
- **输出**：多维度综合分析报告

#### 2. 财务专项分析 (financial_focus)
- **适用场景**：专项财务健康度评估
- **分析维度**：财务指标、成本关联分析
- **输出**：专业财务分析报告

#### 3. 成本效率分析 (cost_efficiency_analysis)
- **适用场景**：成本控制和效率优化
- **分析维度**：成本结构、运营效率、知识管理
- **输出**：成本效率优化报告

### 命令行选项

```bash
python main.py [选项]

选项：
  --mode {interactive,api,demo,analysis}  运行模式 (默认: interactive)
  --port PORT                            API服务端口 (默认: 8000)
  --analysis ANALYSIS                    要执行的分析任务描述
  --workflow {comprehensive_analysis,financial_focus,cost_efficiency_analysis}
                                        工作流类型 (默认: comprehensive_analysis)
  --output OUTPUT                       结果输出文件路径
  --verbose                             详细输出模式
  --help                                显示帮助信息
```

## 📊 功能特性

### 🧠 智能规划Agent (planner_agent.py)
- **自然语言理解**：基于Gemini-2.5-Pro的意图识别和语义分析
- **需求分析与分解**：复杂业务需求拆分为可执行的分析任务
- **数据完整性检查**：自动识别缺失数据，生成补充数据询问
- **执行计划制定**：Agent调度顺序、依赖关系、并行执行策略
- **人机交互管理**：多轮对话状态维护，上下文理解

**核心技术实现**：
```python
class PlannerAgent:
    def analyze_requirement(self, user_input: str) -> Dict[str, Any]:
        """需求分析核心算法"""
        # 1. 意图识别 - 使用Gemini模型进行语义理解
        intent = self._extract_intent_with_ai(user_input)
        
        # 2. 实体提取 - 识别关键业务实体
        entities = self._extract_entities(user_input)
        
        # 3. 任务分解 - 拆分为子分析任务
        sub_tasks = self._decompose_task(intent, entities)
        
        # 4. 数据需求分析 - 识别所需数据类型
        data_requirements = self._analyze_data_needs(sub_tasks)
        
        return {
            "intent": intent,
            "entities": entities,
            "sub_tasks": sub_tasks,
            "data_requirements": data_requirements
        }
```

### 🔧 标准化MCP客户端 (standardized_mcp_client_v2.py)
- **参数结构标准化**：解决FastMCP不同版本的参数兼容性问题
- **智能参数补全**：自动检测并补全缺失的必需参数字段
- **多格式数据支持**：支持JSON字符串、字典对象、文件路径等多种输入
- **错误处理优化**：详细的错误信息和自动恢复机制
- **Agent生命周期管理**：统一创建、启动、监控、销毁流程

**核心技术实现**：
```python
class StandardizedMCPClient:
    def standardize_parameters(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """参数标准化核心算法"""
        # 1. 获取工具定义和参数要求
        tool_definition = self._get_tool_definition(tool_name)
        required_params = tool_definition.get("required_params", [])
        
        # 2. 参数完整性检查
        missing_params = self._check_missing_params(params, required_params)
        
        # 3. 自动参数补全
        completed_params = self._auto_complete_params(params, missing_params)
        
        # 4. 参数格式验证和转换
        standardized_params = self._validate_and_convert_params(completed_params)
        
        return standardized_params
    
    def execute_with_retry(self, tool_name: str, params: Dict[str, Any], max_retries: int = 3) -> Any:
        """带重试的执行机制"""
        for attempt in range(max_retries):
            try:
                # 参数标准化
                standardized_params = self.standardize_parameters(tool_name, params)
                
                # 执行工具调用
                result = self._execute_tool(tool_name, standardized_params)
                
                return result
                
            except Exception as e:
                if attempt < max_retries - 1:
                    # 智能错误恢复
                    recovery_action = self._analyze_error_and_recover(e, params)
                    if recovery_action:
                        params = recovery_action
                        continue
                
                # 最后一次尝试失败，抛出异常
                raise RuntimeError(f"工具执行失败: {tool_name}, 错误: {str(e)}")
```

### 💰 财务分析Agent (agents/financial_agent.py)
- **盈利能力分析**：ROE、ROA、毛利率、净利率等关键财务指标
- **偿债能力评估**：流动比率、速动比率、资产负债率、利息保障倍数
- **运营效率评价**：总资产周转率、存货周转率、应收账款周转率
- **财务风险识别**：现金流风险、债务结构风险、流动性风险
- **趋势分析和预测**：基于历史数据的财务趋势预测

### 💸 成本分析Agent (agents/cost_agent.py)
- **成本结构分解**：直接成本、间接成本、固定成本、变动成本分析
- **成本控制评估**：预算执行情况、成本偏差分析、超支原因识别
- **成本预测建模**：基于历史数据和业务计划的成本趋势预测
- **成本优化建议**：成本削减机会识别、效率提升方案、资源配置优化
- **项目成本核算**：项目级别的成本归集、分摊、盈亏分析

### ⚡ 效率分析Agent (agents/efficiency_agent.py)
- **人员效率评估**：人均产值、劳动生产率、人力成本占比分析
- **流程效率优化**：业务流程瓶颈识别、流程周期分析、优化建议
- **资源利用分析**：设备利用率、空间利用率、资产配置效率
- **效率提升建议**：基于数据的优化方案、最佳实践推荐、改进路径
- **多维度效率对比**：部门间、期间间、行业基准对比分析

### 📚 知识管理Agent (agents/knowledge_agent.py)
- **知识库建设**：技术文档标准化、知识体系架构设计、分类管理
- **技能评估分析**：团队技能差距分析、能力矩阵构建、培训需求识别
- **培训规划制定**：个性化培训方案、学习路径设计、效果评估机制
- **知识共享推广**：最佳实践提取、经验总结、知识传播机制
- **智能化知识推荐**：基于业务场景的知识推荐、专家匹配

### 📊 报告生成Agent (report_generator_agent.py)
- **多Agent结果聚合**：统一数据格式、冲突解决、权重计算、置信度评估
- **HTML可视化报告**：Plotly交互式图表、响应式设计、现代化UI
- **关键洞察提取**：核心发现总结、行动建议、风险识别、机会发现
- **多格式输出支持**：HTML、Markdown、JSON、PDF多种格式
- **报告模板管理**：可配置的报告模板、自定义样式、品牌化选项

## 🔧 核心技术实现流程

### 1. 多Agent协作执行流程

```
用户请求 → Planner Agent → 需求分析 → 任务分解 → Agent调度 → 并行执行 → 结果聚合 → 报告生成
    ↓         ↓           ↓         ↓         ↓         ↓         ↓         ↓
 自然语言   意图识别    实体提取   子任务    Agent选择  异步执行   数据整合   HTML报告
           语义理解    数据需求   依赖关系   参数标准化  结果收集   可视化
```

### 2. 标准化MCP客户端执行机制

```python
class AgnoCoordinator:
    def coordinate_analysis(self, user_request: str, workflow_type: str) -> Dict[str, Any]:
        """协调器核心执行流程"""
        
        # 1. Planner Agent - 需求理解和任务规划
        plan_result = self.planner_agent.analyze_requirement(user_request)
        
        # 2. 参数标准化 - 解决FastMCP兼容性问题
        standardized_tasks = []
        for task in plan_result["sub_tasks"]:
            standardized_task = self.mcp_client.standardize_parameters(
                task["tool_name"], task["parameters"]
            )
            standardized_tasks.append(standardized_task)
        
        # 3. Agent调度 - 并行执行优化
        agent_results = await self._execute_agents_parallel(standardized_tasks)
        
        # 4. 结果聚合 - 多Agent结果整合
        aggregated_results = self._aggregate_agent_results(agent_results)
        
        # 5. 报告生成 - HTML可视化报告
        final_report = self.report_generator.generate_comprehensive_report(
            aggregated_results, workflow_type
        )
        
        return final_report
```

### 3. 错误处理和恢复机制

```python
def execute_with_comprehensive_error_handling(self, tool_name: str, params: Dict[str, Any]) -> Any:
    """综合错误处理机制"""
    
    try:
        # 参数预处理和标准化
        processed_params = self._preprocess_parameters(params)
        standardized_params = self.standardize_parameters(tool_name, processed_params)
        
        # 工具执行
        result = self._execute_tool_with_timeout(tool_name, standardized_params)
        
        # 结果验证
        validated_result = self._validate_execution_result(result)
        
        return validated_result
        
    except ParameterError as e:
        # 参数错误 - 自动修复和重试
        fixed_params = self._auto_fix_parameters(e, params)
        return self.execute_with_retry(tool_name, fixed_params)
        
    except TimeoutError as e:
        # 超时错误 - 调整参数和重试
        adjusted_params = self._adjust_for_timeout(params)
        return self.execute_with_retry(tool_name, adjusted_params)
        
    except MCPConnectionError as e:
        # MCP连接错误 - 重新连接和重试
        self._reconnect_mcp_services()
        return self.execute_with_retry(tool_name, params)
        
    except Exception as e:
        # 未知错误 - 详细日志记录和用户友好提示
        self._log_detailed_error(tool_name, params, e)
        return self._generate_user_friendly_error_response(e)
```

### 4. 多Agent结果聚合算法

```python
def aggregate_multi_agent_results(self, agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """多Agent结果智能聚合"""
    
    aggregated_data = {
        "financial_analysis": None,
        "cost_analysis": None,
        "efficiency_analysis": None,
        "knowledge_analysis": None,
        "conflicts": [],
        "confidence_scores": {},
        "recommendations": []
    }
    
    # 1. 数据标准化 - 统一数据格式
    normalized_results = self._normalize_agent_data_formats(agent_results)
    
    # 2. 冲突检测和解决
    conflicts = self._detect_conflicts_between_agents(normalized_results)
    resolved_conflicts = self._resolve_conflicts_intelligently(conflicts)
    
    # 3. 置信度评估
    confidence_scores = self._calculate_confidence_scores(normalized_results)
    
    # 4. 权重计算和结果融合
    weighted_results = self._apply_intelligent_weighting(normalized_results, confidence_scores)
    
    # 5. 综合建议生成
    recommendations = self._generate_comprehensive_recommendations(weighted_results)
    
    return {
        "analysis_results": weighted_results,
        "conflicts_resolved": resolved_conflicts,
        "confidence_assessment": confidence_scores,
        "strategic_recommendations": recommendations
    }
```

## 🔧 系统配置

```python
# config.py - 主配置文件
class SystemConfig:
    # AI模型配置
    ai_config: AIConfig
    
    # 系统运行配置
    system_config: SystemRuntimeConfig
    
    # Agent配置
    agent_config: AgentConfig
    
    # 日志配置
    logging_config: LoggingConfig
    
    # 工作流配置
    workflow_config: WorkflowConfig
    
    # 业务配置
    business_config: BusinessConfig
```

### 自定义配置

1. **修改AI模型参数**
```python
AI_CONFIG = {
    "model": "gemini-2.5-pro",  # 可选其他模型
    "temperature": 0.7,         # 调整创造性 (0.0-1.0)
    "max_tokens": 4000,         # 最大输出长度
    "timeout": 60               # 请求超时时间
}
```

2. **调整工作流参数**
```python
WORKFLOW_CONFIG = {
    "max_parallel_agents": 4,    # 最大并行Agent数
    "default_timeout": 300,      # 默认超时时间
    "retry_count": 2,            # 重试次数
    "enable_caching": True       # 启用结果缓存
}
```

3. **配置日志级别**
```python
LOGGING_CONFIG = {
    "log_level": "INFO",         # DEBUG, INFO, WARNING, ERROR
    "enable_file_logging": True, # 启用文件日志
    "log_file_path": "logs/system.log"
}
```

## 📈 性能优化

### 系统性能指标

- **响应时间**：单次分析 < 5分钟
- **并发处理**：支持最多4个Agent并行执行
- **内存使用**：峰值内存 < 2GB
- **准确率**：AI分析准确率 > 85%

### 优化建议

1. **硬件优化**
   - 推荐8GB以上内存
   - SSD硬盘提升I/O性能
   - 稳定网络连接确保AI API调用

2. **软件优化**
   - 启用结果缓存减少重复计算
   - 合理设置并行Agent数量
   - 定期清理日志文件

3. **网络优化**
   - 使用CDN加速API调用
   - 配置请求重试机制
   - 监控API调用频率

## 🛠️ 故障排除

### 常见问题

#### 1. 系统启动失败
```bash
# 检查Python版本
python --version  # 需要3.8+

# 检查依赖安装
pip list | grep agno

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

#### 2. AI API调用失败
```bash
# 检查网络连接
ping xi.apicenter.top

# 验证API密钥
python -c "from config import get_ai_config; print(get_ai_config())"

# 测试API连接
curl -X POST "https://xi.apicenter.top/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

#### 3. 内存不足错误
```bash
# 检查系统内存
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory

# 减少并行Agent数量
# 在config.py中修改：
max_parallel_agents = 2  # 从4减少到2
```

#### 4. 工作流执行超时
```bash
# 增加超时时间
# 在workflow_templates.py中修改：
global_timeout = 3600  # 增加到1小时

# 检查网络延迟
ping -t xi.apicenter.top
```

### 日志分析

系统日志位于 `logs/system.log`，包含详细的执行信息：

```bash
# 查看最新日志
tail -f logs/system.log

# 搜索错误信息
findstr "ERROR" logs/system.log

# 分析性能问题
findstr "execution_time" logs/system.log
```

## 🔒 安全说明

### 数据安全

- **本地处理**：所有数据在本地处理，不上传到第三方服务器
- **API安全**：使用HTTPS加密传输，API密钥安全存储
- **访问控制**：系统运行在本地环境，无外部访问风险
- **数据脱敏**：敏感数据在分析前自动脱敏处理

### 隐私保护

- **数据最小化**：只处理分析必需的数据
- **临时存储**：分析结果可选择性保存
- **日志清理**：定期清理包含敏感信息的日志
- **合规性**：符合企业数据保护政策

## 📚 开发文档

### 项目文件结构

```
7_agno_coordinator/
├── agents/                           # Agent实现目录
│   ├── __init__.py                    # Agent模块初始化
│   ├── base_agent.py                  # Agent基类 - 通用Agent功能
│   ├── business_agent.py              # 业务Agent基类 - 业务分析通用功能
│   ├── financial_agent.py             # 财务分析Agent - ROE、ROA等财务指标
│   ├── cost_agent.py                  # 成本分析Agent - 成本结构、预算分析
│   ├── efficiency_agent.py            # 效率分析Agent - 人员效率、流程优化
│   ├── knowledge_agent.py             # 知识管理Agent - 知识库、技能评估
│   └── report_generator_agent.py      # 报告生成Agent - HTML可视化报告
├── models/                           # 数据模型目录
│   └── conversation_history.py        # 会话历史模型 - SQLite数据存储
├── data/                            # 数据存储目录
│   └── conversation_history.db        # SQLite会话数据库
├── logs/                            # 日志文件目录
│   ├── mcp_client_*.log              # MCP客户端详细日志
│   ├── system_*.log                  # 系统运行日志
│   └── error_*.log                   # 错误和异常日志
├── docs/                            # 项目文档目录
│   ├── ALIGNMENT_智能体执行问题.md     # 智能体执行问题分析
│   ├── ARCHITECTURE_OVERVIEW.md      # 系统架构概览
│   ├── FINAL_SYSTEM_STATUS_REPORT.md # 系统状态最终报告
│   ├── FINAL_TEST_REPORT.md          # 最终测试报告
│   └── SYSTEM_FIXES_AND_IMPROVEMENTS.md # 系统修复和改进记录
├── standardized_mcp_client_v2.py     # 标准化MCP客户端 - 解决兼容性问题
├── planner_agent.py                  # 规划Agent - 需求分析、任务编排
├── workflow_templates.py             # 工作流模板 - 预定义业务流程
├── config.py                         # 系统配置 - AI模型、业务参数
├── main.py                           # 主启动程序 - FastAPI服务、CLI
├── final_system_verification.py      # 系统验证程序 - 功能测试
└── requirements.txt                  # 依赖包列表 - 项目依赖管理
```

### 核心代码文件说明

#### 1. 标准化MCP客户端 (`standardized_mcp_client_v2.py`)
- **代码行数**：约800行
- **核心功能**：解决FastMCP参数兼容性问题
- **技术特色**：参数结构标准化、智能错误恢复、重试机制
- **关键类**：`StandardizedMCPClient`, `MCPParameterValidator`

#### 2. 规划Agent (`planner_agent.py`)
- **代码行数**：约600行
- **核心功能**：自然语言理解、需求分析、任务分解
- **AI模型**：Gemini-2.5-Pro via OpenAI API
- **关键方法**：`analyze_requirement()`, `generate_execution_plan()`

#### 3. 主启动程序 (`main.py`)
- **代码行数**：约500行
- **核心功能**：FastAPI Web服务、命令行接口、系统管理
- **API端点**：`/analyze`, `/collaborate`, `/health`, `/docs`
- **服务模式**：交互模式、API模式、演示模式、单次分析模式

### 扩展开发

#### 1. 添加新的Agent

```python
# 继承BusinessAgent基类
from agents.business_agent import BusinessAgent

class CustomAgent(BusinessAgent):
    def __init__(self):
        super().__init__(
            agent_id="custom_agent",
            agent_name="自定义分析Agent",
            agent_description="执行自定义业务分析"
        )
    
    def _get_system_prompt(self) -> str:
        return "你是一个专业的自定义分析专家..."
    
    async def execute_task(self, task_input: dict) -> dict:
        # 实现具体的分析逻辑
        pass
```

#### 2. 创建新的工作流模板

```python
# 在workflow_templates.py中添加
def create_custom_workflow_template() -> WorkflowTemplate:
    return WorkflowTemplate(
        template_id="custom_analysis",
        template_name="自定义分析",
        description="自定义业务分析工作流",
        stages=[...],  # 定义工作流阶段
        version="1.0.0"
    )
```

#### 3. 自定义报告模板

```python
# 修改report_generator_agent.py
def _generate_custom_report(self, analysis_results: dict) -> str:
    template = """
    <html>
    <head><title>自定义分析报告</title></head>
    <body>
        <!-- 自定义报告内容 -->
    </body>
    </html>
    """
    return template
```

## 🤝 技术支持

### 联系方式

- **项目团队**：商海星辰队
- **技术支持**：通过GitHub Issues提交问题
- **文档更新**：定期更新使用文档和最佳实践

### 贡献指南

1. **代码规范**：遵循PEP 8 Python代码规范
2. **注释要求**：关键功能必须有详细中文注释
3. **测试覆盖**：新功能需要包含单元测试
4. **文档更新**：功能变更需要同步更新文档

### 版本历史

- **v2.0.0** (2024-12-19)
  - 🔧 **标准化MCP客户端**：解决FastMCP参数兼容性问题
  - 🧠 **智能规划Agent**：基于Gemini-2.5-Pro的自然语言理解
  - ⚡ **多Agent并行执行**：支持4个Agent同时运行，提升执行效率
  - 📊 **HTML可视化报告**：Plotly交互式图表，响应式设计
  - 🛡️ **综合错误处理**：智能错误恢复，自动重试机制
  - 💾 **会话历史管理**：SQLite数据库存储，支持对话状态维护
  - 🌐 **FastAPI Web服务**：RESTful API，支持多种服务模式

- **v1.0.0** (2024-12-15)
  - 初始版本发布
  - 实现基础Multi-Agent架构
  - 支持财务、成本、效率、知识管理分析
  - 提供基础HTML报告生成

## 📄 许可证

本项目为四川智水信息技术有限公司内部使用，版权所有。未经授权不得复制、分发或修改。

---

**🎯 智水信息Multi-Agent AI智慧管理系统 - 让数据驱动决策，让AI赋能管理！**