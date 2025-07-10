@echo off
echo ========================================
echo Nightingale 项目环境清理工具
echo ========================================
echo.

echo 正在检查当前环境状态...
echo.

echo 1. 检查虚拟环境...
if exist ".venv" (
    echo   - 发现根目录 .venv 环境
) else (
    echo   - 根目录无 .venv 环境
)

if exist "venv_gemini" (
    echo   - 发现根目录 venv_gemini 环境
) else (
    echo   - 根目录无 venv_gemini 环境
)

if exist "backend\venv_api" (
    echo   - 发现 backend\venv_api 环境
) else (
    echo   - backend 目录无 venv_api 环境
)

if exist "backend\venv_audio" (
    echo   - 发现 backend\venv_audio 环境
) else (
    echo   - backend 目录无 venv_audio 环境
)

if exist "backend\venv311" (
    echo   - 发现 backend\venv311 环境
) else (
    echo   - backend 目录无 venv311 环境
)

echo.
echo 2. 检查启动脚本...
if exist "start_all.bat" (
    echo   - 发现根目录 start_all.bat
) else (
    echo   - 根目录无 start_all.bat
)

if exist "backend\start_stable_audio.bat" (
    echo   - 发现 backend\start_stable_audio.bat
) else (
    echo   - backend 目录无 start_stable_audio.bat
)

if exist "backend\start_gemini.bat" (
    echo   - 发现 backend\start_gemini.bat
) else (
    echo   - backend 目录无 start_gemini.bat
)

if exist "backend\start_backend.bat" (
    echo   - 发现 backend\start_backend.bat
) else (
    echo   - backend 目录无 start_backend.bat
)

echo.
echo ========================================
echo 清理选项:
echo ========================================
echo 1. 清理所有虚拟环境 (保留项目文件)
echo 2. 清理重复的启动脚本
echo 3. 创建标准化的环境结构
echo 4. 显示环境使用情况
echo 5. 退出
echo.

set /p choice="请选择操作 (1-5): "

if "%choice%"=="1" goto cleanup_envs
if "%choice%"=="2" goto cleanup_scripts
if "%choice%"=="3" goto create_standard
if "%choice%"=="4" goto show_usage
if "%choice%"=="5" goto exit
goto invalid_choice

:cleanup_envs
echo.
echo 正在清理虚拟环境...
echo 注意: 这将删除所有虚拟环境，但保留项目文件
echo.
set /p confirm="确认删除所有虚拟环境? (y/N): "
if /i "%confirm%"=="y" (
    echo 删除根目录虚拟环境...
    if exist ".venv" rmdir /s /q ".venv"
    if exist "venv_gemini" rmdir /s /q "venv_gemini"
    
    echo 删除 backend 虚拟环境...
    if exist "backend\venv_api" rmdir /s /q "backend\venv_api"
    if exist "backend\venv_audio" rmdir /s /q "backend\venv_audio"
    if exist "backend\venv311" rmdir /s /q "backend\venv311"
    
    echo 虚拟环境清理完成！
) else (
    echo 取消清理操作
)
goto end

:cleanup_scripts
echo.
echo 正在清理重复的启动脚本...
echo.
echo 建议保留的脚本:
echo - backend\start_gemini.bat (主要服务)
echo - backend\start_stable_audio.bat (音频服务)
echo - start_all.bat (统一启动)
echo.
echo 建议删除的脚本:
echo - backend\start_backend.bat (功能重复)
echo - 其他重复的启动脚本
echo.
set /p confirm="确认清理重复脚本? (y/N): "
if /i "%confirm%"=="y" (
    if exist "backend\start_backend.bat" del "backend\start_backend.bat"
    echo 重复脚本清理完成！
) else (
    echo 取消清理操作
)
goto end

:create_standard
echo.
echo 创建标准化的环境结构...
echo.
echo 建议的环境结构:
echo backend/
echo ├── venv_stableaudio/     # Stable Audio 环境
echo ├── venv_gemini/         # Gemini API 环境
echo ├── start_stable_audio.bat
echo ├── start_gemini.bat
echo └── setup_environments.bat
echo.
set /p confirm="创建标准化环境? (y/N): "
if /i "%confirm%"=="y" (
    echo 请运行 backend\setup_environments.bat 来创建标准化环境
    echo 这将创建两个独立的虚拟环境
) else (
    echo 取消操作
)
goto end

:show_usage
echo.
echo ========================================
echo 环境使用情况说明
echo ========================================
echo.
echo 当前推荐的环境结构:
echo.
echo 1. Stable Audio 环境 (venv_stableaudio)
echo    - 用途: AI音频生成
echo    - 端口: 8001
echo    - 启动: backend\start_stable_audio.bat
echo.
echo 2. Gemini API 环境 (venv_gemini)
echo    - 用途: Google AI 服务
echo    - 端口: 8000
echo    - 启动: backend\start_gemini.bat
echo.
echo 3. 前端环境
echo    - 项目: ambiance-weaver-react
echo    - 启动: npm start
echo.
echo 建议:
echo - 删除不需要的虚拟环境以节省空间
echo - 使用 setup_environments.bat 重新创建标准化环境
echo - 保留必要的启动脚本，删除重复的
echo.
goto end

:invalid_choice
echo 无效选择，请重新输入
goto end

:end
echo.
echo 清理完成！按任意键退出...
pause >nul

:exit 