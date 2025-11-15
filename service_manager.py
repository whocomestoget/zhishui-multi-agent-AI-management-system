#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================================
文件：service_manager.py
功能：四川智水AI智慧管理解决方案 - 服务管理器
技术：自动监控、重启断开的服务，解决内存不足导致的服务中断问题
============================================================================

解决智水信息的服务稳定性问题：
- 自动检测断开的服务
- 自动重启断开的服务  
- 持续监控所有服务状态
- 提供服务状态报告
"""

import subprocess
import time
import requests
import os
import sys
from datetime import datetime
import threading
import signal

class ServiceManager:
    """服务管理器 - 自动监控和重启AI服务"""
    
    def __init__(self):
        # 服务配置：[服务名, 端口, 启动目录, 启动脚本]
        self.services = [
            {
                "name": "财务分析MCP",
                "port": 8001,
                "directory": "2_financial_ai_mcp",
                "script": "financial_mcp.py",
                "process": None
            },
            {
                "name": "成本预测MCP", 
                "port": 8002,
                "directory": "3_cost_prediction_mcp",
                "script": "cost_prediction_mcp.py",
                "process": None
            },
            {
                "name": "运维知识库MCP",
                "port": 8003,
                "directory": "4_operation_knowledge_mcp", 
                "script": "knowledge_mcp.py",
                "process": None
            },
            {
                "name": "人员效能MCP",
                "port": 8004,
                "directory": "5_hr_efficiency_mcp",
                "script": "zhishui_efficiency_mcp.py", 
                "process": None
            },
            {
                "name": "Agno协调中心",
                "port": 8000,
                "directory": "7_agno_coordinator",
                "script": "start_optimized.py",
                "process": None
            }
        ]
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.running = True
        
    def check_service_health(self, service):
        """检查单个服务的健康状态"""
        try:
            if service["port"] == 8000:
                # Agno协调中心使用健康检查端点
                response = requests.get(f"http://127.0.0.1:{service['port']}/health", timeout=3)
                return response.status_code == 200
            else:
                # MCP服务检查端口是否监听
                response = requests.get(f"http://127.0.0.1:{service['port']}", timeout=3)
                return True  # 只要能连接就认为健康
        except:
            return False
    
    def start_service(self, service):
        """启动单个服务"""
        try:
            service_dir = os.path.join(self.base_dir, service["directory"])
            if not os.path.exists(service_dir):
                print(f"❌ 服务目录不存在: {service_dir}")
                return False
                
            script_path = os.path.join(service_dir, service["script"])
            if not os.path.exists(script_path):
                print(f"❌ 服务脚本不存在: {script_path}")
                return False
            
            print(f"🚀 启动服务: {service['name']} (端口 {service['port']})")
            
            # 启动服务进程
            process = subprocess.Popen(
                [sys.executable, service["script"]],
                cwd=service_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            service["process"] = process
            
            # 等待服务启动
            time.sleep(5)
            
            # 检查服务是否成功启动
            if self.check_service_health(service):
                print(f"✅ {service['name']} 启动成功")
                return True
            else:
                print(f"❌ {service['name']} 启动失败")
                return False
                
        except Exception as e:
            print(f"❌ 启动 {service['name']} 时出错: {str(e)}")
            return False
    
    def stop_service(self, service):
        """停止单个服务"""
        if service["process"] and service["process"].poll() is None:
            try:
                if os.name == 'nt':
                    # Windows
                    service["process"].terminate()
                else:
                    # Linux/Mac
                    service["process"].terminate()
                service["process"].wait(timeout=5)
                print(f"🛑 {service['name']} 已停止")
            except:
                if os.name == 'nt':
                    service["process"].kill()
                else:
                    service["process"].kill()
                print(f"🔪 强制停止 {service['name']}")
    
    def get_service_status(self):
        """获取所有服务状态"""
        status = []
        healthy_count = 0
        
        for service in self.services:
            is_healthy = self.check_service_health(service)
            status.append({
                "name": service["name"],
                "port": service["port"], 
                "healthy": is_healthy
            })
            if is_healthy:
                healthy_count += 1
                
        return status, healthy_count
    
    def print_status_report(self):
        """打印服务状态报告"""
        print("\n" + "="*60)
        print(f"📊 四川智水AI服务状态报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        status, healthy_count = self.get_service_status()
        
        for service_status in status:
            status_icon = "✅" if service_status["healthy"] else "❌"
            print(f"{status_icon} {service_status['name']} - 端口 {service_status['port']}")
        
        print(f"\n📈 服务健康状态: {healthy_count}/{len(self.services)} 个服务正常运行")
        
        if healthy_count == len(self.services):
            print("🎉 所有服务运行正常！")
        else:
            print("⚠️  部分服务需要重启")
        
        print("="*60)
        return healthy_count == len(self.services)
    
    def restart_failed_services(self):
        """重启失败的服务"""
        print("\n🔄 检查并重启失败的服务...")
        
        for service in self.services:
            if not self.check_service_health(service):
                print(f"🔧 重启服务: {service['name']}")
                self.stop_service(service)
                time.sleep(2)
                self.start_service(service)
    
    def start_all_services(self):
        """启动所有服务"""
        print("🚀 启动所有服务...")
        
        for service in self.services:
            if not self.check_service_health(service):
                self.start_service(service)
                time.sleep(3)  # 错开启动时间，减少资源竞争
    
    def stop_all_services(self):
        """停止所有服务"""
        print("\n🛑 停止所有服务...")
        for service in self.services:
            self.stop_service(service)
    
    def monitor_loop(self):
        """监控循环"""
        print("👁️  开始监控服务状态...")
        
        while self.running:
            try:
                # 打印状态报告
                all_healthy = self.print_status_report()
                
                # 如果有服务失败，尝试重启
                if not all_healthy:
                    self.restart_failed_services()
                
                # 等待30秒后再次检查
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("\n⏹️  收到停止信号...")
                self.running = False
                break
            except Exception as e:
                print(f"❌ 监控过程中出错: {str(e)}")
                time.sleep(10)
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n⏹️  收到信号 {signum}，正在停止服务...")
        self.running = False
        self.stop_all_services()
        sys.exit(0)

def main():
    """主函数"""
    print("="*60)
    print("🎯 四川智水AI智慧管理解决方案 - 服务管理器")
    print("="*60)
    print("功能：自动监控和重启AI服务，解决内存不足导致的服务中断问题")
    print("操作：按 Ctrl+C 停止所有服务并退出")
    print("="*60)
    
    manager = ServiceManager()
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, manager.signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, manager.signal_handler)
    
    try:
        # 启动所有服务
        manager.start_all_services()
        
        # 等待所有服务启动完成
        time.sleep(10)
        
        # 开始监控
        manager.monitor_loop()
        
    except KeyboardInterrupt:
        print("\n⏹️  用户中断...")
    except Exception as e:
        print(f"❌ 程序出错: {str(e)}")
    finally:
        manager.stop_all_services()
        print("👋 服务管理器已退出")

if __name__ == "__main__":
    main()