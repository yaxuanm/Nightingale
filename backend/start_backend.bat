@echo off
echo === Nightingale 后端启动脚本 ===

REM 检查是否在正确的目录
if not exist "venv_api" (
    echo 错误: 请在 backend 目录下运行此脚本
    pause
    exit /b 1
)

echo 正在激活虚拟环境...
call venv_api\Scripts\activate.bat

echo 启动 FastAPI 服务...
echo 服务地址: http://localhost:8000/
echo API 文档: http://localhost:8000/docs
echo 按 Ctrl+C 停止服务
echo.

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

pause 