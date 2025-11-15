#!/usr/bin/env python3
"""
智水信息Multi-Agent智能分析系统 - 效能评估专家
专注于水电企业人员效能评估、团队分析和组织绩效优化

核心能力：
1. 基于改进型平衡计分卡的员工效能评分（四维度智能评估）
2. 多层级人员效能分析报告（个人/团队/部门/公司级别）
3. 人力资源优化和管理决策支持

Author: 商海星辰队
Version: 2.0.0 - Stdio MCP
"""

import json
import logging
from typing import Dict, List, Any, Optional
from .business_agent import BusinessAgent, AgentTask, AgentResult

# ================================
# 1. EfficiencyAgent类
# ================================

class EfficiencyAgent(BusinessAgent):
    """效能评估专家Agent"""
    
    def __init__(self):
        """初始化效能评估专家"""
        super().__init__(
            agent_id="efficiency_evaluator",
            agent_name="效能评估专家",
            mcp_service="efficiency"
        )
        
        # 效能评估专业配置 - 与实际MCP工具匹配
        self.analysis_types = {
            "employee_efficiency_evaluation": "员工效能评估",  # 对应 evaluate_employee_efficiency 工具
            "team_efficiency_report": "团队效能报告",        # 对应 generate_efficiency_report 工具，report_type="team"
            "department_efficiency_report": "部门效能报告",   # 对应 generate_efficiency_report 工具，report_type="department"  
            "company_efficiency_report": "公司效能报告"       # 对应 generate_efficiency_report 工具，report_type="company"
        }
        
        # 岗位类型配置
        self.position_types = {
            "生产运维": "发电运行、设备维护、安全管理等一线操作岗位",
            "客户服务": "客户关系、市场营销、售后服务等客户导向岗位",
            "技术研发": "技术创新、产品研发、工程设计等技术导向岗位",
            "管理岗位": "部门管理、项目管理、战略规划等管理导向岗位"
        }
        
        # 评估维度配置
        self.evaluation_dimensions = {
            "经济与价值创造": {
                "权重": "35%",
                "子维度": ["成本优化", "数字化效率"],
                "描述": "员工在降本增效、价值创造方面的贡献"
            },
            "客户与社会贡献": {
                "权重": "25%", 
                "子维度": ["服务可靠性", "客户服务"],
                "描述": "员工在客户满意度、社会责任方面的表现"
            },
            "内部流程与治理": {
                "权重": "25%",
                "子维度": ["流程效率", "风险合规"],
                "描述": "员工在流程优化、制度执行方面的能力"
            },
            "学习成长与环境": {
                "权重": "15%",
                "子维度": ["技能发展", "创新分享", "环保实践"],
                "描述": "员工在能力提升、知识分享方面的积极性"
            }
        }
        
        self.logger.info("效能评估专家初始化完成")

    def get_system_prompt(self) -> str:
        """获取效能评估专家的系统提示词"""
        return """你是智水信息技术有限公司的资深效能评估专家，拥有8年以上水电企业人力资源管理和组织绩效优化经验。

## 🎯 专业定位与职责
你是企业人力资源效能的科学评估者和优化建议者，专精于：
- **员工效能科学评估**：基于改进型平衡计分卡的四维度智能评分系统
- **团队绩效深度分析**：多层级团队效能对比和协作效率评估
- **组织效能优化咨询**：基于数据驱动的人力资源配置和管理决策支持
- **绩效管理体系建设**：建立科学合理的绩效评估标准和激励机制

## 🏢 水电企业人力资源特色认知

### 水电企业人员结构特点
**生产运维人员**：
- **技能要求**：操作技能熟练、安全意识强、应急处置能力
- **工作特征**：24小时值班、设备巡检、故障处理、数据记录
- **评估重点**：设备运行稳定性、安全零事故、操作规范性、应急响应
- **职业发展**：技能等级提升、多岗位轮换、班组长培养

**技术研发人员**：
- **技能要求**：专业技术扎实、创新思维活跃、学习能力强
- **工作特征**：技术攻关、方案设计、项目实施、标准制定
- **评估重点**：技术创新成果、项目完成质量、专利申请、技术传承
- **职业发展**：技术专家路线、项目经理转换、跨专业发展

**管理支撑人员**：
- **技能要求**：综合协调能力、决策分析能力、团队领导力
- **工作特征**：计划制定、资源协调、风险管控、绩效管理
- **评估重点**：管理效果、团队建设、战略执行、创新管理
- **职业发展**：管理层级提升、专业管理转换、复合型人才

### 水电行业绩效管理挑战
**安全生产要求**：
- 安全生产零事故是第一考核指标
- 安全培训和应急演练的效果评估
- 安全文化建设和行为安全管理

**技术能力建设**：
- 新技术学习和应用能力评估
- 技术创新和改进建议的激励机制
- 技能等级评定和职业发展通道

**团队协作效率**：
- 多专业协作的沟通协调能力
- 跨部门项目的执行效率评估
- 知识分享和经验传承机制

## 🔧 核心评估工具箱

### 1. 改进型平衡计分卡评估引擎 (evaluate_employee_efficiency)
**四维度评估体系**：

#### 经济与价值创造维度（权重35%）
**核心指标**：
- **成本优化能力**：节能降耗、成本控制、效率提升的具体贡献
- **数字化效率**：信息化工具使用、数据分析能力、流程数字化推进

**评分标准**：
- **优秀(90-100分)**：年度成本节约>5%，数字化应用娴熟，效率提升显著
- **良好(80-89分)**：成本节约2-5%，数字化工具使用熟练，效率有提升
- **合格(70-79分)**：成本基本控制，数字化工具基本掌握，效率稳定
- **需改进(<70分)**：成本控制不力，数字化应用不足，效率有待提升

#### 客户与社会贡献维度（权重25%）
**核心指标**：
- **服务可靠性**：设备可靠性维护、供电/供水质量保障、服务连续性
- **客户服务水平**：客户满意度、投诉处理、服务创新

**评分标准**：
- **优秀(90-100分)**：服务可靠性>99.5%，客户满意度>95%，零重大投诉
- **良好(80-89分)**：服务可靠性95-99.5%，客户满意度85-95%，投诉及时处理
- **合格(70-79分)**：服务可靠性90-95%，客户满意度75-85%，投诉基本解决
- **需改进(<70分)**：服务可靠性<90%，客户满意度<75%，投诉处理不及时

#### 内部流程与治理维度（权重25%）
**核心指标**：
- **流程效率**：工作流程优化、时间管理、协调配合能力
- **风险合规**：制度执行、风险识别、合规操作

**评分标准**：
- **优秀(90-100分)**：流程优化成效显著，风险识别准确，合规执行到位
- **良好(80-89分)**：流程执行高效，风险基本可控，合规意识强
- **合格(70-79分)**：流程执行正常，风险识别一般，合规执行基本到位
- **需改进(<70分)**：流程执行缓慢，风险识别不足，合规执行有漏洞

#### 学习成长与环境维度（权重15%）
**核心指标**：
- **技能发展**：技能等级提升、培训效果、证书获取
- **创新分享**：改进建议、知识分享、创新实践
- **环保实践**：环保意识、绿色行为、可持续发展贡献

**评分标准**：
- **优秀(90-100分)**：技能等级提升明显，创新成果突出，环保实践积极
- **良好(80-89分)**：技能有所提升，有创新建议，环保意识强
- **合格(70-79分)**：技能基本维持，偶有创新想法，环保行为一般
- **需改进(<70分)**：技能停滞不前，创新意识不足，环保行为消极

### 2. 岗位差异化权重配置
**生产运维岗位权重**：经济维度40% + 客户维度30% + 流程维度25% + 学习维度5%
- 突出设备运行效率和安全生产责任
- 重视客户服务质量和供电可靠性
- 强调操作规范和风险防控

**客户服务岗位权重**：客户维度40% + 流程维度25% + 经济维度25% + 学习维度10%
- 以客户满意度为核心评估指标
- 重视服务流程优化和问题解决能力
- 关注服务成本控制和效率提升

**技术研发岗位权重**：学习维度30% + 经济维度30% + 流程维度25% + 客户维度15%
- 突出技术创新和知识更新能力
- 重视技术成果的经济价值转化
- 关注研发流程管理和项目协作

**管理岗位权重**：经济维度30% + 流程维度30% + 客户维度25% + 学习维度15%
- 平衡各维度发展，体现综合管理能力
- 重视经济效益和流程治理双重责任
- 关注团队建设和人才培养

### 3. 多层级效能分析报告 (generate_efficiency_report)
**个人效能分析**：
- **综合评分**：四维度加权综合评分和等级评定
- **优势分析**：识别个人核心优势和特长领域
- **改进建议**：针对性的能力提升和发展建议
- **发展路径**：基于个人特点的职业发展规划

**团队效能分析**：
- **团队画像**：团队整体效能分布和结构分析
- **协作效率**：团队内部协作和跨部门配合效果
- **互补性分析**：团队成员能力互补和优化配置
- **团队发展**：团队建设重点和能力提升方向

**部门效能分析**：
- **部门对比**：不同部门效能水平的横向对比
- **趋势分析**：部门效能的时间趋势和变化规律
- **资源配置**：人力资源配置的合理性评估
- **管理建议**：部门管理优化和效能提升策略

## 💼 评估方法论与质量控制

### 科学评估方法论
**数据收集方法**：
- **360度评估**：上级、同级、下级、客户多角度评价
- **关键事件法**：记录和分析关键工作事件和表现
- **目标管理法**：基于工作目标达成情况的量化评估
- **行为观察法**：工作行为和职业素养的日常观察

**评分客观性保障**：
- **量化指标**：尽可能使用量化的客观指标进行评估
- **标准统一**：建立统一的评分标准和操作规范
- **多人评价**：采用多人评价求平均值的方式减少主观性
- **定期校准**：定期校准评分标准，确保评估一致性

### 评估质量控制体系
**评估数据质量**：
- **完整性检查**：确保评估数据的完整性和覆盖面
- **一致性验证**：检查评估结果的逻辑一致性
- **异常值识别**：识别和处理异常评估数据
- **可信度评估**：评估数据来源的可信度和权威性

**评估过程质量**：
- **标准化流程**：建立标准化的评估操作流程
- **培训认证**：评估人员的培训和认证机制
- **监督检查**：评估过程的监督检查和质量控制
- **反馈改进**：基于反馈持续改进评估方法

### 评估结果应用策略
**绩效管理应用**：
- **绩效奖金**：基于评估结果的绩效奖金分配
- **晋升考核**：员工晋升和岗位调整的重要依据
- **培训规划**：基于能力短板的针对性培训计划
- **职业发展**：个人职业发展规划和指导建议

**组织优化应用**：
- **人岗匹配**：优化人员配置，实现人岗最佳匹配
- **团队建设**：基于能力互补的团队组建和调整
- **文化建设**：识别和推广优秀员工的行为模式
- **制度优化**：基于评估发现完善管理制度和流程

## 🎯 输出标准与价值体现

### 评估报告标准化输出
**个人评估报告**：
1. **评估总览**：综合评分、等级评定、行业排名
2. **维度分析**：四大维度详细评分和对比分析
3. **能力画像**：个人能力雷达图和核心竞争力
4. **发展建议**：具体可操作的能力提升建议
5. **发展规划**：3-5年职业发展路径规划

**团队分析报告**：
1. **团队概况**：团队规模、结构、整体效能水平
2. **成员分析**：团队成员效能分布和能力构成
3. **协作评估**：团队协作效率和沟通效果分析
4. **优化建议**：团队建设和管理改进建议
5. **发展方向**：团队能力建设和发展重点

### 价值效益量化评估
**管理效率提升**：
- 评估时间缩短50%以上，评估准确性提升30%
- 人才识别精度提升，关键人才流失率降低20%
- 培训针对性增强，培训效果提升40%

**决策支持价值**：
- 为人力资源配置提供科学依据，配置效率提升25%
- 为薪酬体系设计提供量化基础，激励效果提升35%
- 为组织架构优化提供数据支撑，组织效能提升20%

**员工发展价值**：
- 员工职业发展方向更明确，发展满意度提升40%
- 能力提升针对性增强，技能提升速度提升30%
- 工作成就感增强，员工敬业度提升25%

## 🤝 协作策略与系统集成

### 与其他专业Agent协作
**财务分析专家协作**：
- 提供人力成本分析的效能数据支撑
- 支持基于效能的薪酬成本优化建议
- 分析人力投入产出比和效率提升潜力

**成本预测专家协作**：
- 提供人力成本预测的效能基础数据
- 支持项目人力配置的效率评估
- 分析人力成本控制的效能优化方案

**知识管理专家协作**：
- 提供人力资源管理最佳实践案例
- 支持效能评估标准和方法的知识库建设
- 分享组织管理和团队建设的成功经验

### 用户交互优化策略
**评估参与便民化**：
- **移动端支持**：支持手机端的评估数据录入和查询
- **批量导入**：支持Excel批量导入员工基础数据和评估数据
- **进度跟踪**：实时显示评估进度和完成情况
- **结果预览**：评估过程中的实时结果预览和调整

**结果展示个性化**：
- **可视化报告**：图表化展示评估结果，直观易懂
- **对比分析**：个人与团队、部门、行业标杆的对比分析
- **趋势展示**：个人效能的历史趋势和发展轨迹
- **建议清单**：结构化的改进建议和行动计划

你现在开始运用以上专业知识和评估能力，为智水信息的客户提供高质量的效能评估服务。始终保持评估的科学性、客观性和建设性，确保每一次评估都能为员工发展和组织优化提供有价值的指导。"""

    def get_required_fields(self) -> List[str]:
        """获取效能评估必需的字段"""
        return ["analysis_type"]  # 基础必需字段，具体字段根据分析类型动态确定

    def validate_input_data(self, task: AgentTask) -> tuple[bool, List[str]]:
        """验证效能评估输入数据"""
        errors = []
        data = task.input_data
        
        # 兼容处理：从input_data字段或直接从data获取业务数据
        business_data = data.get("input_data", data)
        
        # 检查分析类型
        analysis_type = business_data.get("analysis_type")
        if not analysis_type:
            errors.append("缺少分析类型(analysis_type)")
            return False, errors
            
        if analysis_type not in self.analysis_types:
            errors.append(f"不支持的分析类型: {analysis_type}")
            return False, errors
        
        # 根据分析类型检查特定字段
        if analysis_type == "employee_efficiency_evaluation":
            required_fields = ["employee_data", "metrics_data", "position_type"]
            for field in required_fields:
                if field not in business_data or not business_data[field]:
                    errors.append(f"员工效能评估需要{field}字段")
            
            # 检查岗位类型是否支持
            position_type = business_data.get("position_type")
            if position_type and position_type not in self.position_types:
                errors.append(f"不支持的岗位类型: {position_type}，支持类型: {list(self.position_types.keys())}")
        
        elif analysis_type in ["team_performance_analysis", "department_efficiency_report"]:
            if "team_data" not in business_data and "employee_list" not in business_data:
                errors.append("团队/部门分析需要团队数据(team_data)或员工列表(employee_list)")
        
        elif analysis_type == "organization_optimization":
            if "organization_data" not in business_data:
                errors.append("组织优化分析需要组织数据(organization_data)")
        
        return len(errors) == 0, errors

    def perform_analysis(self, data: Dict[str, Any], task: AgentTask) -> Dict[str, Any]:
        """执行效能评估分析 - 统一使用stdio MCP协议"""
        # 从预处理的数据中获取analysis_type
        input_data = data.get("input_data", data)  # 兼容处理
        analysis_type = input_data.get("analysis_type")
        
        self.logger.info(f"开始效能分析，类型: {analysis_type}")
        self.logger.debug(f"输入数据结构: {list(data.keys())}")
        self.logger.debug(f"业务数据结构: {list(input_data.keys())}")
        
        try:
            # 输入数据验证
            is_valid, errors = self.validate_input_data(task)
            if not is_valid:
                return {
                    "error": f"输入数据验证失败: {'; '.join(errors)}",
                    "analysis_type": analysis_type,
                    "timestamp": self._get_timestamp(),
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "confidence_score": 0.0,
                    "recommendations": []
                }
            
            # 根据分析类型调用相应的MCP服务
            if analysis_type == "employee_efficiency_evaluation":
                mcp_result = self._perform_employee_evaluation(input_data)
            elif analysis_type == "team_efficiency_report":
                mcp_result = self._perform_team_analysis(input_data)
            elif analysis_type == "department_efficiency_report":
                mcp_result = self._perform_department_analysis(input_data)
            elif analysis_type == "company_efficiency_report":
                mcp_result = self._perform_organization_analysis(input_data)
            else:
                return {
                    "error": f"未支持的分析类型: {analysis_type}",
                    "analysis_type": analysis_type,
                    "timestamp": self._get_timestamp(),
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "confidence_score": 0.0,
                    "recommendations": []
                }
            
            if "error" in mcp_result:
                return {
                    "error": "MCP服务调用失败",
                    "analysis_type": analysis_type,
                    "timestamp": self._get_timestamp(),
                    "mcp_result": mcp_result,
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "confidence_score": 0.0,
                    "recommendations": []
                }
            
            # 计算置信度和生成建议
            confidence_score = self.calculate_confidence_score(mcp_result)
            recommendations = self.generate_recommendations(mcp_result)
            
            # 构建最终结果
            result = {
                "analysis_type": analysis_type,
                "timestamp": self._get_timestamp(),
                "mcp_result": mcp_result,
                "confidence_score": confidence_score,
                "recommendations": recommendations,
                "agent_id": self.agent_id,
                "task_id": task.task_id,
                "summary": f"效能评估分析完成 - {analysis_type}"
            }
            
            self.logger.info(f"效能评估分析完成，置信度: {confidence_score}")
            return result
                
        except Exception as e:
            self.logger.error(f"效能评估分析执行失败: {e}")
            return {
                "error": f"分析执行失败: {str(e)}",
                "analysis_type": analysis_type,
                "timestamp": self._get_timestamp(),
                "agent_id": self.agent_id,
                "task_id": task.task_id,
                "confidence_score": 0.0,
                "recommendations": [],
                "error_message": "分析执行异常"
            }

    def _perform_employee_evaluation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行员工效能评估 - 直接调用MCP服务"""
        return self._call_mcp_for_employee_evaluation(data)

    def _perform_team_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行团队绩效分析 - 直接调用MCP服务"""
        return self._call_mcp_for_team_analysis(data)

    def _perform_department_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行部门效率分析 - 直接调用MCP服务"""
        return self._call_mcp_for_department_analysis(data)

    def _perform_organization_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行组织优化分析 - 直接调用MCP服务"""
        return self._call_mcp_for_organization_analysis(data)
    
    # ================================
    # 生成建议方法 - 简化版本
    # ================================
    
    def generate_recommendations(self, mcp_result: Dict[str, Any]) -> List[str]:
        """基于MCP服务结果生成建议 - 简化版本"""
        try:
            recommendations = []
            
            # 从MCP结果中提取建议
            if isinstance(mcp_result, dict):
                # 提取recommendations字段
                if "recommendations" in mcp_result:
                    if isinstance(mcp_result["recommendations"], list):
                        recommendations.extend(mcp_result["recommendations"])
                
                # 提取analysis中的suggestions
                if "analysis" in mcp_result and isinstance(mcp_result["analysis"], dict):
                    if "suggestions" in mcp_result["analysis"]:
                        if isinstance(mcp_result["analysis"]["suggestions"], list):
                            recommendations.extend(mcp_result["analysis"]["suggestions"])
            
            # 去重并返回
            unique_recommendations = []
            for rec in recommendations:
                if rec and rec not in unique_recommendations:
                    unique_recommendations.append(rec)
            
            # 如果没有建议，返回默认建议
            if not unique_recommendations:
                unique_recommendations = [
                    "建议定期进行效能评估，持续优化人员配置",
                    "加强团队协作培训，提升整体工作效率", 
                    "建立完善的绩效考核体系，激发员工积极性",
                    "优化工作流程，减少不必要的重复劳动",
                    "投资员工技能培训，提升专业能力水平"
                ]
            
            return unique_recommendations[:10]  # 最多返回10条建议
            
        except Exception as e:
            logger.error(f"生成建议时出错: {e}")
            return [
                "建议定期进行效能评估，持续优化人员配置",
                "加强团队协作培训，提升整体工作效率", 
                "建立完善的绩效考核体系，激发员工积极性",
                "优化工作流程，减少不必要的重复劳动",
                "投资员工技能培训，提升专业能力水平"
            ]

    # ================================
    # 简化的建议生成方法
    # ================================
    
    def generate_recommendations(self, mcp_result: Dict[str, Any], analysis_type: str) -> List[str]:
        """生成简化的建议"""
        try:
            # 基于分析类型生成基础建议
            if analysis_type == "employee_evaluation":
                return [
                    "建议制定个人发展计划",
                    "加强专业技能培训",
                    "提升工作效率和质量",
                    "增强团队协作能力"
                ]
            elif analysis_type == "team_analysis":
                return [
                    "优化团队协作流程",
                    "加强团队沟通机制",
                    "提升团队整体效能",
                    "建立知识分享平台"
                ]
            elif analysis_type == "department_analysis":
                return [
                    "优化部门资源配置",
                    "完善管理体系",
                    "提升跨部门协作",
                    "建立绩效评估机制"
                ]
            elif analysis_type == "organization_analysis":
                return [
                    "优化组织架构",
                    "完善人才培养体系",
                    "提升组织效能",
                    "建立创新激励机制"
                ]
            else:
                return ["建议进行详细分析"]
                
        except Exception as e:
            self.logger.error(f"生成建议失败: {e}")
            return ["建议制定改进计划"]

    # ================================
    # MCP服务调用方法
    # ================================
    def calculate_confidence_score(self, result: Dict[str, Any]) -> float:
        """计算效能评估置信度"""
        if "error" in result:
            return 0.0
        
        confidence = 0.5  # 基础置信度
        
        # 基于MCP服务结果质量评估置信度
        if "mcp_result" in result and result["mcp_result"]:
            confidence += 0.3
        
        # 基于数据完整性评估置信度
        if "data" in result and result["data"]:
            confidence += 0.2
        
        return min(confidence, 1.0)

    def generate_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """生成效能评估总体建议"""
        analysis_type = result.get("analysis_type", "效能评估")
        
        # 根据分析类型返回基础建议
        if "员工效能评估" in analysis_type:
            return [
                "建议定期开展员工效能评估，跟踪个人发展状况",
                "制定个性化培训计划，提升员工专业技能",
                "建立员工激励机制，激发工作积极性",
                "完善绩效管理体系，明确考核标准"
            ]
        elif "团队绩效分析" in analysis_type:
            return [
                "建议定期开展团队效能评估，跟踪团队发展状况",
                "建立团队绩效管理体系，明确团队目标和考核标准",
                "加强团队领导力建设，提升团队管理水平",
                "建立团队文化，营造积极向上的工作氛围"
            ]
        elif "部门效能报告" in analysis_type:
            return [
                "建议建立部门效能监控体系，定期评估部门绩效",
                "加强部门间协作机制，提升组织整体效率",
                "建立人才梯队建设，确保部门可持续发展",
                "完善部门激励机制，激发员工积极性"
            ]
        elif "组织优化分析" in analysis_type:
            return [
                "建议建立组织效能管理体系，持续监控组织健康度",
                "加强人才发展和继任规划，确保组织可持续发展",
                "建立创新文化，提升组织适应变化的能力",
                "完善绩效管理体系，激发组织整体活力"
            ]
        else:
            return ["建议基于评估结果制定针对性的改进方案", "持续关注效能提升和组织发展"]
    
    # ============================================================================
    # MCP服务调用方法
    # ============================================================================
    
    def _call_mcp_for_employee_evaluation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP服务进行员工效能评估"""
        employee_data = data["employee_data"]
        metrics_data = data["metrics_data"]
        position_type = data["position_type"]
        
        return self.call_mcp_tool(
            "evaluate_employee_efficiency",
            arguments={
                "employee_data": employee_data,
                "metrics_data": metrics_data,
                "position_type": position_type
            }
        )
    
    def _call_mcp_for_team_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP服务进行团队绩效分析"""
        team_data = data.get("team_data", {})
        target_scope = data.get("target_scope", "team")
        time_period = data.get("time_period", "monthly")
        
        # 构建数据源JSON字符串
        data_source = json.dumps({
            "team_data": team_data,
            "performance_metrics": data.get("performance_metrics", {})
        }, ensure_ascii=False)
        
        return self.call_mcp_tool(
            "generate_efficiency_report",  # 使用实际存在的工具
            arguments={
                "report_type": "team",
                "target_scope": target_scope,
                "time_period": time_period,
                "data_source": data_source,
                "output_format": "markdown"
            }
        )
    
    def _call_mcp_for_department_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP服务进行部门效率分析"""
        department_data = data.get("department_data", {})
        target_scope = data.get("target_scope", "department")
        time_period = data.get("time_period", "monthly")
        
        # 构建数据源JSON字符串
        data_source = json.dumps({
            "department_data": department_data,
            "efficiency_metrics": data.get("efficiency_metrics", {})
        }, ensure_ascii=False)
        
        return self.call_mcp_tool(
            "generate_efficiency_report",
            arguments={
                "report_type": "department",
                "target_scope": target_scope,
                "time_period": time_period,
                "data_source": data_source,
                "output_format": "markdown"
            }
        )
    
    def _call_mcp_for_organization_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP服务进行组织优化分析"""
        organization_data = data.get("organization_data", {})
        target_scope = data.get("target_scope", "all")
        time_period = data.get("time_period", "quarterly")
        
        # 构建数据源JSON字符串
        data_source = json.dumps({
            "organization_data": organization_data,
            "optimization_scope": data.get("optimization_scope", "full")
        }, ensure_ascii=False)
        
        return self.call_mcp_tool(
            "generate_efficiency_report",  # 使用实际存在的工具
            arguments={
                "report_type": "company",
                "target_scope": target_scope,
                "time_period": time_period,
                "data_source": data_source,
                "output_format": "markdown"
            }
        )

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # ============================================================================
    # 综合LLM分析方法
    # ============================================================================
    
    # 已删除复杂的LLM分析方法，专注于MCP服务调用
