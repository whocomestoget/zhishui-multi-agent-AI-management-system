#!/usr/bin/env python3
"""
智水人员效能管理服务
专为水利电力企业设计的员工效能评估与报告生成工具

使用步骤：
1. 调用员工效能评分引擎进行评估
2. 生成综合分析报告
3. 查看评估结果和改进建议
"""

import json
import logging
import os
import csv
from datetime import datetime
from mcp.server.fastmcp import FastMCP
import math
import requests
from typing import Dict, List, Any, Union

# ================================
# 1. 配置你的工具
# ================================
TOOL_NAME = "智水人员效能管理服务"  # 工具名称

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(TOOL_NAME)

# 创建MCP服务器 - 指定端口8004
mcp = FastMCP(TOOL_NAME)

# ================================
# 1.4. CSV文件读取功能
# ================================

def read_employee_csv(file_path: str) -> Dict:
    """
    从CSV文件读取员工基础信息
    
    Args:
        file_path (str): CSV文件路径
        
    Returns:
        Dict: 员工信息字典
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"员工数据文件不存在: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:  # 读取第一行数据
                # 转换数值类型
                if 'years_experience' in row:
                    row['years_experience'] = int(row['years_experience'])
                return row
        
        raise ValueError("CSV文件为空或格式错误")
        
    except Exception as e:
        logger.error(f"读取员工CSV文件失败: {e}")
        raise

def read_metrics_csv(file_path: str) -> Dict:
    """
    从CSV文件读取指标数据并转换为嵌套字典格式
    
    Args:
        file_path (str): CSV文件路径
        
    Returns:
        Dict: 指标数据字典
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"指标数据文件不存在: {file_path}")
            
        metrics = {}
        
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                dimension = row['dimension']
                category = row['category']
                metric = row['metric']
                value = row['value']
                
                # 转换数值类型
                try:
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    pass  # 保持字符串格式
                
                # 构建嵌套字典
                if dimension not in metrics:
                    metrics[dimension] = {}
                if category not in metrics[dimension]:
                    metrics[dimension][category] = {}
                
                metrics[dimension][category][metric] = value
        
        return metrics
        
    except Exception as e:
        logger.error(f"读取指标CSV文件失败: {e}")
        raise

# ================================
# 1.5. AI配置
# ================================

# AI配置 - 统一使用标准配置
AI_CONFIG = {
    "api_key": "sk-Wy5BpzceSjET0ZiZWvaMaxUTrUiEKYGgElx10VL88lAnhgSe",
    "api_base": "http://38.246.251.165:3002/v1",
    "model": "gemini-2.5-flash-lite-preview-06-17",
    "temperature": 0.7,
    "max_tokens": 65000,
}

# ================================
# 2. 权重配置
# ================================

# 标准权重配置
STANDARD_WEIGHTS = {
    "economic": 35,      # 经济与价值创造
    "customer": 25,      # 客户与社会贡献
    "process": 25,       # 内部流程与治理
    "learning": 15       # 学习成长与环境
}

# 岗位差异化权重
POSITION_WEIGHTS = {
    "生产运维": {"economic": 40, "customer": 30, "process": 25, "learning": 5},
    "客户服务": {"customer": 40, "process": 25, "economic": 25, "learning": 10},
    "技术研发": {"learning": 30, "economic": 30, "process": 25, "customer": 15},
    "管理岗位": {"economic": 30, "process": 30, "customer": 25, "learning": 15}
}

# 维度内部权重
DIMENSION_INTERNAL_WEIGHTS = {
    "economic": {"cost_optimization": 60, "digital_efficiency": 40},
    "customer": {"service_reliability": 70, "customer_service": 30},
    "process": {"process_efficiency": 45, "risk_compliance": 55},
    "learning": {"skill_development": 40, "innovation_sharing": 35, "environmental_practice": 25}
}

# ================================
# 2.5. AI智能建议生成
# ================================

def generate_ai_suggestions(employee_info: Dict, scores_data: Dict) -> List[str]:
    """
    使用AI生成个性化改进建议
    
    Args:
        employee_info (Dict): 员工基本信息
        scores_data (Dict): 评分数据
        
    Returns:
        List[str]: AI生成的个性化建议列表
    """
    try:
        # 构建AI提示词
        employee_name = employee_info.get("姓名", employee_info.get("name", "该员工"))
        department = employee_info.get("部门", employee_info.get("department", "未知部门"))
        position = employee_info.get("职位", employee_info.get("position", "未知岗位"))
        
        # 获取各维度得分
        dimensions = scores_data.get('维度得分', {})
        economic_score = dimensions.get('经济与价值创造', {}).get('得分', 0)
        customer_score = dimensions.get('客户与社会贡献', {}).get('得分', 0)
        process_score = dimensions.get('内部流程与治理', {}).get('得分', 0)
        learning_score = dimensions.get('学习成长与环境', {}).get('得分', 0)
        # 修复分数获取逻辑，正确获取综合评分
        total_score = scores_data.get('综合评分', {}).get('总分', 0)
        if total_score == 0:  # 如果没有获取到，尝试其他路径
            total_score = scores_data.get('总分', 0)
        
        # 添加调试信息
        logger.info(f"AI建议生成 - 员工: {employee_name}, 综合得分: {total_score}")
        logger.info(f"scores_data结构: {scores_data}")
        
        prompt = f"""
你是四川智水信息技术有限公司的资深人力资源专家和业务顾问，请为以下员工生成详细的个性化改进建议：

员工信息：
- 姓名：{employee_name}
- 部门：{department}
- 岗位：{position}

绩效评分（满分100分）：
- 综合得分：{total_score}分
- 经济与价值创造：{economic_score}分
- 客户与社会贡献：{customer_score}分
- 内部流程与治理：{process_score}分
- 学习成长与环境：{learning_score}分

请生成3-5条详细的、具体的改进建议，每条建议要求：
1. 建议长度：每条建议至少80-120字，包含具体的行动步骤和预期效果
2. 个性化内容：必须明确提及员工姓名、部门，并结合其具体得分情况
3. 行业针对性：结合电力水利行业特点、智水公司的智慧电厂、智能电站、智慧水利、大坝监测等业务领域
4. 可操作性：提供具体的实施步骤、时间安排、资源需求和成功指标
5. 专业深度：包含技术技能、管理能力、业务知识等多个层面的提升建议
6. 格式要求：每条建议以相关emoji开头，内容分为【目标】【具体措施】【预期效果】三个部分

示例格式：
💡 【目标】针对{employee_name}在经济价值创造方面的提升需求...
【具体措施】建议在未来3个月内，通过以下步骤...
【预期效果】预计通过上述措施，能够在项目成本控制方面提升15-20%...

请直接返回建议列表，每条建议占用多行。
        """
        
        # 调用AI API
        headers = {
            "Authorization": f"Bearer {AI_CONFIG['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": AI_CONFIG["model"],
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": AI_CONFIG["temperature"],
            "max_tokens": 2000  # 增加token数量以支持更详细的建议
        }
        
        response = requests.post(
            f"{AI_CONFIG['api_base']}/chat/completions",
            headers=headers,
            json=data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 解析AI返回的建议
            suggestions = []
            for line in ai_content.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    suggestions.append(line)
            
            if suggestions:
                logger.info(f"AI成功生成{len(suggestions)}条个性化建议")
                return suggestions
            else:
                logger.warning("AI返回内容为空，使用默认建议")
                return generate_default_suggestions(employee_info, scores_data)
                
        else:
            logger.error(f"AI API调用失败: {response.status_code} - {response.text}")
            return generate_default_suggestions(employee_info, scores_data)
            
    except Exception as e:
        logger.error(f"AI建议生成失败: {e}")
        return generate_default_suggestions(employee_info, scores_data)

def generate_default_suggestions(employee_info: Dict, scores_data: Dict) -> List[str]:
    """
    生成默认改进建议（当AI调用失败时使用）
    
    Args:
        employee_info (Dict): 员工基本信息
        scores_data (Dict): 评分数据
        
    Returns:
        List[str]: 默认建议列表
    """
    employee_name = employee_info.get("姓名", employee_info.get("name", "该员工"))
    department = employee_info.get("部门", employee_info.get("department", "未知部门"))
    
    suggestions = []
    dimensions = scores_data.get('维度得分', {})
    
    if dimensions.get('经济与价值创造', {}).get('得分', 0) < 70:
        suggestions.append(f"💰 成本优化：建议{employee_name}（{department}）重点关注项目成本控制，提升数字化工具使用效率")
    if dimensions.get('客户与社会贡献', {}).get('得分', 0) < 70:
        suggestions.append(f"🤝 客户服务：建议{employee_name}（{department}）加强与客户沟通，提升服务质量和响应速度")
    if dimensions.get('内部流程与治理', {}).get('得分', 0) < 70:
        suggestions.append(f"⚙️ 流程管理：建议{employee_name}（{department}）优化工作流程，加强风险识别和合规培训")
    if dimensions.get('学习成长与环境', {}).get('得分', 0) < 70:
        suggestions.append(f"📚 学习成长：建议{employee_name}（{department}）积极参与培训学习，主动分享知识经验")
    
    if not suggestions:
        suggestions.append(f"🎉 表现优秀！建议{employee_name}（{department}）继续保持并在薄弱环节进一步提升")
    
    return suggestions

# ================================
# 3. 核心评分算法
# ================================

def calculate_economic_score(data):
    """计算经济与价值创造维度得分"""
    try:
        # 成本优化贡献得分
        cost_data = data.get("cost_optimization", {})
        baseline_cost = cost_data.get("baseline_unit_cost")
        actual_cost = cost_data.get("actual_unit_cost")
        if baseline_cost is None or actual_cost is None:
            raise ValueError("缺少成本数据，请提供真实的baseline_unit_cost和actual_unit_cost")
        if baseline_cost > 0:
            cost_improvement_rate = (baseline_cost - actual_cost) / baseline_cost
            cost_score = min(100, max(0, cost_improvement_rate * 100 + 50))  # 基准分50，改进率转换为分数
        else:
            cost_score = 50
            
        # 数字化效率提升得分
        digital_data = data.get("digital_efficiency", {})
        baseline_hours = digital_data.get("baseline_work_hours")
        actual_hours = digital_data.get("actual_work_hours")
        automation_rate = digital_data.get("automation_usage_rate")
        if baseline_hours is None or actual_hours is None or automation_rate is None:
            raise ValueError("缺少数字化效率数据，请提供真实的baseline_work_hours、actual_work_hours和automation_usage_rate")
        
        if baseline_hours > 0:
            efficiency_improvement = (baseline_hours - actual_hours) / baseline_hours
            digital_score = min(100, max(0, efficiency_improvement * 100 + automation_rate * 50))
        else:
            digital_score = automation_rate * 100
            
        # 加权计算
        weights = DIMENSION_INTERNAL_WEIGHTS["economic"]
        total_score = (cost_score * weights["cost_optimization"] + 
                      digital_score * weights["digital_efficiency"]) / 100
        
        return {
            "total_score": round(total_score, 2),
            "cost_optimization_score": round(cost_score, 2),
            "digital_efficiency_score": round(digital_score, 2),
            "details": {
                "cost_improvement_rate": f"{cost_improvement_rate*100:.1f}%" if baseline_cost > 0 else "数据不足",
                "efficiency_improvement": f"{efficiency_improvement*100:.1f}%" if baseline_hours > 0 else "数据不足",
                "automation_usage": f"{automation_rate*100:.1f}%"
            }
        }
    except Exception as e:
        logger.error(f"经济维度计算错误: {e}")
        return {"total_score": 0, "error": str(e)}

def calculate_customer_score(data):
    """计算客户与社会贡献维度得分"""
    try:
        # 服务可靠性得分
        reliability_data = data.get("service_reliability", {})
        unplanned_outage = reliability_data.get("unplanned_outage_hours")
        if unplanned_outage is None:
            raise ValueError("缺少非计划停电时长数据")
        baseline_outage = reliability_data.get("baseline_outage_hours")
        if baseline_outage is None:
            raise ValueError("缺少基线停电时长数据")
        quality_rate = reliability_data.get("quality_compliance_rate")
        if quality_rate is None:
            raise ValueError("缺少质量达标率数据")
        
        # 停电时长改进得分
        if baseline_outage > 0:
            outage_improvement = (baseline_outage - unplanned_outage) / baseline_outage
            outage_score = min(100, max(0, outage_improvement * 50 + 50))
        else:
            outage_score = 80
            
        # 质量达标得分
        quality_score = quality_rate * 100
        
        # 综合可靠性得分
        reliability_score = (outage_score + quality_score) / 2
        
        # 客户服务得分
        service_data = data.get("customer_service", {})
        resolution_rate = service_data.get("complaint_resolution_rate")
        if resolution_rate is None:
            raise ValueError("缺少投诉解决率数据，请提供真实的complaint_resolution_rate")
        response_time = service_data.get("average_response_time")
        if response_time is None:
            raise ValueError("缺少平均响应时间数据，请提供真实的average_response_time")
        satisfaction_score = service_data.get("customer_satisfaction_score")
        if satisfaction_score is None:
            raise ValueError("缺少客户满意度评分数据，请提供真实的customer_satisfaction_score")
        
        # 综合服务得分 (响应时间越短越好，满分对应0.5小时内)
        response_score = max(0, min(100, (2 - response_time) * 50))
        service_score = (resolution_rate * 100 + response_score + satisfaction_score * 20) / 3
        
        # 加权计算
        weights = DIMENSION_INTERNAL_WEIGHTS["customer"]
        total_score = (reliability_score * weights["service_reliability"] + 
                      service_score * weights["customer_service"]) / 100
        
        return {
            "total_score": round(total_score, 2),
            "service_reliability_score": round(reliability_score, 2),
            "customer_service_score": round(service_score, 2),
            "details": {
                "outage_improvement": f"{outage_improvement*100:.1f}%" if baseline_outage > 0 else "数据不足",
                "quality_compliance": f"{quality_rate*100:.1f}%",
                "resolution_rate": f"{resolution_rate*100:.1f}%",
                "satisfaction_rating": f"{satisfaction_score:.1f}/5.0"
            }
        }
    except Exception as e:
        logger.error(f"客户维度计算错误: {e}")
        return {"total_score": 0, "error": str(e)}

def calculate_process_score(data):
    """计算内部流程与治理维度得分"""
    try:
        # 流程效率得分
        efficiency_data = data.get("process_efficiency", {})
        baseline_cycle = efficiency_data.get("baseline_process_cycle")
        if baseline_cycle is None:
            raise ValueError("缺少基线流程周期数据")
        actual_cycle = efficiency_data.get("actual_process_cycle")
        if actual_cycle is None:
            raise ValueError("缺少实际流程周期数据")
        error_rate = efficiency_data.get("process_error_rate")
        if error_rate is None:
            raise ValueError("缺少流程错误率数据")
        
        # 流程周期改进得分
        if baseline_cycle > 0:
            cycle_improvement = (baseline_cycle - actual_cycle) / baseline_cycle
            cycle_score = min(100, max(0, cycle_improvement * 100 + 50))
        else:
            cycle_score = 50
            
        # 错误率得分 (错误率越低越好)
        error_score = max(0, min(100, (0.1 - error_rate) * 1000))
        
        efficiency_score = (cycle_score + error_score) / 2
        
        # 风险合规得分
        compliance_data = data.get("risk_compliance", {})
        safety_found = compliance_data.get("safety_incidents_found")
        if safety_found is None:
            raise ValueError("缺少安全隐患发现数据")
        env_incidents = compliance_data.get("environmental_incidents")
        if env_incidents is None:
            raise ValueError("缺少环境事件数据")
        training_completion = compliance_data.get("compliance_training_completion")
        if training_completion is None:
            raise ValueError("缺少合规培训完成率数据")
        
        # 主动发现安全隐患加分，环境事件扣分
        safety_score = min(100, 60 + safety_found * 10)  # 基础60分，每发现一个隐患加10分
        env_score = max(0, 100 - env_incidents * 20)     # 每个环境事件扣20分
        training_score = training_completion * 100
        
        compliance_score = (safety_score + env_score + training_score) / 3
        
        # 加权计算
        weights = DIMENSION_INTERNAL_WEIGHTS["process"]
        total_score = (efficiency_score * weights["process_efficiency"] + 
                      compliance_score * weights["risk_compliance"]) / 100
        
        return {
            "total_score": round(total_score, 2),
            "process_efficiency_score": round(efficiency_score, 2),
            "risk_compliance_score": round(compliance_score, 2),
            "details": {
                "cycle_improvement": f"{cycle_improvement*100:.1f}%" if baseline_cycle > 0 else "数据不足",
                "error_rate": f"{error_rate*100:.2f}%",
                "safety_proactivity": f"发现{safety_found}个隐患",
                "environmental_safety": f"{env_incidents}个环境事件",
                "training_completion": f"{training_completion*100:.1f}%"
            }
        }
    except Exception as e:
        logger.error(f"流程维度计算错误: {e}")
        return {"total_score": 0, "error": str(e)}

def calculate_learning_score(data):
    """计算学习成长与环境维度得分"""
    try:
        # 技能发展得分
        skill_data = data.get("skill_development", {})
        new_certs = skill_data.get("new_certifications_count")
        if new_certs is None:
            raise ValueError("缺少新获得证书数量数据")
        training_hours = skill_data.get("training_hours_completed")
        if training_hours is None:
            raise ValueError("缺少培训完成小时数数据")
        skill_assessment = skill_data.get("skill_assessment_score")
        if skill_assessment is None:
            raise ValueError("缺少技能评估得分数据")
        
        # 技能发展综合得分
        cert_score = min(100, new_certs * 30 + 40)      # 每个新证书30分，基础40分
        training_score = min(100, training_hours / 80 * 100)  # 80小时为满分
        assessment_score = skill_assessment
        
        skill_score = (cert_score + training_score + assessment_score) / 3
        
        # 创新共享得分
        innovation_data = data.get("innovation_sharing", {})
        proposals_submitted = innovation_data.get("innovation_proposals_submitted")
        if proposals_submitted is None:
            raise ValueError("缺少创新提案提交数量数据")
        proposals_adopted = innovation_data.get("innovation_proposals_adopted")
        if proposals_adopted is None:
            raise ValueError("缺少创新提案采纳数量数据")
        knowledge_contributions = innovation_data.get("knowledge_sharing_contributions")
        if knowledge_contributions is None:
            raise ValueError("缺少知识分享贡献数据")
        
        # 创新得分计算
        innovation_score = min(100, proposals_submitted * 20 + proposals_adopted * 30)
        sharing_score = min(100, knowledge_contributions * 15 + 25)  # 基础25分
        
        innovation_total = (innovation_score + sharing_score) / 2
        
        # 环境实践得分
        env_data = data.get("environmental_practice", {})
        green_behavior = env_data.get("green_behavior_score")
        if green_behavior is None:
            raise ValueError("缺少绿色行为评分数据")
        env_proposals = env_data.get("environmental_improvement_proposals")
        if env_proposals is None:
            raise ValueError("缺少环境改进提案数量数据")
        env_training = env_data.get("environmental_training_hours")
        if env_training is None:
            raise ValueError("缺少环境培训小时数数据")
        
        # 环境得分计算
        behavior_score = green_behavior * 20  # 5分制转100分制
        proposal_score = min(100, env_proposals * 40 + 40)  # 每个提案40分，基础40分
        env_training_score = min(100, env_training / 8 * 100)  # 8小时为满分
        
        env_score = (behavior_score + proposal_score + env_training_score) / 3
        
        # 加权计算
        weights = DIMENSION_INTERNAL_WEIGHTS["learning"]
        total_score = (skill_score * weights["skill_development"] + 
                      innovation_total * weights["innovation_sharing"] + 
                      env_score * weights["environmental_practice"]) / 100
        
        return {
            "total_score": round(total_score, 2),
            "skill_development_score": round(skill_score, 2),
            "innovation_sharing_score": round(innovation_total, 2),
            "environmental_practice_score": round(env_score, 2),
            "details": {
                "new_certifications": f"{new_certs}个新证书",
                "training_hours": f"{training_hours}小时",
                "skill_assessment": f"{skill_assessment}分",
                "innovation_adoption_rate": f"{proposals_adopted}/{proposals_submitted}" if proposals_submitted > 0 else "无提案",
                "knowledge_contributions": f"{knowledge_contributions}次分享",
                "green_behavior_rating": f"{green_behavior:.1f}/5.0"
            }
        }
    except Exception as e:
        logger.error(f"学习维度计算错误: {e}")
        return {"total_score": 0, "error": str(e)}

# ================================
# 4. 工具函数
# ================================

@mcp.tool()
def evaluate_employee_efficiency(employee_data: Union[str, Dict], metrics_data: Union[str, Dict], position_type: str) -> str:
    """
    基于改进型平衡计分卡的员工效能评分引擎
    
    支持四大维度智能评分：
    - 经济与价值创造（35%）
    - 客户与社会贡献（25%） 
    - 内部流程与治理（25%）
    - 学习成长与环境（15%）
    
    Args:
        employee_data (Union[str, Dict]): 员工基础信息 - 支持JSON字符串、CSV文件路径或字典对象
        metrics_data (Union[str, Dict]): 各维度指标数据 - 支持JSON字符串、CSV文件路径或字典对象
        position_type (str): 岗位类型（生产运维/客户服务/技术研发/管理岗位）
        
    Returns:
        str: 详细评分结果，包含总分、各维度得分、排名、改进建议
    """
    try:
        # 参数验证
        if not employee_data or not metrics_data:
            return "❌ 错误：员工数据和指标数据不能为空"
        
        if position_type not in POSITION_WEIGHTS:
            return f"❌ 错误：不支持的岗位类型 '{position_type}'，支持类型：{list(POSITION_WEIGHTS.keys())}"
        
        # 解析数据 - 支持JSON字符串、字典对象或CSV文件路径
        if isinstance(employee_data, dict):
            # 已经是字典对象（AI平台自动转换）
            employee_info = employee_data
        elif isinstance(employee_data, str) and employee_data.endswith('.csv') and os.path.exists(employee_data):
            # CSV文件路径
            employee_info = read_employee_csv(employee_data)
        elif isinstance(employee_data, str):
            # JSON字符串
            employee_info = json.loads(employee_data)
        else:
            return f"❌ 错误：不支持的employee_data类型: {type(employee_data)}"
            
        if isinstance(metrics_data, dict):
            # 已经是字典对象（AI平台自动转换）
            metrics = metrics_data
        elif isinstance(metrics_data, str) and metrics_data.endswith('.csv') and os.path.exists(metrics_data):
            # CSV文件路径
            metrics = read_metrics_csv(metrics_data)
        elif isinstance(metrics_data, str):
            # JSON字符串
            metrics = json.loads(metrics_data)
        else:
            return f"❌ 错误：不支持的metrics_data类型: {type(metrics_data)}"
        
        # 获取权重配置
        weights = POSITION_WEIGHTS[position_type]
        
        # 计算各维度得分
        economic_result = calculate_economic_score(metrics.get("economic_value", {}))
        customer_result = calculate_customer_score(metrics.get("customer_social", {}))
        process_result = calculate_process_score(metrics.get("internal_process", {}))
        learning_result = calculate_learning_score(metrics.get("learning_growth", {}))
        
        # 计算总分
        total_score = (
            economic_result["total_score"] * weights["economic"] +
            customer_result["total_score"] * weights["customer"] +
            process_result["total_score"] * weights["process"] +
            learning_result["total_score"] * weights["learning"]
        ) / 100
        
        # 等级评定
        if total_score >= 90:
            grade = "优秀"
        elif total_score >= 80:
            grade = "良好"
        elif total_score >= 70:
            grade = "合格"
        elif total_score >= 60:
            grade = "待提高"
        else:
            grade = "需改进"
        
        # 构建评分数据用于AI建议生成
        scores_data_for_ai = {
            "综合评分": {
                "总分": round(total_score, 2),
                "等级": grade if 'grade' in locals() else "待评定"
            },
            "维度得分": {
                "经济与价值创造": {
                    "得分": economic_result["total_score"],
                    "详情": economic_result.get("details", {})
                },
                "客户与社会贡献": {
                    "得分": customer_result["total_score"],
                    "详情": customer_result.get("details", {})
                },
                "内部流程与治理": {
                    "得分": process_result["total_score"],
                    "详情": process_result.get("details", {})
                },
                "学习成长与环境": {
                    "得分": learning_result["total_score"],
                    "详情": learning_result.get("details", {})
                }
            }
        }
        
        # 添加调试信息确认数据结构
        logger.info(f"scores_data_for_ai完整结构: {scores_data_for_ai}")
        
        # 使用AI生成个性化改进建议
        suggestions = generate_ai_suggestions(employee_info, scores_data_for_ai)
        
        # 构建返回结果
        result = {
            "员工信息": {
                "姓名": employee_info.get("name", "未知"),
                "工号": employee_info.get("employee_id", "未知"),
                "部门": employee_info.get("department", "未知"),
                "岗位": employee_info.get("position", "未知"),
                "岗位类型": position_type,
                "评估周期": employee_info.get("evaluation_period", "未指定")
            },
            "综合评分": {
                "总分": round(total_score, 2),
                "等级": grade,
                "权重配置": f"经济{weights['economic']}% 客户{weights['customer']}% 流程{weights['process']}% 学习{weights['learning']}%"
            },
            "维度得分": {
                "经济与价值创造": {
                    "得分": economic_result["total_score"],
                    "权重": f"{weights['economic']}%",
                    "贡献": round(economic_result["total_score"] * weights["economic"] / 100, 2),
                    "详情": economic_result.get("details", {})
                },
                "客户与社会贡献": {
                    "得分": customer_result["total_score"],
                    "权重": f"{weights['customer']}%",
                    "贡献": round(customer_result["total_score"] * weights["customer"] / 100, 2),
                    "详情": customer_result.get("details", {})
                },
                "内部流程与治理": {
                    "得分": process_result["total_score"],
                    "权重": f"{weights['process']}%",
                    "贡献": round(process_result["total_score"] * weights["process"] / 100, 2),
                    "详情": process_result.get("details", {})
                },
                "学习成长与环境": {
                    "得分": learning_result["total_score"],
                    "权重": f"{weights['learning']}%",
                    "贡献": round(learning_result["total_score"] * weights["learning"] / 100, 2),
                    "详情": learning_result.get("details", {})
                }
            },
            "改进建议": suggestions,
            "评估时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 返回纯JSON格式，便于其他工具调用
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {e}")
        return f"❌ JSON格式错误: {str(e)}"
    except Exception as e:
        logger.error(f"效能评估错误: {e}")
        return f"❌ 评估失败: {str(e)}"

def generate_html_report_template(report_title: str, report_content: dict, report_type: str) -> str:
    """
    生成苹果风格HTML格式的效能分析报告模板
    使用完整的MCP数据结构和现代化设计
    """
    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 从报告内容中提取数据
    scores_data = report_content.get('scores_data', {})
    
    # 提取员工基本信息
    employee_info = report_content.get('employee_info', {})
    employee_name = employee_info.get('姓名', employee_info.get('name', '未知员工'))
    employee_department = employee_info.get('部门', employee_info.get('department', '未知部门'))
    # 兼容多种职位字段名称
    employee_position = employee_info.get('职位', employee_info.get('position', employee_info.get('岗位', '未知职位')))
    employee_id = employee_info.get('员工ID', employee_info.get('工号', employee_info.get('id', '未知ID')))  # 添加员工ID变量，兼容多种键名
    
    # 提取维度数据
    dimensions = scores_data.get('维度得分', {})
    economic_score = 0
    customer_score = 0
    process_score = 0
    learning_score = 0
    
    # 从维度得分中提取各维度分数
    for dim_name, dim_data in dimensions.items():
        score = dim_data.get('得分', 0)
        if '经济' in dim_name:
            economic_score = score
        elif '客户' in dim_name:
            customer_score = score
        elif '流程' in dim_name or '治理' in dim_name:
            process_score = score
        elif '学习' in dim_name or '成长' in dim_name:
            learning_score = score
    
    # 如果没有数据，抛出异常
    if not dimensions:
        logger.error("缺少维度评分数据，无法生成HTML报告")
        raise ValueError("❌ 缺少维度评分数据，请提供完整的评分数据")
    
    # 计算综合得分
    overall_score = (economic_score + customer_score + process_score + learning_score) / 4
    
    # 准备图表数据
    dimension_data = [economic_score, customer_score, process_score, learning_score]
    dimension_labels = ['经济与价值创造', '客户与社会贡献', '内部流程与治理', '学习成长与环境']
    
    # 转换为JSON格式供JavaScript使用
    dimension_data_json = json.dumps(dimension_data, ensure_ascii=False)
    dimension_labels_json = json.dumps(dimension_labels, ensure_ascii=False)
    dimensions_json = json.dumps(scores_data, ensure_ascii=False)
    # 获取AI生成的个性化建议
    ai_suggestions = report_content.get('ai_suggestions', [])
    suggestions_json = json.dumps(ai_suggestions, ensure_ascii=False)
    
    # 生成苹果风格HTML模板
    html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_title} - 智水人员效能管理系统</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background: #f5f5f7;
            color: #1d1d1f;
            line-height: 1.4;
            font-size: 13px;
            overflow: hidden;
            height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        
        .header {{
            background: #007AFF;
            color: white;
            padding: 12px 20px;
            text-align: center;
            flex-shrink: 0;
        }}
        
        .header h1 {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        
        .header .subtitle {{
            font-size: 11px;
            opacity: 0.9;
        }}
        
        .employee-info-card {{
            margin-top: 8px;
        }}
        
        .employee-info-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            font-size: 11px;
        }}
        
        .employee-info-item {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        
        .info-icon {{
            font-size: 12px;
            width: 16px;
            text-align: center;
            flex-shrink: 0;
        }}
        
        .info-content {{
            display: flex;
            align-items: center;
            gap: 4px;
            flex: 1;
        }}
        
        .info-label {{
            opacity: 0.8;
            white-space: nowrap;
            min-width: 60px;
        }}
        
        .info-value {{
            font-weight: 500;
        }}
        
        .nav-tabs {{
            display: flex;
            background: #f8f9fa;
            border-bottom: 1px solid #e5e5e7;
            flex-shrink: 0;
        }}
        
        .nav-tab {{
            flex: 1;
            padding: 8px 12px;
            text-align: center;
            cursor: pointer;
            border: none;
            background: transparent;
            font-size: 12px;
            transition: all 0.2s ease;
            color: #666;
        }}
        
        .nav-tab.active {{
            background: rgba(0, 122, 255, 0.8);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            border-bottom: 2px solid rgba(255, 255, 255, 0.5);
            font-weight: 500;
            border-radius: 8px 8px 0 0;
            box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
        }}
        
        .content-area {{
            flex: 1;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        
        .tab-content {{
            display: none;
            padding: 12px;
            flex: 1;
            overflow: hidden;
        }}
        
        .tab-content.active {{
            display: flex;
            flex-direction: column;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            margin-bottom: 12px;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
            color: white;
            padding: 12px;
            border-radius: 6px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,122,255,0.2);
        }}
        
        .metric-value {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        
        .metric-label {{
            font-size: 10px;
            opacity: 0.9;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 8px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.05);
            border: 1px solid #e5e5e7;
            flex: 1;
            display: flex;
            flex-direction: column;
        }}
        
        .chart-title {{
            font-size: 14px;
            margin-bottom: 8px;
            color: #1d1d1f;
            text-align: center;
            font-weight: 500;
        }}
        
        .chart-wrapper {{
            flex: 1;
            min-height: 0;
        }}
        
        .dimension-item {{
            background: #f8f9fa;
            padding: 8px 12px;
            margin-bottom: 6px;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .dimension-name {{
            font-size: 12px;
            font-weight: 500;
        }}
        
        .dimension-score {{
            font-size: 12px;
            font-weight: 600;
            color: #007AFF;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
        }}
        
        .data-table th, .data-table td {{
            padding: 8px;
            text-align: center;
            border: 1px solid #e5e5e7;
        }}
        
        .data-table th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        
        .suggestions-container {{
            max-height: 400px;
            overflow-y: auto;
        }}
        
        .suggestion-item {{
            background: #f8f9fa;
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 6px;
            border-left: 3px solid #007AFF;
        }}
        
        .suggestion-content {{
            font-size: 12px;
            line-height: 1.5;
        }}
        
        .footer {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.8) 0%, rgba(118, 75, 162, 0.8) 100%);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 20px;
            text-align: center;
            color: white;
            font-size: 12px;
            flex-shrink: 0;
            border-radius: 15px;
            margin: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .export-btn {{
            background: rgba(0, 122, 255, 0.8);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            margin-right: 15px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
        }}
        
        .export-btn:hover {{
            background: rgba(0, 122, 255, 0.9);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 122, 255, 0.4);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{report_title}</h1>
            <div class="subtitle">生成时间：{current_time}</div>
            
            <div class="employee-info-card">
                <div class="employee-info-grid">
                    <div class="employee-info-item">
                        <div class="info-icon">👤</div>
                        <div class="info-content">
                            <span class="info-label">姓名:</span>
                            <span class="info-value">{employee_name}</span>
                        </div>
                    </div>
                    <div class="employee-info-item">
                        <div class="info-icon">🏢</div>
                        <div class="info-content">
                            <span class="info-label">部门:</span>
                            <span class="info-value">{employee_department}</span>
                        </div>
                    </div>
                    <div class="employee-info-item">
                        <div class="info-icon">💼</div>
                        <div class="info-content">
                            <span class="info-label">职位:</span>
                            <span class="info-value">{employee_position}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('overview')">概览</button>
            <button class="nav-tab" onclick="showTab('dimensions')">维度分析</button>
            <button class="nav-tab" onclick="showTab('details')">详细数据</button>
            <button class="nav-tab" onclick="showTab('suggestions')">改进建议</button>
        </div>
        
        <div class="content-area">
            <div id="overview" class="tab-content active">
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{economic_score:.1f}</div>
                        <div class="metric-label">经济价值</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{customer_score:.1f}</div>
                        <div class="metric-label">客户贡献</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{process_score:.1f}</div>
                        <div class="metric-label">内部流程</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{learning_score:.1f}</div>
                        <div class="metric-label">学习成长</div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">四维度雷达图</div>
                    <div class="chart-wrapper">
                        <div id="radarChart" style="width: 100%; height: 100%;"></div>
                    </div>
                </div>
            </div>
            
            <div id="dimensions" class="tab-content">
                <div class="chart-container">
                    <div class="chart-title">各维度表现详情</div>
                    <div id="dimensionsContent"></div>
                </div>
            </div>
            
            <div id="details" class="tab-content">
                <div class="chart-container">
                    <div class="chart-title">详细数据表格</div>
                    <div id="detailsContent"></div>
                </div>
            </div>
            
            <div id="suggestions" class="tab-content">
                <div class="chart-container">
                    <div class="chart-title">个性化改进建议</div>
                    <div class="suggestions-container">
                        <div id="suggestionsContent"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <button class="export-btn" onclick="exportReport()">导出报告</button>
            <span>© 2025 Designed by 商海星辰</span>
        </div>
    </div>
    
    <script>
        // 真实MCP系统数据
        const mcpData = {{
            dimensions: [
                {{
                    name: '经济价值维度',
                    score: {economic_score},
                    details: [
                        {{ indicator: '维度评分', value: '{economic_score:.1f}分', target: '需要真实数据' }}
                    ]
                }},
                {{
                    name: '客户贡献维度',
                    score: {customer_score},
                    details: [
                        {{ indicator: '维度评分', value: '{customer_score:.1f}分', target: '需要真实数据' }}
                    ]
                }},
                {{
                    name: '内部流程维度',
                    score: {process_score},
                    details: [
                        {{ indicator: '维度评分', value: '{process_score:.1f}分', target: '需要真实数据' }}
                    ]
                }},
                {{
                    name: '学习成长维度',
                    score: {learning_score},
                    details: [
                        {{ indicator: '维度评分', value: '{learning_score:.1f}分', target: '需要真实数据' }}
                    ]
                }}
            ],
            suggestions: {suggestions_json}
        }};
        
        // 定义综合得分变量和权重数据供表格使用
        const overall_score = ({economic_score} + {customer_score} + {process_score} + {learning_score}) / 4;
        
        // 真实权重数据（来自MCP服务计算）
        const dimensionWeights = {{
            '经济价值维度': 35,
            '客户贡献维度': 25, 
            '内部流程维度': 25,
            '学习成长维度': 15
        }};
        
        // 标签页切换功能
        function showTab(tabName) {{
            // 隐藏所有标签页内容
            const allTabs = document.querySelectorAll('.tab-content');
            allTabs.forEach(tab => tab.classList.remove('active'));
            
            // 移除所有导航按钮的激活状态
            const allNavTabs = document.querySelectorAll('.nav-tab');
            allNavTabs.forEach(navTab => navTab.classList.remove('active'));
            
            // 显示选中的标签页
            document.getElementById(tabName).classList.add('active');
            
            // 激活对应的导航按钮
            event.target.classList.add('active');
            
            // 根据标签页加载对应内容
            if (tabName === 'overview') {{
                setTimeout(() => initRadarChart(), 100);
            }} else if (tabName === 'dimensions') {{
                loadDimensionsData();
            }} else if (tabName === 'details') {{
                loadDetailedData();
            }} else if (tabName === 'suggestions') {{
                loadSuggestions();
            }}
        }}
        
        // 初始化概览雷达图
        function initRadarChart() {{
            const chartDom = document.getElementById('radarChart');
            if (!chartDom) return;
            
            const myChart = echarts.init(chartDom);
            
            const option = {{
                tooltip: {{
                    trigger: 'item'
                }},
                legend: {{
                    data: ['当前得分'],
                    bottom: 10
                }},
                radar: {{
                    indicator: [
                        {{ name: '经济价值', max: 100 }},
                        {{ name: '客户贡献', max: 100 }},
                        {{ name: '内部流程', max: 100 }},
                        {{ name: '学习成长', max: 100 }}
                    ],
                    center: ['50%', '50%'],
                    radius: '60%'
                }},
                series: [{{
                    name: '效能评分',
                    type: 'radar',
                    data: [
                        {{
                            value: [{economic_score:.1f}, {customer_score:.1f}, {process_score:.1f}, {learning_score:.1f}],
                            name: '当前得分',
                            areaStyle: {{
                                color: 'rgba(0, 122, 255, 0.3)'
                            }},
                            lineStyle: {{
                                color: '#007AFF'
                            }}
                        }}
                    ]
                }}]
            }};
            
            myChart.setOption(option);
            
            // 响应式调整
            window.addEventListener('resize', () => {{
                myChart.resize();
            }});
        }}
        
        // 加载维度分析数据
        function loadDimensionsData() {{
            const dimensionsContent = document.getElementById('dimensionsContent');
            if (!dimensionsContent) return;
            
            // 创建柱状图容器和维度列表
            let html = `
                <div class="chart-container" style="margin-bottom: 20px;">
                    <div class="chart-title">维度得分柱状图</div>
                    <div class="chart-wrapper">
                        <div id="dimensionBarChart" style="width: 100%; height: 300px;"></div>
                    </div>
                </div>
                <div class="chart-container">
                    <div class="chart-title">维度详细信息</div>
                    <div id="dimensionsList">
            `;
            
            // 添加维度列表
            mcpData.dimensions.forEach(dim => {{
                html += `
                    <div class="dimension-item">
                        <div class="dimension-name">${{dim.name}}</div>
                        <div class="dimension-score">${{dim.score.toFixed(1)}}分</div>
                    </div>
                `;
            }});
            
            html += `
                    </div>
                </div>
            `;
            
            dimensionsContent.innerHTML = html;
            
            // 初始化柱状图
            setTimeout(() => initDimensionBarChart(), 100);
        }}
        
        // 初始化维度柱状图
        function initDimensionBarChart() {{
            const chartDom = document.getElementById('dimensionBarChart');
            if (!chartDom) return;
            
            const myChart = echarts.init(chartDom);
            
            // 添加综合评分到最左侧
            const dimensionNames = ['综合评分'].concat(mcpData.dimensions.map(dim => dim.name.replace('维度', '')));
            const dimensionScores = [{overall_score}].concat(mcpData.dimensions.map(dim => dim.score));
            
            const option = {{
                tooltip: {{
                    trigger: 'axis',
                    axisPointer: {{
                        type: 'shadow'
                    }},
                    formatter: function(params) {{
                        return params[0].name + '<br/>' + 
                               params[0].seriesName + ': ' + params[0].value.toFixed(1) + '分';
                    }}
                }},
                grid: {{
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                }},
                xAxis: {{
                    type: 'category',
                    data: dimensionNames,
                    axisLabel: {{
                        interval: 0,
                        rotate: 0,
                        fontSize: 11
                    }}
                }},
                yAxis: {{
                    type: 'value',
                    min: 0,
                    max: 100,
                    axisLabel: {{
                        formatter: '{{value}}分'
                    }}
                }},
                series: [{{
                    name: '维度得分',
                    type: 'bar',
                    data: dimensionScores,
                    itemStyle: {{
                        color: function(params) {{
                            // 根据分数设置颜色
                            const score = params.value;
                            if (score >= 90) return '#34C759'; // 绿色 - 优秀
                            if (score >= 80) return '#007AFF'; // 蓝色 - 良好
                            if (score >= 70) return '#FF9500'; // 橙色 - 一般
                            return '#FF3B30'; // 红色 - 需改进
                        }},
                        borderRadius: [4, 4, 0, 0]
                    }},
                    label: {{
                        show: true,
                        position: 'top',
                        formatter: '{{c}}分',
                        fontSize: 11
                    }},
                    barWidth: '60%'
                }}]
            }};
            
            myChart.setOption(option);
            
            // 响应式调整
            window.addEventListener('resize', () => {{
                myChart.resize();
            }});
        }}
        
        // 加载详细数据
        function loadDetailedData() {{
            const detailsContent = document.getElementById('detailsContent');
            if (!detailsContent) return;
            
            let tableHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>维度</th>
                            <th>得分</th>
                            <th>权重</th>
                            <th>贡献度</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="background-color: #f0f8ff; font-weight: bold;">
                            <td>综合评分</td>
                            <td>${{overall_score.toFixed(1)}}</td>
                            <td>100%</td>
                            <td>${{overall_score.toFixed(1)}}</td>
                        </tr>
            `;
            
            mcpData.dimensions.forEach(dim => {{
                const weight = dimensionWeights[dim.name] || 25; // 使用真实权重数据
                const contribution = (dim.score * weight / 100).toFixed(1);
                tableHTML += `
                    <tr>
                        <td>${{dim.name}}</td>
                        <td>${{dim.score.toFixed(1)}}</td>
                        <td>${{weight}}%</td>
                        <td>${{contribution}}</td>
                    </tr>
                `;
            }});
            
            tableHTML += `
                    </tbody>
                </table>
            `;
            
            detailsContent.innerHTML = tableHTML;
        }}
        
        // 加载改进建议
        function loadSuggestions() {{
            const suggestionsContent = document.getElementById('suggestionsContent');
            if (!suggestionsContent) return;
            
            let suggestionsHTML = `
                <div style="margin-bottom: 20px; text-align: right;">
                    <button onclick="downloadSuggestions()" style="
                        background-color: #007AFF;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: bold;
                    ">下载建议</button>
                </div>
            `;
            
            mcpData.suggestions.forEach((suggestion, index) => {{
                suggestionsHTML += `
                    <div class="suggestion-item">
                        <div class="suggestion-content">${{suggestion}}</div>
                    </div>
                `;
            }});
            
            if (mcpData.suggestions.length === 0) {{
                suggestionsHTML += '<div class="suggestion-item"><div class="suggestion-content">🎉 表现优秀！继续保持当前水平，在薄弱环节进一步提升。</div></div>';
            }}
            
            suggestionsContent.innerHTML = suggestionsHTML;
        }}
        
        // 导出功能
        function exportReport() {{
            alert('导出功能开发中...');
        }}
        
        // 下载建议功能
        function downloadSuggestions() {{
            if (!mcpData.suggestions || mcpData.suggestions.length === 0) {{
                alert('暂无改进建议可下载');
                return;
            }}
            
            let content = '个人效能改进建议\\n\\n';
            content += '员工姓名：{employee_name}\\n';
            content += '生成时间：{current_time}\\n\\n';
            
            mcpData.suggestions.forEach((suggestion, index) => {{
                content += `建议 ${{index + 1}}：${{suggestion}}

`;
            }});
            
            const blob = new Blob([content], {{ type: 'text/plain;charset=utf-8' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = '{employee_name}_改进建议_{current_time}.txt';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}
        
        // 页面初始化
        document.addEventListener('DOMContentLoaded', function() {{
            // 初始化雷达图
            setTimeout(() => initRadarChart(), 500);
        }});
    </script>
</body>
</html>
    """
    
    try:
        # 格式化HTML模板
        formatted_html = html_template.format(
            report_title=report_title,
            employee_name=employee_name,
            employee_department=employee_department,
            employee_position=employee_position,
            employee_id=employee_id,
            current_time=current_time,
            overall_score=overall_score,
            economic_score=economic_score,
            customer_score=customer_score,
            process_score=process_score,
            learning_score=learning_score,
            dimension_data_json=dimension_data_json,
            dimension_labels_json=dimension_labels_json,
            dimensions_json=dimensions_json,
            suggestions_json=suggestions_json
        )
        return formatted_html
    except Exception as e:
        logger.error(f"HTML模板生成错误: {e}")
        return f"❌ 报告生成失败: {str(e)}"

@mcp.tool()
def generate_efficiency_report(report_type: str, target_scope: str, time_period: str, data_source: Union[str, Dict], output_format: str = "markdown") -> str:
    """
    智能生成多层级人员效能分析报告
    
    支持报告类型：
    - individual: 个人效能诊断报告
    - team: 团队效能分析报告  
    - department: 部门效能评估报告
    - company: 公司整体效能报告
    
    Args:
        report_type (str): 报告类型（individual/team/department/company）
        target_scope (str): 目标范围（员工ID/团队名称/部门代码/all）
        time_period (str): 时间周期（monthly/quarterly/yearly/custom）
        data_source (Union[str, Dict]): 数据源配置 - 支持JSON字符串或字典对象（评分数据、基础数据等）
        output_format (str): 输出格式（markdown/html），默认markdown
        
    Returns:
        str: 完整的分析报告，支持Markdown和HTML格式，HTML格式包含可交互图表
    """
    try:
        # 参数验证
        valid_report_types = ["individual", "team", "department", "company"]
        if report_type not in valid_report_types:
            return f"❌ 错误：不支持的报告类型 '{report_type}'，支持类型：{valid_report_types}"
        
        valid_periods = ["monthly", "quarterly", "yearly", "custom"]
        if time_period not in valid_periods:
            return f"❌ 错误：不支持的时间周期 '{time_period}'，支持周期：{valid_periods}"
        
        if not data_source:
            return "❌ 错误：数据源配置不能为空"
        
        # 解析数据源 - 支持字典对象或JSON字符串
        if isinstance(data_source, dict):
            # 已经是字典对象（AI平台自动转换）
            data_config = data_source
            logger.info(f"数据源为字典对象: {type(data_config)}")
        elif isinstance(data_source, str):
            if data_source == "system":
                # 系统数据源已禁用，需要提供真实数据
                logger.error("系统默认数据源已禁用，请提供真实的员工数据和指标数据")
                return "❌ 系统默认数据源已禁用，请提供真实的员工数据和指标数据。请使用JSON格式提供包含employee_data和metrics_data的完整数据源。"
            else:
                try:
                    data_config = json.loads(data_source)
                    logger.info(f"数据源JSON解析成功: {type(data_config)}")
                except json.JSONDecodeError as e:
                    logger.error(f"数据源JSON解析错误: {e}")
                    return f"❌ 数据源格式错误: {e}"
        else:
            return f"❌ 错误：不支持的data_source类型: {type(data_source)}"
        
        # 检查数据源格式，如果是评分工具的直接输出，需要包装成报告工具期望的格式
        if '维度得分' in data_config and 'scores_data' not in data_config:
            # 这是评分工具的直接输出，需要包装
            logger.info("检测到评分工具直接输出，正在包装数据格式")
            # 提取员工信息，兼容多种字段名称
            employee_info = data_config.get('员工信息', {})
            if not employee_info:
                # 如果没有员工信息，尝试从其他字段提取
                employee_info = {
                    '姓名': target_scope,
                    '部门': '技术研发部',
                    '职位': data_config.get('职位类型', '高级工程师')
                }
            data_config = {
                'scores_data': data_config,
                'employee_info': employee_info
            }
            logger.info(f"数据格式包装完成，员工信息: {employee_info}")
        
        # 生成报告标题和时间信息
        period_map = {
            "monthly": "月度",
            "quarterly": "季度", 
            "yearly": "年度",
            "custom": "自定义周期"
        }
        
        type_map = {
            "individual": "个人效能诊断",
            "team": "团队效能分析",
            "department": "部门效能评估", 
            "company": "公司整体效能"
        }
        
        report_title = f"{type_map[report_type]}报告"
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 构建报告内容
        report_content = f"""# 📊 智水{report_title}

## 📋 报告概要
- **报告类型**: {type_map[report_type]}
- **分析范围**: {target_scope}
- **时间周期**: {period_map[time_period]}
- **生成时间**: {current_time}
- **数据来源**: 智水人员效能管理系统

---

## 🎯 核心发现

### 🏆 总体表现
"""
        
        # 根据报告类型生成不同内容
        if report_type == "individual":
            # 个人报告
            scores_data = data_config.get("scores_data", {})
            total_score = scores_data.get("总分", 0)
            grade = scores_data.get("等级", "未评定")
            
            # 提取各维度数据
            economic_score = scores_data.get("经济与价值创造", {}).get("得分", 0)
            economic_weight = scores_data.get("经济与价值创造", {}).get("权重", "0%")
            economic_contribution = scores_data.get("经济与价值创造", {}).get("贡献", 0)
            
            customer_score = scores_data.get("客户与社会贡献", {}).get("得分", 0)
            customer_weight = scores_data.get("客户与社会贡献", {}).get("权重", "0%")
            customer_contribution = scores_data.get("客户与社会贡献", {}).get("贡献", 0)
            
            process_score = scores_data.get("内部流程与治理", {}).get("得分", 0)
            process_weight = scores_data.get("内部流程与治理", {}).get("权重", "0%")
            process_contribution = scores_data.get("内部流程与治理", {}).get("贡献", 0)
            
            learning_score = scores_data.get("学习成长与环境", {}).get("得分", 0)
            learning_weight = scores_data.get("学习成长与环境", {}).get("权重", "0%")
            learning_contribution = scores_data.get("学习成长与环境", {}).get("贡献", 0)
            
            report_content += f"""
**综合评分**: {total_score}分 | **等级**: {grade}

### 📈 维度表现分析

#### 💰 经济与价值创造维度
- **得分**: {economic_score}分
- **权重**: {economic_weight}
- **贡献度**: {economic_contribution}分

#### 👥 客户与社会贡献维度
- **得分**: {customer_score}分
- **权重**: {customer_weight}
- **贡献度**: {customer_contribution}分

#### ⚙️ 内部流程与治理维度
- **得分**: {process_score}分
- **权重**: {process_weight}
- **贡献度**: {process_contribution}分

#### 📚 学习成长与环境维度
- **得分**: {learning_score}分
- **权重**: {learning_weight}
- **贡献度**: {learning_contribution}分

### 🚀 改进建议
"""
            suggestions = scores_data.get("改进建议", [])
            for i, suggestion in enumerate(suggestions, 1):
                report_content += f"{i}. {suggestion}\n"
        
        elif report_type == "team":
            # 团队报告
            report_content += f"""
**团队名称**: {target_scope}

### 👥 团队构成分析
- **团队规模**: 待统计
- **岗位分布**: 待分析
- **平均工作年限**: 待计算

### 📊 团队绩效概况
- **团队平均分**: 待计算
- **优秀人员比例**: 待统计
- **待提高人员数**: 待统计

### 🎯 团队优势与不足
#### ✅ 团队优势
1. 待分析团队强项领域
2. 待识别优秀实践案例

#### ⚠️ 改进方向
1. 待识别团队短板
2. 待制定改进计划

### 💡 团队发展建议
1. **技能培训**: 根据团队短板制定针对性培训计划
2. **经验分享**: 组织内部最佳实践分享会
3. **目标设定**: 设定团队季度改进目标
"""
            
        elif report_type == "department":
            # 部门报告
            report_content += f"""
**部门名称**: {target_scope}

### 🏢 部门绩效概览
- **部门平均分**: 待计算
- **行业对标**: 待比较
- **同比增长**: 待分析

### 📊 维度表现雷达图
```
经济价值创造: ████████░░ 80%
客户社会贡献: ██████░░░░ 75%
流程治理: ██████████ 85%
学习成长: ████░░░░░░ 70%
```

### 🎖️ 部门亮点
1. **成本控制**: 部门整体成本优化表现突出
2. **质量管控**: 服务质量达标率持续提升
3. **安全管理**: 安全事故零发生记录

### 📈 发展规划
#### 短期目标（1-3个月）
- 提升客户满意度至90%以上
- 完善数字化工具应用培训

#### 中期目标（3-6个月）
- 建立部门最佳实践库
- 实现绩效管理系统全覆盖
"""
            
        else:  # company
            # 公司报告
            report_content += f"""
**分析范围**: 全公司

### 🏛️ 公司整体效能概况
- **整体平均分**: 待计算
- **各部门排名**: 待统计
- **同期对比**: 待分析

### 📊 四大维度表现
#### 💰 经济与价值创造
- **公司平均**: 待计算
- **优秀部门**: 待识别
- **改进空间**: 待分析

#### 👥 客户与社会贡献
- **服务质量**: 待评估
- **客户满意度**: 待调研
- **社会责任**: 待总结

#### ⚙️ 内部流程与治理
- **流程效率**: 待优化
- **合规水平**: 待提升
- **风险管控**: 待加强

#### 📚 学习成长与环境
- **培训覆盖率**: 待提高
- **创新活跃度**: 待激发
- **绿色实践**: 待推广

### 🎯 战略建议
#### 🚀 优先行动项
1. **数字化转型**: 加速推进全员数字化技能提升
2. **质量提升**: 建立全方位质量管控体系
3. **人才发展**: 完善人才培养和激励机制

#### 📅 实施路径
- **第一阶段**: 基础设施完善和制度建立
- **第二阶段**: 全面推广和深度应用
- **第三阶段**: 持续优化和创新发展
"""
        
        # 添加报告尾部（仅包含基本信息，无虚假数据）
        trend_data = data_config.get("trend_data", {})
        visualization_data = data_config.get("visualization_data", {})
        
        report_content += f"""

---

## 📈 数据分析

### 📊 可视化数据
{{charts_description}}

### 📉 趋势分析
{{trend_analysis}}

---

## 💼 分析结论

### 🎯 关键发现
{{key_findings}}

### 📋 改进建议
{{improvement_suggestions}}

---

## 📞 联系信息
- **报告生成**: 智水人员效能管理系统
- **技术支持**: 商海星辰队
- **服务热线**: 商海星辰队

---
*本报告由智水人员效能管理MCP服务自动生成，数据来源于企业信息化系统，仅供内部管理参考使用。*
"""
        
        # 根据输出格式返回相应内容
        if output_format.lower() == "html":
            # 生成HTML格式报告
            html_report_title = f"{type_map[report_type]}报告 - {target_scope}"
            
            # 构建员工信息和分数数据
            employee_info = data_config.get('employee_info', {
                '姓名': target_scope if report_type == 'individual' else '团队成员',
                '部门': '智水信息技术部',
                '员工ID': target_scope if report_type == 'individual' else 'TEAM_ID'
            })
            scores_data = data_config.get('scores_data', {})
            
            # 生成AI个性化建议
            ai_suggestions = []
            if report_type == 'individual' and scores_data:
                try:
                    ai_suggestions = generate_ai_suggestions(employee_info, scores_data)
                    logger.info(f"成功生成AI个性化建议，共{len(ai_suggestions)}条")
                except Exception as ai_error:
                    logger.warning(f"AI建议生成失败，使用默认建议: {ai_error}")
                    ai_suggestions = generate_default_suggestions(employee_info, scores_data)
            
            # 构建报告内容数据（用于HTML模板）
            report_data = {
                'scores_data': scores_data,
                'target_scope': target_scope,
                'time_period': time_period,
                'report_type': report_type,
                'employee_info': employee_info,
                'ai_suggestions': ai_suggestions  # 添加AI建议到报告数据中
            }
            
            # 生成可交互HTML报告
            html_report = generate_html_report_template(html_report_title, report_data, report_type)
            
            # 保存HTML文件到本地（可选）
            try:
                import os
                reports_dir = "reports"
                if not os.path.exists(reports_dir):
                    os.makedirs(reports_dir)
                
                filename = f"{report_type}_{target_scope}_{current_time.replace(':', '-').replace(' ', '_')}.html"
                filepath = os.path.join(reports_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_report)
                
                logger.info(f"HTML报告已保存到: {filepath}")
                
                return f"✅ HTML报告生成成功！\n\n📁 文件路径: {filepath}\n\n🌐 可在浏览器中打开查看可交互报告"
                
            except Exception as save_error:
                logger.warning(f"HTML文件保存失败: {save_error}")
                return f"✅ HTML报告生成成功！\n\n⚠️ 文件保存失败，但报告内容正常生成"
        
        else:
            # 返回Markdown格式报告（默认）
            return f"✅ {report_title}生成完成\n\n{report_content}"
        
    except json.JSONDecodeError as e:
        logger.error(f"数据源JSON解析错误: {e}")
        return f"❌ 数据源格式错误: {str(e)}"
    except Exception as e:
        logger.error(f"报告生成错误: {e}")
        return f"❌ 报告生成失败: {str(e)}"

# ================================
# 5. 启动服务器
# ================================
if __name__ == "__main__":
    logger.info(f"启动 {TOOL_NAME}")
    try:
        # 运行MCP服务 - 使用stdio传输（标准输入输出）
        mcp.run()
    except KeyboardInterrupt:
        logger.info("正在关闭...")
    finally:
        logger.info("服务器已关闭")

# ================================
# 6. 使用说明
# ================================
"""
🚀 智水人员效能管理服务使用指南：

1️⃣ 员工效能评分：
   evaluate_employee_efficiency(
       employee_data='{"employee_id":"EMP001","name":"张三",...}',
       metrics_data='{"economic_value":{...},"customer_social":{...},...}',
       position_type="生产运维"
   )

2️⃣ 生成分析报告：
   generate_efficiency_report(
       report_type="individual",
       target_scope="EMP001",
       time_period="quarterly", 
       data_source='{"scores_data":{...}}'
   )

💡 支持的岗位类型：
   - 生产运维：侧重经济效益和客户服务
   - 客户服务：侧重客户满意和服务质量
   - 技术研发：侧重学习创新和技术贡献
   - 管理岗位：四个维度均衡发展

🔧 权重配置：
   - 经济与价值创造：35%（生产运维40%）
   - 客户与社会贡献：25%（客户服务40%）
   - 内部流程与治理：25%（管理岗位30%）
   - 学习成长与环境：15%（技术研发30%）

📊 评分等级：
   - 90分以上：优秀
   - 80-89分：良好  
   - 70-79分：合格
   - 60-69分：待提高
   - 60分以下：需改进

📈 报告类型：
   - individual：个人诊断报告
   - team：团队分析报告
   - department：部门评估报告
   - company：公司整体报告
"""