#!/usr/bin/env python3
"""
智水信息Multi-Agent智能分析系统 - Planner Agent
基于Agno框架的任务编排智能体

功能职责：
1. 解析用户输入，识别分析需求
2. 检查数据完整性，生成补充询问  
3. 制定Agent执行计划和依赖关系
4. 管理人机交互流程

Author: 商海星辰队
Version: 1.0.0
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from openai import OpenAI

# ================================
# 1. 配置和初始化
# ================================

# AI模型配置
from config import get_ai_config
AI_CONFIG = get_ai_config()

# 初始化OpenAI客户端
client = OpenAI(
    api_key=AI_CONFIG.get("api_key", ""),
    base_url=AI_CONFIG.get("api_base", "")
)

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PlannerAgent")

# ================================
# 2. 数据结构定义
# ================================

@dataclass
class UserInput:
    """用户输入数据结构"""
    raw_text: str
    uploaded_files: List[str] = None
    data_content: Dict[str, Any] = None
    user_preferences: Dict[str, Any] = None

@dataclass
class AnalysisIntent:
    """分析意图识别结果"""
    intent_type: str  # financial, cost, efficiency, knowledge, comprehensive
    confidence: float
    keywords: List[str]
    required_agents: List[str]
    optional_agents: List[str]

@dataclass
class DataValidation:
    """数据完整性检查结果"""
    is_complete: bool
    missing_required: List[str]
    missing_optional: List[str]
    data_quality_score: float
    suggestions: List[str]

@dataclass
class ExecutionPlan:
    """执行计划"""
    workflow_type: str
    agent_sequence: List[Dict[str, Any]]
    estimated_duration: int  # 分钟
    parallel_stages: List[List[str]]
    dependencies: Dict[str, List[str]]

# ================================
# 3. Planner Agent核心类
# ================================

class PlannerAgent:
    """智水信息Multi-Agent系统任务编排智能体"""
    
    def __init__(self):
        """初始化Planner Agent"""
        self.agent_name = "任务规划智能体"
        self.system_prompt = self._build_system_prompt()
        self.mcp_services = self._load_mcp_services_config()
        self.workflow_templates = self._load_workflow_templates()
        
        logger.info("PlannerAgent初始化完成")

    def _build_system_prompt(self) -> str:
        """构建完整的系统提示词"""
        return """你是智水信息Multi-Agent智能分析系统的核心任务编排智能体（Planner Agent）。

## 🎯 核心职责定位
作为水电企业智能分析系统的"大脑"，你负责统筹协调四个专业分析智能体，为用户提供全面、准确、可操作的业务分析服务。

## 🏢 业务背景理解
智水信息技术有限公司专注于电力、水利行业的信息化解决方案。你需要理解以下业务场景：
- **水电企业运营管理**：发电效率、设备维护、成本控制、人员管理
- **项目投资决策**：新建水电站、技改项目、设备更新的财务分析
- **运营效率提升**：员工绩效评估、流程优化、数字化转型
- **知识管理应用**：技术规范查询、最佳实践分享、故障处理经验

## 🤖 可调用的专业智能体团队

### 1. Financial Analyst (财务分析专家)
**调用服务**: financial_mcp (端口8001)
**核心能力**:
- `predict_cash_flow`: 基于改进灰色马尔科夫模型的现金流预测，支持3-12期预测
- `financial_qa_assistant`: 智能财务问答，涵盖电力、水利、IT行业专业知识
- `calculate_IRR_metrics`: IRR内部收益率和NPV净现值计算，支持项目投资评估
- `monitor_budget_execution`: SFA随机前沿分析的预算执行效率监控

**适用场景**: 财务规划、投资决策、成本分析、预算监控、现金流管理

### 2. Cost Prediction Analyst (成本预测专家)  
**调用服务**: cost_prediction_mcp (端口8002)
**核心能力**:
- `predict_hydropower_cost`: 智慧水电成本预测，支持常规大坝/抽水蓄能/径流式项目
- `assess_investment_risk`: 智能风险评估，基于AHP层次分析法的多维度风险分析
- `generate_analysis_data`: 成本分析数据生成器，整合成本预测和风险评估结果

**适用场景**: 项目成本预测、投资风险评估、工程造价分析、决策支持

### 3. Knowledge Manager (知识管理专家)
**调用服务**: knowledge_mcp (端口8003)  
**核心能力**:
- `search_knowledge`: 基于FAISS向量搜索的知识检索，支持电力水利行业专业文档
- `import_document`: 智能文档导入，支持PDF/Word/Excel等格式
- `manage_documents`: 文档生命周期管理，支持分类、统计、删除等操作

**适用场景**: 技术规范查询、操作手册检索、故障案例分析、最佳实践分享

### 4. Efficiency Evaluator (效能评估专家)
**调用服务**: zhishui_efficiency_mcp (端口8004)
**核心能力**:
- `evaluate_employee_efficiency`: 基于改进型平衡计分卡的员工效能评分，四维度智能评估
- `generate_efficiency_report`: 多层级人员效能分析报告，支持个人/团队/部门/公司级别

**适用场景**: 员工绩效评估、团队效能分析、人力资源优化、管理决策支持

## 🧠 智能任务编排策略

### 任务识别与分类
1. **关键词识别**: 从用户输入中提取业务关键词
   - 财务类: 现金流、投资、成本、预算、IRR、NPV、财务分析
   - 成本类: 工程造价、项目成本、风险评估、投资预测
   - 效能类: 员工评估、绩效管理、团队分析、效率提升
   - 知识类: 技术规范、操作手册、故障处理、最佳实践

2. **数据类型识别**: 分析上传数据的结构和内容
   - 财务数据: 现金流记录、财务报表、预算数据
   - 项目数据: 装机容量、建设周期、技术参数
   - 人员数据: 员工信息、绩效指标、评估数据
   - 文档数据: PDF/Word文档、技术手册、规范标准

3. **业务场景判断**: 确定用户的核心业务需求
   - 投资决策: 需要财务分析+成本预测的组合分析
   - 运营优化: 需要效能评估+知识管理的协同分析  
   - 项目评估: 需要成本预测+财务分析+风险评估
   - 问题咨询: 主要依靠知识管理+专业问答

### 数据完整性智能检查
根据预期分析类型，检查必需和可选数据字段：

**财务分析必需数据**:
- 现金流预测: 历史现金流数据(至少3期)
- IRR计算: 项目现金流序列、初始投资
- 预算监控: 项目收入、各项成本数据

**成本预测必需数据**:
- 装机容量(MW)、项目类型、建设周期
- 可选: 经济指标、地理位置、技术参数

**效能评估必需数据**:
- 员工基础信息、岗位类型
- 四维度评估指标: 经济价值、客户服务、内部流程、学习成长

**知识检索必需数据**:
- 查询关键词、检索范围
- 可选: 文档类别、检索数量限制

### 工作流编排模式
1. **全面分析模式**: Planner → [Financial + Cost + Knowledge + Efficiency] → Report
2. **财务专项模式**: Planner → [Financial + Cost] → Report  
3. **运营效率模式**: Planner → [Efficiency + Knowledge] → Report
4. **项目评估模式**: Planner → [Cost + Financial + Knowledge] → Report
5. **智能问答模式**: Planner → [Knowledge] → 直接回答

## 💬 人机交互管理原则

### 启动确认策略
- 明确告知用户检测到的数据类型和推荐分析范围
- 提供可选择的分析维度，支持用户自定义
- 估算分析时间和预期输出内容

### 数据补充引导
- 识别关键缺失数据，标注为"必需"或"可选"
- 解释数据缺失对分析结果的影响程度
- 提供数据格式示例和录入指导

### 进度反馈机制
- 实时显示各Agent的执行状态和预计完成时间
- 支持部分成功策略，即使个别Agent失败也能生成报告
- 提供错误处理选项：重试、跳过、或手动补充数据

### 结果确认与优化
- 汇总分析结果前询问用户是否需要深度分析特定维度
- 支持报告格式选择：简要总结、详细分析、交互式报告
- 提供后续分析建议和数据补充方向

## 🔄 执行状态管理

你需要全程跟踪以下执行状态：
1. **INIT**: 初始接收用户输入
2. **PLANNING**: 意图识别和执行计划制定
3. **VALIDATION**: 数据完整性检查和用户确认
4. **EXECUTION**: Agent并行/顺序执行
5. **AGGREGATION**: 结果汇总和分析
6. **REPORTING**: 最终报告生成
7. **COMPLETE**: 任务完成和后续建议

## 📋 输出格式要求

### 任务编排阶段输出
```json
{
  "intent_analysis": {
    "detected_intent": "项目投资决策分析",
    "confidence": 0.92,
    "key_keywords": ["投资", "成本", "风险", "IRR"],
    "recommended_agents": ["financial_analyst", "cost_analyst"],
    "optional_agents": ["knowledge_manager"]
  },
  "data_validation": {
    "status": "需要补充数据",
    "missing_required": ["项目建设周期"],
    "missing_optional": ["历史成本数据"],
    "completion_rate": 0.75
  },
  "execution_plan": {
    "workflow_type": "项目评估模式",
    "estimated_duration": 8,
    "execution_stages": [
      {"stage": "成本预测", "agents": ["cost_analyst"], "duration": 3},
      {"stage": "财务分析", "agents": ["financial_analyst"], "duration": 4},
      {"stage": "结果整合", "agents": ["report_generator"], "duration": 1}
    ]
  },
  "user_confirmation": {
    "question": "检测到您希望进行项目投资分析，建议包含成本预测和财务评估。是否需要同时查询相关技术规范？",
    "options": ["确认执行", "添加知识检索", "修改分析范围"]
  }
}
```

## ⚠️ 重要约束条件

1. **绝不编造数据**: 任何分析都必须基于用户提供的真实数据，不得添加虚假信息
2. **透明化决策**: 所有Agent选择和执行计划都要向用户说明原因
3. **错误恢复**: 个别Agent失败时要有降级策略，确保用户能获得有价值的结果
4. **资源优化**: 避免不必要的重复分析，优先使用高效的Agent组合
5. **用户导向**: 始终以解决用户实际业务问题为目标，而非展示技术复杂性

你现在开始接收用户输入，运用以上专业知识和策略，为智水信息的客户提供优质的智能分析编排服务。"""

    def _load_mcp_services_config(self) -> Dict[str, Any]:
        """加载MCP服务配置信息"""
        return {
            "financial": {
                "name": "财务分析服务",
                "port": 8001,
                "capabilities": ["predict_cash_flow", "financial_qa_assistant", "calculate_IRR_metrics", "monitor_budget_execution"],
                "required_fields": {
                    "predict_cash_flow": ["historical_data"],
                    "calculate_IRR_metrics": ["cash_flows", "initial_investment"],
                    "monitor_budget_execution": ["project_revenue", "costs_data"]
                }
            },
            "cost_prediction": {
                "name": "成本预测服务",
                "port": 8002,
                "capabilities": ["predict_hydropower_cost", "assess_investment_risk", "generate_analysis_data"],
                "required_fields": {
                    "predict_hydropower_cost": ["capacity_mw", "project_type", "construction_period"],
                    "assess_investment_risk": ["project_params", "risk_factors"]
                }
            },
            "knowledge": {
                "name": "知识管理服务", 
                "port": 8003,
                "capabilities": ["search_knowledge", "import_document", "manage_documents"],
                "required_fields": {
                    "search_knowledge": ["query"]
                }
            },
            "efficiency": {
                "name": "效能评估服务",
                "port": 8004,
                "capabilities": ["evaluate_employee_efficiency", "generate_efficiency_report"],
                "required_fields": {
                    "evaluate_employee_efficiency": ["employee_data", "metrics_data", "position_type"]
                }
            }
        }

    def _load_workflow_templates(self) -> Dict[str, Any]:
        """加载工作流模板配置"""
        return {
            "comprehensive_analysis": {
                "name": "全面分析模式",
                "description": "适用于企业全面诊断和重大决策分析",
                "agents": ["financial_analyst", "cost_analyst", "knowledge_manager", "efficiency_evaluator"],
                "execution_type": "parallel_then_report",
                "estimated_duration": 15
            },
            "financial_focus": {
                "name": "财务专项模式", 
                "description": "适用于投资决策、成本控制、财务规划",
                "agents": ["financial_analyst", "cost_analyst"],
                "execution_type": "parallel_then_report",
                "estimated_duration": 8
            },
            "operational_efficiency": {
                "name": "运营效率模式",
                "description": "适用于人员管理、流程优化、最佳实践",
                "agents": ["efficiency_evaluator", "knowledge_manager"],
                "execution_type": "parallel_then_report", 
                "estimated_duration": 10
            },
            "project_evaluation": {
                "name": "项目评估模式",
                "description": "适用于项目可行性、风险评估、技术选型",
                "agents": ["cost_analyst", "financial_analyst", "knowledge_manager"],
                "execution_type": "sequential_then_report",
                "estimated_duration": 12
            },
            "smart_qa": {
                "name": "智能问答模式",
                "description": "适用于技术咨询、标准查询、经验分享", 
                "agents": ["knowledge_manager"],
                "execution_type": "direct_response",
                "estimated_duration": 3
            }
        }

    def analyze_user_input(self, user_input: UserInput) -> AnalysisIntent:
        """分析用户输入，识别分析意图"""
        try:
            # 使用AI进行智能意图识别
            prompt = f"""
            分析以下用户输入，识别其业务分析意图：
            
            用户输入文本: {user_input.raw_text}
            上传文件: {user_input.uploaded_files if user_input.uploaded_files else "无"}
            
            请分析并返回JSON格式结果，包含：
            1. intent_type: 主要意图类型 (financial/cost/efficiency/knowledge/comprehensive)
            2. confidence: 置信度 (0-1)
            3. keywords: 提取的关键词列表
            4. required_agents: 必需的智能体列表
            5. optional_agents: 可选的智能体列表
            
            基于以下业务场景判断：
            - financial: 现金流、投资、IRR、NPV、财务分析、预算
            - cost: 成本预测、工程造价、项目投资、风险评估
            - efficiency: 员工评估、绩效管理、团队分析、效率提升
            - knowledge: 技术咨询、规范查询、故障处理、最佳实践
            - comprehensive: 需要多维度综合分析
            """
            
            # 创建OpenAI客户端
            client = OpenAI(
                api_key=AI_CONFIG["api_key"],
                base_url=AI_CONFIG["api_base"]
            )
            
            response = client.chat.completions.create(
                model=AI_CONFIG["model"],
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=AI_CONFIG["temperature"]
            )
            
            # 检查响应有效性
            if response is None:
                logger.error("LLM调用返回None响应")
                raise Exception("API响应为空")
            
            if not hasattr(response, 'choices') or not response.choices:
                logger.error("LLM调用响应缺少choices字段")
                raise Exception("API响应格式异常")
            
            if not hasattr(response.choices[0], 'message') or not response.choices[0].message:
                logger.error("LLM调用响应choices[0]缺少message字段")
                raise Exception("API响应格式异常")
            
            # 解析AI响应
            ai_response = response.choices[0].message.content
            
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                result_data = json.loads(json_match.group())
                
                return AnalysisIntent(
                    intent_type=result_data.get("intent_type", "comprehensive"),
                    confidence=result_data.get("confidence", 0.8),
                    keywords=result_data.get("keywords", []),
                    required_agents=result_data.get("required_agents", []),
                    optional_agents=result_data.get("optional_agents", [])
                )
            else:
                # 如果无法解析JSON，使用规则基础的分析
                return self._rule_based_intent_analysis(user_input)
                
        except Exception as e:
            logger.error(f"AI意图识别失败: {e}")
            # 降级为规则基础分析
            return self._rule_based_intent_analysis(user_input)

    def _rule_based_intent_analysis(self, user_input: UserInput) -> AnalysisIntent:
        """基于LLM的意图识别 (备用方案)"""
        try:
            # 使用LLM进行意图分析
            prompt = f"""
            请分析以下用户输入的意图，并返回JSON格式的结果：
            
            用户输入：{user_input.raw_text}
            
            请识别用户的主要分析需求，从以下类型中选择：
            - financial: 财务分析（现金流、投资、IRR、NPV等）
            - cost: 成本预测（工程造价、项目成本、风险评估等）
            - efficiency: 效能评估（员工绩效、团队分析、人员管理等）
            - knowledge: 知识查询（技术规范、文档检索、最佳实践等）
            - comprehensive: 综合分析（多个方面的分析需求）
            
            返回格式：
            {{
                "intent_type": "分析类型",
                "confidence": 置信度(0-1),
                "keywords": ["关键词列表"],
                "required_agents": ["必需的智能体列表"],
                "optional_agents": ["可选的智能体列表"]
            }}
            """
            
            # 创建OpenAI客户端
            client = OpenAI(
                api_key=AI_CONFIG["api_key"],
                base_url=AI_CONFIG["api_base"]
            )
            
            response = client.chat.completions.create(
                model=AI_CONFIG["model"],
                messages=[
                    {"role": "system", "content": "你是智水信息的任务编排专家，专门分析用户的业务分析需求。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=AI_CONFIG["temperature"]
            )
            
            # 检查响应有效性
            if response is None:
                logger.error("LLM调用返回None响应")
                raise Exception("API返回空响应")
            
            if not hasattr(response, 'choices') or not response.choices:
                logger.error("LLM调用响应缺少choices字段")
                raise Exception("API响应格式异常")
            
            if not response.choices[0].message:
                logger.error("LLM调用响应choices[0]缺少message")
                raise Exception("API响应消息内容为空")
            
            result_text = response.choices[0].message.content.strip()
            
            # 尝试解析JSON结果
            if result_text.startswith('```json'):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith('```'):
                result_text = result_text[3:-3].strip()
            
            result_data = json.loads(result_text)
            
            return AnalysisIntent(
                intent_type=result_data.get("intent_type", "comprehensive"),
                confidence=result_data.get("confidence", 0.5),
                keywords=result_data.get("keywords", []),
                required_agents=result_data.get("required_agents", ["financial_analyst"]),
                optional_agents=result_data.get("optional_agents", [])
            )
            
        except Exception as e:
            logger.error(f"LLM意图分析失败: {e}")
            # 最基本的降级方案
            return AnalysisIntent(
                intent_type="comprehensive",
                confidence=0.3,
                keywords=["综合分析"],
                required_agents=["financial_analyst", "cost_analyst"],
                optional_agents=[]
            )

    def validate_data_completeness(self, user_input: UserInput, analysis_intent: AnalysisIntent) -> DataValidation:
        """检查数据完整性"""
        missing_required = []
        missing_optional = []
        suggestions = []
        
        # 根据意图检查必需数据
        if "financial_analyst" in analysis_intent.required_agents:
            if not self._has_financial_data(user_input):
                missing_required.extend(["历史财务数据", "现金流记录"])
                suggestions.append("财务分析需要历史现金流数据，建议提供至少3期的数据")
        
        if "cost_analyst" in analysis_intent.required_agents:
            if not self._has_project_data(user_input):
                missing_required.extend(["项目基本参数", "装机容量", "建设周期"])
                suggestions.append("成本预测需要项目基本信息，如装机容量(MW)和建设周期")
        
        if "efficiency_evaluator" in analysis_intent.required_agents:
            if not self._has_employee_data(user_input):
                missing_required.extend(["员工基础信息", "绩效指标数据"])
                suggestions.append("效能评估需要员工信息和各维度绩效数据")
        
        # 计算完整性得分
        total_checks = len(analysis_intent.required_agents) * 2  # 每个agent假设需要2项数据
        missing_count = len(missing_required)
        completion_rate = max(0, (total_checks - missing_count) / total_checks) if total_checks > 0 else 1.0
        
        return DataValidation(
            is_complete=len(missing_required) == 0,
            missing_required=missing_required,
            missing_optional=missing_optional,
            data_quality_score=completion_rate,
            suggestions=suggestions
        )

    def _has_financial_data(self, user_input: UserInput) -> bool:
        """检查是否包含财务数据"""
        if user_input.data_content:
            # 检查是否有数值数据或财务关键字
            text = str(user_input.data_content).lower()
            return any(keyword in text for keyword in ["现金流", "收入", "成本", "利润", "投资"])
        return False

    def _has_project_data(self, user_input: UserInput) -> bool:
        """检查是否包含项目数据"""
        if user_input.data_content:
            text = str(user_input.data_content).lower()
            return any(keyword in text for keyword in ["mw", "装机", "容量", "建设", "工期"])
        return False

    def _has_employee_data(self, user_input: UserInput) -> bool:
        """检查是否包含员工数据"""
        if user_input.data_content:
            text = str(user_input.data_content).lower()
            return any(keyword in text for keyword in ["员工", "姓名", "部门", "岗位", "绩效"])
        return False

    def create_execution_plan(self, analysis_intent: AnalysisIntent, data_validation: DataValidation) -> ExecutionPlan:
        """制定执行计划"""
        # 根据意图选择工作流模板
        if analysis_intent.intent_type == "comprehensive":
            template = self.workflow_templates["comprehensive_analysis"]
        elif analysis_intent.intent_type == "financial":
            template = self.workflow_templates["financial_focus"]
        elif analysis_intent.intent_type == "efficiency":
            template = self.workflow_templates["operational_efficiency"]
        elif analysis_intent.intent_type == "knowledge":
            template = self.workflow_templates["smart_qa"]
        else:
            template = self.workflow_templates["project_evaluation"]
        
        # 构建agent序列
        agent_sequence = []
        for agent_name in template["agents"]:
            agent_info = {
                "agent_name": agent_name,
                "service": self._get_service_for_agent(agent_name),
                "estimated_duration": 3,  # 默认3分钟
                "priority": "high" if agent_name in analysis_intent.required_agents else "medium"
            }
            agent_sequence.append(agent_info)
        
        # 设置并行执行组
        if template["execution_type"] == "parallel_then_report":
            parallel_stages = [template["agents"]]
        else:
            parallel_stages = [[agent] for agent in template["agents"]]
        
        return ExecutionPlan(
            workflow_type=template["name"],
            agent_sequence=agent_sequence,
            estimated_duration=template["estimated_duration"],
            parallel_stages=parallel_stages,
            dependencies={}
        )

    def _get_service_for_agent(self, agent_name: str) -> str:
        """获取agent对应的服务名称"""
        mapping = {
            "financial_analyst": "financial",
            "cost_analyst": "cost_prediction", 
            "knowledge_manager": "knowledge",
            "efficiency_evaluator": "efficiency"
        }
        return mapping.get(agent_name, "unknown")

    def generate_user_confirmation(self, intent: AnalysisIntent, validation: DataValidation, plan: ExecutionPlan) -> Dict[str, Any]:
        """生成用户确认信息"""
        return {
            "analysis_summary": {
                "detected_intent": intent.intent_type,
                "confidence": f"{intent.confidence:.2f}",
                "workflow_type": plan.workflow_type,
                "estimated_duration": f"{plan.estimated_duration}分钟"
            },
            "data_status": {
                "completion_rate": f"{validation.data_quality_score:.1%}",
                "missing_required": validation.missing_required,
                "suggestions": validation.suggestions
            },
            "execution_preview": {
                "agents_to_activate": [agent["agent_name"] for agent in plan.agent_sequence],
                "parallel_execution": len(plan.parallel_stages) > 0 and len(plan.parallel_stages[0]) > 1
            },
            "user_options": [
                "确认开始分析",
                "修改分析范围", 
                "补充必需数据",
                "查看详细计划"
            ]
        }

    def process_user_input(self, raw_input: str, uploaded_files: List[str] = None, data_content: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理用户输入的主函数"""
        try:
            # 1. 构建用户输入对象
            user_input = UserInput(
                raw_text=raw_input,
                uploaded_files=uploaded_files or [],
                data_content=data_content or {}
            )
            
            # 2. 分析意图
            logger.info("开始分析用户意图...")
            analysis_intent = self.analyze_user_input(user_input)
            
            # 3. 验证数据完整性
            logger.info("检查数据完整性...")
            data_validation = self.validate_data_completeness(user_input, analysis_intent)
            
            # 4. 制定执行计划
            logger.info("制定执行计划...")
            execution_plan = self.create_execution_plan(analysis_intent, data_validation)
            
            # 5. 生成用户确认信息
            confirmation = self.generate_user_confirmation(analysis_intent, data_validation, execution_plan)
            
            return {
                "status": "planning_complete",
                "intent_analysis": {
                    "intent_type": analysis_intent.intent_type,
                    "confidence": analysis_intent.confidence,
                    "keywords": analysis_intent.keywords,
                    "required_agents": analysis_intent.required_agents
                },
                "data_validation": {
                    "is_complete": data_validation.is_complete,
                    "missing_required": data_validation.missing_required,
                    "quality_score": data_validation.data_quality_score,
                    "suggestions": data_validation.suggestions
                },
                "execution_plan": {
                    "workflow_type": execution_plan.workflow_type,
                    "agent_sequence": execution_plan.agent_sequence,
                    "estimated_duration": execution_plan.estimated_duration,
                    "parallel_stages": execution_plan.parallel_stages
                },
                "user_confirmation": confirmation,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"处理用户输入时发生错误: {e}")
            return {
                "status": "error",
                "message": f"处理失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def execute_task(self, task) -> Dict[str, Any]:
        """执行规划任务
        
        Args:
            task: AgentTask对象，包含任务信息
            
        Returns:
            Dict: 执行结果，包含分析意图、数据验证和执行计划
        """
        import time
        start_time = time.time()
        
        try:
            # 从任务数据中提取输入信息
            input_data = task.input_data if hasattr(task, 'input_data') else task
            
            # 提取用户输入文本
            user_question = input_data.get('question', '')
            uploaded_files = input_data.get('uploaded_files', [])
            data_content = input_data.get('data_content', {})
            
            # 构建用户输入对象
            user_input = UserInput(
                raw_text=user_question,
                uploaded_files=uploaded_files,
                data_content=data_content
            )
            
            # 执行完整的规划流程
            result = self.process_user_input(
                raw_input=user_question,
                uploaded_files=uploaded_files,
                data_content=data_content
            )
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 构建标准化返回结果
            return {
                "status": "success",
                "agent_id": "planner_agent",
                "task_id": getattr(task, 'task_id', f"planner_task_{int(time.time())}"),
                "result_data": result,
                "confidence_score": result.get('confidence', 0.8),
                "recommendations": result.get('recommendations', []),
                "processing_time": processing_time,
                "analysis_intent": result.get('analysis_intent', {}),
                "execution_plan": result.get('execution_plan', {}),
                "data_validation": result.get('data_validation', {})
            }
            
        except Exception as e:
            error_msg = f"PlannerAgent执行失败: {str(e)}"
            logger.error(error_msg)
            
            return {
                "status": "error",
                "agent_id": "planner_agent", 
                "task_id": getattr(task, 'task_id', f"planner_task_{int(time.time())}"),
                "result_data": {},
                "confidence_score": 0.0,
                "recommendations": [],
                "error_message": error_msg,
                "processing_time": time.time() - start_time
             }

# ================================
# 4. 主要对外接口
# ================================

def create_planner_agent():
    """创建Planner Agent实例"""
    return PlannerAgent()

__all__ = ['PlannerAgent', 'UserInput', 'AnalysisIntent', 'DataValidation', 'ExecutionPlan', 'create_planner_agent']