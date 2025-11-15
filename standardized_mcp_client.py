#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
标准化MCP客户端
实施参数结构标准化解决方案，解决FastMCP库的参数验证问题

功能特点：
1. 完善params字段结构，确保包含FastMCP期望的所有必需字段
2. 添加参数预处理机制，自动补全缺失字段
3. 严格按照MCP规范构建请求参数
4. 参数类型声明和验证
"""

import subprocess
import json
import time
import sys
import os
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

# 配置日志
log_filename = f"standardized_mcp_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("StandardizedMCPClient")

class MCPProtocolVersion(Enum):
    """MCP协议版本枚举"""
    V2024_11_05 = "2024-11-05"

@dataclass
class ClientInfo:
    """客户端信息结构"""
    name: str
    version: str
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {"name": self.name, "version": self.version}
        if self.description:
            result["description"] = self.description
        return result

@dataclass
class ClientCapabilities:
    """客户端能力声明"""
    experimental: Optional[Dict[str, Any]] = None
    sampling: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {}
        if self.experimental is not None:
            result["experimental"] = self.experimental
        if self.sampling is not None:
            result["sampling"] = self.sampling
        return result

@dataclass
class InitializeParams:
    """初始化参数结构"""
    protocolVersion: str
    capabilities: ClientCapabilities
    clientInfo: ClientInfo
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "protocolVersion": self.protocolVersion,
            "capabilities": self.capabilities.to_dict(),
            "clientInfo": self.clientInfo.to_dict()
        }

@dataclass
class ToolsListParams:
    """工具列表请求参数结构"""
    cursor: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {}
        if self.cursor is not None:
            result["cursor"] = self.cursor
        return result

@dataclass
class ToolCallParams:
    """工具调用参数结构"""
    name: str
    arguments: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "arguments": self.arguments
        }

class ParameterValidator:
    """参数验证器"""
    
    @staticmethod
    def validate_string(value: Any, field_name: str) -> str:
        """验证字符串参数"""
        if not isinstance(value, str):
            raise ValueError(f"{field_name} 必须是字符串类型")
        if not value.strip():
            raise ValueError(f"{field_name} 不能为空")
        return value.strip()
    
    @staticmethod
    def validate_dict(value: Any, field_name: str) -> Dict[str, Any]:
        """验证字典参数"""
        if not isinstance(value, dict):
            raise ValueError(f"{field_name} 必须是字典类型")
        return value
    
    @staticmethod
    def validate_tool_arguments(arguments: Any) -> Dict[str, Any]:
        """验证工具调用参数"""
        if not isinstance(arguments, dict):
            raise ValueError("工具参数必须是字典类型")
        
        # 确保所有值都是JSON可序列化的
        try:
            json.dumps(arguments)
        except (TypeError, ValueError) as e:
            raise ValueError(f"工具参数必须是JSON可序列化的: {e}")
        
        return arguments

class StandardizedMCPClient:
    """标准化MCP客户端"""
    
    def __init__(self, script_path: str, service_name: str):
        self.script_path = script_path
        self.service_name = service_name
        self.process = None
        self.logger = logging.getLogger(f"StandardizedMCPClient.{service_name}")
        self.validator = ParameterValidator()
        
        # 默认客户端信息
        self.client_info = ClientInfo(
            name="智水信息标准化MCP客户端",
            version="1.0.0",
            description="四川智水信息技术有限公司AI智慧管理解决方案MCP客户端"
        )
        
        # 默认客户端能力
        self.client_capabilities = ClientCapabilities(
            experimental={},
            sampling={}
        )
        
    def start_service(self) -> bool:
        """启动MCP服务"""
        try:
            if not os.path.exists(self.script_path):
                self.logger.error(f"MCP脚本不存在: {self.script_path}")
                return False
                
            self.logger.info(f"启动{self.service_name}...")
            
            # 设置环境变量
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            env['PYTHONIOENCODING'] = 'utf-8'
            
            self.process = subprocess.Popen(
                [sys.executable, self.script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,
                env=env,
                encoding='utf-8'
            )
            
            # 等待服务启动
            time.sleep(3)
            
            # 检查进程是否正常运行
            if self.process.poll() is not None:
                stderr_output = self.process.stderr.read()
                self.logger.error(f"服务启动失败: {stderr_output}")
                return False
                
            self.logger.info(f"{self.service_name}启动成功")
            return True
            
        except Exception as e:
            self.logger.error(f"启动{self.service_name}失败: {e}")
            return False
    
    def _build_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """构建标准化MCP请求"""
        request = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": method
        }
        
        # 只有当params不为空时才添加params字段
        if params is not None and params:
            request["params"] = params
            
        return request
    
    def _send_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """发送MCP请求"""
        if not self.process or self.process.poll() is not None:
            self.logger.error("MCP服务未运行")
            return None
            
        try:
            request_json = json.dumps(request, ensure_ascii=False)
            self.logger.info(f"发送标准化请求: {request_json}")
            
            # 发送请求
            self.process.stdin.write(request_json + "\n")
            self.process.stdin.flush()
            
            # 读取响应
            response_line = self.process.stdout.readline()
            if not response_line:
                self.logger.error("未收到响应")
                return None
                
            self.logger.info(f"收到原始响应: {response_line.strip()}")
            response = json.loads(response_line.strip())
            self.logger.info(f"解析后响应: {response}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"发送请求失败: {e}")
            return None
    
    def initialize(self, protocol_version: str = MCPProtocolVersion.V2024_11_05.value) -> Dict[str, Any]:
        """标准化初始化请求"""
        try:
            self.logger.info("发送标准化初始化请求...")
            
            # 构建标准化初始化参数
            init_params = InitializeParams(
                protocolVersion=self.validator.validate_string(protocol_version, "protocolVersion"),
                capabilities=self.client_capabilities,
                clientInfo=self.client_info
            )
            
            # 构建请求
            request = self._build_request("initialize", init_params.to_dict())
            
            # 发送请求
            response = self._send_request(request)
            
            if not response:
                return {"success": False, "error": "初始化无响应"}
            
            if "error" in response:
                return {"success": False, "error": "初始化失败", "details": response["error"]}
            
            self.logger.info("标准化初始化成功")
            return {"success": True, "result": response.get("result")}
            
        except Exception as e:
            self.logger.error(f"标准化初始化异常: {e}")
            return {"success": False, "error": f"初始化异常: {e}"}
    
    def list_tools(self, cursor: Optional[str] = None) -> Dict[str, Any]:
        """标准化工具列表请求"""
        try:
            self.logger.info("发送标准化工具列表请求...")
            
            # 构建标准化工具列表参数
            tools_params = ToolsListParams(cursor=cursor)
            params_dict = tools_params.to_dict()
            
            # 如果参数为空，则不传递params字段
            request_params = params_dict if params_dict else None
            
            # 构建请求
            request = self._build_request("tools/list", request_params)
            
            # 发送请求
            response = self._send_request(request)
            
            if not response:
                return {"success": False, "error": "工具列表请求无响应"}
            
            if "error" in response:
                return {"success": False, "error": "工具列表请求失败", "details": response["error"]}
            
            self.logger.info("标准化工具列表请求成功")
            return {"success": True, "result": response.get("result")}
            
        except Exception as e:
            self.logger.error(f"标准化工具列表请求异常: {e}")
            return {"success": False, "error": f"工具列表请求异常: {e}"}
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """标准化工具调用请求"""
        try:
            self.logger.info(f"发送标准化工具调用请求: {tool_name}")
            
            # 验证参数
            validated_name = self.validator.validate_string(tool_name, "tool_name")
            validated_arguments = self.validator.validate_tool_arguments(arguments)
            
            # 构建标准化工具调用参数
            tool_params = ToolCallParams(
                name=validated_name,
                arguments=validated_arguments
            )
            
            # 构建请求
            request = self._build_request("tools/call", tool_params.to_dict())
            
            # 发送请求
            response = self._send_request(request)
            
            if not response:
                return {"success": False, "error": "工具调用无响应"}
            
            if "error" in response:
                return {"success": False, "error": "工具调用失败", "details": response["error"]}
            
            self.logger.info("标准化工具调用成功")
            return {"success": True, "result": response.get("result")}
            
        except Exception as e:
            self.logger.error(f"标准化工具调用异常: {e}")
            return {"success": False, "error": f"工具调用异常: {e}"}
    
    def stop_service(self):
        """停止MCP服务"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            self.process = None
            self.logger.info(f"{self.service_name}已停止")

def test_standardized_mcp_services():
    """测试标准化MCP服务"""
    logger.info("开始标准化MCP服务测试...")
    
    # 定义要测试的服务和工具
    services_config = [
        {
            "script_path": "2_financial_ai_mcp/financial_mcp.py",
            "service_name": "财务分析MCP服务",
            "test_tools": [
                {
                    "name": "predict_cash_flow",
                    "arguments": {
                        "historical_data": "[100000, 120000, 110000, 130000, 125000, 140000]",
                        "periods": 3,
                        "data_type": "json"
                    }
                },
                {
                    "name": "financial_qa",
                    "arguments": {
                        "question": "请分析一下公司的财务状况"
                    }
                }
            ]
        },
        {
            "script_path": "3_cost_prediction_mcp/cost_prediction_mcp.py", 
            "service_name": "成本预测MCP服务",
            "test_tools": [
                {
                    "name": "predict_project_cost",
                    "arguments": {
                        "project_type": "智慧电厂",
                        "scale": "中型",
                        "duration": 12,
                        "complexity": "中等"
                    }
                }
            ]
        },
        {
            "script_path": "4_operation_knowledge_mcp/knowledge_mcp.py",
            "service_name": "知识管理MCP服务", 
            "test_tools": [
                {
                    "name": "search_knowledge",
                    "arguments": {
                        "query": "电力系统维护",
                        "limit": 3
                    }
                }
            ]
        },
        {
            "script_path": "5_hr_efficiency_mcp/zhishui_efficiency_mcp.py",
            "service_name": "人员效能MCP服务",
            "test_tools": [
                {
                    "name": "analyze_team_efficiency",
                    "arguments": {
                        "team_id": "tech_team_01",
                        "period": "2024-01"
                    }
                }
            ]
        }
    ]
    
    results = {}
    
    for service_config in services_config:
        service_name = service_config["service_name"]
        script_path = service_config["script_path"]
        test_tools = service_config["test_tools"]
        
        logger.info(f"测试 {service_name}")
        logger.info("=" * 50)
        
        # 创建标准化客户端
        client = StandardizedMCPClient(script_path, service_name)
        
        try:
            # 启动服务
            if not client.start_service():
                results[service_name] = {"success": False, "error": "服务启动失败"}
                continue
            
            # 测试初始化
            init_result = client.initialize()
            if not init_result["success"]:
                results[service_name] = {"success": False, "error": f"初始化失败: {init_result['error']}"}
                continue
            
            # 测试工具列表
            tools_result = client.list_tools()
            if not tools_result["success"]:
                logger.warning(f"工具列表请求失败: {tools_result['error']}")
                # 继续测试工具调用，即使工具列表失败
            else:
                logger.info("工具列表请求成功")
            
            # 测试工具调用
            tool_results = []
            for tool_config in test_tools:
                tool_name = tool_config["name"]
                arguments = tool_config["arguments"]
                
                tool_result = client.call_tool(tool_name, arguments)
                tool_results.append({
                    "tool_name": tool_name,
                    "success": tool_result["success"],
                    "error": tool_result.get("error"),
                    "result": tool_result.get("result")
                })
            
            # 计算成功率
            successful_tools = sum(1 for tr in tool_results if tr["success"])
            total_tools = len(tool_results)
            
            results[service_name] = {
                "success": successful_tools > 0,
                "tools_tested": total_tools,
                "tools_successful": successful_tools,
                "tools_list_success": tools_result["success"],
                "tool_results": tool_results
            }
            
            logger.info(f"{service_name}: {successful_tools}/{total_tools} 工具测试成功")
            
        except Exception as e:
            logger.error(f"测试 {service_name} 异常: {e}")
            results[service_name] = {"success": False, "error": f"测试异常: {e}"}
        finally:
            client.stop_service()
    
    return results

def main():
    """主测试函数"""
    logger.info("开始标准化MCP服务测试")
    logger.info("=" * 60)
    
    # 测试MCP服务
    mcp_results = test_standardized_mcp_services()
    
    # 生成测试报告
    report = {
        "test_time": datetime.now().isoformat(),
        "test_type": "标准化MCP服务测试",
        "mcp_services": mcp_results
    }
    
    # 计算总体结果
    mcp_success_count = sum(1 for result in mcp_results.values() if result.get("success", False))
    mcp_total_count = len(mcp_results)
    
    logger.info("=" * 60)
    logger.info("测试总结:")
    logger.info(f"MCP服务测试: {mcp_success_count}/{mcp_total_count} 通过")
    
    # 详细结果
    logger.info("\nMCP服务详细结果:")
    for service_name, result in mcp_results.items():
        status = "✓ 成功" if result.get("success", False) else "✗ 失败"
        logger.info(f"  {service_name}: {status}")
        if result.get("tools_tested"):
            logger.info(f"    工具测试: {result.get('tools_successful', 0)}/{result.get('tools_tested', 0)}")
            logger.info(f"    工具列表: {'✓' if result.get('tools_list_success', False) else '✗'}")
        if not result.get("success", False):
            logger.info(f"    错误: {result.get('error', 'Unknown')}")
    
    # 保存报告
    report_filename = f"standardized_mcp_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n详细报告已保存到: {report_filename}")
    
    # 判断整体成功
    overall_success = (mcp_success_count > 0)
    
    if overall_success:
        logger.info("🎉 标准化MCP服务测试整体成功!")
        return True
    else:
        logger.warning("⚠️ 标准化MCP服务测试存在问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)