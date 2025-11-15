#!/usr/bin/env python3
"""
智水人员效能管理MCP服务启动器
启动MCP服务器，提供员工效能评估和报告生成功能
"""

import sys
import logging
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from zhishui_efficiency_mcp import mcp, logger
except ImportError as e:
    print(f"❌ 导入MCP服务失败: {e}")
    sys.exit(1)

def main():
    """启动MCP服务器"""
    try:
        logger.info("🚀 启动智水人员效能管理MCP服务")
        logger.info(f"📁 服务目录: {current_dir}")
        logger.info("📋 可用工具:")
        logger.info("  - evaluate_employee_efficiency: 员工效能评估")
        logger.info("  - generate_efficiency_report: 效能报告生成")
        logger.info("🌐 MCP服务器正在启动...")
        
        # 启动MCP服务器
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("⏹️  收到停止信号，正在关闭服务...")
    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        sys.exit(1)
    finally:
        logger.info("✅ 智水人员效能管理MCP服务已关闭")

if __name__ == "__main__":
    main()