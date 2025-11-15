#!/usr/bin/env python3
"""
智水信息Multi-Agent系统 - 主启动脚本
系统统一启动入口

功能职责：
1. 系统初始化和配置加载
2. 所有Agent和协调器启动
3. 系统健康检查和监控
4. 提供命令行和API接口
5. 优雅关闭和资源清理

Author: 商海星辰队
Version: 1.0.0
"""

import sys
import os
import asyncio
import argparse
import signal
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import json
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional as OptionalType

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入系统组件
from config import config_manager, get_ai_config, get_business_context
from agno_coordinator import AgnoCoordinator, create_agno_coordinator
from models.conversation_history import (
    conversation_db, 
    save_conversation_message, 
    get_conversation_history,
    generate_session_id
)

# ================================
# FastAPI 数据模型
# ================================

class CollaborateRequest(BaseModel):
    """协作请求数据模型"""
    task: str
    agents: OptionalType[List[str]] = None
    context: OptionalType[Dict[str, Any]] = None
    timestamp: OptionalType[str] = None
    workflow_type: OptionalType[str] = "comprehensive_analysis"

class CollaborateResponse(BaseModel):
    """协作响应模型"""
    success: bool
    workflow_id: OptionalType[str] = None
    execution_time: float = 0.0
    status: str
    stages_completed: int = 0
    final_report: OptionalType[str] = None
    stage_results: Dict[str, Any] = {}
    error: OptionalType[Dict[str, Any]] = None

class SaveConversationRequest(BaseModel):
    """保存对话请求模型"""
    session_id: str
    user_message: str
    ai_response: Dict[str, Any]
    file_info: OptionalType[Dict[str, Any]] = None

class ConversationHistoryResponse(BaseModel):
    """对话历史响应模型"""
    success: bool
    session_id: str
    history: List[Dict[str, Any]] = []
    total_count: int = 0
    error: OptionalType[Dict[str, Any]] = None

# ================================
# 1. 日志配置
# ================================

def setup_logging():
    """配置系统日志"""
    logging_config = config_manager.logging_config
    
    # 创建日志格式器
    formatter = logging.Formatter(logging_config.log_format)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, logging_config.log_level))
    
    # 清除现有处理器
    root_logger.handlers.clear()
    
    # 文件日志处理器
    if logging_config.enable_file_logging:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            logging_config.log_file_path,
            maxBytes=logging_config.max_file_size,
            backupCount=logging_config.backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 控制台日志处理器
    if logging_config.enable_console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, logging_config.console_log_level))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    return logging.getLogger("MainSystem")

# ================================
# 2. 系统管理器
# ================================

class SystemManager:
    """系统管理器
    
    负责整个系统的生命周期管理
    """
    
    def __init__(self):
        """初始化系统管理器"""
        self.logger = setup_logging()
        self.coordinator: Optional[AgnoCoordinator] = None
        self.is_running = False
        self.startup_time = None
        self.app: Optional[FastAPI] = None
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("系统管理器初始化完成")
    
    def create_fastapi_app(self) -> FastAPI:
        """创建FastAPI应用实例"""
        if self.app is not None:
            return self.app
        
        # 创建FastAPI应用
        self.app = FastAPI(
            title="智水信息Multi-Agent协作系统",
            description="四川智水信息技术有限公司AI智慧管理解决方案",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # 配置CORS中间件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # 生产环境应该限制具体域名
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 注册路由
        self._register_routes()
        
        self.logger.info("FastAPI应用创建完成")
        return self.app
    
    def _create_error_response(self, error_code: str, error_message: str, status_code: int) -> CollaborateResponse:
        """创建标准化错误响应"""
        return CollaborateResponse(
            success=False,
            workflow_id=None,
            execution_time=0.0,
            status="error",
            stages_completed=0,
            final_report=None,
            stage_results={},
            error={
                "code": error_code,
                "message": error_message,
                "status_code": status_code,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def _create_success_response(self, result: dict) -> CollaborateResponse:
        """创建标准化成功响应"""
        return CollaborateResponse(
            success=result.get("success", True),
            workflow_id=result.get("workflow_id"),
            execution_time=result.get("execution_time", 0.0),
            status=result.get("status", "completed"),
            stages_completed=result.get("stages_completed", 0),
            final_report=result.get("final_report"),
            stage_results=result.get("stage_results", {}),
            error=result.get("error")
        )
    
    def _register_routes(self):
        """注册API路由"""
        if not self.app:
            return
        
        @self.app.get("/")
        async def root():
            """根路径 - 系统信息"""
            return {
                "message": "智水信息Multi-Agent协作系统",
                "version": "1.0.0",
                "status": "running" if self.is_running else "stopped",
                "docs": "/docs"
            }
        
        @self.app.get("/health")
        async def health_check():
            """健康检查接口"""
            if not self.is_running or not self.coordinator:
                raise HTTPException(status_code=503, detail="系统未运行")
            
            status = self.get_system_status()
            return {
                "status": "healthy",
                "system_info": status
            }
        
        @self.app.post("/collaborate", response_model=CollaborateResponse)
        async def collaborate(request: CollaborateRequest):
            """智能体协作接口 - JSON格式"""
            # 参数验证
            if not request.task or not request.task.strip():
                return self._create_error_response(
                    "INVALID_PARAMETER", 
                    "任务描述不能为空", 
                    400
                )
            
            if not self.is_running or not self.coordinator:
                return self._create_error_response(
                    "SERVICE_UNAVAILABLE", 
                    "系统未运行，请稍后重试", 
                    503
                )
            
            try:
                # 从请求中提取参数
                task = request.task
                agents = request.agents
                context = request.context or {}
                timestamp = request.timestamp
                workflow_type = request.workflow_type or "comprehensive_analysis"
                
                # 执行分析任务
                start_time = datetime.now()
                
                result = await self.coordinator.execute_workflow(
                    user_input_text=task,
                    data_content=context,
                    workflow_type=workflow_type
                )
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # 构建响应
                return CollaborateResponse(
                    success=True,
                    workflow_id=result.workflow_id,
                    execution_time=execution_time,
                    status=result.overall_status,
                    stages_completed=len(result.stage_results),
                    final_report=result.final_report or "",
                    stage_results=result.stage_results
                )
                
            except Exception as e:
                self.logger.error(f"协作执行失败: {str(e)}")
                return self._create_error_response(
                    "EXECUTION_ERROR",
                    f"执行失败: {str(e)}",
                    500
                )
            
        @self.app.post("/collaborate_with_file", response_model=CollaborateResponse)
        async def collaborate_with_file(
            task: str = Form(...),
            agents: OptionalType[str] = Form(None),
            context: OptionalType[str] = Form(None),
            timestamp: OptionalType[str] = Form(None),
            workflow_type: OptionalType[str] = Form("comprehensive_analysis"),
            file: OptionalType[UploadFile] = File(None)
        ):
            """智能体协作接口 - JSON格式"""
            # 参数验证
            if not task or not task.strip():
                return self._create_error_response(
                    "INVALID_PARAMETER", 
                    "任务描述不能为空", 
                    400
                )
            
            if not self.is_running or not self.coordinator:
                return self._create_error_response(
                    "SERVICE_UNAVAILABLE", 
                    "系统未运行，请稍后重试", 
                    503
                )
            
            try:
                # 处理agents参数
                agents_list = agents if isinstance(agents, list) else None
                
                # 处理context参数
                context_dict = context if isinstance(context, dict) else {}
                
                # 执行分析任务（不支持文件上传）
                result = await self.execute_analysis(
                    user_input=task,
                    workflow_type=workflow_type,
                    uploaded_files=[],
                    data_content=context_dict
                )
                
                # 确保返回格式标准化
                return self._create_success_response(result)
                
            except HTTPException:
                # 重新抛出HTTP异常
                raise
            except ValueError as e:
                self.logger.error(f"参数验证错误: {str(e)}")
                return self._create_error_response(
                    "VALIDATION_ERROR", 
                    f"参数验证失败: {str(e)}", 
                    400
                )
            except TimeoutError as e:
                self.logger.error(f"执行超时: {str(e)}")
                return self._create_error_response(
                    "EXECUTION_TIMEOUT", 
                    "任务执行超时，请稍后重试", 
                    408
                )
            except Exception as e:
                self.logger.error(f"协作接口执行失败: {str(e)}", exc_info=True)
                return self._create_error_response(
                    "INTERNAL_ERROR", 
                    f"系统内部错误: {str(e)}", 
                    500
                )
        
        @self.app.post("/collaborate_with_file", response_model=CollaborateResponse)
        async def collaborate_with_file(
            task: str = Form(...),
            agents: OptionalType[str] = Form(None),
            context: OptionalType[str] = Form(None),
            timestamp: OptionalType[str] = Form(None),
            workflow_type: OptionalType[str] = Form("comprehensive_analysis"),
            file: OptionalType[UploadFile] = File(None)
        ):
            """智能体协作接口 - 支持文件上传"""
            # 参数验证
            if not task or not task.strip():
                return self._create_error_response(
                    "INVALID_PARAMETER", 
                    "任务描述不能为空", 
                    400
                )
            
            if not self.is_running or not self.coordinator:
                return self._create_error_response(
                    "SERVICE_UNAVAILABLE", 
                    "系统未运行，请稍后重试", 
                    503
                )
            
            try:
                # 处理上传的文件
                uploaded_files = []
                if file:
                    # 验证文件大小（限制为10MB）
                    if file.size and file.size > 10 * 1024 * 1024:
                        return self._create_error_response(
                            "FILE_TOO_LARGE", 
                            "文件大小不能超过10MB", 
                            413
                        )
                    
                    try:
                        # 读取文件内容
                        file_content = await file.read()
                        uploaded_files.append({
                            "filename": file.filename,
                            "content": file_content,
                            "content_type": file.content_type
                        })
                    except Exception as e:
                        self.logger.error(f"文件读取失败: {str(e)}")
                        return self._create_error_response(
                            "FILE_READ_ERROR", 
                            f"文件读取失败: {str(e)}", 
                            400
                        )
                
                # 解析agents参数（如果是JSON字符串）
                agents_list = None
                if agents:
                    try:
                        agents_list = json.loads(agents) if isinstance(agents, str) else agents
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"agents参数解析失败，使用默认处理: {str(e)}")
                        agents_list = [agents]  # 如果不是JSON，当作单个agent处理
                
                # 解析context参数（如果是JSON字符串）
                context_dict = {}
                if context:
                    try:
                        context_dict = json.loads(context) if isinstance(context, str) else context
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"context参数解析失败，使用原始文本: {str(e)}")
                        context_dict = {"raw_context": context}
                
                # 执行分析任务
                result = await self.execute_analysis(
                    user_input=task,
                    workflow_type=workflow_type or "comprehensive_analysis",
                    uploaded_files=uploaded_files,
                    data_content=context_dict
                )
                
                # 确保返回格式标准化
                return self._create_success_response(result)
                
            except HTTPException:
                # 重新抛出HTTP异常
                raise
            except ValueError as e:
                self.logger.error(f"参数验证错误: {str(e)}")
                return self._create_error_response(
                    "VALIDATION_ERROR", 
                    f"参数验证失败: {str(e)}", 
                    400
                )
            except TimeoutError as e:
                self.logger.error(f"执行超时: {str(e)}")
                return self._create_error_response(
                    "EXECUTION_TIMEOUT", 
                    "任务执行超时，请稍后重试", 
                    408
                )
            except Exception as e:
                self.logger.error(f"协作接口执行失败: {str(e)}", exc_info=True)
                return self._create_error_response(
                    "INTERNAL_ERROR", 
                    f"系统内部错误: {str(e)}", 
                    500
                )
        
        @self.app.get("/status")
        async def get_status():
            """获取系统状态"""
            try:
                status_data = self.get_system_status()
                return {
                    "success": True,
                    "data": status_data,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                self.logger.error(f"获取系统状态失败: {str(e)}")
                return {
                    "success": False,
                    "error": {
                        "code": "STATUS_ERROR",
                        "message": f"获取系统状态失败: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }
                }
        
        @self.app.get("/history")
        async def get_history(limit: int = 10):
            """获取工作流历史"""
            try:
                # 参数验证
                if limit < 1 or limit > 100:
                    return {
                        "success": False,
                        "error": {
                            "code": "INVALID_PARAMETER",
                            "message": "limit参数必须在1-100之间",
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                
                history_data = self.get_workflow_history(limit)
                return {
                    "success": True,
                    "data": history_data,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                self.logger.error(f"获取工作流历史失败: {str(e)}")
                return {
                    "success": False,
                    "error": {
                        "code": "HISTORY_ERROR",
                        "message": f"获取工作流历史失败: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }
                }
        
        @self.app.post("/conversations")
        async def save_conversation(request: SaveConversationRequest):
            """保存对话消息"""
            try:
                # 保存用户消息
                save_conversation_message(
                    session_id=request.session_id,
                    message_type="user",
                    content=request.user_message,
                    metadata=request.file_info
                )
                
                # 保存AI回复
                save_conversation_message(
                    session_id=request.session_id,
                    message_type="assistant",
                    content=json.dumps(request.ai_response, ensure_ascii=False),
                    metadata=None
                )
                
                return {
                    "success": True,
                    "message": "对话已保存",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                self.logger.error(f"保存对话失败: {str(e)}")
                return {
                    "success": False,
                    "error": {
                        "code": "SAVE_CONVERSATION_ERROR",
                        "message": f"保存对话失败: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }
                }
        
        @self.app.get("/conversations/{session_id}")
        async def get_conversation(session_id: str, limit: int = 50):
            """获取对话历史"""
            try:
                # 参数验证
                if limit < 1 or limit > 200:
                    return ConversationHistoryResponse(
                        success=False,
                        session_id=session_id,
                        error={
                            "code": "INVALID_PARAMETER",
                            "message": "limit参数必须在1-200之间",
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                
                history = get_conversation_history(session_id, limit)
                
                return ConversationHistoryResponse(
                    success=True,
                    session_id=session_id,
                    history=history,
                    total_count=len(history)
                )
            except Exception as e:
                self.logger.error(f"获取对话历史失败: {str(e)}")
                return ConversationHistoryResponse(
                    success=False,
                    session_id=session_id,
                    error={
                        "code": "GET_CONVERSATION_ERROR",
                        "message": f"获取对话历史失败: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }
                )
        
        @self.app.delete("/conversations/{session_id}")
        async def delete_conversation(session_id: str):
            """删除对话历史"""
            try:
                conversation_db.delete_session(session_id)
                return {
                    "success": True,
                    "message": f"会话 {session_id} 已删除",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                self.logger.error(f"删除对话历史失败: {str(e)}")
                return {
                    "success": False,
                    "error": {
                        "code": "DELETE_CONVERSATION_ERROR",
                        "message": f"删除对话历史失败: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }
                }
        
        @self.app.post("/conversations/session")
        async def create_session():
            """创建新的会话ID"""
            try:
                session_id = generate_session_id()
                return {
                    "success": True,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                self.logger.error(f"创建会话失败: {str(e)}")
                return {
                    "success": False,
                    "error": {
                        "code": "CREATE_SESSION_ERROR",
                        "message": f"创建会话失败: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }
                }
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info(f"接收到信号 {signum}，开始优雅关闭系统...")
        self.shutdown()
    
    async def startup(self) -> bool:
        """启动系统"""
        try:
            self.logger.info("开始启动智水信息Multi-Agent系统...")
            self.startup_time = datetime.now()
            
            # 1. 系统配置验证
            if not self._validate_system_config():
                self.logger.error("系统配置验证失败")
                return False
            
            # 2. 创建Agno协调器
            self.logger.info("正在初始化Agno协调器...")
            self.coordinator = create_agno_coordinator()
            
            # 3. 系统健康检查
            if not await self._health_check():
                self.logger.error("系统健康检查失败")
                return False
            
            # 4. 标记系统运行状态
            self.is_running = True
            
            # 5. 显示系统信息
            self._display_system_info()
            
            self.logger.info("智水信息Multi-Agent系统启动成功！")
            return True
            
        except Exception as e:
            self.logger.error(f"系统启动失败: {str(e)}")
            return False
    
    def _validate_system_config(self) -> bool:
        """验证系统配置"""
        try:
            self.logger.info("验证系统配置...")
            
            # 验证AI配置
            ai_config = get_ai_config()
            required_ai_keys = ['api_key', 'api_base', 'model']
            for key in required_ai_keys:
                if not ai_config.get(key):
                    self.logger.error(f"AI配置缺少必要参数: {key}")
                    return False
            
            # 验证业务配置
            business_context = get_business_context()
            if not business_context.get('company_info', {}).get('name'):
                self.logger.error("业务配置缺少公司信息")
                return False
            
            self.logger.info("系统配置验证通过")
            return True
            
        except Exception as e:
            self.logger.error(f"配置验证异常: {str(e)}")
            return False
    
    async def _health_check(self) -> bool:
        """系统健康检查"""
        try:
            self.logger.info("执行系统健康检查...")
            
            if not self.coordinator:
                self.logger.error("协调器未初始化")
                return False
            
            # 检查Agent状态
            system_status = self.coordinator.get_system_status()
            agent_count = system_status['coordinator_info']['total_agents']
            
            if agent_count < 5:  # 期望至少5个Agent
                self.logger.warning(f"Agent数量不足，当前: {agent_count}，期望: 5+")
            
            self.logger.info(f"健康检查通过 - 协调器状态正常，Agent数量: {agent_count}")
            return True
            
        except Exception as e:
            self.logger.error(f"健康检查失败: {str(e)}")
            return False
    
    def _display_system_info(self):
        """显示系统信息"""
        if not self.coordinator:
            return
        
        system_status = self.coordinator.get_system_status()
        business_context = get_business_context()
        
        print("\n" + "="*80)
        print(f"🚀 {business_context['company_info']['name']} - AI智慧管理系统")
        print("="*80)
        print(f"📊 系统版本: {system_status['coordinator_info']['version']}")
        print(f"🏢 业务领域: {business_context['company_info']['industry']}")
        print(f"🤖 Agent数量: {system_status['coordinator_info']['total_agents']}")
        print(f"⏰ 启动时间: {self.startup_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n🔧 可用Agent列表:")
        
        for agent_id, agent_info in system_status['agent_status'].items():
            print(f"  • {agent_info['agent_name']} ({agent_id})")
        
        print("\n📋 可用工作流模板:")
        for template in system_status['workflow_templates']:
            print(f"  • {template}")
        
        print("\n💡 使用说明:")
        print("  1. 使用 execute_analysis() 方法执行分析任务")
        print("  2. 使用 get_system_status() 查看系统状态")
        print("  3. 使用 Ctrl+C 优雅关闭系统")
        print("="*80 + "\n")
    
    async def execute_analysis(self, user_input: str, 
                             workflow_type: str = "comprehensive_analysis",
                             uploaded_files: list = None,
                             data_content: dict = None) -> Dict[str, Any]:
        """执行分析任务"""
        if not self.is_running or not self.coordinator:
            raise Exception("系统未运行或协调器未初始化")
        
        try:
            self.logger.info(f"开始执行分析任务: {workflow_type}")
            
            # 执行工作流
            workflow_result = await self.coordinator.execute_workflow(
                user_input_text=user_input,
                uploaded_files=uploaded_files or [],
                data_content=data_content or {},
                workflow_type=workflow_type
            )
            
            # 构建返回结果
            result = {
                "success": workflow_result.overall_status == "completed",
                "workflow_id": workflow_result.workflow_id,
                "execution_time": workflow_result.total_execution_time,
                "status": workflow_result.overall_status,
                "stages_completed": len(workflow_result.stage_results),
                "final_report": workflow_result.final_report,
                "stage_results": {}
            }
            
            # 添加各阶段结果摘要
            for stage_id, stage_results in workflow_result.stage_results.items():
                result["stage_results"][stage_id] = [
                    {
                        "agent_name": r.agent_name,
                        "success": r.success,
                        "confidence_score": r.confidence_score,
                        "execution_time": r.execution_time,
                        "error_message": r.error_message
                    }
                    for r in stage_results
                ]
            
            self.logger.info(f"分析任务完成: {workflow_result.workflow_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"分析任务执行失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": None,
                "execution_time": 0.0
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        if not self.coordinator:
            return {"status": "not_initialized"}
        
        base_status = self.coordinator.get_system_status()
        base_status["system_manager"] = {
            "is_running": self.is_running,
            "startup_time": self.startup_time.isoformat() if self.startup_time else None,
            "uptime_seconds": (datetime.now() - self.startup_time).total_seconds() if self.startup_time else 0
        }
        
        return base_status
    
    def get_workflow_history(self, limit: int = 10) -> list:
        """获取工作流历史"""
        if not self.coordinator:
            return []
        
        return self.coordinator.get_workflow_history(limit)
    
    def shutdown(self):
        """关闭系统"""
        if not self.is_running:
            return
        
        self.logger.info("开始关闭系统...")
        
        try:
            # 关闭协调器
            if self.coordinator:
                self.coordinator.shutdown()
            
            # 标记系统停止
            self.is_running = False
            
            # 计算运行时间
            if self.startup_time:
                uptime = datetime.now() - self.startup_time
                self.logger.info(f"系统运行时间: {uptime}")
            
            self.logger.info("系统已安全关闭")
            
        except Exception as e:
            self.logger.error(f"系统关闭异常: {str(e)}")
        
        finally:
            # 强制退出
            os._exit(0)

# ================================
# 3. 命令行接口
# ================================

def create_argument_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="智水信息Multi-Agent智慧管理系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --mode interactive          # 交互模式
  python main.py --mode api --port 8000     # API服务模式
  python main.py --mode demo                 # 演示模式
  python main.py --analysis "分析财务状况"    # 单次分析
        """
    )
    
    parser.add_argument(
        "--mode", 
        choices=["interactive", "api", "demo", "analysis"],
        default="interactive",
        help="运行模式 (默认: interactive)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8006,
        help="API服务端口 (默认: 8006)"
    )
    
    parser.add_argument(
        "--analysis",
        type=str,
        help="要执行的分析任务描述"
    )
    
    parser.add_argument(
        "--workflow",
        choices=["comprehensive_analysis", "financial_focus", "cost_efficiency_analysis"],
        default="comprehensive_analysis",
        help="工作流类型 (默认: comprehensive_analysis)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="结果输出文件路径"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出模式"
    )
    
    return parser

# ================================
# 4. 运行模式实现
# ================================

async def run_interactive_mode(system_manager: SystemManager):
    """交互模式"""
    print("\n🎯 进入交互模式 - 输入 'help' 查看帮助，输入 'quit' 退出")
    
    while system_manager.is_running:
        try:
            user_input = input("\n💬 请输入分析需求: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_input.lower() == 'help':
                print("""
📖 可用命令:
  • 直接输入分析需求，如: "分析我们公司的财务状况"
  • status - 查看系统状态
  • history - 查看工作流历史
  • help - 显示此帮助
  • quit/exit/q - 退出系统
                """)
                continue
            
            if user_input.lower() == 'status':
                status = system_manager.get_system_status()
                print(f"\n📊 系统状态: {json.dumps(status, indent=2, ensure_ascii=False)}")
                continue
            
            if user_input.lower() == 'history':
                history = system_manager.get_workflow_history(5)
                print(f"\n📋 工作流历史: {json.dumps(history, indent=2, ensure_ascii=False)}")
                continue
            
            # 执行分析
            print("\n🔄 正在执行分析，请稍候...")
            result = await system_manager.execute_analysis(user_input)
            
            if result["success"]:
                print(f"\n✅ 分析完成！")
                print(f"📊 工作流ID: {result['workflow_id']}")
                print(f"⏱️ 执行时间: {result['execution_time']:.2f}秒")
                print(f"📈 完成阶段: {result['stages_completed']}")
                
                if result.get("final_report"):
                    print("📄 已生成HTML报告")
                    
                    # 询问是否保存报告
                    save_report = input("\n💾 是否保存HTML报告到文件? (y/n): ").strip().lower()
                    if save_report in ['y', 'yes']:
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"analysis_report_{timestamp}.html"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(result["final_report"])
                        print(f"📁 报告已保存到: {filename}")
            else:
                print(f"\n❌ 分析失败: {result.get('error', '未知错误')}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n❌ 执行异常: {str(e)}")
    
    print("\n👋 感谢使用智水信息AI智慧管理系统！")

async def run_analysis_mode(system_manager: SystemManager, analysis_text: str, 
                          workflow_type: str, output_file: str = None):
    """单次分析模式"""
    print(f"\n🎯 执行单次分析: {analysis_text}")
    print(f"📋 工作流类型: {workflow_type}")
    
    try:
        result = await system_manager.execute_analysis(analysis_text, workflow_type)
        
        if result["success"]:
            print(f"\n✅ 分析完成！")
            print(f"📊 工作流ID: {result['workflow_id']}")
            print(f"⏱️ 执行时间: {result['execution_time']:.2f}秒")
            
            # 保存结果
            if output_file:
                output_data = {
                    "analysis_request": analysis_text,
                    "workflow_type": workflow_type,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    if output_file.endswith('.json'):
                        json.dump(output_data, f, indent=2, ensure_ascii=False)
                    elif output_file.endswith('.html') and result.get("final_report"):
                        f.write(result["final_report"])
                    else:
                        json.dump(output_data, f, indent=2, ensure_ascii=False)
                
                print(f"📁 结果已保存到: {output_file}")
        else:
            print(f"\n❌ 分析失败: {result.get('error', '未知错误')}")
            return 1
    
    except Exception as e:
        print(f"\n❌ 执行异常: {str(e)}")
        return 1
    
    return 0

async def run_demo_mode(system_manager: SystemManager):
    """演示模式"""
    print("\n🎪 进入演示模式 - 展示系统核心功能")
    
    demo_tasks = [
        {
            "description": "财务状况综合分析",
            "input": "请分析我们公司2024年的财务状况，包括盈利能力、偿债能力和运营效率",
            "workflow": "financial_focus"
        },
        {
            "description": "项目成本效率分析", 
            "input": "分析我们智慧电厂项目的成本控制情况和人员效率",
            "workflow": "cost_efficiency_analysis"
        },
        {
            "description": "运维知识管理优化",
            "input": "如何提升我们的运维知识管理体系和技术文档标准化",
            "workflow": "comprehensive_analysis"
        }
    ]
    
    for i, task in enumerate(demo_tasks, 1):
        print(f"\n🔄 演示任务 {i}/3: {task['description']}")
        print(f"📝 分析需求: {task['input']}")
        print(f"📋 工作流类型: {task['workflow']}")
        
        try:
            result = await system_manager.execute_analysis(
                task['input'], 
                task['workflow']
            )
            
            if result["success"]:
                print(f"✅ 任务完成 - 耗时: {result['execution_time']:.2f}秒")
                print(f"📊 完成阶段: {result['stages_completed']}")
            else:
                print(f"❌ 任务失败: {result.get('error', '未知错误')}")
        
        except Exception as e:
            print(f"❌ 任务异常: {str(e)}")
        
        # 演示间隔
        if i < len(demo_tasks):
            print("\n⏳ 等待3秒后继续下一个演示...")
            await asyncio.sleep(3)
    
    print("\n🎉 演示完成！系统功能展示结束。")

async def run_api_mode(system_manager: SystemManager, port: int = 8006):
    """API服务模式"""
    print(f"\n🌐 启动API服务模式 - 端口: {port}")
    
    try:
        # 创建FastAPI应用
        app = system_manager.create_fastapi_app()
        
        # 配置uvicorn服务器
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        
        print(f"\n🚀 API服务器启动成功！")
        print(f"📍 服务地址: http://localhost:{port}")
        print(f"📖 API文档: http://localhost:{port}/docs")
        print(f"🔍 ReDoc文档: http://localhost:{port}/redoc")
        print(f"\n🔗 主要接口:")
        print(f"  • POST /collaborate - 智能体协作接口")
        print(f"  • GET /health - 健康检查")
        print(f"  • GET /status - 系统状态")
        print(f"  • GET /history - 工作流历史")
        print(f"\n💡 使用 Ctrl+C 停止服务")
        
        # 启动服务器
        await server.serve()
        
    except Exception as e:
        print(f"\n❌ API服务启动失败: {str(e)}")
        system_manager.logger.error(f"API服务启动失败: {str(e)}")
        raise

# ================================
# 5. 主程序入口
# ================================

async def main():
    """主程序入口"""
    # 解析命令行参数
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # 创建系统管理器
    system_manager = SystemManager()
    
    try:
        # 启动系统
        if not await system_manager.startup():
            print("❌ 系统启动失败")
            return 1
        
        # 根据模式运行
        if args.mode == "interactive":
            await run_interactive_mode(system_manager)
        
        elif args.mode == "analysis":
            if not args.analysis:
                print("❌ 分析模式需要提供 --analysis 参数")
                return 1
            
            return await run_analysis_mode(
                system_manager, 
                args.analysis, 
                args.workflow,
                args.output
            )
        
        elif args.mode == "demo":
            await run_demo_mode(system_manager)
        
        elif args.mode == "api":
            await run_api_mode(system_manager, args.port)
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\n⚠️ 接收到中断信号")
        return 0
    
    except Exception as e:
        print(f"\n❌ 系统运行异常: {str(e)}")
        return 1
    
    finally:
        # 确保系统关闭
        system_manager.shutdown()

if __name__ == "__main__":
    # 设置事件循环策略（Windows兼容性）
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # 运行主程序
    exit_code = asyncio.run(main())
    sys.exit(exit_code)