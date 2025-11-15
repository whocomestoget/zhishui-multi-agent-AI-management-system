#!/usr/bin/env python3
"""
智水信息Multi-Agent智能分析系统 - BusinessAgent基类
负责与MCP服务通信，为具体业务Agent提供统一的服务调用接口

功能：解决智水信息的数据分散和系统割裂问题，提供统一的MCP服务调用接口
技术：使用标准Stdio MCP Client进行JSON-RPC 2.0通信

Author: 商海星辰队
Version: 2.0.0 - 重构版本，统一使用stdio协议
"""

import json
import logging
import time
import os
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent, AgentTask, AgentResult
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from standardized_mcp_client_v2 import StandardizedMCPClient
from config import get_ai_config

# AI配置 - 统一使用环境变量模式
AI_CONFIG = get_ai_config()

# ================================
# BusinessAgent基类 - 重构版本
# ================================

class BusinessAgent(BaseAgent):
    """
    业务分析Agent基类，负责与MCP服务通信
    
    功能：
    - 提供统一的MCP服务调用接口
    - 管理stdio MCP客户端连接
    - 处理业务分析任务的通用流程
    - 集成AI分析和建议生成
    """
    
    def __init__(self, agent_id: str, agent_name: str, mcp_service: str):
        """
        初始化BusinessAgent
        
        Args:
            agent_id: Agent唯一标识
            agent_name: Agent显示名称
            mcp_service: 绑定的MCP服务名称（financial/cost_prediction/knowledge/efficiency）
        """
        super().__init__(agent_id, agent_name)
        
        self.mcp_service = mcp_service
        self.mcp_client: Optional[StandardizedMCPClient] = None
        
        # 初始化标准化MCP客户端
        try:
            self.mcp_client = StandardizedMCPClient()
            self.service_name = f"{mcp_service}_service"
            self.capabilities = self.mcp_client.capabilities
            self.logger.info(f"{self.agent_name} 成功初始化标准化MCP客户端: {self.service_name}")
        except Exception as e:
            self.logger.error(f"初始化标准化MCP客户端失败: {e}")
            raise

    def check_service_health(self) -> bool:
        """
        检查MCP服务健康状态
        
        Returns:
            bool: 服务是否健康
        """
        try:
            if not self.mcp_client:
                return False
            # 标准化MCP客户端总是可用的
            return True
        except Exception as e:
            self.logger.warning(f"MCP服务健康检查失败: {e}")
            return False

    def call_mcp_tool(self, tool_name: str, arguments: dict = None, **kwargs) -> dict:
        """
        调用MCP工具 - 使用标准化MCP客户端
        
        Args:
            tool_name: MCP工具名称
            arguments: 工具参数字典
            **kwargs: 额外的关键字参数，会合并到arguments中
            
        Returns:
            dict: MCP工具调用结果
        """
        if arguments is None:
            arguments = {}
        
        # 如果使用了关键字参数，将其合并到arguments中
        if kwargs:
            arguments.update(kwargs)
            
        try:
            # 检查MCP客户端是否可用
            if not self.mcp_client:
                return {
                    "error": f"标准化MCP客户端未初始化: {self.mcp_service}",
                    "tool_name": tool_name,
                    "arguments": arguments
                }
            
            # 调用标准化MCP工具
            self.logger.debug(f"调用标准化MCP工具: {tool_name}, 参数: {arguments}")
            result = self.mcp_client.call_tool(tool_name, arguments)
            
            # 检查结果
            if isinstance(result, dict) and "error" in result:
                self.logger.warning(f"标准化MCP工具调用返回错误: {result['error']}")
                return result
            
            self.logger.debug(f"标准化MCP工具调用成功: {tool_name}")
            return result if isinstance(result, dict) else {"result": result}
            
        except Exception as e:
            error_msg = f"标准化MCP工具调用异常: {str(e)}"
            self.logger.error(error_msg)
            return {
                "error": error_msg,
                "tool_name": tool_name,
                "arguments": arguments
            }
    
    def cleanup_mcp_client(self):
        """
        清理标准化MCP客户端资源
        """
        if hasattr(self, 'mcp_client') and self.mcp_client:
            try:
                # 标准化MCP客户端不需要显式断开连接
                self.logger.info(f"标准化MCP客户端资源已清理: {getattr(self, 'service_name', 'unknown')}")
            except Exception as e:
                self.logger.error(f"清理标准化MCP客户端时出错: {e}")
            finally:
                self.mcp_client = None
    
    def __del__(self):
        """
        析构函数，确保资源清理
        """
        self.cleanup_mcp_client()
    
    def call_llm(self, prompt: str, **kwargs) -> str:
        """调用LLM进行智能分析
        
        Args:
            prompt: 分析提示词
            **kwargs: 额外参数
            
        Returns:
            str: LLM响应结果
        """
        try:
            import openai
            
            self.logger.info(f"开始LLM调用，提示词长度: {len(prompt)}")
            
            # 配置OpenAI客户端
            client = openai.OpenAI(
                api_key=AI_CONFIG.get("api_key", ""),
                base_url=AI_CONFIG.get("api_base", ""),
                timeout=kwargs.get("timeout", 30)
            )
            
            self.logger.info("OpenAI客户端配置完成，开始发送请求...")
            
            # 调用LLM
            response = client.chat.completions.create(
                model=AI_CONFIG.get("model", ""),
                messages=[
                    {"role": "system", "content": "你是智水信息技术有限公司的专业AI分析助手，专注于电力和水利行业的智慧管理解决方案。请提供专业、准确、实用的分析建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", AI_CONFIG.get("temperature", 0.7)),
                max_tokens=kwargs.get("max_tokens", 2000)
            )
            
            self.logger.info("LLM请求发送完成，开始处理响应...")
            
            # 检查响应有效性
            if response is None:
                error_msg = "LLM调用返回None响应"
                self.logger.error(error_msg)
                return f"LLM调用失败: {error_msg}"
            
            if not hasattr(response, 'choices') or not response.choices:
                error_msg = "LLM调用响应缺少choices字段"
                self.logger.error(error_msg)
                return f"LLM调用失败: {error_msg}"
            
            if not response.choices[0].message:
                error_msg = "LLM调用响应choices[0]缺少message"
                self.logger.error(error_msg)
                return f"LLM调用失败: {error_msg}"
            
            result = response.choices[0].message.content
            self.logger.info(f"LLM调用成功，返回{len(result)}字符")
            return result
            
        except ImportError:
            error_msg = "缺少openai依赖包，请安装: pip install openai"
            self.logger.error(error_msg)
            return f"LLM调用失败: {error_msg}"
        except Exception as e:
            error_msg = f"LLM调用异常: {str(e)}"
            self.logger.error(error_msg)
            return f"LLM调用失败: {error_msg}"

    def execute_task(self, task: AgentTask) -> AgentResult:
        """执行业务分析任务（基础实现）"""
        start_time = time.time()
        
        # 添加详细的执行日志
        self.logger.info(f"🚀 开始执行任务: {task.task_id}, 智能体: {self.agent_id}")
        self.logger.info(f"📝 任务类型: {task.task_type}, 优先级: {task.priority}")
        
        try:
            # 设置忙碌状态
            self.is_busy = True
            self.logger.info(f"⚡ 智能体 {self.agent_id} 已设置为忙碌状态")
            
            # 1. 验证输入数据
            self.logger.info(f"🔍 开始验证输入数据: {self.agent_id}")
            is_valid, errors = self.validate_input_data(task)
            if not is_valid:
                self.logger.error(f"❌ 输入数据验证失败: {task.task_id}, 错误: {errors}")
                return AgentResult(
                    task_id=task.task_id,
                    agent_id=self.agent_id,
                    status="error",
                    result_data={},
                    confidence_score=0.0,
                    recommendations=[],
                    error_message=f"输入数据验证失败: {'; '.join(errors)}",
                    processing_time=time.time() - start_time
                )
            self.logger.info(f"✅ 输入数据验证通过: {self.agent_id}")
            
            # 2. 检查服务健康状态
            self.logger.info(f"🏥 开始检查服务健康状态: {self.agent_id}")
            if not self.check_service_health():
                self.logger.error(f"❌ 服务健康检查失败: {self.agent_id}")
                return AgentResult(
                    task_id=task.task_id,
                    agent_id=self.agent_id,
                    status="error",
                    result_data={},
                    confidence_score=0.0,
                    recommendations=[],
                    error_message=f"MCP服务 {self.service_name} 不可用",
                    processing_time=time.time() - start_time
                )
            self.logger.info(f"✅ 服务健康检查通过: {self.agent_id}")
            
            # 3. 预处理数据
            self.logger.info(f"🔄 开始预处理数据: {self.agent_id}")
            processed_data = self.preprocess_data(task)
            self.logger.info(f"✅ 数据预处理完成: {self.agent_id}")
            
            # 4. 执行具体的业务分析（子类实现）
            self.logger.info(f"🔍 开始执行业务分析: {self.agent_id}")
            raw_result = self.perform_analysis(processed_data, task)
            self.logger.info(f"✅ 业务分析完成: {self.agent_id}")
            
            # 5. 后处理结果
            self.logger.info(f"🔧 开始后处理结果: {self.agent_id}")
            final_result = self.postprocess_result(raw_result, task)
            self.logger.info(f"✅ 结果后处理完成: {self.agent_id}")
            
            # 6. 生成AI分析总结
            self.logger.info("🤖 开始生成AI分析总结...")
            ai_summary = self.generate_ai_summary(final_result, task)
            self.logger.info("✅ AI分析总结生成完成")
            final_result["ai_analysis"] = ai_summary
            
            execution_time = time.time() - start_time
            
            result = AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                status="success",
                result_data=final_result,
                confidence_score=self.calculate_confidence_score(final_result),
                recommendations=self.generate_recommendations(final_result),
                processing_time=execution_time
            )
            
            # 执行历史记录（暂时跳过）
            # TODO: 实现执行历史记录功能
            
            return result
            
        except Exception as e:
            return self.handle_error(e, task)
        finally:
            self.is_busy = False

    def preprocess_data(self, task: AgentTask) -> Dict[str, Any]:
        """预处理任务数据（子类可以重写）"""
        try:
            # 基础数据预处理 - 直接返回input_data，并添加元数据
            processed_data = task.input_data.copy() if task.input_data else {}
            
            # 添加元数据
            processed_data.update({
                "task_id": task.task_id,
                "task_type": task.task_type,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # 数据验证
            if not task.input_data:
                self.logger.warning(f"任务 {task.task_id} 输入数据为空")
                processed_data["data_quality"] = 0.3
            else:
                processed_data["data_quality"] = 0.8
            
            self.logger.info(f"数据预处理完成，质量评分: {processed_data['data_quality']}")
            return processed_data
            
        except Exception as e:
            self.logger.error(f"数据预处理失败: {e}")
            return {
                "task_id": task.task_id,
                "error": f"数据预处理失败: {str(e)}",
                "data_quality": 0.0
            }
    
    def postprocess_result(self, raw_result: Dict[str, Any], task: AgentTask) -> Dict[str, Any]:
        """后处理分析结果（子类可以重写）"""
        try:
            # 基础结果后处理
            processed_result = {
                "task_id": task.task_id,
                "agent_id": self.agent_id,
                "analysis_type": task.task_type,
                "raw_data": raw_result,
                "processed_at": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 合并原始结果
            if isinstance(raw_result, dict):
                processed_result.update(raw_result)
            else:
                processed_result["result"] = raw_result
            
            # 结果质量评估
            if "error" in processed_result:
                processed_result["result_quality"] = 0.0
            elif "prediction" in processed_result or "analysis" in processed_result:
                processed_result["result_quality"] = 0.9
            else:
                processed_result["result_quality"] = 0.6
            
            self.logger.info(f"结果后处理完成，质量评分: {processed_result['result_quality']}")
            return processed_result
            
        except Exception as e:
            self.logger.error(f"结果后处理失败: {e}")
            return {
                "task_id": task.task_id,
                "error": f"结果后处理失败: {str(e)}",
                "result_quality": 0.0,
                "raw_data": raw_result
            }

    def perform_analysis(self, data: Dict[str, Any], task: AgentTask) -> Dict[str, Any]:
        """执行具体的业务分析（子类必须重写）"""
        raise NotImplementedError("子类必须实现perform_analysis方法")

    def generate_ai_summary(self, result: Dict[str, Any], task: AgentTask) -> Dict[str, Any]:
        """生成AI分析总结"""
        try:
            # 构建AI分析提示词
            analysis_prompt = f"""
            请对以下{self.agent_name}的分析结果进行专业总结：
            
            原始结果数据：
            {json.dumps(result, ensure_ascii=False, indent=2)}
            
            请提供：
            1. 核心发现：3-5个关键洞察点
            2. 风险提示：潜在风险和注意事项
            3. 业务建议：具体可执行的改进建议
            4. 置信度评估：分析结果的可信度说明
            
            请以专业、简洁的方式回答，重点突出实用性和可操作性。
            """
            
            ai_response = self.call_llm(analysis_prompt)
            
            return {
                "summary_content": ai_response,
                "generated_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "agent_name": self.agent_name
            }
            
        except Exception as e:
            self.logger.warning(f"AI总结生成失败: {e}")
            return {
                "summary_content": "AI总结生成失败，请查看原始分析结果",
                "error": str(e),
                "generated_at": time.strftime('%Y-%m-%d %H:%M:%S')
            }

    def calculate_confidence_score(self, result: Dict[str, Any]) -> float:
        """基于实际数据质量计算置信度（子类可以重写）"""
        confidence_factors = []
        
        # 基础错误检查
        if "error" in result:
            return 0.0
        
        # 数据完整性评估
        if "data_quality" in result:
            data_quality = result.get("data_quality", 0.5)
            confidence_factors.append(data_quality * 0.4)
        else:
            confidence_factors.append(0.3)  # 默认数据质量
        
        # 分析结果质量评估
        if any(key in result for key in ["prediction", "analysis", "metrics", "score"]):
            confidence_factors.append(0.3)  # 有具体分析结果
            
            # 结果质量评估
            if "result_quality" in result:
                result_quality = result.get("result_quality", 0.5)
                confidence_factors.append(result_quality * 0.2)
        
        # AI分析质量评估
        if "ai_analysis" in result:
            ai_content = result["ai_analysis"].get("summary_content", "")
            if ai_content and len(ai_content) > 100:
                confidence_factors.append(0.1)  # 详细AI分析
        
        return min(sum(confidence_factors), 1.0) if confidence_factors else 0.3

    def generate_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """基于LLM分析生成业务建议（子类可以重写）"""
        try:
            # 使用LLM生成专业的业务建议
            prompt = f"""
            基于以下业务分析结果，请生成3-5条具体的业务管理建议：
            
            分析结果：{json.dumps(result, ensure_ascii=False, indent=2)}
            
            请提供：
            1. 业务流程优化建议
            2. 市场拓展建议
            3. 客户关系管理建议
            4. 运营效率提升建议
            5. 风险管控建议
            
            每条建议要具体、可操作，针对智水信息的电力和水利行业特点。
            """
            
            response = self.call_llm(prompt)
            
            # 解析建议列表
            recommendations = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•')) or len(line) > 10):
                    # 清理编号和符号
                    import re
                    clean_line = re.sub(r'^[0-9]+\.\s*', '', line)
                    clean_line = re.sub(r'^[-•]\s*', '', clean_line)
                    if clean_line:
                        recommendations.append(clean_line)
            
            return recommendations if recommendations else ["基于当前分析结果，建议制定业务发展策略"]
            
        except Exception as e:
            self.logger.error(f"生成业务建议失败: {e}")
            return ["建议基于分析结果制定业务管理策略"]

    def get_service_info(self) -> Dict[str, Any]:
        """获取绑定的MCP服务信息"""
        return {
            "service_name": self.service_name,
            "api_url": self.api_url,
            "capabilities": self.capabilities,
            "health_status": self.check_service_health()
        }

# ================================
# 3. 错误处理和重试机制
# ================================

    def handle_error(self, error: Exception, task: AgentTask) -> AgentResult:
        """处理执行错误"""
        self.logger.error(f"Agent {self.agent_id} 执行任务 {task.task_id} 失败: {str(error)}")
        
        return AgentResult(
            task_id=task.task_id,
            agent_id=self.agent_id,
            status="error",
            result_data={},
            confidence_score=0.0,
            recommendations=[],
            error_message=str(error)
        )

class MCPServiceError(Exception):
    """MCP服务调用错误"""
    pass

def retry_mcp_call(func, max_retries: int = 3, delay: float = 1.0):
    """MCP服务调用重试装饰器"""
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(delay * (attempt + 1))
        return None
    return wrapper
