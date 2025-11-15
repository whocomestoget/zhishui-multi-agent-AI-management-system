#!/usr/bin/env python3
"""
智慧水电成本预测MCP工具集
基于Lasso回归模型的水电项目成本预测、动态AHP多准则风险评估和分析数据生成
集成AI专家系统的层次分析法(AHP)，实现智能化项目风险评估
"""

import json
import logging
import numpy as np
import requests
from datetime import datetime
from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP

# 导入已训练的成本预测器
try:
    from predict_cost import HydropowerCostPredictor
except ImportError:
    print("警告: 无法导入predict_cost模块，将使用模拟预测器")
    HydropowerCostPredictor = None

# 配置
TOOL_NAME = "智慧水电成本预测MCP工具集"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(TOOL_NAME)

# AI配置 - 用于内部AHP专家评估（环境变量优先）
import os
AI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY", ""),
    "api_base": os.getenv("OPENAI_API_BASE", "http://38.246.251.165:3002/v1"),
    "model": os.getenv("OPENAI_MODEL", "gemini-2.5-flash-lite-preview-06-17"),
    "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
    "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "200000")),
}

# 创建MCP服务器 - 指定端口8002
mcp = FastMCP(TOOL_NAME)

# 全局预测器实例
cost_predictor = None

def init_predictor():
    """初始化成本预测器"""
    global cost_predictor
    if HydropowerCostPredictor and cost_predictor is None:
        try:
            cost_predictor = HydropowerCostPredictor()
            logger.info("成本预测器初始化成功")
        except Exception as e:
            logger.error(f"预测器初始化失败: {e}")
            cost_predictor = None

# AHP风险评估指标定义
AHP_CRITERIA = {
    "C1": "对经济社会环境发展态势判断失误",
    "C2": "决策体制机制缺陷", 
    "C3": "相关法律法规政策缺陷",
    "C4": "次生自然灾害",
    "C5": "损害相关行业经济利益",
    "C6": "破坏生态系统",
    "C7": "项目资金风险"
}

def call_llm_expert(prompt: str) -> str:
    """
    调用LLM进行专家评估
    
    Args:
        prompt: 专家评估提示词
        
    Returns:
        LLM的评估结果
    """
    try:
        headers = {
            "Authorization": f"Bearer {AI_CONFIG.get('api_key', '')}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": AI_CONFIG.get("model", ""),
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": AI_CONFIG.get("temperature", 0.7)
        }
        
        response = requests.post(
            f"{AI_CONFIG.get('api_base', '')}/chat/completions",
            headers=headers,
            json=data,
            timeout=600
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            # 清理响应内容，移除可能的markdown代码块标记
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            return content.strip()
        else:
            logger.error(f"LLM调用失败: {response.status_code} - {response.text}")
            return "LLM调用失败"
            
    except Exception as e:
        logger.error(f"LLM调用异常: {e}")
        return "LLM调用异常"

def ahp_expert_assessment(project_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    AHP专家评估 - 使用LLM进行标准AHP层次分析法评估
    严格按照判断矩阵两两比较的方式进行评估
    
    Args:
        project_info: 项目背景信息
        
    Returns:
        AHP评估结果
    """
    try:
        # 构建标准AHP专家评估提示词
        expert_prompt = f"""
你是一位资深的水电项目风险评估专家，拥有20年以上的项目管理和风险控制经验。
请基于以下项目信息，严格运用层次分析法(AHP)的判断矩阵方法对项目风险进行专业评估。

项目基本信息：
- 项目类型：{project_info.get('project_type', '未知')}
- 装机容量：{project_info.get('capacity_mw', 0)}MW
- 建设周期：{project_info.get('construction_period', 0)}年
- 客户类型：{project_info.get('client_type', '未知')}
- 项目复杂度：{project_info.get('project_complexity', '未知')}
- 项目背景描述：{project_info.get('project_description', '无详细描述')}
- 地理位置：{project_info.get('location', '未知')}
- 环境条件：{project_info.get('environmental_conditions', '未知')}

风险评估指标说明：
C1: 对经济社会环境发展态势判断失误
C2: 决策体制机制缺陷
C3: 相关法律法规政策缺陷
C4: 次生自然灾害
C5: 损害相关行业经济利益
C6: 破坏生态系统
C7: 项目资金风险

请按照AHP标准方法，对上述7个风险指标进行两两比较，构建判断矩阵。

AHP标度含义：
1 = 同等重要
3 = 稍微重要
5 = 明显重要
7 = 强烈重要
9 = 极端重要
2,4,6,8 = 中间值

请对以下21对指标进行两两比较，给出相对重要性评分（如果Ci比Cj重要，给出1-9的值；如果Cj比Ci重要，给出1/2到1/9的倒数值）：

1. C1 vs C2: C1相对于C2的重要性
2. C1 vs C3: C1相对于C3的重要性
3. C1 vs C4: C1相对于C4的重要性
4. C1 vs C5: C1相对于C5的重要性
5. C1 vs C6: C1相对于C6的重要性
6. C1 vs C7: C1相对于C7的重要性
7. C2 vs C3: C2相对于C3的重要性
8. C2 vs C4: C2相对于C4的重要性
9. C2 vs C5: C2相对于C5的重要性
10. C2 vs C6: C2相对于C6的重要性
11. C2 vs C7: C2相对于C7的重要性
12. C3 vs C4: C3相对于C4的重要性
13. C3 vs C5: C3相对于C5的重要性
14. C3 vs C6: C3相对于C6的重要性
15. C3 vs C7: C3相对于C7的重要性
16. C4 vs C5: C4相对于C5的重要性
17. C4 vs C6: C4相对于C6的重要性
18. C4 vs C7: C4相对于C7的重要性
19. C5 vs C6: C5相对于C6的重要性
20. C5 vs C7: C5相对于C7的重要性
21. C6 vs C7: C6相对于C7的重要性

请严格按照以下JSON格式输出评估结果：
{{
    "pairwise_comparisons": {{
        "C1_vs_C2": {{"value": X, "reasoning": "比较理由"}},
        "C1_vs_C3": {{"value": X, "reasoning": "比较理由"}},
        "C1_vs_C4": {{"value": X, "reasoning": "比较理由"}},
        "C1_vs_C5": {{"value": X, "reasoning": "比较理由"}},
        "C1_vs_C6": {{"value": X, "reasoning": "比较理由"}},
        "C1_vs_C7": {{"value": X, "reasoning": "比较理由"}},
        "C2_vs_C3": {{"value": X, "reasoning": "比较理由"}},
        "C2_vs_C4": {{"value": X, "reasoning": "比较理由"}},
        "C2_vs_C5": {{"value": X, "reasoning": "比较理由"}},
        "C2_vs_C6": {{"value": X, "reasoning": "比较理由"}},
        "C2_vs_C7": {{"value": X, "reasoning": "比较理由"}},
        "C3_vs_C4": {{"value": X, "reasoning": "比较理由"}},
        "C3_vs_C5": {{"value": X, "reasoning": "比较理由"}},
        "C3_vs_C6": {{"value": X, "reasoning": "比较理由"}},
        "C3_vs_C7": {{"value": X, "reasoning": "比较理由"}},
        "C4_vs_C5": {{"value": X, "reasoning": "比较理由"}},
        "C4_vs_C6": {{"value": X, "reasoning": "比较理由"}},
        "C4_vs_C7": {{"value": X, "reasoning": "比较理由"}},
        "C5_vs_C6": {{"value": X, "reasoning": "比较理由"}},
        "C5_vs_C7": {{"value": X, "reasoning": "比较理由"}},
        "C6_vs_C7": {{"value": X, "reasoning": "比较理由"}}
    }},
    "overall_assessment": "基于项目特点的整体风险评估总结"
}}

注意：
1. value值可以是：9, 7, 5, 3, 1, 0.33, 0.2, 0.14, 0.11 (对应1/3, 1/5, 1/7, 1/9)
2. 评估理由要结合具体项目情况和两个指标的相对重要性
3. 必须严格按照JSON格式输出，不要添加其他内容
4. 考虑项目类型、客户特点、环境条件等因素进行专业判断
"""
        
        # 调用LLM专家
        llm_response = call_llm_expert(expert_prompt)
        
        # 解析LLM响应
        try:
            # 尝试提取JSON部分
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                assessment_result = json.loads(json_str)
            else:
                raise ValueError("无法找到有效的JSON格式")
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"LLM响应解析失败: {e}, 响应内容: {llm_response}")
            return {
                "status": "error",
                "message": f"LLM专家评估失败，无法解析响应: {str(e)}"
            }
        
        # 构建AHP判断矩阵
        matrix = np.ones((7, 7))  # 7x7矩阵，对角线为1
        
        # 填充判断矩阵的上三角部分
        pairwise = assessment_result.get("pairwise_comparisons", {})
        comparisons = [
            ("C1_vs_C2", 0, 1), ("C1_vs_C3", 0, 2), ("C1_vs_C4", 0, 3), ("C1_vs_C5", 0, 4), ("C1_vs_C6", 0, 5), ("C1_vs_C7", 0, 6),
            ("C2_vs_C3", 1, 2), ("C2_vs_C4", 1, 3), ("C2_vs_C5", 1, 4), ("C2_vs_C6", 1, 5), ("C2_vs_C7", 1, 6),
            ("C3_vs_C4", 2, 3), ("C3_vs_C5", 2, 4), ("C3_vs_C6", 2, 5), ("C3_vs_C7", 2, 6),
            ("C4_vs_C5", 3, 4), ("C4_vs_C6", 3, 5), ("C4_vs_C7", 3, 6),
            ("C5_vs_C6", 4, 5), ("C5_vs_C7", 4, 6),
            ("C6_vs_C7", 5, 6)
        ]
        
        for comp_key, i, j in comparisons:
            value = pairwise.get(comp_key, {}).get("value", 1)
            matrix[i][j] = value
            matrix[j][i] = 1 / value  # 对称填充下三角
        
        # 计算权重向量 (特征向量法)
        try:
            eigenvalues, eigenvectors = np.linalg.eig(matrix)
            max_eigenvalue_index = np.argmax(eigenvalues.real)
            principal_eigenvector = eigenvectors[:, max_eigenvalue_index].real
            weights = principal_eigenvector / np.sum(principal_eigenvector)
            
            # 一致性检验
            lambda_max = eigenvalues[max_eigenvalue_index].real
            ci = (lambda_max - 7) / 6  # n=7
            ri = 1.32  # n=7的随机一致性指标
            cr = ci / ri
            
        except Exception as e:
            logger.error(f"特征向量计算失败: {e}，使用平均权重")
            weights = np.ones(7) / 7  # 平均权重
            cr = 0.0
        
        # 标准AHP方案层评估 - 针对每个准则进行方案间两两比较
        alternative_result = _ahp_alternative_assessment(project_info, assessment_result)
        alternative_scores = alternative_result.get("scores", {})
        alternative_reasoning = alternative_result.get("reasoning", {})
        
        # 计算最终综合得分 (准则权重 × 方案得分)
        # 检查alternative_scores是否有效
        if not alternative_scores or alternative_result.get("status") == "error":
            # 如果方案层评估失败，直接返回错误
            logger.error("方案层评估失败，无法计算最终风险得分")
            return {
                    "status": "error",
                    "message": "方案层评估失败，无法完成风险评估",
                    "risk_level": "未知",
                    "expert_reasoning_display": "方案层评估失败，无法获取专家评估理由"
                }
        else:
            try:
                # 严格检查alternative_scores的完整性
                missing_criteria = []
                for i in range(7):
                    criterion = f"C{i+1}"
                    if criterion not in alternative_scores or not alternative_scores[criterion]:
                        missing_criteria.append(criterion)
                
                if missing_criteria:
                    logger.error(f"方案层评估数据不完整，缺少准则: {missing_criteria}")
                    return {
                        "status": "error",
                        "message": f"方案层评估数据不完整，缺少准则: {missing_criteria}",
                        "risk_level": "未知",
                        "expert_reasoning_display": "方案层评估数据不完整，无法获取专家评估理由"
                    }
                
                # 计算最终得分（不使用任何默认值）
                final_scores = {
                    "A1_低风险": sum(weights[i] * alternative_scores[f"C{i+1}"]["A1"] for i in range(7)),
                    "A2_中等风险": sum(weights[i] * alternative_scores[f"C{i+1}"]["A2"] for i in range(7)),
                    "A3_高风险": sum(weights[i] * alternative_scores[f"C{i+1}"]["A3"] for i in range(7))
                }
            except Exception as e:
                logger.error(f"计算最终得分失败: {e}")
                return {
                    "status": "error",
                    "message": f"计算最终得分失败: {e}",
                    "risk_level": "未知",
                    "expert_reasoning_display": "最终得分计算失败，无法获取专家评估理由"
                }
        
        # 确定最终风险等级（得分最高的方案）
        max_score_alternative = max(final_scores, key=final_scores.get)
        if "A1" in max_score_alternative:
            risk_level = "低"
        elif "A2" in max_score_alternative:
            risk_level = "中等"
        else:
            risk_level = "高"
            
        # 构建专家理由显示内容
        expert_reasoning_display = "\n=== LLM专家AHP方案层比较理由 ===\n"
        
        if alternative_reasoning:
            for criterion, comparisons in alternative_reasoning.items():
                criterion_name = AHP_CRITERIA.get(criterion, criterion)
                expert_reasoning_display += f"\n【{criterion}: {criterion_name}】\n"
                
                for comparison, data in comparisons.items():
                    value = data.get('value', 1)
                    reasoning = data.get('reasoning', '无理由说明')
                    expert_reasoning_display += f"  • {comparison}: {value} - {reasoning}\n"
        else:
            expert_reasoning_display += "方案层评估失败，无法获取专家比较理由\n"
        
        return {
            "status": "success",
            "risk_level": risk_level,
            "criteria_assessment": assessment_result,
            "expert_evaluation": "基于LLM专家智能评估",
            "assessment_method": "标准AHP层次分析法(含方案层两两比较)",
            "ahp_weights": weights.tolist(),
            "consistency_ratio": round(cr, 4),
            "alternative_scores": alternative_scores,
            "alternative_reasoning": alternative_reasoning,
            "expert_reasoning_display": expert_reasoning_display,
            "final_scores": {k: round(v, 4) for k, v in final_scores.items()},
            "selected_alternative": max_score_alternative
        }
        
    except Exception as e:
        logger.error(f"AHP专家评估失败: {e}")
        return {
            "status": "error",
            "message": f"专家评估失败: {str(e)}"
        }

def _ahp_alternative_assessment(project_info: Dict[str, Any], criteria_assessment: Dict[str, Any]) -> Dict[str, Any]:
    """
    标准AHP方案层评估 - 针对每个准则进行方案间两两比较
    
    Args:
        project_info: 项目信息
        criteria_assessment: 准则层评估结果
        
    Returns:
        包含scores和reasoning的字典
    """
    try:
        # 构建方案层评估提示词
        json_template = '''
{
    "C1": {
        "A1_vs_A2": {"value": X, "reasoning": "比较理由"},
        "A1_vs_A3": {"value": X, "reasoning": "比较理由"},
        "A2_vs_A3": {"value": X, "reasoning": "比较理由"}
    },
    "C2": {
        "A1_vs_A2": {"value": X, "reasoning": "比较理由"},
        "A1_vs_A3": {"value": X, "reasoning": "比较理由"},
        "A2_vs_A3": {"value": X, "reasoning": "比较理由"}
    },
    "C3": {
        "A1_vs_A2": {"value": X, "reasoning": "比较理由"},
        "A1_vs_A3": {"value": X, "reasoning": "比较理由"},
        "A2_vs_A3": {"value": X, "reasoning": "比较理由"}
    },
    "C4": {
        "A1_vs_A2": {"value": X, "reasoning": "比较理由"},
        "A1_vs_A3": {"value": X, "reasoning": "比较理由"},
        "A2_vs_A3": {"value": X, "reasoning": "比较理由"}
    },
    "C5": {
        "A1_vs_A2": {"value": X, "reasoning": "比较理由"},
        "A1_vs_A3": {"value": X, "reasoning": "比较理由"},
        "A2_vs_A3": {"value": X, "reasoning": "比较理由"}
    },
    "C6": {
        "A1_vs_A2": {"value": X, "reasoning": "比较理由"},
        "A1_vs_A3": {"value": X, "reasoning": "比较理由"},
        "A2_vs_A3": {"value": X, "reasoning": "比较理由"}
    },
    "C7": {
        "A1_vs_A2": {"value": X, "reasoning": "比较理由"},
        "A1_vs_A3": {"value": X, "reasoning": "比较理由"},
        "A2_vs_A3": {"value": X, "reasoning": "比较理由"}
    }
}
'''
        
        alternative_prompt = f"""你是AHP层次分析法专家，现在需要对项目风险评估的方案层进行两两比较。

项目基本信息：
- 项目类型：{project_info.get('project_type', '未知')}
- 装机容量：{project_info.get('capacity_mw', 0)}MW
- 建设周期：{project_info.get('construction_period', 0)}年
- 客户类型：{project_info.get('client_type', '未知')}
- 项目复杂度：{project_info.get('project_complexity', '未知')}
- 地理位置：{project_info.get('location', '未知')}

方案定义：
A1: 项目风险低 (风险可控，正常推进)
A2: 项目风险中等 (需要重点关注和缓解措施)
A3: 项目风险高 (需要暂缓或重新评估)

请针对以下7个准则，分别对3个方案进行两两比较，构建3×3判断矩阵：

C1: 对经济社会环境发展态势判断失误
C2: 决策体制机制缺陷
C3: 相关法律法规政策缺陷
C4: 次生自然灾害
C5: 损害相关行业经济利益
C6: 破坏生态系统
C7: 项目资金风险

对于每个准则，请评估在该准则下，哪个方案更符合项目实际情况。
注意：数值越大表示该方案在此准则下的适用性越强。

AHP标度：1=同等重要, 3=稍微重要, 5=明显重要, 7=强烈重要, 9=极端重要
倒数表示相反关系：1/3, 1/5, 1/7, 1/9

请严格按照以下JSON格式输出：{json_template}"""
        
        # 调用LLM进行方案层评估
        llm_response = call_llm_expert(alternative_prompt)
        
        # 解析LLM响应
        try:
            import re
            # 更强的JSON提取正则表达式
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # 清理可能的格式问题
                json_str = json_str.strip()
                alternative_comparisons = json.loads(json_str)
                logger.info(f"成功解析方案层评估结果，包含{len(alternative_comparisons)}个准则")
            else:
                raise ValueError("无法找到有效的JSON格式")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"方案层评估解析失败: {e}")
            logger.error(f"LLM原始响应: {llm_response[:500]}...")
            # 完全依赖LLM专家评估，不使用硬编码保险方案
            return {
                "status": "error",
                "message": f"LLM专家方案层评估失败: {e}",
                "scores": {},
                "reasoning": {}
            }
        
        # 计算每个准则下的方案权重
        alternative_scores = {}
        alternative_reasoning = {}
        
        for criterion in ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]:
            # 构建3x3判断矩阵
            matrix = np.ones((3, 3))
            
            criterion_data = alternative_comparisons.get(criterion, {})
            
            # 填充矩阵
            a1_vs_a2 = criterion_data.get("A1_vs_A2", {}).get("value", 1)
            a1_vs_a3 = criterion_data.get("A1_vs_A3", {}).get("value", 1)
            a2_vs_a3 = criterion_data.get("A2_vs_A3", {}).get("value", 1)
            
            matrix[0][1] = a1_vs_a2
            matrix[1][0] = 1 / a1_vs_a2
            matrix[0][2] = a1_vs_a3
            matrix[2][0] = 1 / a1_vs_a3
            matrix[1][2] = a2_vs_a3
            matrix[2][1] = 1 / a2_vs_a3
            
            # 提取reasoning信息
            alternative_reasoning[criterion] = {
                "A1_vs_A2": {
                    "value": a1_vs_a2,
                    "reasoning": criterion_data.get("A1_vs_A2", {}).get("reasoning", "")
                },
                "A1_vs_A3": {
                    "value": a1_vs_a3,
                    "reasoning": criterion_data.get("A1_vs_A3", {}).get("reasoning", "")
                },
                "A2_vs_A3": {
                    "value": a2_vs_a3,
                    "reasoning": criterion_data.get("A2_vs_A3", {}).get("reasoning", "")
                }
            }
            
            # 计算特征向量（权重）
            try:
                eigenvalues, eigenvectors = np.linalg.eig(matrix)
                max_eigenvalue_index = np.argmax(eigenvalues.real)
                principal_eigenvector = eigenvectors[:, max_eigenvalue_index].real
                weights = principal_eigenvector / np.sum(principal_eigenvector)
                
                alternative_scores[criterion] = {
                    "A1": abs(weights[0]),
                    "A2": abs(weights[1]),
                    "A3": abs(weights[2])
                }
                logger.info(f"准则{criterion}权重计算成功: A1={abs(weights[0]):.3f}, A2={abs(weights[1]):.3f}, A3={abs(weights[2]):.3f}")
            except Exception as e:
                logger.error(f"准则{criterion}特征向量计算失败: {e}")
                # 不使用假分数，直接返回错误
                return {
                    "status": "error",
                    "message": f"准则{criterion}权重计算失败: {e}",
                    "scores": {},
                    "reasoning": {}
                }
        
        return {
            "status": "success",
            "scores": alternative_scores,
            "reasoning": alternative_reasoning
        }
        
    except Exception as e:
        logger.error(f"方案层评估失败: {e}")
        # 完全依赖LLM专家评估，不使用任何硬编码假分数
        return {
            "status": "error",
            "message": f"LLM专家评估失败，无法完成方案层评估: {str(e)}",
            "scores": {},
            "reasoning": {}
        }

# 已删除硬编码的默认方案层评估函数
# 现在完全依赖LLM专家评估，提高评估质量和透明度

# 已删除所有硬编码的风险评估函数
# 现在完全依赖LLM专家的智能评估，确保评估的专业性和透明度
# 删除的函数包括：
# - _assess_economic_risk (C1经济风险)
# - _assess_decision_risk (C2决策风险) 
# - _assess_policy_risk (C3政策风险)
# - _assess_disaster_risk (C4自然灾害风险)
# - _assess_industry_risk (C5行业风险)
# - _assess_ecological_risk (C6生态风险)
# - _assess_financial_risk (C7财务风险)

@mcp.tool()
def predict_hydropower_cost(
    capacity_mw: float,
    project_type: str,
    construction_period: int,
    economic_indicator: float
) -> str:
    """
    智慧水电成本预测器
    
    Args:
        capacity_mw: 装机容量(MW)
        project_type: 项目类型(常规大坝/抽水蓄能/径流式)  
        construction_period: 建设周期(年)
        economic_indicator: 经济指标(0-1之间)
    
    Returns:
        JSON格式的成本预测结果
    """
    try:
        # 确保预测器已初始化
        global cost_predictor
        if cost_predictor is None:
            init_predictor()
        
        # 如果仍然无法初始化，检查是否可以导入模块
        if cost_predictor is None:
            if HydropowerCostPredictor is None:
                return json.dumps({
                    "status": "error",
                    "message": "无法导入predict_cost模块，请检查模型文件是否存在"
                }, ensure_ascii=False, indent=2)
            else:
                return json.dumps({
                    "status": "error",
                    "message": "成本预测器初始化失败，请检查模型文件完整性"
                }, ensure_ascii=False, indent=2)
        
        # 参数验证
        if capacity_mw <= 0:
            return json.dumps({
                "status": "error", 
                "message": "装机容量必须大于0"
            }, ensure_ascii=False, indent=2)
            
        if project_type not in ["常规大坝", "抽水蓄能", "径流式"]:
            return json.dumps({
                "status": "error",
                "message": f"无效的项目类型: {project_type}"
            }, ensure_ascii=False, indent=2)
        
        # 调用预测模型
        predicted_cost = cost_predictor.predict_single(
            capacity_mw, project_type, construction_period, economic_indicator
        )
        
        # 计算置信区间 (±15%)
        confidence_lower = predicted_cost * 0.85
        confidence_upper = predicted_cost * 1.15
        
        # 获取特征重要性
        feature_importance = cost_predictor.get_feature_importance()
        
        # 智慧水电成本分解估算 - AI提示词生成
        cost_breakdown_prompt = f"""
请根据以下信息为智慧水电项目提供个性化的成本分解估算：

项目基本信息：
- 装机容量：{capacity_mw}MW
- 项目类型：{project_type}
- 建设周期：{construction_period}年
- 经济指标：{economic_indicator}
- 预测总成本：{predicted_cost:.2f}亿元

请将总成本按以下三个维度进行分解，并给出具体的比例和金额：
1. 物理基础设施 (physical_infrastructure)：包括大坝、发电机组、输电线路等硬件设施
2. 数字化系统 (digital_systems)：包括智能监控、数据采集、自动化控制等软件系统
3. 集成服务 (integration_services)：包括系统集成、调试、培训、维护等服务

请以JSON格式返回，包含每个维度的比例（小数形式，总和为1.0）和对应的金额（亿元）。
格式示例：
{{
    "physical_infrastructure": {{"ratio": 0.xx, "amount": x.xx}},
    "digital_systems": {{"ratio": 0.xx, "amount": x.xx}},
    "integration_services": {{"ratio": 0.xx, "amount": x.xx}}
}}
"""
        
        # 调用AI生成个性化成本分解
        try:
            cost_breakdown_response = call_llm_expert(cost_breakdown_prompt)
            # 尝试解析AI返回的JSON
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cost_breakdown_response)
            if json_match:
                cost_breakdown_data = json.loads(json_match.group())
                # 严格要求AI提供完整的比例数据，不使用任何默认值
                physical_ratio = cost_breakdown_data.get("physical_infrastructure", {}).get("ratio")
                digital_ratio = cost_breakdown_data.get("digital_systems", {}).get("ratio")
                integration_ratio = cost_breakdown_data.get("integration_services", {}).get("ratio")
                
                if physical_ratio is None or digital_ratio is None or integration_ratio is None:
                    raise ValueError("AI返回的成本分解数据不完整")
                
                cost_breakdown = {
                    "physical_infrastructure": physical_ratio,
                    "digital_systems": digital_ratio,
                    "integration_services": integration_ratio
                }
            else:
                raise ValueError("AI返回格式不正确，无法解析JSON")
        except Exception as e:
            logger.error(f"AI成本分解生成失败: {e}")
            return json.dumps({
                "status": "error",
                "message": f"成本分解估算失败，AI调用异常: {str(e)}"
            }, ensure_ascii=False, indent=2)
        
        result = {
            "status": "success",
            "predicted_cost_million_rmb": round(predicted_cost * 100, 2),  # 转换为万元
            "predicted_cost_billion_rmb": round(predicted_cost, 2),
            "confidence_interval": {
                "lower": round(confidence_lower, 2),
                "upper": round(confidence_upper, 2)
            },
            "cost_breakdown": cost_breakdown,
            "feature_importance": feature_importance,
            "unit_cost_per_mw": round(predicted_cost * 10000 / capacity_mw, 2),
            "prediction_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"成本预测失败: {e}")
        return json.dumps({
            "status": "error",
            "message": f"预测失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def assess_project_risk(
    predicted_cost: float,
    project_type: str,
    capacity_mw: float,
    construction_period: int,
    client_type: str,
    project_complexity: str,
    project_description: str = "",
    location: str = "",
    environmental_conditions: str = ""
) -> str:
    """
    智能项目风险评估器 - 基于动态AHP和LLM专家评估
    
    Args:
        predicted_cost: 基础成本预测(亿元)
        project_type: 项目类型(常规大坝/抽水蓄能/径流式)
        capacity_mw: 装机容量(MW)
        construction_period: 建设周期(年)
        client_type: 客户类型(央企/国企/民企/外企)
        project_complexity: 项目复杂度(简单/中等/复杂)
        project_description: 项目背景描述(可选)
        location: 地理位置(可选)
        environmental_conditions: 环境条件描述(可选)
    
    Returns:
        JSON格式的智能风险评估结果
    """
    try:
        # 参数验证
        if predicted_cost <= 0:
            return json.dumps({
                "status": "error",
                "message": "预测成本必须大于0"
            }, ensure_ascii=False, indent=2)
            
        if capacity_mw <= 0:
            return json.dumps({
                "status": "error",
                "message": "装机容量必须大于0"
            }, ensure_ascii=False, indent=2)
            
        if construction_period <= 0:
            return json.dumps({
                "status": "error",
                "message": "建设周期必须大于0"
            }, ensure_ascii=False, indent=2)
        
        # 构建项目信息字典
        project_info = {
            "project_type": project_type,
            "capacity_mw": capacity_mw,
            "construction_period": construction_period,
            "client_type": client_type,
            "project_complexity": project_complexity,
            "project_description": project_description,
            "location": location,
            "environmental_conditions": environmental_conditions,
            "predicted_cost": predicted_cost
        }
        
        # 调用AHP专家评估
        ahp_result = ahp_expert_assessment(project_info)
        
        if ahp_result.get("status") != "success":
            return json.dumps(ahp_result, ensure_ascii=False, indent=2)
        
        # 获取AHP评估结果
        risk_level = ahp_result["risk_level"]
        final_scores = ahp_result.get("final_scores", {})
        criteria_assessment = ahp_result["criteria_assessment"]
        ahp_weights = ahp_result.get("ahp_weights", [])
        
        # 从final_scores计算risk_score（最高得分作为风险分数）
        risk_score = max(final_scores.values()) if final_scores else 0.0
        
        # 基于风险等级确定成本超支概率和应急费用
        if risk_level == "低":
            overrun_prob = {"0-10%": 0.60, "10-20%": 0.25, "20-30%": 0.10, "30%+": 0.05}
            contingency_pct = 8.0
        elif risk_level == "中等":
            overrun_prob = {"0-10%": 0.35, "10-20%": 0.30, "20-30%": 0.20, "30%+": 0.15}
            contingency_pct = 15.0
        else:  # 高风险
            overrun_prob = {"0-10%": 0.20, "10-20%": 0.25, "20-30%": 0.30, "30%+": 0.25}
            contingency_pct = 25.0
        
        # 提取关键风险因素和缓解建议
        key_risk_factors = []
        mitigation_suggestions = []
        
        # 获取alternative_scores用于风险因素分析
        alternative_scores = ahp_result.get("alternative_scores", {})
        
        # 基于AHP权重和风险因子分数识别关键风险
        for i, criteria_id in enumerate(["C1", "C2", "C3", "C4", "C5", "C6", "C7"]):
            weight = ahp_weights[i] if i < len(ahp_weights) else 0
            
            # 从alternative_scores获取该准则的最高风险分数
            criteria_scores = alternative_scores.get(criteria_id, {})
            if criteria_scores:
                # 取最高风险方案的分数作为该准则的风险分数
                score = max(criteria_scores.get("A1", 0), criteria_scores.get("A2", 0), criteria_scores.get("A3", 0))
            else:
                score = 0
                
            weighted_score = score * weight
            
            # 高风险指标(加权分数>=0.1)作为关键风险因素
            if weighted_score >= 0.1:
                criteria_name = AHP_CRITERIA.get(criteria_id, criteria_id)
                key_risk_factors.append(f"{criteria_name}(风险分数:{score:.2f}, 权重:{weight:.3f})")
                
                # 基于指标类型生成缓解建议
                if criteria_id == "C1":
                    mitigation_suggestions.append("加强宏观经济环境分析和政策研判")
                elif criteria_id == "C2":
                    mitigation_suggestions.append("完善项目决策体制和管理机制")
                elif criteria_id == "C3":
                    mitigation_suggestions.append("密切关注法规政策变化，确保合规性")
                elif criteria_id == "C4":
                    mitigation_suggestions.append("制定自然灾害应急预案和防护措施")
                elif criteria_id == "C5":
                    mitigation_suggestions.append("加强利益相关方沟通协调")
                elif criteria_id == "C6":
                    mitigation_suggestions.append("严格执行环保标准，制定生态保护方案")
                elif criteria_id == "C7":
                    mitigation_suggestions.append("优化资金筹措方案，加强财务风险管控")
        
        # 正确提取criteria_scores - 从成对比较结果中获取value值
        criteria_scores = {}
        for key, comparison in criteria_assessment.items():
            if key.startswith('C') and '_vs_' in key and isinstance(comparison, dict):
                criteria_scores[key] = comparison.get('value', 0)
        
        # 生成外部AI分析提示词
        risk_analysis_prompt = {
            "instruction": "请基于AHP专家评估结果，生成专业的项目风险分析报告",
            "context": "智慧水电项目风险管理，需要为项目决策提供专业建议",
            "assessment_data": {
                "risk_level": risk_level,
                "risk_score": risk_score,
                "criteria_scores": criteria_scores,
                "overall_assessment": criteria_assessment.get('overall_assessment', '')
            },
            "project_context": project_info,
            "requirements": [
                "结合具体项目情况进行风险分析",
                "体现水电行业专业特色",
                "提供可操作的风险管控建议",
                "语言专业且具有指导价值"
            ]
        }
        
        # 提取详细的专家评估理由
        detailed_reasoning = {
            "criteria_layer_reasoning": {},
            "alternative_layer_reasoning": {}
        }
        
        # 提取准则层评估的详细理由
        pairwise_comparisons = criteria_assessment.get("pairwise_comparisons", {})
        for comparison_key, comparison_data in pairwise_comparisons.items():
            if isinstance(comparison_data, dict) and "reasoning" in comparison_data:
                detailed_reasoning["criteria_layer_reasoning"][comparison_key] = {
                    "value": comparison_data.get("value", 1),
                    "reasoning": comparison_data.get("reasoning", "")
                }
        
        # 提取方案层评估的详细理由
        alternative_scores = ahp_result.get("alternative_scores", {})
        if "alternative_reasoning" in ahp_result:
            detailed_reasoning["alternative_layer_reasoning"] = ahp_result["alternative_reasoning"]
        
        # 构建LLM专家评估理由的可读性摘要
        expert_reasoning_summary = []
        expert_reasoning_summary.append("\n=== 🤖 LLM专家评估详细理由 ===")
        expert_reasoning_summary.append(f"📊 评估方法: 动态AHP层次分析法 + LLM专家评估")
        expert_reasoning_summary.append(f"🎯 风险等级: {risk_level} (评分: {risk_score:.3f})")
        expert_reasoning_summary.append(f"⏰ 评估时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 准则层专家评估理由
        expert_reasoning_summary.append("\n📋 准则层专家评估理由:")
        pairwise_comparisons = criteria_assessment.get("pairwise_comparisons", {})
        for comparison_key, comparison_data in pairwise_comparisons.items():
            if isinstance(comparison_data, dict) and "reasoning" in comparison_data:
                value = comparison_data.get("value", 1)
                reasoning = comparison_data.get("reasoning", "")
                expert_reasoning_summary.append(f"  • {comparison_key}: 重要性比值={value:.2f}")
                expert_reasoning_summary.append(f"    理由: {reasoning}")
        
        # 方案层专家评估理由
        alternative_reasoning = ahp_result.get("alternative_reasoning", {})
        if alternative_reasoning:
            expert_reasoning_summary.append("\n🔍 方案层专家评估理由:")
            for criterion, comparisons in alternative_reasoning.items():
                if isinstance(comparisons, dict):
                    criterion_name = AHP_CRITERIA.get(criterion, criterion)
                    expert_reasoning_summary.append(f"  📌 {criterion_name}:")
                    for comp_key, comp_data in comparisons.items():
                        if isinstance(comp_data, dict) and "reasoning" in comp_data:
                            value = comp_data.get("value", 1)
                            reasoning = comp_data.get("reasoning", "")
                            expert_reasoning_summary.append(f"    • {comp_key}: 比值={value:.2f}")
                            expert_reasoning_summary.append(f"      理由: {reasoning}")
        
        # 整体评估总结
        overall_assessment = criteria_assessment.get("overall_assessment", "")
        if overall_assessment:
            expert_reasoning_summary.append("\n💡 专家整体评估总结:")
            expert_reasoning_summary.append(f"  {overall_assessment}")
        
        expert_reasoning_text = "\n".join(expert_reasoning_summary)
        
        # 构建最终结果 - 将专家理由放在顶层便于AI直接看到
        result = {
            "status": "success",
            "expert_reasoning_display": expert_reasoning_text,
            "assessment_method": "动态AHP层次分析法 + LLM专家评估",
            "risk_level": risk_level,
            "risk_score": risk_score,
            "cost_overrun_probability": overrun_prob,
            "contingency_recommendation": {
                "percentage": contingency_pct,
                "amount_million_rmb": round(predicted_cost * contingency_pct * 10, 2),
                "justification": f"基于{risk_level}风险等级(评分:{risk_score})的专业建议"
            },
            "key_risk_factors": key_risk_factors,
            "mitigation_suggestions": mitigation_suggestions,
            "detailed_expert_reasoning": detailed_reasoning,
            "llm_expert_insights": {
                "criteria_layer_summary": criteria_assessment.get("overall_assessment", ""),
                "total_comparisons": len(pairwise_comparisons),
                "reasoning_available": len([r for r in pairwise_comparisons.values() if isinstance(r, dict) and "reasoning" in r]),
                "alternative_reasoning": ahp_result.get("alternative_reasoning", {})
            },
            "criteria_assessment": criteria_assessment,
            "expert_analysis_prompt": risk_analysis_prompt,
            "requires_external_ai_analysis": True,
            "assessment_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            # 添加方案层得分对比信息
            "alternative_scores": ahp_result.get("alternative_scores", {}),
            "final_scores": ahp_result.get("final_scores", {}),
            "selected_alternative": ahp_result.get("selected_alternative", ""),
            "ahp_weights": ahp_result.get("ahp_weights", []),
            "consistency_ratio": ahp_result.get("consistency_ratio", 0.0)
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"智能风险评估失败: {e}")
        return json.dumps({
            "status": "error", 
            "message": f"评估失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

# @mcp.tool()  # 工具3已停用 - 保留代码但不注册为MCP工具
def generate_analysis_data(
    cost_prediction_json: str,
    risk_assessment_json: str,
    project_params_json: str
) -> str:
    """
    成本分析数据生成器 - 已停用
    
    Args:
        cost_prediction_json: 工具1的JSON输出
        risk_assessment_json: 工具2的JSON输出  
        project_params_json: 原始项目参数JSON
        
    Returns:
        整合后的结构化分析数据JSON
    """
    try:
        # 解析输入数据
        cost_data = json.loads(cost_prediction_json)
        risk_data = json.loads(risk_assessment_json)
        project_params = json.loads(project_params_json)
        
        if cost_data.get("status") != "success" or risk_data.get("status") != "success":
            return json.dumps({
                "status": "error",
                "message": "输入数据状态异常"
            }, ensure_ascii=False, indent=2)
        
        # 提取关键数据
        total_cost = cost_data["predicted_cost_billion_rmb"]
        capacity_mw = project_params.get("capacity_mw", 0)
        construction_period = project_params.get("construction_period", 0)
        
        # 项目摘要
        project_summary = {
            "total_cost_million_rmb": cost_data["predicted_cost_million_rmb"],
            "total_cost_billion_rmb": total_cost,
            "cost_per_mw": round(total_cost * 10000 / capacity_mw, 2) if capacity_mw > 0 else 0,
            "construction_duration_months": construction_period * 12,
            "confidence_level": "85%"
        }
        
        # 成本驱动因素分析
        feature_importance = cost_data.get("feature_importance", {})
        cost_drivers_analysis = []
        
        # 成本驱动因素分析提示词（供外部AI模型使用）
        cost_driver_analysis_prompt = {
            "instruction": "请基于以下成本驱动因素的重要性数据，为每个因素生成专业的影响描述分析",
            "context": "这是智慧水电项目成本预测分析，需要解释各因素对项目成本的具体影响机制",
            "requirements": [
                "分析应体现水电行业专业特色",
                "说明因素对成本的影响机制和程度", 
                "语言专业且易于理解",
                "每个描述控制在30字以内"
            ],
            "factor_context": {
                "capacity_mw": "装机容量(MW)",
                "capacity_per_period": "建设强度指标", 
                "project_type_encoded": "项目类型编码",
                "economic_indicator": "经济环境指标"
            }
        }
        
        for factor, importance in feature_importance.items():
            cost_drivers_analysis.append({
                "factor": factor,
                "importance": importance,
                "analysis_prompt": cost_driver_analysis_prompt,
                "requires_ai_analysis": True
            })
        
        # 行业对标分析
        industry_avg_cost_per_mw = 45.0  # 行业平均值
        project_cost_per_mw = project_summary["cost_per_mw"]
        vs_industry = ((project_cost_per_mw - industry_avg_cost_per_mw) / industry_avg_cost_per_mw * 100) if industry_avg_cost_per_mw > 0 else 0
        
        industry_benchmarking = {
            "industry_average_cost_per_mw": industry_avg_cost_per_mw,
            "project_vs_industry": f"{vs_industry:+.1f}%",
            "position_percentile": 75 if vs_industry > 0 else 25,
            "comparable_projects": ["大型抽水蓄能电站", "智慧化水电站改造项目"]
        }
        
        # 风险分析整合
        contingency_justification_prompt = {
            "instruction": "请基于项目风险评估结果，生成应急费用建议的专业分析说明",
            "context": "智慧水电项目成本管控，需要解释应急费用比例的合理性",
            "data_context": {
                "risk_level": risk_data["risk_level"],
                "risk_score": risk_data["risk_score"],
                "recommended_percentage": risk_data["contingency_recommendation"]["percentage"]
            },
            "requirements": [
                "结合具体风险等级和评分进行分析",
                "体现水电行业项目管理专业性",
                "说明应急费用比例的依据和合理性",
                "语言专业且具有说服力"
            ]
        }
        
        risk_analysis = {
            "overall_risk": risk_data["risk_level"],
            "risk_score": risk_data["risk_score"], 
            "key_risks": risk_data["key_risk_factors"],
            "contingency_analysis": {
                "recommended_percentage": risk_data["contingency_recommendation"]["percentage"],
                "recommended_amount": risk_data["contingency_recommendation"]["amount_million_rmb"],
                "justification_prompt": contingency_justification_prompt,
                "requires_ai_analysis": True
            },
            "overrun_probability": risk_data["cost_overrun_probability"]
        }
        
        # 优化建议
        optimization_opportunities = []
        
        # 优化建议生成提示词（供外部AI模型使用）
        optimization_prompt_base = {
            "instruction": "请基于项目成本分析结果，生成具体的优化实施建议",
            "context": "智慧水电项目成本优化，需要提供可操作的改进措施",
            "project_context": {
                "cost_per_mw": project_summary["cost_per_mw"],
                "industry_avg": industry_avg_cost_per_mw,
                "risk_score": risk_data["risk_score"],
                "project_type": project_params.get("project_type", "未知")
            },
            "requirements": [
                "提供具体可操作的实施方案",
                "体现水电行业专业特色和最佳实践",
                "结合项目实际情况进行针对性建议",
                "语言专业且具有指导价值"
            ]
        }
        
        if project_summary["cost_per_mw"] > industry_avg_cost_per_mw:
            equipment_optimization_prompt = dict(optimization_prompt_base)
            equipment_optimization_prompt["specific_focus"] = "设备采购成本控制和供应链优化策略"
            
            construction_optimization_prompt = dict(optimization_prompt_base)
            construction_optimization_prompt["specific_focus"] = "建设管理效率提升和施工组织优化"
            
            optimization_opportunities.extend([
                {
                    "area": "设备采购优化",
                    "potential_saving": "5-8%", 
                    "implementation_prompt": equipment_optimization_prompt,
                    "requires_ai_analysis": True
                },
                {
                    "area": "建设管理优化",
                    "potential_saving": "3-5%",
                    "implementation_prompt": construction_optimization_prompt,
                    "requires_ai_analysis": True
                }
            ])
            
        if risk_data["risk_score"] > 60:
            risk_optimization_prompt = dict(optimization_prompt_base)
            risk_optimization_prompt["specific_focus"] = "项目风险管控体系建设和不确定性成本控制"
            
            optimization_opportunities.append({
                "area": "风险管控优化",
                "potential_saving": "2-4%",
                "implementation_prompt": risk_optimization_prompt,
                "requires_ai_analysis": True
            })
        
        # 整合结果
        result = {
            "status": "success",
            "project_summary": project_summary,
            "cost_drivers_analysis": cost_drivers_analysis,
            "industry_benchmarking": industry_benchmarking,
            "risk_analysis": risk_analysis,
            "optimization_opportunities": optimization_opportunities,
            "analysis_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "data_sources": {
                "cost_model": "Lasso回归模型",
                "risk_model": "多因子风险评估模型",
                "benchmark_data": "行业统计数据"
            }
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except json.JSONDecodeError as e:
        return json.dumps({
            "status": "error",
            "message": f"JSON解析失败: {str(e)}"
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"分析数据生成失败: {e}")
        return json.dumps({
            "status": "error",
            "message": f"生成失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

# 启动服务器
if __name__ == "__main__":
    logger.info(f"启动 {TOOL_NAME}")
    logger.info("🎯 核心功能: Lasso回归成本预测 + 动态AHP多准则风险评估")
    logger.info("🤖 集成AI专家系统，实现智能化项目风险评估")
    logger.info("📊 支持7大风险维度的层次分析法(AHP)评估")
    
    # 初始化预测器
    init_predictor()
    
    try:
        # 运行MCP服务 - 使用stdio传输（标准输入输出）
        mcp.run()
    except KeyboardInterrupt:
        logger.info("正在关闭...")
    finally:
        logger.info("服务器已关闭")