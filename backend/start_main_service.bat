@echo off
echo ========================================
echo 启动 Main 服务 (Worker + 拼接逻辑)
echo ========================================
echo.

REM 检查虚拟环境是否存在
if not exist "venv_stableaudio" (
    echo ❌ 错误: venv_stableaudio 虚拟环境不存在
    echo 请先运行: py -3.11 -m venv venv_stableaudio
    pause
    exit /b 1
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv_stableaudio\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ 错误: 激活虚拟环境失败
    pause
    exit /b 1
)

REM 检查 .env 文件
if not exist ".env" (
    echo ⚠️  警告: .env 文件不存在
    echo 请复制 env.example 到 .env 并配置 API keys
    echo.
)

REM 检查环境变量
echo 🔧 检查环境变量...
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('STABILITY_API_KEY:', '已配置' if os.getenv('STABILITY_API_KEY') else '未配置')"

echo.
echo 🚀 启动 Main 服务 (Worker + 拼接逻辑)...
echo 📍 服务地址: http://127.0.0.1:8000
echo 📍 健康检查: http://127.0.0.1:8000/
echo.
echo ✅ 所有mode都会使用worker和拼接逻辑
echo ✅ 生成20秒音频，支持无缝拼接
echo.

REM 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause 