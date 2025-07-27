@echo off
chcp 65001
echo ========================================
echo Nightingale 简化启动脚本
echo ========================================
echo.

echo 选择操作:
echo.
echo 1. 检查当前包版本 (推荐先运行)
echo 2. 修复 Python 3.13 兼容性问题
echo 3. 修复 requirements 版本
echo 4. 启动所有服务
echo 5. 退出
echo.

set /p choice="请选择 (1-5): "

if "%choice%"=="1" goto check_versions
if "%choice%"=="2" goto fix_compatibility
if "%choice%"=="3" goto fix_requirements
if "%choice%"=="4" goto start_all
if "%choice%"=="5" goto exit
goto invalid_choice

:check_versions
echo.
echo 检查当前包版本...
cd backend
if exist "scripts\check_current_versions.bat" (
    call scripts\check_current_versions.bat
) else (
    echo 错误: 检查脚本不存在
)
cd ..
echo.
echo 检查完成！请查看生成的文件了解详情
pause
goto start

:fix_compatibility
echo.
echo 修复 Python 3.13 兼容性问题...
cd backend
if exist "scripts\compatibility_only_fix.bat" (
    call scripts\compatibility_only_fix.bat
) else (
    echo 错误: 修复脚本不存在
)
cd ..
echo.
echo 兼容性修复完成！
pause
goto start

:fix_requirements
echo.
echo 修复 requirements 版本...
cd backend
if exist "scripts\fix_requirements_versions.bat" (
    call scripts\fix_requirements_versions.bat
) else (
    echo 错误: 修复脚本不存在
)
cd ..
echo.
echo Requirements 修复完成！
pause
goto start

:start_all
echo.
echo 启动所有服务...
cd backend

REM 启动 Gemini API Service
if exist "venv_gemini\Scripts\activate.bat" (
    start cmd /k "cd /d %CD% && call venv_gemini\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    echo Gemini API Service 已启动 (http://127.0.0.1:8000)
) else (
    echo 警告: venv_gemini 环境不存在
)

REM 启动 Stable Audio Service
if exist "venv_stableaudio\Scripts\activate.bat" (
    start cmd /k "cd /d %CD% && call venv_stableaudio\Scripts\activate.bat && python -m uvicorn app.main_stable_audio:app --host 0.0.0.0 --port 8001"
    echo Stable Audio Service 已启动 (http://127.0.0.1:8001)
) else (
    echo 警告: venv_stableaudio 环境不存在
)

cd ..

REM 启动前端
cd ambiance-weaver-react
if exist "node_modules" (
    start cmd /k "npm start"
    echo 前端应用已启动 (http://localhost:3000)
) else (
    echo 警告: node_modules 不存在
)
cd ..

echo.
echo 所有服务已启动！
echo 前端: http://localhost:3000
echo Gemini API: http://127.0.0.1:8000
echo Stable Audio: http://127.0.0.1:8001
pause
goto start

:invalid_choice
echo 无效选择，请重新输入
pause
goto start

:exit
echo 退出启动脚本 