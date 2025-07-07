@echo off
echo ========================================
echo Stable Audio Open Small 模型测试
echo ========================================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查是否在虚拟环境中
echo 检查虚拟环境...
if "%VIRTUAL_ENV%"=="" (
    echo 警告: 建议在虚拟环境中运行测试
    echo 如果遇到依赖问题，请先创建虚拟环境:
    echo python -m venv venv_stable_audio
    echo venv_stable_audio\Scripts\activate
    echo.
)

REM 安装依赖
echo 安装依赖包...
pip install stable-audio-tools einops psutil pytest requests

REM 检查安装结果
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo.
echo 依赖安装完成！
echo.

REM 运行简单测试
echo 开始运行简单测试...
python test_stable_audio_simple.py

echo.
echo 测试完成！
echo 生成的音频文件保存在 audio_output 目录中
echo.
pause 