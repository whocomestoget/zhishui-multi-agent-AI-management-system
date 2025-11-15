#!/usr/bin/env python3
"""
智水信息Multi-Agent智能分析系统 - 财务分析专家 
真正由LLM驱动的智能分析，不包含任何硬编码假数据

Author: 商海星辰队
Version: 2.0.0 (Stdio MCP)
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional
from .business_agent import BusinessAgent, AgentTask, AgentResult

class FinancialAgent(BusinessAgent):
    """财务分析专家Agent - 完全由LLM驱动"""
    
    def __init__(self):
        """初始化财务分析专家"""
        super().__init__(
            agent_id="financial_analyst",
            agent_name="财务分析专家",
            mcp_service="financial"
        )
        
        # 财务分析专业配置
        self.analysis_types = {
            "cash_flow_prediction": "现金流预测分析",      # 对应 predict_cash_flow 工具
            "investment_analysis": "投资回报评估",         # 对应 calculate_IRR_metrics 工具
            "budget_monitoring": "预算执行监控",           # 对应 monitor_budget_execution 工具
            "financial_consultation": "财务咨询服务"       # 对应 financial_qa_assistant 工具
        }
        
        self.logger.info("财务分析专家初始化完成")

    def get_system_prompt(self) -> str:
        """获取财务分析专家的系统提示词"""
        return """你是智水信息技术有限公司的资深财务分析专家，拥有15年以上电力水利行业财务管理经验。

## 🎯 专业定位与职责
你是水电企业财务决策的核心智囊，专精于：
- **现金流预测与管理**：运用改进灰色马尔科夫模型，为企业提供3-12期精准现金流预测
- **投资决策支持**：通过IRR、NPV等核心指标，科学评估项目投资价值和风险
- **预算执行监控**：基于SFA随机前沿分析，量化预算执行效率，识别改进机会
- **财务战略咨询**：涵盖电力、水利、IT信息化行业的专业财务知识服务

## 🏢 行业背景深度理解

### 水电企业财务特点
- **资产密集型**：固定资产占比高，折旧政策影响重大
- **现金流稳定性**：发电收入相对稳定，但受汛期、用电需求波动影响
- **投资回收期长**：水电站建设投资巨大，回收期通常10-20年
- **政策敏感性强**：电价政策、环保政策直接影响经营效益

### 关键财务指标体系
- **盈利能力指标**：发电利润率、资产回报率(ROA)、净资产收益率(ROE)
- **运营效率指标**：设备利用率、度电成本、维护费用率
- **财务风险指标**：资产负债率、流动比率、利息保障倍数
- **发展能力指标**：装机容量增长率、营收增长率、技改投资强度

## 💼 分析原则

### 数据驱动决策
- **绝不编造数据**：任何分析都必须基于MCP服务返回的真实数据
- **透明化分析**：清楚说明分析的数据来源和计算逻辑
- **量化评估**：用具体数字支撑分析结论
- **风险意识**：充分识别和提示潜在风险

### 专业分析框架
- **现状分析**：基于当前数据的客观描述
- **趋势判断**：基于历史数据的发展趋势分析
- **风险识别**：潜在风险点和影响程度评估
- **决策建议**：具体可操作的改进措施

你现在需要基于MCP服务返回的真实数据进行专业的财务分析，提供有价值的洞察和建议。"""

    def get_required_fields(self) -> List[str]:
        """获取财务分析必需的字段"""
        return ["analysis_type"]

    def validate_input_data(self, task: AgentTask) -> tuple[bool, List[str]]:
        """验证财务分析输入数据"""
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
        
        # 根据分析类型检查特定字段 - 兼容start_optimized.py中的数据结构
        if analysis_type == "cash_flow_prediction":
            # 检查cash_flow_data.historical_data或直接的historical_data
            if ("cash_flow_data" not in business_data or 
                "historical_data" not in business_data.get("cash_flow_data", {})) and \
               "historical_data" not in business_data:
                errors.append("现金流预测需要历史数据(cash_flow_data.historical_data)")
        
        elif analysis_type == "investment_analysis":
            # 检查investment_data结构或直接字段
            investment_data = business_data.get("investment_data", {})
            if ("project_cash_flows" not in investment_data and "cash_flows" not in business_data) or \
               ("initial_investment" not in investment_data and "initial_investment" not in business_data):
                errors.append("投资评估需要现金流序列(investment_data.project_cash_flows)和初始投资(investment_data.initial_investment)")
        
        elif analysis_type == "budget_monitoring":
            # 检查budget_data结构或直接字段
            budget_data = business_data.get("budget_data", {})
            if ("project_data" not in budget_data and "project_revenue" not in business_data) or \
               ("project_data" not in budget_data and "costs_data" not in business_data):
                errors.append("预算监控需要项目数据(budget_data.project_data)")
        
        elif analysis_type == "financial_consultation":
            if "question" not in business_data:
                errors.append("财务咨询需要问题内容(question)")
        
        return len(errors) == 0, errors

    def perform_analysis(self, data: Dict[str, Any], task: AgentTask) -> Dict[str, Any]:
        """执行财务分析 - 统一使用stdio MCP协议"""
        # 从预处理的数据中获取analysis_type
        input_data = data.get("input_data", data)  # 兼容处理
        analysis_type = input_data.get("analysis_type")
        
        self.logger.info(f"开始财务分析，类型: {analysis_type}")
        self.logger.debug(f"输入数据结构: {list(data.keys())}")
        self.logger.debug(f"业务数据结构: {list(input_data.keys())}")
        
        try:
            # 调用MCP服务获取分析结果
            if analysis_type == "cash_flow_prediction":
                mcp_result = self._call_mcp_for_cash_flow(input_data)
            elif analysis_type == "investment_analysis":
                mcp_result = self._call_mcp_for_investment(input_data)
            elif analysis_type == "budget_monitoring":
                mcp_result = self._call_mcp_for_budget(input_data)
            elif analysis_type == "financial_consultation":
                mcp_result = self._call_mcp_for_consultation(input_data)
            else:
                raise ValueError(f"未实现的分析类型: {analysis_type}")
            
            if "error" in mcp_result:
                return mcp_result
            
            # 构建最终结果
            result = {
                "analysis_type": self.analysis_types.get(analysis_type, analysis_type),
                "timestamp": self._get_timestamp(),
                "input_parameters": input_data,
                "mcp_result": mcp_result,
                "status": "success",
                "data_quality": "high" if mcp_result else "low"
            }
            
            return result
                
        except Exception as e:
            self.logger.error(f"财务分析执行失败: {e}")
            return {"error": f"分析执行失败: {str(e)}"}





    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # ============================================================================
    # MCP服务调用方法
    # ============================================================================
    
    def _call_mcp_for_cash_flow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP服务进行现金流预测"""
        historical_data = data["historical_data"]
        periods = data.get("periods", 6)
        data_type = data.get("data_type", "csv")  # 默认使用csv格式
        
        # 修复：使用arguments字典传递参数，添加data_type参数
        return self.call_mcp_tool(
            "predict_cash_flow",
            arguments={
                "historical_data": historical_data,
                "periods": periods,
                "data_type": data_type
            }
        )
    
    def _call_mcp_for_investment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP服务进行投资回报计算"""
        cash_flows = data["cash_flows"]
        initial_investment = data["initial_investment"]
        project_name = data.get("project_name", "投资项目")
        
        # 修复：使用arguments字典传递参数，纠正参数名称
        return self.call_mcp_tool(
            "calculate_IRR_metrics",
            arguments={
                "cash_flows": cash_flows,  # 修正参数名称：应该是cash_flows而不是project_cash_flows
                "initial_investment": initial_investment,
                "project_name": project_name
            }
        )
    
    def _call_mcp_for_budget(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP服务进行预算监控"""
        # 直接使用project_data字段，匹配start_optimized.py中的数据结构
        project_data = data.get("project_data", "")
        project_name = data.get("project_name", "预算项目")
        data_format = data.get("data_format", "csv")  # 默认使用csv格式
        
        # 修复：使用arguments字典传递参数，确保数据格式正确
        return self.call_mcp_tool(
            "monitor_budget_execution",
            arguments={
                "project_data": project_data,
                "project_name": project_name,
                "data_format": data_format
            }
        )
    
    def _call_mcp_for_consultation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP服务进行财务咨询"""
        question = data["question"]
        industry = data.get("industry", "general")
        
        # 修复：使用arguments字典传递参数
        return self.call_mcp_tool(
            "financial_qa_assistant",
            arguments={
                "question": question,
                "industry": industry
            }
        )
    



    def calculate_confidence_score(self, result: Dict[str, Any]) -> float:
        """基于MCP服务结果质量计算置信度"""
        if "error" in result:
            return 0.0
        
        confidence_factors = []
        
        # MCP服务结果质量评估
        if "mcp_result" in result and "error" not in result["mcp_result"]:
            mcp_result = result["mcp_result"]
            confidence_factors.append(0.6)  # MCP服务成功调用
            
            # 数据完整性评估
            data_quality = mcp_result.get("data_quality", 0.7)
            confidence_factors.append(data_quality * 0.3)
            
            # 预测精度评估
            prediction_accuracy = mcp_result.get("prediction_accuracy", 0.7)
            confidence_factors.append(prediction_accuracy * 0.1)
        else:
            # MCP服务调用失败
            confidence_factors.append(0.2)
        
        return min(sum(confidence_factors), 1.0) if confidence_factors else 0.3

    def generate_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """基于MCP服务结果生成财务管理建议"""
        try:
            recommendations = []
            
            # 从MCP结果中提取建议
            if "mcp_result" in result:
                mcp_result = result["mcp_result"]
                
                # 提取MCP服务返回的建议
                if "recommendations" in mcp_result:
                    mcp_rec = mcp_result["recommendations"]
                    if isinstance(mcp_rec, list):
                        for rec in mcp_rec:
                            if isinstance(rec, dict):
                                recommendations.append(rec.get("action", str(rec)))
                            else:
                                recommendations.append(str(rec))
                
                # 从分析结果中提取建议
                if "analysis" in mcp_result and isinstance(mcp_result["analysis"], dict):
                    analysis = mcp_result["analysis"]
                    if "suggestions" in analysis:
                        suggestions = analysis["suggestions"]
                        if isinstance(suggestions, list):
                            recommendations.extend([str(s) for s in suggestions])
            
            # 去重并限制数量
            unique_recommendations = list(set(recommendations))
            return unique_recommendations[:5] if unique_recommendations else [
                "建议进行详细的财务分析", 
                "制定合理的投资策略", 
                "优化现金流管理",
                "加强成本控制",
                "提升资金使用效率"
            ]
            
        except Exception as e:
            self.logger.error(f"生成建议失败: {e}")
            return [
                "建议进行详细的财务分析", 
                "制定合理的投资策略", 
                "优化现金流管理",
                "加强成本控制",
                "提升资金使用效率"
            ]
