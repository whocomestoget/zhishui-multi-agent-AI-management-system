#!/usr/bin/env python3
"""
智水信息Multi-Agent系统 - 工作流模板配置
定义各种分析场景的工作流模板

功能职责：
1. 定义标准化工作流模板
2. 配置Agent执行顺序和依赖关系
3. 设置工作流参数和约束条件
4. 提供工作流模板管理接口
5. 支持动态工作流定制

Author: 商海星辰队
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

# ================================
# 1. 工作流基础定义
# ================================

class WorkflowStage(Enum):
    """工作流阶段枚举"""
    PLANNING = "planning"                    # 规划阶段
    BUSINESS_ANALYSIS = "business_analysis"  # 业务分析阶段
    REPORT_GENERATION = "report_generation"  # 报告生成阶段
    VALIDATION = "validation"                # 验证阶段

class AgentExecutionMode(Enum):
    """Agent执行模式"""
    SEQUENTIAL = "sequential"    # 顺序执行
    PARALLEL = "parallel"        # 并行执行
    CONDITIONAL = "conditional"  # 条件执行

@dataclass
class AgentTask:
    """Agent任务定义"""
    agent_id: str                    # Agent标识
    task_description: str            # 任务描述
    priority: int = 1                # 优先级 (1-10)
    timeout_seconds: int = 600       # 超时时间
    retry_count: int = 2             # 重试次数
    required_inputs: List[str] = None    # 必需输入
    optional_inputs: List[str] = None    # 可选输入
    output_keys: List[str] = None        # 输出键名
    dependencies: List[str] = None       # 依赖的其他任务
    conditions: Dict[str, Any] = None    # 执行条件
    
    def __post_init__(self):
        if self.required_inputs is None:
            self.required_inputs = []
        if self.optional_inputs is None:
            self.optional_inputs = []
        if self.output_keys is None:
            self.output_keys = []
        if self.dependencies is None:
            self.dependencies = []
        if self.conditions is None:
            self.conditions = {}

@dataclass
class WorkflowStageConfig:
    """工作流阶段配置"""
    stage_id: str                        # 阶段标识
    stage_name: str                      # 阶段名称
    description: str                     # 阶段描述
    execution_mode: AgentExecutionMode   # 执行模式
    agent_tasks: List[AgentTask]         # Agent任务列表
    stage_timeout: int = 1200            # 阶段超时时间
    min_success_count: int = 1           # 最少成功任务数
    continue_on_failure: bool = True     # 失败时是否继续
    output_aggregation: str = "merge"    # 输出聚合方式

@dataclass
class WorkflowTemplate:
    """工作流模板定义"""
    template_id: str                     # 模板标识
    template_name: str                   # 模板名称
    description: str                     # 模板描述
    version: str                         # 版本号
    stages: List[WorkflowStageConfig]    # 工作流阶段
    global_timeout: int = 3600           # 全局超时时间
    max_parallel_agents: int = 5         # 最大并行Agent数
    error_handling: str = "graceful"     # 错误处理策略
    metadata: Dict[str, Any] = None      # 元数据
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

# ================================
# 2. 预定义工作流模板
# ================================

def create_comprehensive_analysis_template() -> WorkflowTemplate:
    """创建综合分析工作流模板
    
    适用场景：
    - 全面的企业管理分析
    - 多维度业务洞察
    - 综合决策支持
    """
    
    # 规划阶段
    planning_stage = WorkflowStageConfig(
        stage_id="planning",
        stage_name="需求分析与规划",
        description="分析用户需求，制定分析计划和策略",
        execution_mode=AgentExecutionMode.SEQUENTIAL,
        agent_tasks=[
            AgentTask(
                agent_id="planner_agent",
                task_description="分析用户输入，识别分析意图，制定执行计划",
                priority=10,
                timeout_seconds=120,
                required_inputs=["user_input", "uploaded_files", "data_content"],
                output_keys=["analysis_intent", "execution_plan", "data_validation"]
            )
        ],
        stage_timeout=180,
        min_success_count=1,
        continue_on_failure=False
    )
    
    # 业务分析阶段
    business_analysis_stage = WorkflowStageConfig(
        stage_id="business_analysis",
        stage_name="多维度业务分析",
        description="并行执行财务、成本、效率、知识管理等专业分析",
        execution_mode=AgentExecutionMode.PARALLEL,
        agent_tasks=[
            AgentTask(
                agent_id="financial_agent",
                task_description="执行财务分析，包括盈利能力、偿债能力、运营效率等",
                priority=9,
                timeout_seconds=300,
                required_inputs=["analysis_intent", "execution_plan"],
                output_keys=["financial_analysis", "financial_insights", "financial_recommendations"]
            ),
            AgentTask(
                agent_id="cost_agent",
                task_description="执行成本分析，包括成本结构、成本控制、成本预测等",
                priority=8,
                timeout_seconds=300,
                required_inputs=["analysis_intent", "execution_plan"],
                output_keys=["cost_analysis", "cost_insights", "cost_recommendations"]
            ),
            AgentTask(
                agent_id="efficiency_agent",
                task_description="执行效率分析，包括人员效率、流程效率、资源利用等",
                priority=8,
                timeout_seconds=300,
                required_inputs=["analysis_intent", "execution_plan"],
                output_keys=["efficiency", "efficiency_insights", "efficiency_recommendations"]
            ),
            AgentTask(
                agent_id="knowledge_agent",
                task_description="执行知识管理分析，包括知识库建设、技能提升、标准化等",
                priority=7,
                timeout_seconds=300,
                required_inputs=["analysis_intent", "execution_plan"],
                output_keys=["knowledge_analysis", "knowledge_insights", "knowledge_recommendations"]
            )
        ],
        stage_timeout=900,
        min_success_count=2,
        continue_on_failure=True
    )
    
    # 报告生成阶段
    report_generation_stage = WorkflowStageConfig(
        stage_id="report_generation",
        stage_name="综合报告生成",
        description="整合所有分析结果，生成可视化HTML报告",
        execution_mode=AgentExecutionMode.SEQUENTIAL,
        agent_tasks=[
            AgentTask(
                agent_id="report_generator_agent",
                task_description="聚合多Agent分析结果，生成综合性HTML可视化报告",
                priority=10,
                timeout_seconds=180,
                required_inputs=[
                    "financial_analysis", "cost_analysis", 
                    "efficiency", "knowledge_analysis"
                ],
                output_keys=["final_report", "report_summary", "key_insights"]
            )
        ],
        stage_timeout=300,
        min_success_count=1,
        continue_on_failure=False
    )
    
    return WorkflowTemplate(
        template_id="comprehensive_analysis",
        template_name="综合管理分析",
        description="全面的企业管理分析，涵盖财务、成本、效率、知识管理等多个维度",
        version="1.0.0",
        stages=[planning_stage, business_analysis_stage, report_generation_stage],
        global_timeout=1800,
        max_parallel_agents=4,
        error_handling="graceful",
        metadata={
            "target_audience": "企业管理层",
            "analysis_depth": "comprehensive",
            "report_format": "html_visual",
            "business_domains": ["finance", "cost", "efficiency", "knowledge"]
        }
    )

def create_financial_focus_template() -> WorkflowTemplate:
    """创建财务专项分析工作流模板
    
    适用场景：
    - 专项财务分析
    - 财务健康度评估
    - 投资决策支持
    """
    
    # 规划阶段
    planning_stage = WorkflowStageConfig(
        stage_id="planning",
        stage_name="财务分析规划",
        description="制定财务分析策略和重点",
        execution_mode=AgentExecutionMode.SEQUENTIAL,
        agent_tasks=[
            AgentTask(
                agent_id="planner_agent",
                task_description="分析财务分析需求，制定专项分析计划",
                priority=10,
                timeout_seconds=120,
                required_inputs=["user_input", "uploaded_files", "data_content"],
                output_keys=["analysis_intent", "execution_plan", "data_validation"],
                conditions={"focus_area": "financial"}
            )
        ],
        stage_timeout=180,
        min_success_count=1,
        continue_on_failure=False
    )
    
    # 财务分析阶段
    financial_analysis_stage = WorkflowStageConfig(
        stage_id="financial_analysis",
        stage_name="深度财务分析",
        description="执行深度财务分析和成本关联分析",
        execution_mode=AgentExecutionMode.PARALLEL,
        agent_tasks=[
            AgentTask(
                agent_id="financial_agent",
                task_description="执行深度财务分析，重点关注盈利能力和财务风险",
                priority=10,
                timeout_seconds=400,
                required_inputs=["analysis_intent", "execution_plan"],
                output_keys=["financial_analysis", "financial_insights", "financial_recommendations"]
            ),
            AgentTask(
                agent_id="cost_agent",
                task_description="执行成本分析，支撑财务分析结论",
                priority=8,
                timeout_seconds=300,
                required_inputs=["analysis_intent", "execution_plan"],
                output_keys=["cost_analysis", "cost_insights", "cost_recommendations"]
            )
        ],
        stage_timeout=600,
        min_success_count=1,
        continue_on_failure=True
    )
    
    # 报告生成阶段
    report_generation_stage = WorkflowStageConfig(
        stage_id="report_generation",
        stage_name="财务报告生成",
        description="生成专业财务分析报告",
        execution_mode=AgentExecutionMode.SEQUENTIAL,
        agent_tasks=[
            AgentTask(
                agent_id="report_generator_agent",
                task_description="生成专业财务分析HTML报告",
                priority=10,
                timeout_seconds=180,
                required_inputs=["financial_analysis", "cost_analysis"],
                output_keys=["final_report", "report_summary", "key_insights"],
                conditions={"report_focus": "financial"}
            )
        ],
        stage_timeout=300,
        min_success_count=1,
        continue_on_failure=False
    )
    
    return WorkflowTemplate(
        template_id="financial_focus",
        template_name="财务专项分析",
        description="专注于财务健康度和盈利能力的深度分析",
        version="1.0.0",
        stages=[planning_stage, financial_analysis_stage, report_generation_stage],
        global_timeout=1200,
        max_parallel_agents=2,
        error_handling="graceful",
        metadata={
            "target_audience": "财务管理层",
            "analysis_depth": "deep",
            "report_format": "html_financial",
            "business_domains": ["finance", "cost"]
        }
    )

def create_cost_efficiency_template() -> WorkflowTemplate:
    """创建成本效率分析工作流模板
    
    适用场景：
    - 成本控制优化
    - 运营效率提升
    - 资源配置优化
    """
    
    # 规划阶段
    planning_stage = WorkflowStageConfig(
        stage_id="planning",
        stage_name="成本效率分析规划",
        description="制定成本效率分析策略",
        execution_mode=AgentExecutionMode.SEQUENTIAL,
        agent_tasks=[
            AgentTask(
                agent_id="planner_agent",
                task_description="分析成本效率优化需求，制定分析计划",
                priority=10,
                timeout_seconds=120,
                required_inputs=["user_input", "uploaded_files", "data_content"],
                output_keys=["analysis_intent", "execution_plan", "data_validation"],
                conditions={"focus_area": "cost_efficiency"}
            )
        ],
        stage_timeout=180,
        min_success_count=1,
        continue_on_failure=False
    )
    
    # 成本效率分析阶段
    cost_efficiency_stage = WorkflowStageConfig(
        stage_id="cost_efficiency_analysis",
        stage_name="成本效率深度分析",
        description="并行执行成本分析和效率分析",
        execution_mode=AgentExecutionMode.PARALLEL,
        agent_tasks=[
            AgentTask(
                agent_id="cost_agent",
                task_description="执行深度成本分析，识别成本优化机会",
                priority=10,
                timeout_seconds=400,
                required_inputs=["analysis_intent", "execution_plan"],
                output_keys=["cost_analysis", "cost_insights", "cost_recommendations"]
            ),
            AgentTask(
                agent_id="efficiency_agent",
                task_description="执行效率分析，识别效率提升机会",
                priority=9,
                timeout_seconds=400,
                required_inputs=["analysis_intent", "execution_plan"],
                output_keys=["efficiency", "efficiency_insights", "efficiency_recommendations"]
            ),
            AgentTask(
                agent_id="knowledge_agent",
                task_description="分析知识管理对成本效率的影响",
                priority=7,
                timeout_seconds=300,
                required_inputs=["analysis_intent", "execution_plan"],
                output_keys=["knowledge_analysis", "knowledge_insights", "knowledge_recommendations"]
            )
        ],
        stage_timeout=800,
        min_success_count=2,
        continue_on_failure=True
    )
    
    # 报告生成阶段
    report_generation_stage = WorkflowStageConfig(
        stage_id="report_generation",
        stage_name="成本效率报告生成",
        description="生成成本效率优化报告",
        execution_mode=AgentExecutionMode.SEQUENTIAL,
        agent_tasks=[
            AgentTask(
                agent_id="report_generator_agent",
                task_description="生成成本效率优化HTML报告",
                priority=10,
                timeout_seconds=180,
                required_inputs=[
                    "cost_analysis", "efficiency", "knowledge_analysis"
                ],
                output_keys=["final_report", "report_summary", "key_insights"],
                conditions={"report_focus": "cost_efficiency"}
            )
        ],
        stage_timeout=300,
        min_success_count=1,
        continue_on_failure=False
    )
    
    return WorkflowTemplate(
        template_id="cost_efficiency_analysis",
        template_name="成本效率分析",
        description="专注于成本控制和运营效率优化的分析",
        version="1.0.0",
        stages=[planning_stage, cost_efficiency_stage, report_generation_stage],
        global_timeout=1500,
        max_parallel_agents=3,
        error_handling="graceful",
        metadata={
            "target_audience": "运营管理层",
            "analysis_depth": "optimization_focused",
            "report_format": "html_operational",
            "business_domains": ["cost", "efficiency", "knowledge"]
        }
    )

# ================================
# 3. 工作流模板管理器
# ================================

class WorkflowTemplateManager:
    """工作流模板管理器
    
    负责工作流模板的注册、获取和管理
    """
    
    def __init__(self):
        """初始化模板管理器"""
        self._templates: Dict[str, WorkflowTemplate] = {}
        self._register_default_templates()
    
    def _register_default_templates(self):
        """注册默认工作流模板"""
        default_templates = [
            create_comprehensive_analysis_template(),
            create_financial_focus_template(),
            create_cost_efficiency_template()
        ]
        
        for template in default_templates:
            self._templates[template.template_id] = template
    
    def register_template(self, template: WorkflowTemplate) -> bool:
        """注册新的工作流模板"""
        try:
            # 验证模板
            if not self._validate_template(template):
                return False
            
            # 注册模板
            self._templates[template.template_id] = template
            return True
            
        except Exception:
            return False
    
    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """获取工作流模板"""
        return self._templates.get(template_id)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """列出所有可用模板"""
        return [
            {
                "template_id": template.template_id,
                "template_name": template.template_name,
                "description": template.description,
                "version": template.version,
                "stage_count": len(template.stages),
                "metadata": template.metadata
            }
            for template in self._templates.values()
        ]
    
    def _validate_template(self, template: WorkflowTemplate) -> bool:
        """验证工作流模板"""
        try:
            # 基本字段验证
            if not all([template.template_id, template.template_name, template.stages]):
                return False
            
            # 阶段验证
            for stage in template.stages:
                if not all([stage.stage_id, stage.stage_name, stage.agent_tasks]):
                    return False
                
                # Agent任务验证
                for task in stage.agent_tasks:
                    if not all([task.agent_id, task.task_description]):
                        return False
            
            return True
            
        except Exception:
            return False
    
    def get_template_by_focus(self, focus_area: str) -> Optional[WorkflowTemplate]:
        """根据关注领域获取推荐模板"""
        focus_mapping = {
            "financial": "financial_focus",
            "finance": "financial_focus",
            "cost": "cost_efficiency_analysis",
            "efficiency": "cost_efficiency_analysis",
            "comprehensive": "comprehensive_analysis",
            "general": "comprehensive_analysis"
        }
        
        template_id = focus_mapping.get(focus_area.lower(), "comprehensive_analysis")
        return self.get_template(template_id)
    
    def export_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """导出模板配置"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        # 转换为可序列化的字典
        return {
            "template_id": template.template_id,
            "template_name": template.template_name,
            "description": template.description,
            "version": template.version,
            "global_timeout": template.global_timeout,
            "max_parallel_agents": template.max_parallel_agents,
            "error_handling": template.error_handling,
            "metadata": template.metadata,
            "stages": [
                {
                    "stage_id": stage.stage_id,
                    "stage_name": stage.stage_name,
                    "description": stage.description,
                    "execution_mode": stage.execution_mode.value,
                    "stage_timeout": stage.stage_timeout,
                    "min_success_count": stage.min_success_count,
                    "continue_on_failure": stage.continue_on_failure,
                    "output_aggregation": stage.output_aggregation,
                    "agent_tasks": [
                        {
                            "agent_id": task.agent_id,
                            "task_description": task.task_description,
                            "priority": task.priority,
                            "timeout_seconds": task.timeout_seconds,
                            "retry_count": task.retry_count,
                            "required_inputs": task.required_inputs,
                            "optional_inputs": task.optional_inputs,
                            "output_keys": task.output_keys,
                            "dependencies": task.dependencies,
                            "conditions": task.conditions
                        }
                        for task in stage.agent_tasks
                    ]
                }
                for stage in template.stages
            ]
        }

# ================================
# 4. 全局模板管理器实例
# ================================

# 创建全局模板管理器实例
workflow_template_manager = WorkflowTemplateManager()

# ================================
# 5. 便捷函数
# ================================

def get_workflow_template(template_id: str) -> Optional[WorkflowTemplate]:
    """获取工作流模板的便捷函数"""
    return workflow_template_manager.get_template(template_id)

def list_available_workflows() -> List[Dict[str, Any]]:
    """列出可用工作流的便捷函数"""
    return workflow_template_manager.list_templates()

def get_recommended_workflow(focus_area: str) -> Optional[WorkflowTemplate]:
    """获取推荐工作流的便捷函数"""
    return workflow_template_manager.get_template_by_focus(focus_area)

# ================================
# 6. 模块导出
# ================================

__all__ = [
    # 枚举和数据类
    'WorkflowStage',
    'AgentExecutionMode', 
    'AgentTask',
    'WorkflowStageConfig',
    'WorkflowTemplate',
    
    # 模板创建函数
    'create_comprehensive_analysis_template',
    'create_financial_focus_template',
    'create_cost_efficiency_template',
    
    # 管理器类
    'WorkflowTemplateManager',
    
    # 全局实例
    'workflow_template_manager',
    
    # 便捷函数
    'get_workflow_template',
    'list_available_workflows',
    'get_recommended_workflow'
]