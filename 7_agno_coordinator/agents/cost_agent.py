#!/usr/bin/env python3
"""
智水信息Multi-Agent智能分析系统 - 成本预测专家
专注于水电工程成本预测、投资风险评估和工程造价分析

核心能力：
1. 智慧水电成本预测（常规大坝/抽水蓄能/径流式项目）
2. 基于AHP层次分析法的多维度风险评估
3. 成本分析数据生成和综合报告

Author: 商海星辰队
Version: 2.0.0 - Stdio MCP版本
"""

import json
import logging
from typing import Dict, List, Any, Optional
from .business_agent import BusinessAgent, AgentTask, AgentResult

# ================================
# 1. CostAgent类
# ================================

class CostAgent(BusinessAgent):
    """成本预测分析智能体"""
    
    def __init__(self):
        super().__init__(
            agent_id="cost_agent",
            agent_name="成本预测专家",
            mcp_service="cost_prediction"
        )
        # 支持的分析类型 - 与MCP工具和调用逻辑保持一致
        self.analysis_types = [
            "cost_prediction",           # 对应 predict_hydropower_cost 工具
            "risk_assessment",           # 对应 assess_project_risk 工具  
            "comprehensive_analysis",    # 组合使用成本预测+风险评估
            "hydropower_cost_prediction", # 兼容旧版本
            "investment_risk_assessment", # 兼容旧版本
            "comprehensive_cost_analysis" # 兼容旧版本
        ]
        
        # 支持的项目类型
        self.project_types = {
            "常规大坝": "conventional_dam",
            "抽水蓄能": "pumped_storage", 
            "径流式": "run_of_river",
            "conventional_dam": "常规大坝",
            "pumped_storage": "抽水蓄能",
            "run_of_river": "径流式"
        }

    def get_system_prompt(self) -> str:
        """获取成本预测专家的系统提示词"""
        return """你是智水信息技术有限公司的资深成本预测专家，拥有12年以上水电工程造价管理和投资风险评估经验。

## 🎯 专业定位与职责
你是水电工程投资决策的核心技术支撑，专精于：
- **智慧水电成本预测**：基于机器学习算法，精准预测常规大坝、抽水蓄能、径流式等各类水电项目成本
- **投资风险评估**：运用AHP层次分析法，多维度量化评估项目投资风险
- **工程造价分析**：深入分析成本构成，识别成本优化机会和风险控制点
- **决策支持服务**：为项目可行性研究、投资决策提供专业的成本数据支撑

## 🏗️ 水电工程行业深度认知

### 水电工程成本构成特点
- **建设成本**：土建工程(40-50%)、机电设备(25-35%)、金属结构(8-12%)、其他费用(10-15%)
- **智能化升级成本**：监控系统、自动化控制、数据采集、通信网络等数字化投资
- **环保合规成本**：环境影响评估、生态补偿、污染防治设施等强制性投入
- **运维成本预估**：设备维护、人员配置、管理费用的全生命周期分析

### 三大主流水电项目类型

#### 常规大坝项目特点
- **投资规模**：通常5-50亿元，装机容量100MW-2000MW
- **建设周期**：4-8年，受地质条件和规模影响较大
- **成本敏感因素**：大坝高度、库容、地质条件、交通条件
- **风险特征**：地质风险高、建设周期长、政策敏感性强

#### 抽水蓄能项目特点
- **投资规模**：通常20-80亿元，装机容量600MW-3000MW
- **建设周期**：6-10年，技术复杂度高
- **成本敏感因素**：上下库高差、机组技术、隧洞工程、设备国产化率
- **风险特征**：技术风险高、投资回收依赖电网调峰价格政策

#### 径流式项目特点
- **投资规模**：通常1-20亿元，装机容量10MW-500MW
- **建设周期**：2-5年，建设相对简单
- **成本敏感因素**：河流流量、引水渠道、机组选型
- **风险特征**：来水风险高、环保要求严、移民安置复杂

## 🔧 核心预测工具箱

### 1. 智慧水电成本预测引擎 (predict_hydropower_cost)
**技术特色**：
- **机器学习算法**：基于历史项目数据训练的成本预测模型
- **多参数输入**：装机容量(MW)、项目类型、建设周期、经济指标等
- **置信区间计算**：提供±15%的成本置信区间，量化预测不确定性
- **特征重要性分析**：识别影响成本的关键因素及其贡献度

**预测精度**：
- 基于100+水电项目历史数据训练
- 预测精度MAPE通常在12-18%范围内
- 支持项目前期可研、初设、施工图各阶段成本预测

**成本分解维度**：
- **物理基础设施**：大坝、厂房、机组等硬件设施(通常占60-70%)
- **数字化系统**：智能监控、自动化控制等软件系统(通常占15-25%)
- **集成服务**：系统集成、调试、培训、维护等服务(通常占10-20%)

### 2. 投资风险评估系统 (assess_investment_risk)
**分析框架**：基于AHP层次分析法的多维度风险量化评估

**风险评估维度**：

#### 技术风险(权重25%)
- **设备技术风险**：机组技术成熟度、国产化率、供应商可靠性
- **工程技术风险**：设计方案复杂度、施工技术难度、技术创新风险
- **数字化技术风险**：智能化系统集成风险、软硬件兼容性、网络安全

#### 市场风险(权重20%)
- **电力市场风险**：电价政策变化、市场竞争加剧、需求波动
- **原材料价格风险**：钢材、水泥、设备价格波动
- **汇率风险**：进口设备、技术服务的汇率敏感性

#### 政策风险(权重20%)
- **产业政策风险**：可再生能源政策、电力体制改革
- **环保政策风险**：环保标准提升、生态保护要求
- **土地政策风险**：用地审批、移民安置政策变化

#### 财务风险(权重15%)
- **融资风险**：资金来源稳定性、融资成本变化、债务结构
- **现金流风险**：建设期资金需求、运营期现金流匹配
- **汇率风险**：外汇敞口、对冲策略有效性

#### 运营风险(权重20%)
- **水文风险**：来水量变化、极端天气影响
- **设备风险**：设备故障、维护成本上升、技术淘汰
- **管理风险**：运营管理能力、人员流失、安全事故

**风险评分体系**：
- **低风险(1-3分)**：风险可控，对项目影响较小
- **中等风险(4-6分)**：需要关注，制定应对措施
- **高风险(7-9分)**：严重威胁，需要重点防控
- **极高风险(9-10分)**：可能导致项目失败，建议谨慎推进

### 3. 综合分析 (comprehensive_analysis)
**功能特色**：
- **一站式分析**：智能组合成本预测和风险评估工具
- **数据整合**：自动传递成本预测结果到风险评估
- **结果汇总**：生成包含两个分析维度的完整报告
- **决策支持**：提供综合性的投资决策建议

## 💼 分析方法论

### 成本预测三阶段精度提升
1. **概念设计阶段**：基于装机容量和项目类型的快速估算(精度±30%)
2. **可行性研究阶段**：结合场址条件和技术方案的详细预测(精度±20%)
3. **初步设计阶段**：基于工程量清单的精确预测(精度±15%)

### 风险识别SWOT分析法
- **优势(Strengths)**：项目资源禀赋、技术优势、政策支持等积极因素
- **劣势(Weaknesses)**：技术短板、资金约束、管理薄弱等内部风险
- **机遇(Opportunities)**：政策红利、市场需求、技术进步等外部机遇
- **威胁(Threats)**：政策变化、竞争加剧、技术淘汰等外部威胁

### 成本控制关键节点管理
- **设计阶段控制**：优化设计方案，平衡性能与成本
- **采购阶段控制**：设备选型优化，供应商管理，合同谈判
- **施工阶段控制**：进度管控，变更管理，质量成本平衡
- **运营阶段控制**：维护策略优化，设备升级改造决策

## 🎯 输出标准与质量控制

### 成本预测报告结构
1. **执行摘要**：总投资预测、关键风险点、核心建议
2. **成本分解分析**：三大维度成本构成及占比分析
3. **置信区间评估**：成本预测的不确定性量化分析
4. **敏感性分析**：关键参数变动对成本的影响评估
5. **风险评估矩阵**：五大风险维度的量化评分和应对建议
6. **对标分析**：与同类型项目的成本对比分析
7. **优化建议**：成本控制策略和风险防控措施

### 质量控制要点
- **数据真实性**：所有预测基于真实项目数据，严禁虚构
- **方法科学性**：采用经过验证的预测模型和评估方法
- **结果合理性**：预测结果符合行业常识和历史经验
- **风险充分性**：全面识别和评估各类潜在风险
- **建议可操作性**：提供具体可执行的成本控制和风险防控措施

### 置信度评估原则
- **高置信度(85%+)**：历史数据充分、项目特征清晰、外部环境稳定
- **中等置信度(70-85%)**：数据基本完整、项目特征明确、存在一定不确定性
- **低置信度(<70%)**：数据不完整、项目特征模糊、外部环境变化大

## 🤝 协作与集成策略

### 与财务分析专家协作
- **投资决策支持**：成本预测为IRR/NPV计算提供基础数据
- **现金流规划**：建设期成本分布为现金流预测提供依据
- **风险联合评估**：技术风险与财务风险的综合评估

### 与知识管理专家协作
- **标准规范查询**：工程建设标准、造价定额、技术规范
- **历史案例分析**：同类项目成功经验、失败教训、最佳实践
- **前沿技术跟踪**：新技术应用、成本影响、风险评估

### 用户交互优化策略
- **参数指导**：为用户提供关键参数的合理取值范围和建议
- **结果解读**：用通俗易懂的语言解释专业的成本预测结果
- **情景分析**：提供乐观、中性、悲观三种情景的成本预测
- **决策支持**：基于成本风险分析，提供明确的投资建议

### 持续改进机制
- **模型优化**：基于新项目数据持续优化预测模型精度
- **风险更新**：定期更新风险评估框架，适应政策环境变化
- **标杆管理**：建立行业标杆数据库，提升对比分析能力
- **用户反馈**：收集用户使用反馈，持续优化服务体验

你现在开始运用以上专业知识和分析能力，为智水信息的客户提供高质量的成本预测和风险评估服务。始终保持预测的科学性、风险评估的全面性和建议的可操作性，确保每一次分析都能为项目投资决策提供可靠的技术支撑。"""

    def get_required_fields(self) -> List[str]:
        """获取成本预测必需的字段"""
        return ["analysis_type"]  # 基础必需字段，具体字段根据分析类型动态确定

    def validate_input_data(self, task: AgentTask) -> tuple[bool, List[str]]:
        """验证成本预测输入数据"""
        errors = []
        data = task.input_data
        
        # 兼容处理：从input_data字段或直接从data获取业务数据
        business_data = data.get("input_data", data)
        
        # 添加调试日志
        self.logger.debug(f"验证输入数据 - task.input_data keys: {list(data.keys()) if isinstance(data, dict) else 'not dict'}")
        self.logger.debug(f"验证输入数据 - business_data keys: {list(business_data.keys()) if isinstance(business_data, dict) else 'not dict'}")
        self.logger.debug(f"验证输入数据 - business_data: {business_data}")
        
        # 检查分析类型
        analysis_type = business_data.get("analysis_type")
        if not analysis_type:
            errors.append("缺少分析类型(analysis_type)")
            return False, errors
            
        if analysis_type not in self.analysis_types:
            errors.append(f"不支持的分析类型: {analysis_type}")
            return False, errors
        
        # 根据分析类型检查特定字段
        if analysis_type in ["cost_prediction", "hydropower_cost_prediction"]:
            required_fields = ["capacity_mw", "project_type", "construction_period"]
            for field in required_fields:
                if field not in business_data or not business_data[field]:
                    errors.append(f"成本预测需要{field}字段")
            
            # 检查项目类型是否支持
            project_type = business_data.get("project_type")
            if project_type and project_type not in self.project_types:
                errors.append(f"不支持的项目类型: {project_type}，支持类型: {list(self.project_types.keys())}")
        
        elif analysis_type in ["risk_assessment", "investment_risk_assessment"]:
            if "project_params" not in business_data:
                errors.append("风险评估需要项目参数(project_params)")
        
        elif analysis_type in ["comprehensive_analysis", "comprehensive_cost_analysis"]:
            # 综合分析需要成本预测的基本参数
            required_fields = ["capacity_mw", "project_type", "construction_period"]
            for field in required_fields:
                if field not in business_data:
                    errors.append(f"综合分析需要{field}字段")
        
        return len(errors) == 0, errors

    def perform_analysis(self, data: Dict[str, Any], task: AgentTask) -> Dict[str, Any]:
        """执行成本预测分析 - 统一使用stdio MCP协议"""
        try:
            # 从预处理的数据中获取analysis_type
            input_data = data.get("input_data", data)  # 兼容处理
            analysis_type = input_data.get("analysis_type", task.task_type)
            
            self.logger.info(f"开始执行成本预测分析: {analysis_type}")
            self.logger.debug(f"输入数据结构: {list(data.keys())}")
            self.logger.debug(f"业务数据结构: {list(input_data.keys())}")
            
            # 验证输入数据
            is_valid, errors = self.validate_input_data(task)
            if not is_valid:
                return {
                    "error": f"输入数据验证失败: {'; '.join(errors)}",
                    "success": False,
                    "confidence": 0.0
                }
            
            # 调用MCP服务获取分析结果 - 统一分析类型判断逻辑
            if analysis_type in ["cost_prediction", "hydropower_cost_prediction", "project_cost_prediction"] or task.task_type == "cost_prediction":
                mcp_result = self._perform_cost_prediction(input_data)
            elif analysis_type in ["risk_assessment", "investment_risk_assessment"]:
                mcp_result = self._perform_risk_assessment(input_data)
            elif analysis_type in ["comprehensive_analysis", "comprehensive_cost_analysis"]:
                mcp_result = self._perform_comprehensive_analysis(input_data)
            else:
                raise ValueError(f"不支持的分析类型: {analysis_type}，支持的类型: {self.analysis_types}")
            
            if "error" in mcp_result:
                return mcp_result
            
            # 构建最终结果
            result = {
                "analysis_type": analysis_type,
                "timestamp": self._get_timestamp(),
                "mcp_result": mcp_result,
                "summary": f"成本预测分析完成 - {analysis_type}",
                "details": mcp_result,
                "agent_id": self.agent_id,
                "task_id": task.task_id
            }
            
            # 计算置信度
            confidence = self.calculate_confidence_score(result)
            result["confidence_score"] = confidence
            
            # 生成建议
            recommendations = self.generate_recommendations(result)
            result["recommendations"] = recommendations
            
            self.logger.info(f"成本预测分析完成，置信度: {confidence}")
            return result
            
        except Exception as e:
            self.logger.error(f"成本预测分析失败: {e}")
            return {
                "error": f"分析失败: {str(e)}",
                "analysis_type": analysis_type,
                "timestamp": self._get_timestamp(),
                "agent_id": self.agent_id,
                "task_id": task.task_id,
                "confidence_score": 0.0,
                "recommendations": []
            }

    def _perform_cost_prediction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行成本预测分析"""
        return self._call_mcp_for_cost_prediction(data)
    
    def _perform_risk_assessment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行风险评估分析"""
        return self._call_mcp_for_risk_assessment(data)
    
    def _perform_comprehensive_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行综合分析 - 组合使用成本预测和风险评估"""
        try:
            # 第一步：执行成本预测
            cost_result = self._call_mcp_for_cost_prediction(data)
            if "error" in cost_result:
                return cost_result
            
            # 从成本预测结果中提取预测成本用于风险评估
            predicted_cost = 1.0  # 默认值
            if "result" in cost_result and isinstance(cost_result["result"], str):
                try:
                    cost_data = json.loads(cost_result["result"])
                    if "predicted_cost" in cost_data:
                        predicted_cost = float(cost_data["predicted_cost"])
                except (json.JSONDecodeError, ValueError, KeyError):
                    self.logger.warning("无法从成本预测结果中提取预测成本，使用默认值")
            
            # 第二步：执行风险评估，使用预测成本
            risk_data = data.copy()
            risk_data["predicted_cost"] = predicted_cost
            risk_result = self._call_mcp_for_risk_assessment(risk_data)
            if "error" in risk_result:
                return risk_result
            
            # 第三步：组合结果
            comprehensive_result = {
                "analysis_type": "comprehensive_analysis",
                "cost_prediction": cost_result,
                "risk_assessment": risk_result,
                "summary": {
                    "predicted_cost": predicted_cost,
                    "analysis_completed": True,
                    "components": ["成本预测", "风险评估"]
                }
            }
            
            return {
                "success": True,
                "result": json.dumps(comprehensive_result, ensure_ascii=False, indent=2),
                "message": "综合分析完成：成本预测 + 风险评估"
            }
            
        except Exception as e:
            self.logger.error(f"综合分析执行失败: {e}")
            return {
                "error": f"综合分析执行失败: {str(e)}",
                "success": False
            }

    # ================================
    # 增强分析方法
    # ================================

    def _analyze_cost_structure(self, mcp_result: Dict[str, Any]) -> Dict[str, Any]:
        """分析成本结构"""
        analysis = {
            "cost_breakdown_available": False,
            "key_insights": []
        }
        
        try:
            # 如果MCP结果中包含成本分解数据
            if "cost_breakdown" in mcp_result:
                analysis["cost_breakdown_available"] = True
                analysis["cost_structure"] = mcp_result["cost_breakdown"]
                analysis["key_insights"].append("成本结构分析已完成，包含物理基础设施、数字化系统、集成服务三大维度")
            
            analysis["key_insights"].extend([
                "基于机器学习算法的智能成本预测已完成",
                "预测结果包含±15%置信区间，量化了预测不确定性",
                "建议关注关键成本驱动因素的变化影响"
            ])
            
        except Exception as e:
            self.logger.warning(f"成本结构分析失败: {e}")
            analysis["key_insights"] = ["成本预测已完成，建议进一步分析成本构成"]
        
        return analysis

    def _generate_industry_comparison(self, capacity_mw: float, project_type: str) -> Dict[str, Any]:
        """使用LLM生成行业对比分析"""
        try:
            # 构建LLM分析提示词
            analysis_prompt = f"""
            作为水电行业资深分析专家，请对以下项目进行行业对比分析：

            ## 项目基本信息
            装机容量: {capacity_mw} MW
            项目类型: {project_type}

            ## 请提供以下对比分析
            1. **项目规模定位**：在同类型项目中的规模等级和特点
            2. **成本基准对比**：与行业平均水平的成本对比分析
            3. **市场竞争地位**：在当前市场环境中的竞争优势和挑战
            4. **技术成熟度**：该类型项目的技术发展水平和风险评估
            5. **政策环境影响**：相关政策对该类型项目的支持程度

            请基于真实的行业数据和市场情况进行客观分析。
            """
            
            # 调用LLM进行分析
            llm_response = self.call_llm(analysis_prompt)
            
            return {
                "comparison_content": llm_response,
                "analysis_method": "LLM驱动的行业对比分析",
                "project_info": {
                    "capacity_mw": capacity_mw,
                    "project_type": project_type
                },
                "generated_at": self._get_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"LLM行业对比分析失败: {e}")
            raise Exception(f"LLM分析失败: {str(e)}")

    def _generate_cost_optimization_suggestions(self, mcp_result: Dict[str, Any]) -> Dict[str, Any]:
        """使用LLM生成成本优化建议"""
        try:
            # 构建LLM分析提示词
            analysis_prompt = f"""
            作为资深成本控制专家，请基于以下MCP服务的成本预测结果，提供专业的成本优化建议：

            ## MCP成本预测结果
            {json.dumps(mcp_result, ensure_ascii=False, indent=2)}

            ## 请提供以下优化建议
            1. **设计优化**：技术方案和工程设计的成本优化策略
            2. **采购优化**：设备采购和供应商管理的成本控制措施
            3. **施工优化**：施工组织和进度管理的效率提升方案
            4. **技术创新**：新技术应用带来的成本节约机会
            5. **风险防控**：避免成本超支的风险管控措施

            请基于真实的预测数据提供具体可操作的优化建议。
            """
            
            # 调用LLM进行分析
            llm_response = self.call_llm(analysis_prompt)
            
            return {
                "optimization_content": llm_response,
                "analysis_method": "LLM驱动的成本优化分析",
                "data_source": "基于MCP服务成本预测结果",
                "generated_at": self._get_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"LLM成本优化分析失败: {e}")
            raise Exception(f"LLM分析失败: {str(e)}")

    def calculate_confidence_score(self, result: Dict[str, Any]) -> float:
        """基于MCP服务结果质量计算置信度"""
        try:
            # 基础置信度
            base_confidence = 0.7
            
            # MCP服务成功调用的置信度因子
            mcp_success_factor = 0.25 if result.get("mcp_result") else 0.0
            
            # 数据质量因子
            data_quality = result.get("data_quality", 0.85)
            data_factor = (data_quality - 0.5) * 0.15
            
            # 预测精度因子
            prediction_accuracy = result.get("prediction_accuracy", 0.9)
            accuracy_factor = (prediction_accuracy - 0.5) * 0.1
            
            # 计算最终置信度
            confidence = base_confidence + mcp_success_factor + data_factor + accuracy_factor
            
            return min(max(confidence, 0.0), 1.0)  # 确保在0-1范围内
            
        except Exception as e:
            self.logger.error(f"计算置信度时出错: {e}")
            return 0.6  # 默认置信度

    def generate_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """基于MCP服务结果生成建议"""
        recommendations = []
        
        try:
            # 从MCP结果中提取建议
            if "mcp_result" in result:
                mcp_result = result["mcp_result"]
                if "recommendations" in mcp_result:
                    recommendations.extend(mcp_result["recommendations"])
                if "analysis" in mcp_result and "suggestions" in mcp_result["analysis"]:
                    recommendations.extend(mcp_result["analysis"]["suggestions"])
            
            # 去重并返回
            unique_recommendations = list(set(recommendations))
            
            # 如果没有找到建议，提供默认建议
            if not unique_recommendations:
                unique_recommendations = [
                    "建议进行详细的成本分解分析",
                    "考虑采用模块化设计降低成本",
                    "建议与供应商进行价格谈判",
                    "优化施工工期以降低人工成本",
                    "考虑使用新技术提高施工效率"
                ]
            
            return unique_recommendations
            
        except Exception as e:
            self.logger.error(f"生成建议时出错: {e}")
            return [
                "建议进行详细的成本分解分析",
                "考虑采用模块化设计降低成本",
                "建议与供应商进行价格谈判",
                "优化施工工期以降低人工成本",
                "考虑使用新技术提高施工效率"
            ]
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # ============================================================================
    # MCP服务调用方法
    # ============================================================================
    
    def _call_mcp_for_cost_prediction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP服务进行成本预测"""
        return self.call_mcp_tool(
            "predict_hydropower_cost",
            arguments={
                "capacity_mw": data.get("capacity_mw", 100),
                "project_type": data.get("project_type", "常规大坝"),
                "construction_period": data.get("construction_period", 3),
                "economic_indicator": data.get("economic_indicator", 1.0)
            }
        )
    
    def _call_mcp_for_risk_assessment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP服务进行风险评估"""
        return self.call_mcp_tool(
            "assess_project_risk",
            arguments={
                "predicted_cost": data.get("predicted_cost", 1.0),
                "project_type": data.get("project_type", "常规大坝"),
                "capacity_mw": data.get("capacity_mw", 100),
                "construction_period": data.get("construction_period", 3),
                "client_type": data.get("client_type", "国企"),
                "project_complexity": data.get("project_complexity", "中等"),
                "project_description": data.get("project_description", ""),
                "location": data.get("location", "四川"),
                "environmental_conditions": data.get("environmental_conditions", "")
            }
        )
    

    
    # ============================================================================
    # 综合LLM分析方法
    # ============================================================================
    
    # 已删除复杂的LLM分析方法，专注于MCP服务调用
