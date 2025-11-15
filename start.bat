@echo off
chcp 65001 >nul
echo.
echo ================================================================
echo                四川智水AI智慧管理解决方案
echo                     快速启动脚本
echo ================================================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8或更高版本
    echo 📥 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo.

:: 检查是否首次运行
if not exist ".env" (
    echo 🔧 首次运行，正在初始化环境...
    python deploy.py --install
    if errorlevel 1 (
        echo ❌ 环境初始化失败
        pause
        exit /b 1
    )
    echo.
)

:: 启动系统
echo 🚀 正在启动四川智水AI智慧管理解决方案...
echo.
echo 📌 启动顺序:
echo    1. 项目信息整合服务 (端口: 8001)
echo    2. Agno智能体协调中心 (端口: 8006)
echo    3. 前端界面 (端口: 8501)
echo.
echo ⏳ 请稍候，系统正在启动中...
echo.

python deploy.py --start

echo.
echo 👋 感谢使用四川智水AI智慧管理解决方案！
pause