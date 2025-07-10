@echo off
echo ========================================
echo 启动 Gemini API 服务 (端口 8000)
echo ========================================

REM 激活 Gemini 虚拟环境
call venv_gemini\Scripts\activate

REM 启动服务
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

pause 