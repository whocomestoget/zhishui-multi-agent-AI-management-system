# ============================================================================
# 文件：1_frontend_dashboard/api_client.py
# 功能：API客户端 - 与后端智能体服务通信
# 技术：HTTP客户端 + 异步处理
# ============================================================================

"""
四川智水AI智慧管理平台 - API客户端

功能模块：
1. 项目信息整合服务客户端
2. AI财务分析服务客户端
3. 运维知识库服务客户端
4. 成本核算预测服务客户端
5. 数据决策分析服务客户端
6. Agno智能体协调中心客户端
"""

import requests
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import streamlit as st
from urllib.parse import urljoin
import time
from dataclasses import dataclass
from enum import Enum

from config import get_config
from models import AgentRequest, AgentResponse, AgentType

# ============================================================================
# 配置和常量 - 智能路由重构版本
# ============================================================================

config = get_config("agent_api")

# API服务配置 - 只保留项目服务和Agno协调中心
API_CONFIG = {
    "project_service": {
        "base_url": "http://localhost:8001",
        "timeout": 120,
        "retry_count": 3
    },
    "agno_coordinator": {
        "base_url": "http://localhost:8000",
        "timeout": 300,
        "retry_count": 3
    }
}

# ============================================================================
# 异常类定义
# ============================================================================

class APIException(Exception):
    """API异常基类"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class ServiceUnavailableException(APIException):
    """服务不可用异常"""
    pass

class TimeoutException(APIException):
    """超时异常"""
    pass

class ValidationException(APIException):
    """验证异常"""
    pass

# ============================================================================
# 基础API客户端
# ============================================================================

class BaseAPIClient:
    """基础API客户端"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.config = API_CONFIG.get(service_name, {})
        self.base_url = self.config.get("base_url", "")
        self.timeout = self.config.get("timeout", 30)
        self.retry_count = self.config.get("retry_count", 2)
        self.session = requests.Session()
        
        # 设置默认请求头
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "ZhiShui-Frontend/1.0",
            "Accept": "application/json"
        })
    
    def _make_url(self, endpoint: str) -> str:
        """构建完整URL"""
        return urljoin(self.base_url, endpoint.lstrip('/'))
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """处理响应"""
        try:
            # 检查状态码
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise APIException(f"API端点不存在: {response.url}", response.status_code)
            elif response.status_code == 422:
                error_data = response.json() if response.content else {}
                raise ValidationException(f"请求参数验证失败", response.status_code, error_data)
            elif response.status_code >= 500:
                raise ServiceUnavailableException(f"服务器内部错误: {response.status_code}", response.status_code)
            else:
                raise APIException(f"请求失败: {response.status_code}", response.status_code)
                
        except json.JSONDecodeError:
            raise APIException(f"响应格式错误: 无法解析JSON")
    
    def _request_with_retry(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """带重试的请求"""
        url = self._make_url(endpoint)
        last_exception = None
        
        for attempt in range(self.retry_count + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                return self._handle_response(response)
                
            except requests.exceptions.Timeout:
                last_exception = TimeoutException(f"请求超时: {url}")
            except requests.exceptions.ConnectionError:
                last_exception = ServiceUnavailableException(f"连接失败: {url}")
            except APIException:
                raise  # 直接抛出API异常，不重试
            except Exception as e:
                last_exception = APIException(f"请求异常: {str(e)}")
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.retry_count:
                time.sleep(2 ** attempt)  # 指数退避
        
        # 所有重试都失败了
        raise last_exception
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET请求"""
        return self._request_with_retry("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """POST请求"""
        kwargs = {}
        if data:
            kwargs["data"] = data
        if json_data:
            kwargs["json"] = json_data
        return self._request_with_retry("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """PUT请求"""
        kwargs = {}
        if data:
            kwargs["data"] = data
        if json_data:
            kwargs["json"] = json_data
        return self._request_with_retry("PUT", endpoint, **kwargs)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE请求"""
        return self._request_with_retry("DELETE", endpoint)
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            response = self.get("/health")
            return response.get("status") == "healthy"
        except Exception:
            return False
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'session'):
            self.session.close()

# ============================================================================
# 项目信息整合服务客户端
# ============================================================================

class ProjectServiceClient(BaseAPIClient):
    """项目信息整合服务客户端"""
    
    def __init__(self):
        super().__init__("project_service")
    
    def get_projects(self, filters: Optional[Dict] = None) -> List[Dict]:
        """获取项目列表"""
        try:
            params = filters or {}
            response = self.get("/projects", params=params)
            return response.get("projects", [])
        except Exception as e:
            st.error(f"获取项目列表失败: {str(e)}")
            return []
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """获取单个项目信息"""
        try:
            response = self.get(f"/projects/{project_id}")
            return response.get("project")
        except Exception as e:
            st.error(f"获取项目信息失败: {str(e)}")
            return None
    
    def create_project(self, project_data: Dict) -> Optional[Dict]:
        """创建项目"""
        try:
            response = self.post("/projects", json_data=project_data)
            return response.get("project")
        except Exception as e:
            st.error(f"创建项目失败: {str(e)}")
            return None
    
    def update_project(self, project_id: str, project_data: Dict) -> Optional[Dict]:
        """更新项目"""
        try:
            response = self.put(f"/projects/{project_id}", json_data=project_data)
            return response.get("project")
        except Exception as e:
            st.error(f"更新项目失败: {str(e)}")
            return None
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        try:
            self.delete(f"/projects/{project_id}")
            return True
        except Exception as e:
            st.error(f"删除项目失败: {str(e)}")
            return False
    
    def import_projects(self, file_data: bytes, file_type: str = "excel") -> Dict:
        """导入项目数据"""
        try:
            files = {"file": ("projects.xlsx", file_data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            response = self.session.post(
                self._make_url("/projects/import"),
                files=files,
                data={"file_type": file_type},
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            st.error(f"导入项目数据失败: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def export_projects(self, format: str = "excel", filters: Optional[Dict] = None) -> Optional[bytes]:
        """导出项目数据"""
        try:
            params = {"format": format}
            if filters:
                params.update(filters)
            
            response = self.session.get(
                self._make_url("/projects/export"),
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.content
            else:
                st.error(f"导出失败: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"导出项目数据失败: {str(e)}")
            return None
    
    def get_project_statistics(self) -> Dict:
        """获取项目统计信息"""
        try:
            response = self.get("/projects/statistics")
            return response.get("statistics", {})
        except Exception as e:
            st.error(f"获取项目统计失败: {str(e)}")
            return {}

# ============================================================================
# 智能路由枚举类型
# ============================================================================

class CallMode(Enum):
    """调用模式枚举"""
    BASIC_TOOL = "basic_tool"      # 基础工具调用
    AGENT_ANALYSIS = "agent"       # 智能Agent分析
    FULL_WORKFLOW = "workflow"     # 完整工作流

class ComplexityLevel(Enum):
    """功能复杂度级别"""
    BASIC = "basic"        # 基础功能：健康检查、文件操作、数据验证
    INTELLIGENT = "intelligent"  # 智能功能：分析、预测、问答
    COMPLEX = "complex"    # 复杂功能：综合分析、多维决策、完整报告

# ============================================================================
# 增强的Agno智能体协调中心客户端
# ============================================================================

# ============================================================================
# Agno智能体协调中心客户端
# ============================================================================

class AgnoCoordinatorClient(BaseAPIClient):
    """增强的Agno智能体协调中心客户端 - 支持智能路由"""
    
    def __init__(self):
        super().__init__("agno_coordinator")
        # 功能复杂度映射表
        self._complexity_mapping = {
            # 基础功能
            "health_check": ComplexityLevel.BASIC,
            "file_upload": ComplexityLevel.BASIC,
            "file_download": ComplexityLevel.BASIC,
            "data_validation": ComplexityLevel.BASIC,
            "get_tools": ComplexityLevel.BASIC,
            
            # 智能功能
            "financial_analysis": ComplexityLevel.INTELLIGENT,
            "cost_prediction": ComplexityLevel.INTELLIGENT,
            "efficiency_assessment": ComplexityLevel.INTELLIGENT,
            "knowledge_qa": ComplexityLevel.INTELLIGENT,
            "single_analysis": ComplexityLevel.INTELLIGENT,
            
            # 复杂功能
            "comprehensive_analysis": ComplexityLevel.COMPLEX,
            "multi_dimensional_decision": ComplexityLevel.COMPLEX,
            "full_report": ComplexityLevel.COMPLEX,
            "workflow_execution": ComplexityLevel.COMPLEX
        }
    
    def _determine_call_mode(self, function_name: str, **kwargs) -> CallMode:
        """根据功能复杂度自动判断调用模式"""
        complexity = self._complexity_mapping.get(function_name, ComplexityLevel.INTELLIGENT)
        
        if complexity == ComplexityLevel.BASIC:
            return CallMode.BASIC_TOOL
        elif complexity == ComplexityLevel.INTELLIGENT:
            return CallMode.AGENT_ANALYSIS
        else:
            return CallMode.FULL_WORKFLOW
    
    # ========================================================================
    # 三种调用方法
    # ========================================================================
    
    def call_agent_analysis(self, agent_type: str, task_description: str, context: Optional[Dict] = None) -> Dict:
        """调用Agent进行智能分析"""
        try:
            request_data = {
                "agent_type": agent_type,
                "task_description": task_description,
                "context": context or {},
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.post("/agent/call", json_data=request_data)
            return response
            
        except Exception as e:
            st.error(f"Agent智能分析失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def call_basic_tool(self, service_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict:
        """调用基础MCP工具"""
        try:
            request_data = {
                "service_name": service_name,
                "tool_name": tool_name,
                "arguments": arguments,
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.post("/tools/call", json_data=request_data)
            return response
            
        except Exception as e:
            st.error(f"基础工具调用失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def execute_workflow(self, task: str, agents: List[str] = None, workflow_type: str = "sequential", timeout: int = 300) -> Dict:
        """执行完整工作流"""
        try:
            request_data = {
                "task": task,
                "agents": agents or ["planner", "business", "report"],
                "workflow_type": workflow_type,
                "timeout": timeout,
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.post("/collaborate", json_data=request_data)
            return response
            
        except Exception as e:
            st.error(f"完整工作流执行失败: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    # ========================================================================
    # 智能路由方法 - 自动选择最佳调用方式
    # ========================================================================
    
    def smart_call(self, function_name: str, **kwargs) -> Dict:
        """智能路由调用 - 根据功能复杂度自动选择调用方式"""
        call_mode = self._determine_call_mode(function_name, **kwargs)
        
        if call_mode == CallMode.BASIC_TOOL:
            return self._handle_basic_call(function_name, **kwargs)
        elif call_mode == CallMode.AGENT_ANALYSIS:
            return self._handle_agent_call(function_name, **kwargs)
        else:
            return self._handle_workflow_call(function_name, **kwargs)
    
    def _handle_basic_call(self, function_name: str, **kwargs) -> Dict:
        """处理基础工具调用"""
        service_mapping = {
            "health_check": "system",
            "file_upload": "file_service",
            "file_download": "file_service",
            "data_validation": "validation_service"
        }
        
        service_name = service_mapping.get(function_name, "system")
        return self.call_basic_tool(service_name, function_name, kwargs)
    
    def _handle_agent_call(self, function_name: str, **kwargs) -> Dict:
        """处理Agent智能分析调用"""
        agent_mapping = {
            "financial_analysis": "financial",
            "cost_prediction": "cost",
            "efficiency_assessment": "hr",
            "knowledge_qa": "knowledge"
        }
        
        agent_type = agent_mapping.get(function_name, "general")
        task_description = kwargs.get("task_description", f"执行{function_name}任务")
        context = kwargs.get("context", {})
        
        return self.call_agent_analysis(agent_type, task_description, context)
    
    def _handle_workflow_call(self, function_name: str, **kwargs) -> Dict:
        """处理完整工作流调用"""
        task = kwargs.get("task", f"执行{function_name}完整工作流")
        agents = kwargs.get("agents")
        workflow_type = kwargs.get("workflow_type", "sequential")
        
        return self.execute_workflow(task, agents, workflow_type)
    
    # ========================================================================
    # 兼容性方法 - 保持原有接口
    # ========================================================================
    
    def query_agent(self, agent_type: str, query: str, context: Optional[Dict] = None) -> Dict:
        """查询智能体（兼容性方法）"""
        return self.call_agent_analysis(agent_type, query, context)
    
    def multi_agent_collaboration(self, task: str, agents: List[str], workflow_type: str = "sequential", timeout: int = 300) -> Dict:
        """多智能体协作（兼容性方法）"""
        return self.execute_workflow(task, agents, workflow_type, timeout)
    
    def get_agent_status(self) -> Dict:
        """获取智能体状态"""
        try:
            response = self.get("/agents/status")
            return response.get("agents", {})
        except Exception as e:
            st.error(f"获取智能体状态失败: {str(e)}")
            return {}
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """获取对话历史"""
        try:
            response = self.get(f"/conversations/{session_id}")
            return response.get("history", [])
        except Exception as e:
            st.error(f"获取对话历史失败: {str(e)}")
            return []
    
    def save_conversation(self, session_id: str, user_message: str, ai_response: Dict, file_info: Optional[Dict] = None) -> bool:
        """保存对话到后端"""
        try:
            data = {
                "session_id": session_id,
                "user_message": user_message,
                "ai_response": ai_response,
                "file_info": file_info
            }
            response = self.post("/conversations/save", json_data=data)
            return response.get("success", False)
        except Exception as e:
            st.error(f"保存对话失败: {str(e)}")
            return False
    
    def create_session(self) -> Optional[str]:
        """创建新的会话ID"""
        try:
            response = self.post("/conversations/session")
            if response.get("success"):
                return response.get("session_id")
            return None
        except Exception as e:
            st.error(f"创建会话失败: {str(e)}")
            return None
    
    def delete_conversation(self, session_id: str) -> bool:
        """删除对话历史"""
        try:
            response = self.delete(f"/conversations/{session_id}")
            return response.get("success", False)
        except Exception as e:
            st.error(f"删除对话失败: {str(e)}")
            return False
    
    def get_all_conversations(self, limit: int = 20, offset: int = 0) -> Dict:
        """获取所有会话列表"""
        try:
            response = self.get(f"/conversations?limit={limit}&offset={offset}")
            return response
        except Exception as e:
            st.error(f"获取会话列表失败: {str(e)}")
            return {"success": False, "conversations": [], "total_count": 0}

# ============================================================================
# API客户端管理器
# ============================================================================

class APIClientManager:
    """简化的API客户端管理器 - 只管理AgnoCoordinatorClient"""
    
    def __init__(self):
        self._clients = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """初始化客户端"""
        try:
            # 项目服务客户端
            self._clients["project"] = ProjectServiceClient()
            
            # Agno协调中心客户端（统一入口）
            self._clients["agno"] = AgnoCoordinatorClient()
            
            # 为向后兼容，创建别名
            self._clients["financial"] = self._clients["agno"]
            self._clients["knowledge"] = self._clients["agno"]
            self._clients["cost"] = self._clients["agno"]
            self._clients["decision"] = self._clients["agno"]
            self._clients["hr"] = self._clients["agno"]
            
        except Exception as e:
            st.error(f"初始化API客户端失败: {str(e)}")
    
    def get_client(self, service_name: str) -> Optional[BaseAPIClient]:
        """获取指定服务的客户端"""
        return self._clients.get(service_name)
    
    def health_check_all(self) -> Dict[str, bool]:
        """检查所有服务健康状态"""
        health_status = {}
        
        # 检查项目服务
        try:
            project_client = self._clients.get("project")
            if project_client and hasattr(project_client, 'health_check'):
                health_status["project"] = project_client.health_check()
            else:
                health_status["project"] = True
        except Exception:
            health_status["project"] = False
        
        # 检查Agno协调中心（代表所有MCP服务）
        try:
            agno_client = self._clients.get("agno")
            if agno_client and hasattr(agno_client, 'get_agent_status'):
                agent_status = agno_client.get_agent_status()
                health_status["agno"] = bool(agent_status)
                
                # 为向后兼容，设置各个服务的状态
                health_status["financial"] = health_status["agno"]
                health_status["knowledge"] = health_status["agno"]
                health_status["cost"] = health_status["agno"]
                health_status["decision"] = health_status["agno"]
                health_status["hr"] = health_status["agno"]
            else:
                health_status["agno"] = True
        except Exception:
            health_status["agno"] = False
        
        return health_status
    
    def get_available_services(self) -> List[str]:
        """获取可用服务列表"""
        health_status = self.health_check_all()
        return [service for service, is_healthy in health_status.items() if is_healthy]
    
    def __del__(self):
        """清理所有客户端"""
        for client in self._clients.values():
            if hasattr(client, '__del__'):
                client.__del__()

# ============================================================================
# 全局API客户端实例
# ============================================================================

# 创建全局API客户端管理器实例
api_manager = APIClientManager()

# 便捷访问函数
def get_project_client() -> ProjectServiceClient:
    """获取项目服务客户端"""
    return api_manager.get_client("project")

def get_financial_client() -> AgnoCoordinatorClient:
    """获取财务分析客户端（通过Agno协调中心）"""
    return api_manager.get_client("financial")

def get_knowledge_client() -> AgnoCoordinatorClient:
    """获取知识库客户端（通过Agno协调中心）"""
    return api_manager.get_client("knowledge")

def get_cost_client() -> AgnoCoordinatorClient:
    """获取成本核算客户端（通过Agno协调中心）"""
    return api_manager.get_client("cost")

def get_decision_client() -> AgnoCoordinatorClient:
    """获取决策分析客户端（通过Agno协调中心）"""
    return api_manager.get_client("decision")

def get_agno_client() -> AgnoCoordinatorClient:
    """获取Agno协调中心客户端"""
    return api_manager.get_client("agno")

def check_services_health() -> Dict[str, bool]:
    """检查所有服务健康状态"""
    return api_manager.health_check_all()

def call_multi_agent_system_with_file(message: str, data_context: Dict, file_content: Any = None, file_info: Dict = None) -> Dict:
    """
    调用Multi-Agent系统API（支持文件上传）
    
    Args:
        message: 用户消息
        data_context: 数据上下文
        file_content: 文件内容
        file_info: 文件信息
    
    Returns:
        AI回复结果
    """
    try:
        # 首先尝试获取Agno客户端
        agno_client = get_agno_client()
        if not agno_client:
            print("⚠️ Agno客户端不可用，尝试直接调用API")
            # 如果客户端不可用，直接调用API
            return _call_agno_api_directly(message, data_context, file_content, file_info)
        
        # 构建任务描述，包含文件信息
        task_description = message
        if file_content is not None and file_info is not None:
            task_description += f"\n\n文件信息：{file_info.get('name', '未知文件')}"
            if file_info.get('type'):
                task_description += f"，类型：{file_info['type']}"
            if file_info.get('size'):
                task_description += f"，大小：{file_info['size']} bytes"
            task_description += f"\n文件内容：{str(file_content)[:1000]}..."  # 限制内容长度
        
        print(f"📤 发送请求到Agno协调中心: {message[:50]}...")
        
        # 调用execute_workflow方法
        response = agno_client.execute_workflow(
            task=task_description,
            agents=["financial", "knowledge", "cost", "decision"],
            workflow_type="comprehensive_analysis",
            timeout=120
        )
        
        print(f"📥 收到Agno响应: {response}")
        
        # 检查响应状态 - Agno使用"status": "success"格式
        if response and response.get("status") == "success":
            # 提取实际的AI回复内容 - 优先从comprehensive_analysis字段获取
            ai_response = ""
            
            # 1. 优先获取综合分析内容
            comprehensive_analysis = response.get("comprehensive_analysis", "")
            if comprehensive_analysis and comprehensive_analysis.strip():
                ai_response = comprehensive_analysis
            
            # 2. 如果没有综合分析，尝试从execution_summary获取
            elif response.get("execution_summary"):
                ai_response = response.get("execution_summary", "")
            
            # 3. 如果还没有，尝试从agent_results中提取
            elif response.get("agent_results"):
                agent_results = response.get("agent_results", {})
                analysis_parts = []
                for agent_id, result in agent_results.items():
                    if isinstance(result, dict) and result.get("result"):
                        analysis_parts.append(f"【{agent_id}】: {result['result']}")
                ai_response = "\n\n".join(analysis_parts) if analysis_parts else "智能体分析完成"
            
            # 4. 最后的备选方案
            else:
                ai_response = "智水AI系统已处理您的请求，工作流执行完成"
            
            # 构建返回结果
            result_data = {
                "success": True,
                "response": ai_response,
                "agents_used": list(response.get("agent_results", {}).keys()),
                "processing_time": response.get("response_time", 0),
                "workflow_type": response.get("workflow_type", ""),
                "success_rate": response.get("success_rate", ""),
                "timestamp": datetime.now().isoformat()
            }
            
            # 如果有Word文档路径，添加到返回结果中
            if response.get("word_file_path"):
                result_data["word_file_path"] = response["word_file_path"]
                result_data["report_type"] = response.get("report_type", "")
                result_data["generation_timestamp"] = response.get("generation_timestamp", "")
                
                # 在AI回复中添加Word文档信息
                if "Word文档路径" not in ai_response:
                    ai_response += f"\n\n📄 Word决策支持报告已生成：{response['word_file_path']}"
                    result_data["response"] = ai_response
            
            return result_data
        else:
            error_msg = response.get("error", "处理请求时发生未知错误") if response else "无响应数据"
            print(f"❌ Agno处理失败: {error_msg}")
            return {
                "success": False,
                "response": f"智能体协作失败：{error_msg}",
                "error": "PROCESSING_ERROR",
                "timestamp": datetime.now().isoformat()
            }
            
    except requests.exceptions.ConnectionError as e:
        print(f"🔌 连接错误: {str(e)}")
        return {
            "success": False,
            "response": "无法连接到智能体协调中心，请检查服务是否正常运行",
            "error": "CONNECTION_ERROR",
            "timestamp": datetime.now().isoformat()
        }
    except requests.exceptions.Timeout as e:
        print(f"⏰ 请求超时: {str(e)}")
        return {
            "success": False,
            "response": "请求超时，请稍后重试",
            "error": "TIMEOUT_ERROR",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"💥 系统异常: {str(e)}")
        return {
            "success": False,
            "response": f"系统异常：{str(e)}",
            "error": "SYSTEM_ERROR",
            "timestamp": datetime.now().isoformat()
        }

def _call_agno_api_directly(message: str, data_context: Dict, file_content: Any = None, file_info: Dict = None) -> Dict:
    """
    直接调用Agno协调中心API（备用方案）
    """
    try:
        import requests
        
        # 构建请求数据 - 修复：匹配后端CollaborationRequest模型
        request_data = {
            "task": message,
            "agents": ["financial_agent", "knowledge_agent", "cost_agent", "decision_agent"],
            "workflow_type": "comprehensive_analysis",  # 添加必需字段
            "timeout": 60  # 设置超时时间
        }
        
        # 注意：移除context字段，因为后端CollaborationRequest不接受此字段
        # 文件和上下文信息将通过task描述传递
        if file_content is not None and file_info is not None:
            # 将文件信息嵌入到task描述中
            file_desc = f"\n\n[文件信息: {file_info.get('name', '未知文件')}]"
            request_data["task"] = message + file_desc
        
        print(f"🔄 直接调用Agno API: http://localhost:8000/collaborate")
        
        # 直接调用API
        response = requests.post(
            "http://localhost:8000/collaborate",
            json=request_data,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 API响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API调用成功: {result}")
            
            return {
                "success": True,
                "response": result.get("final_report", result.get("result", "智水AI系统已处理您的请求")),
                "agents_used": result.get("agents_used", []),
                "processing_time": result.get("response_time", 0),
                "timestamp": datetime.now().isoformat()
            }
        else:
            error_msg = f"API返回错误状态码: {response.status_code}"
            if response.content:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", error_msg)
                except:
                    pass
            
            print(f"❌ API调用失败: {error_msg}")
            return {
                "success": False,
                "response": f"API调用失败：{error_msg}",
                "error": "API_ERROR",
                "timestamp": datetime.now().isoformat()
            }
            
    except requests.exceptions.ConnectionError:
        print("🔌 无法连接到Agno协调中心")
        return {
            "success": False,
            "response": "无法连接到智能体协调中心，请检查服务是否在http://localhost:8000运行",
            "error": "CONNECTION_ERROR",
            "timestamp": datetime.now().isoformat()
        }
    except requests.exceptions.Timeout:
        print("⏰ API请求超时")
        return {
            "success": False,
            "response": "请求超时，智能体处理时间较长，请稍后重试",
            "error": "TIMEOUT_ERROR",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"💥 直接API调用异常: {str(e)}")
        return {
            "success": False,
            "response": f"API调用异常：{str(e)}",
            "error": "SYSTEM_ERROR",
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# 测试函数
# ============================================================================

def test_api_clients():
    """测试API客户端"""
    print(" 开始测试API客户端...")
    
    # 测试健康检查
    health_status = check_services_health()
    print(f" 服务健康检查完成: {health_status}")
    
    # 测试项目服务客户端
    project_client = get_project_client()
    if project_client:
        print(" 项目服务客户端初始化成功")
    
    # 测试财务分析客户端
    financial_client = get_financial_client()
    if financial_client:
        print(" 财务分析客户端初始化成功")
    
    # 测试Agno协调中心客户端
    agno_client = get_agno_client()
    if agno_client:
        print(" Agno协调中心客户端初始化成功")
    
    print(" 所有API客户端测试完成！")

if __name__ == "__main__":
    test_api_clients()