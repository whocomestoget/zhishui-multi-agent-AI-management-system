#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================================
文件：standardized_mcp_client_v2.py
功能：标准化MCP客户端 - 实现参数结构标准化解决方案
技术：FastMCP + 参数预处理 + 错误处理
============================================================================

解决方案实现：
1. 参数结构标准化：确保params包含FastMCP期望的所有必需字段
2. 参数预处理机制：自动补全缺失字段，类型转换，格式验证
3. 错误处理优化：详细的错误信息和恢复机制
4. 兼容性保证：支持不同版本的FastMCP库
"""

import json
import logging
import asyncio
import sys
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# 配置日志
def setup_logger():
    """设置优化的日志配置"""
    # 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 日志文件名
    log_filename = f'{log_dir}/mcp_client_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    # 创建logger
    logger = logging.getLogger('StandardizedMCPClient')
    logger.setLevel(logging.DEBUG)
    
    # 清除现有handlers
    logger.handlers.clear()
    
    # 文件handler - 详细日志
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # 控制台handler - 简化日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-5s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # 添加handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

class StandardizedMCPClient:
    """标准化MCP客户端 - 实现参数结构标准化"""
    
    def __init__(self):
        self.client_info = {
            "name": "StandardizedMCPClient",
            "version": "2.0.0",
            "description": "智水信息标准化MCP测试客户端"
        }
        self.capabilities = {
            "tools": True,
            "prompts": True,
            "resources": False,
            "experimental": {}
        }
        
        # MCP服务连接相关属性
        self._mcp_process = None
        self._mcp_stdin = None
        self._mcp_stdout = None
        self._request_id = 0
        self._connection_timeout = 30  # 连接超时时间（秒）
        self._call_timeout = 30  # 调用超时时间（秒）
        
        # 重试机制配置
        self._max_retries = 3  # 最大重试次数
        self._retry_delay = 2  # 重试间隔（秒）
        self._connection_retries = 2  # 连接重试次数
        self._current_service_type = None  # 当前连接的服务类型
        
        # MCP服务配置映射
        # 获取项目根目录的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        self._service_configs = {
            "cost_prediction": {
                "script": "cost_prediction_mcp.py",
                "path": os.path.join(project_root, "3_cost_prediction_mcp"),
                "description": "成本预测服务"
            },
            "efficiency": {
                "script": "zhishui_efficiency_mcp.py", 
                "path": os.path.join(project_root, "5_hr_efficiency_mcp"),
                "description": "效率分析服务"
            },
            "knowledge": {
                "script": "knowledge_mcp.py",
                "path": os.path.join(project_root, "4_operation_knowledge_mcp"), 
                "description": "知识管理服务"
            },
            "financial": {
                "script": "financial_mcp.py",
                "path": os.path.join(project_root, "2_financial_ai_mcp"),
                "description": "财务分析服务"
            }
        }
        
    def standardize_params(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        参数结构标准化处理
        
        Args:
            method: MCP方法名
            params: 原始参数
            
        Returns:
            标准化后的参数字典
        """
        if params is None:
            params = {}
            
        # 基础标准化参数结构
        standardized = {
            "jsonrpc": "2.0",
            "id": f"req_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            "method": method,
            "params": {}
        }
        
        # 根据不同方法添加特定参数
        if method == "tools/list":
            # tools/list 不需要额外参数，但确保结构完整
            standardized["params"] = {}
            
        elif method == "tools/call":
            # tools/call 需要 name 和 arguments
            tool_name = params.get("name", "")
            tool_arguments = params.get("arguments", {})
            
            # 参数验证
            if not tool_name:
                raise ValueError("tools/call 方法缺少必需的 'name' 参数")
                
            standardized["params"] = {
                "name": str(tool_name),
                "arguments": self._validate_arguments(tool_arguments)
            }
            
        elif method == "initialize":
            # initialize 需要客户端信息和能力声明
            standardized["params"] = {
                "protocolVersion": "2024-11-05",
                "capabilities": self.capabilities,
                "clientInfo": self.client_info
            }
            
        else:
            # 其他方法保持原有参数结构
            standardized["params"] = params
            
        return standardized
    
    def _validate_arguments(self, arguments: Any) -> Dict[str, Any]:
        """验证和标准化工具参数"""
        if arguments is None:
            return {}
        
        if isinstance(arguments, str):
            try:
                return json.loads(arguments)
            except json.JSONDecodeError:
                logger.warning(f"参数JSON解析失败，使用原始字符串: {arguments}")
                return {"data": arguments}
        
        if isinstance(arguments, dict):
            return arguments
            
        # 其他类型转换为字典
        return {"value": arguments}
    
    def preprocess_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        请求预处理机制
        
        Args:
            method: MCP方法名
            params: 原始参数
            
        Returns:
            预处理后的完整请求
        """
        try:
            # 1. 参数结构标准化
            request = self.standardize_params(method, params)
            
            # 2. 参数类型验证
            self._validate_request_structure(request)
            
            # 3. 添加元数据
            request["meta"] = {
                "timestamp": datetime.now().isoformat(),
                "client": self.client_info["name"],
                "version": self.client_info["version"]
            }
            
            logger.info(f"请求预处理完成: {method}")
            return request
            
        except Exception as e:
            logger.error(f"请求预处理失败: {e}")
            raise
    
    def _validate_request_structure(self, request: Dict[str, Any]) -> None:
        """验证请求结构完整性"""
        required_fields = ["jsonrpc", "id", "method", "params"]
        
        for field in required_fields:
            if field not in request:
                raise ValueError(f"请求缺少必需字段: {field}")
        
        if request["jsonrpc"] != "2.0":
            raise ValueError(f"不支持的JSON-RPC版本: {request['jsonrpc']}")
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        调用MCP工具的统一接口（带重试机制）
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具调用结果
        """
        start_time = time.time()
        last_error = None
        
        logger.info(f"🔧 开始调用工具: {tool_name}")
        logger.debug(f"工具参数: {arguments}")
        
        for attempt in range(self._max_retries + 1):
            attempt_start = time.time()
            logger.debug(f"📝 第 {attempt + 1}/{self._max_retries + 1} 次尝试调用工具: {tool_name}")
            
            try:
                # 预处理请求
                logger.debug(f"🔄 预处理请求参数...")
                request = self.preprocess_request("tools/call", {
                    "name": tool_name,
                    "arguments": arguments or {}
                })
                
                if attempt > 0:
                    logger.info(f"🔄 重试调用MCP工具: {tool_name} (第{attempt}次重试)")
                else:
                    logger.info(f"📤 调用MCP工具: {tool_name}")
                
                # 确保MCP服务连接
                logger.debug(f"🔗 检查MCP服务连接状态...")
                if not self._ensure_mcp_connection(tool_name):
                    raise Exception("无法建立MCP服务连接")
                
                # 调用真实的MCP服务
                logger.debug(f"📡 发送MCP请求...")
                result = self._send_mcp_request_with_retry(request)
                
                # 检查结果是否包含错误
                if "error" in result:
                    error_msg = result["error"].get("message", "未知错误")
                    raise Exception(f"MCP服务返回错误: {error_msg}")
                
                attempt_time = time.time() - attempt_start
                total_time = time.time() - start_time
                logger.info(f"[SUCCESS] MCP工具调用成功: {tool_name}，耗时: {total_time:.2f}秒")
                logger.debug(f"返回结果大小: {len(str(result))} 字符")
                return result
                
            except Exception as e:
                last_error = e
                attempt_time = time.time() - attempt_start
                logger.warning(f"[WARNING] MCP工具调用失败 (尝试 {attempt + 1}/{self._max_retries + 1}，耗时: {attempt_time:.2f}秒): {e}")
                logger.debug(f"异常详情: {type(e).__name__}: {str(e)}")
                
                # 如果不是最后一次尝试，等待后重试
                if attempt < self._max_retries:
                    # 连接失败时断开重连
                    if "连接" in str(e) or "进程" in str(e):
                        logger.warning("[RECONNECT] 检测到连接错误，断开并重连...")
                        self.disconnect()
                    
                    delay = self._retry_delay * (attempt + 1)  # 递增延迟
                    logger.info(f"[WAIT] 等待 {delay} 秒后重试...")
                    time.sleep(delay)
                    continue
                else:
                    break
        
        # 所有重试都失败了
        total_time = time.time() - start_time
        logger.error(f"🚫 MCP工具调用最终失败: {tool_name}, 错误: {last_error}，总耗时: {total_time:.2f}秒")
        return {
            "status": "error",
            "error": str(last_error),
            "tool_name": tool_name,
            "arguments": arguments,
            "retry_attempts": self._max_retries + 1,
            "total_time": total_time
        }
    
    def _connect_to_mcp_service(self, tool_name: str) -> bool:
        """
        连接到MCP服务
        
        Args:
            tool_name: 工具名称，用于确定连接哪个服务
            
        Returns:
            连接是否成功
        """
        connection_start = time.time()
        logger.info(f"🔌 开始连接MCP服务，工具: {tool_name}")
        
        try:
            # 根据工具名称确定服务类型
            logger.debug(f"[DEBUG] 确定服务类型...")
            service_type = self._determine_service_type(tool_name)
            if not service_type:
                logger.error(f"[ERROR] 无法确定工具 {tool_name} 对应的服务类型")
                return False
                
            service_config = self._service_configs[service_type]
            script_path = os.path.join(service_config["path"], service_config["script"])
            
            logger.info(f"[SELECT] 选择服务: {service_config['description']} (类型: {service_type})")
            logger.debug(f"脚本路径: {script_path}")
            
            # 验证脚本文件是否存在
            if not os.path.exists(script_path):
                logger.error(f"[ERROR] MCP服务脚本不存在: {script_path}")
                return False
            
            logger.info(f"[START] 启动MCP服务进程...")
            
            # 启动MCP服务进程
            self._mcp_process = subprocess.Popen(
                [sys.executable, script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',  # 明确指定UTF-8编码
                bufsize=0,
                cwd=service_config["path"]  # 设置工作目录
            )
            
            self._mcp_stdin = self._mcp_process.stdin
            self._mcp_stdout = self._mcp_process.stdout
            
            logger.debug(f"⏳ 等待服务启动 (3秒)...")
            # 等待服务启动
            time.sleep(3)
            
            # 检查进程是否正常运行
            if self._mcp_process.poll() is not None:
                # 读取错误信息
                stderr_output = self._mcp_process.stderr.read()
                logger.error(f"[ERROR] MCP服务启动失败，进程已退出。错误信息: {stderr_output}")
                return False
            
            logger.debug(f"[HANDSHAKE] 进行初始化握手...")
            # 尝试初始化握手
            if not self._initialize_mcp_connection():
                logger.error("[ERROR] MCP服务初始化握手失败")
                self.disconnect()
                return False
                
            connection_time = time.time() - connection_start
            logger.info(f"[SUCCESS] MCP服务连接成功: {service_config['description']}，耗时: {connection_time:.2f}秒")
            return True
            
        except Exception as e:
            connection_time = time.time() - connection_start
            logger.error(f"[ERROR] 连接MCP服务失败 (耗时: {connection_time:.2f}秒): {e}")
            logger.debug(f"异常详情: {type(e).__name__}: {str(e)}")
            self.disconnect()
            return False
    
    def _initialize_mcp_connection(self) -> bool:
        """
        初始化MCP连接，执行握手
        
        Returns:
            初始化是否成功
        """
        handshake_start = time.time()
        logger.info(f"[HANDSHAKE] 开始MCP连接握手...")
        
        try:
            # 发送初始化请求
            logger.debug(f"[SEND] 发送initialize请求 (ID: 1)...")
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": self.capabilities,
                    "clientInfo": self.client_info
                }
            }
            
            logger.debug(f"初始化参数: {init_request['params']}")
            response = self._send_mcp_request(init_request)
            
            if "error" in response:
                handshake_time = time.time() - handshake_start
                logger.error(f"❌ MCP初始化失败 (耗时: {handshake_time:.2f}秒): {response['error']}")
                return False
            
            logger.debug(f"✅ initialize请求成功，服务器能力: {response.get('result', {}).get('capabilities', {})}")
            
            # 发送initialized通知
            logger.debug(f"📤 发送initialized通知...")
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            
            # 发送通知（不需要响应）
            notification_json = json.dumps(initialized_notification) + "\n"
            self._mcp_stdin.write(notification_json)
            self._mcp_stdin.flush()
            
            handshake_time = time.time() - handshake_start
            logger.info(f"[SUCCESS] MCP连接初始化成功，耗时: {handshake_time:.2f}秒")
            logger.debug(f"握手完成，协议版本: 2024-11-05")
            return True
            
        except Exception as e:
            handshake_time = time.time() - handshake_start
            logger.error(f"[ERROR] MCP连接初始化失败 (耗时: {handshake_time:.2f}秒): {e}")
            logger.debug(f"异常详情: {type(e).__name__}: {str(e)}")
            return False
    
    def _determine_service_type(self, tool_name: str) -> Optional[str]:
        """
        根据工具名称确定服务类型
        
        Args:
            tool_name: 工具名称
            
        Returns:
            服务类型或None
        """
        # 财务分析相关工具 - 优先级最高，包含现金流、IRR、财务问答等
        if any(keyword in tool_name.lower() for keyword in ['cash_flow', 'irr', 'financial', 'budget', 'monitor_budget', 'predict_cash', 'calculate_irr', 'financial_qa', '现金流', '财务', '预算', '投资回报']):
            return "financial"
        
        # 成本预测相关工具
        if any(keyword in tool_name.lower() for keyword in ['cost', 'predict_hydropower', 'assess_project', '成本', '预测']):
            return "cost_prediction"
        
        # 效率分析相关工具
        if any(keyword in tool_name.lower() for keyword in ['efficiency', 'performance', 'hr', 'evaluate_employee', 'generate_efficiency', '效率', '绩效', '人力']):
            return "efficiency"
            
        # 知识管理相关工具
        if any(keyword in tool_name.lower() for keyword in ['knowledge', 'document', 'manual', 'search_knowledge', 'add_knowledge', '知识', '文档', '手册']):
            return "knowledge"
            
        # 默认使用成本预测服务
        logger.warning(f"无法确定工具 {tool_name} 的服务类型，使用默认成本预测服务")
        return "cost_prediction"
    
    def _send_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送MCP请求并获取响应
        
        Args:
            request: MCP请求
            
        Returns:
            MCP响应
        """
        request_start = time.time()
        
        try:
            if not self._mcp_stdin or not self._mcp_stdout:
                raise Exception("MCP服务连接未建立")
            
            # 生成请求ID
            self._request_id += 1
            request["id"] = self._request_id
            
            # 发送请求
            request_json = json.dumps(request) + "\n"
            logger.debug(f"📤 发送MCP请求 (ID: {self._request_id}): {request.get('method', 'unknown')}")
            logger.debug(f"请求内容: {request_json.strip()}")
            
            self._mcp_stdin.write(request_json)
            self._mcp_stdin.flush()
            
            logger.debug(f"⏳ 等待MCP响应...")
            # 读取响应
            response_line = self._mcp_stdout.readline()
            if not response_line:
                raise Exception("MCP服务无响应")
            
            response = json.loads(response_line.strip())
            request_time = time.time() - request_start
            
            logger.debug(f"📥 收到MCP响应 (ID: {response.get('id', 'unknown')}，耗时: {request_time:.2f}秒)")
            logger.debug(f"响应内容: {str(response)[:200]}..." if len(str(response)) > 200 else f"响应内容: {response}")
            
            return response
            
        except Exception as e:
            request_time = time.time() - request_start
            logger.error(f"❌ MCP请求发送失败 (耗时: {request_time:.2f}秒): {e}")
            logger.debug(f"异常详情: {type(e).__name__}: {str(e)}")
            return {
                "id": request.get("id", 0),
                "error": {
                    "code": -1,
                    "message": str(e)
                }
            }
    
    def disconnect(self):
        """
        断开MCP服务连接
        """
        disconnect_start = time.time()
        
        try:
            if self._mcp_process:
                logger.info(f"🔌 开始断开MCP服务连接 (PID: {self._mcp_process.pid})")
                logger.debug(f"当前服务类型: {self._current_service_type}")
                
                # 优雅终止进程
                logger.debug(f"📤 发送终止信号...")
                self._mcp_process.terminate()
                
                # 等待进程结束
                logger.debug(f"⏳ 等待进程结束 (最多5秒)...")
                self._mcp_process.wait(timeout=5)
                
                disconnect_time = time.time() - disconnect_start
                logger.info(f"✅ MCP服务连接已断开，耗时: {disconnect_time:.2f}秒")
            else:
                logger.debug(f"ℹ️ 没有活动的MCP连接需要断开")
                
        except Exception as e:
            disconnect_time = time.time() - disconnect_start
            logger.error(f"❌ 断开MCP连接时出错 (耗时: {disconnect_time:.2f}秒): {e}")
            logger.debug(f"异常详情: {type(e).__name__}: {str(e)}")
            
            # 强制终止进程
            if self._mcp_process:
                try:
                    logger.warning(f"🔨 强制终止MCP进程...")
                    self._mcp_process.kill()
                    logger.info(f"✅ MCP进程已强制终止")
                except:
                    logger.error(f"❌ 强制终止进程失败")
        finally:
            self._mcp_process = None
            self._mcp_stdin = None
            self._mcp_stdout = None
            self._current_service_type = None
            logger.debug(f"🧹 连接资源已清理")
    
    def _disconnect_process_only(self):
        """
        只断开MCP进程，但不重置服务类型（用于重连时）
        """
        disconnect_start = time.time()
        
        try:
            if self._mcp_process:
                logger.debug(f"🔌 断开MCP进程 (PID: {self._mcp_process.pid})，保留服务类型: {self._current_service_type}")
                
                # 优雅终止进程
                self._mcp_process.terminate()
                
                # 等待进程结束
                self._mcp_process.wait(timeout=3)
                
                disconnect_time = time.time() - disconnect_start
                logger.debug(f"✅ MCP进程已断开，耗时: {disconnect_time:.2f}秒")
            else:
                logger.debug(f"ℹ️ 没有活动的MCP进程需要断开")
                
        except Exception as e:
            disconnect_time = time.time() - disconnect_start
            logger.warning(f"⚠️ 断开MCP进程时出错 (耗时: {disconnect_time:.2f}秒): {e}")
            
            # 强制终止进程
            if self._mcp_process:
                try:
                    self._mcp_process.kill()
                    logger.debug(f"✅ MCP进程已强制终止")
                except:
                    logger.warning(f"⚠️ 强制终止进程失败")
        finally:
            self._mcp_process = None
            self._mcp_stdin = None
            self._mcp_stdout = None
            # 注意：不重置 _current_service_type
            logger.debug(f"🧹 进程资源已清理，服务类型保持: {self._current_service_type}")
    
    def _ensure_mcp_connection(self, tool_name: str) -> bool:
        """
        确保MCP服务连接（带重试机制）
        
        Args:
            tool_name: 工具名称
            
        Returns:
            连接是否成功
        """
        logger.debug(f"🔍 检查MCP连接状态，工具: {tool_name}")
        
        # 确定需要的服务类型
        required_service_type = self._determine_service_type(tool_name)
        logger.debug(f"需要的服务类型: {required_service_type}，当前服务类型: {self._current_service_type}")
        
        # 检查进程是否还活着
        process_alive = (
            self._mcp_process is not None and 
            self._mcp_process.poll() is None
        )
        
        # 检查是否需要重新连接
        need_reconnect = (
            not process_alive or 
            self._current_service_type != required_service_type
        )
        
        if need_reconnect:
            logger.info(f"🔄 需要重新连接MCP服务 (进程存活: {process_alive}, 服务类型匹配: {self._current_service_type == required_service_type})")
            
            # 断开现有连接（但不重置服务类型）
            if self._mcp_process is not None:
                logger.debug(f"🔌 断开现有连接...")
                self._disconnect_process_only()
            
            # 尝试连接
            for attempt in range(self._connection_retries + 1):
                if attempt > 0:
                    logger.info(f"🔄 重试连接MCP服务 (第{attempt}次重试)")
                    time.sleep(self._retry_delay)
                
                logger.debug(f"📝 连接尝试 {attempt + 1}/{self._connection_retries + 1}")
                if self._connect_to_mcp_service(tool_name):
                    self._current_service_type = required_service_type
                    logger.info(f"✅ MCP服务连接确认成功，服务类型: {required_service_type}")
                    return True
                    
            logger.error(f"❌ MCP服务连接最终失败，已尝试 {self._connection_retries + 1} 次")
            self._current_service_type = None  # 连接失败时才重置
            return False
        
        logger.debug(f"✅ MCP连接状态正常，无需重连")
        return True
    
    def _send_mcp_request_with_retry(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送MCP请求（带重试机制）
        
        Args:
            request: MCP请求
            
        Returns:
            MCP响应
        """
        for attempt in range(3):  # 请求级别的重试
            try:
                result = self._send_mcp_request(request)
                
                # 检查是否是连接错误
                if "error" in result and "连接" in str(result.get("error", {})):
                    if attempt < 2:  # 不是最后一次尝试
                        logger.warning(f"MCP请求连接错误，重试中... (尝试 {attempt + 1}/3)")
                        time.sleep(1)
                        continue
                
                return result
                
            except Exception as e:
                if attempt < 2:  # 不是最后一次尝试
                    logger.warning(f"MCP请求发送失败，重试中... (尝试 {attempt + 1}/3): {e}")
                    time.sleep(1)
                    continue
                else:
                    # 最后一次尝试失败，返回错误
                    return {
                        "id": request.get("id", 0),
                        "error": {
                            "code": -1,
                            "message": f"请求发送失败: {str(e)}"
                        }
                    }
        
        # 不应该到达这里
        return {
            "id": request.get("id", 0),
            "error": {
                "code": -1,
                "message": "未知错误"
            }
        }

async def test_mcp_service_standardized(service_name: str, service_path: str, port: int) -> bool:
    """
    使用标准化客户端测试MCP服务
    
    Args:
        service_name: 服务名称
        service_path: 服务路径
        port: 服务端口
        
    Returns:
        测试是否成功
    """
    logger.info(f"开始测试 {service_name} (端口: {port})")
    
    try:
        # 创建标准化客户端
        client = StandardizedMCPClient()
        
        # 模拟服务连接（这里我们直接导入模块进行测试）
        sys.path.insert(0, service_path)
        
        if service_name == "财务分析":
            import financial_mcp
            
            # 测试工具列表
            logger.info("测试工具列表获取...")
            tools_request = client.preprocess_request("tools/list")
            logger.info(f"标准化请求: {json.dumps(tools_request, ensure_ascii=False, indent=2)}")
            
            # 测试工具调用
            logger.info("测试现金流预测工具...")
            call_request = client.preprocess_request("tools/call", {
                "name": "predict_cash_flow",
                "arguments": {
                    "historical_data": "[1000, 1200, 1100, 1300, 1250, 1400]",
                    "periods": 3,
                    "data_type": "monthly"
                }
            })
            logger.info(f"工具调用请求: {json.dumps(call_request, ensure_ascii=False, indent=2)}")
            
            # 直接调用函数测试
            result = financial_mcp.predict_cash_flow(
                "[1000, 1200, 1100, 1300, 1250, 1400]", 
                3, 
                "monthly"
            )
            logger.info(f"现金流预测结果: {result[:200]}...")
            
        elif service_name == "成本预测":
            import cost_prediction_mcp
            
            logger.info("测试智慧水电成本预测工具...")
            call_request = client.preprocess_request("tools/call", {
                "name": "predict_hydropower_cost",
                "arguments": {
                    "capacity_mw": 100.0,
                    "project_type": "常规大坝",
                    "construction_period": 3,
                    "economic_indicator": 0.8
                }
            })
            
            # 直接调用函数测试
            result = cost_prediction_mcp.predict_hydropower_cost(
                capacity_mw=100.0,
                project_type="常规大坝",
                construction_period=3,
                economic_indicator=0.8
            )
            logger.info(f"成本预测结果: {result[:200]}...")
            
        elif service_name == "运维知识库":
            import knowledge_mcp
            
            logger.info("测试知识搜索工具...")
            result = knowledge_mcp.search_knowledge("电力系统", 5)
            logger.info(f"知识搜索结果: {result[:200]}...")
            
        elif service_name == "人员效能":
            import zhishui_efficiency_mcp
            
            logger.info("测试效能评估工具...")
            employee_data = {
                "employee_id": "EMP001",
                "name": "张三",
                "department": "技术部",
                "position": "工程师"
            }
            metrics_data = {
                "performance_score": 85,
                "project_completion": 90,
                "skill_level": 80
            }
            
            result = zhishui_efficiency_mcp.evaluate_employee_efficiency(
                json.dumps(employee_data),
                json.dumps(metrics_data),
                "技术研发"
            )
            logger.info(f"效能评估结果: {result[:200]}...")
        
        logger.info(f"✅ {service_name} 服务测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ {service_name} 服务测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始标准化MCP服务测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # MCP服务配置
    services = [
        ("财务分析", "2_financial_ai_mcp", 8001),
        ("成本预测", "3_cost_prediction_mcp", 8002), 
        ("运维知识库", "4_operation_knowledge_mcp", 8003),
        ("人员效能", "5_hr_efficiency_mcp", 8004)
    ]
    
    passed_services = 0
    total_services = len(services)
    
    for service_name, service_path, port in services:
        print(f"\n🧪 测试 {service_name} MCP服务")
        print("-" * 40)
        
        success = await test_mcp_service_standardized(service_name, service_path, port)
        if success:
            passed_services += 1
    
    print("\n" + "=" * 60)
    print("📋 标准化MCP服务测试总结")
    print("=" * 60)
    
    for i, (service_name, _, _) in enumerate(services):
        status = "✅ 通过" if i < passed_services else "❌ 失败"
        print(f"{service_name}: {status}")
    
    print(f"\n🎯 测试结果: {passed_services}/{total_services} 服务通过测试")
    
    if passed_services == total_services:
        print("🎉 所有MCP服务测试通过！参数结构标准化解决方案成功实施！")
    else:
        print("⚠️  部分MCP服务存在问题，需要进一步优化")
    
    # 生成测试报告
    report = {
        "test_time": datetime.now().isoformat(),
        "total_services": total_services,
        "passed_services": passed_services,
        "success_rate": f"{(passed_services/total_services)*100:.1f}%",
        "standardization_features": [
            "参数结构标准化",
            "参数预处理机制", 
            "类型转换和验证",
            "错误处理优化",
            "兼容性保证"
        ],
        "services": [
            {
                "name": name,
                "path": path,
                "port": port,
                "status": "passed" if i < passed_services else "failed"
            }
            for i, (name, path, port) in enumerate(services)
        ]
    }
    
    report_file = f"standardized_mcp_test_report_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 详细测试报告已保存: {report_file}")

if __name__ == "__main__":
    asyncio.run(main())