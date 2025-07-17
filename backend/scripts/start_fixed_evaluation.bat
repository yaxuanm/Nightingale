@echo off
echo ========================================
echo Nightingale 固定音频评测服务
echo ========================================
echo.

echo 1. 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误：未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo.
echo 2. 检查音频文件...
if not exist "audio_test_output\fixed_web\audio_files\*.wav" (
    echo 警告：未找到音频文件
    echo 请先运行 prepare_fixed_audio_for_web.py 生成音频文件
    echo.
    set /p choice="是否继续启动服务？(y/n): "
    if /i not "%choice%"=="y" (
        pause
        exit /b 1
    )
)

echo.
echo 3. 启动固定音频评测服务...
echo 服务将在 http://127.0.0.1:8013/ 启动
echo 使用预先准备好的30个固定音频文件
echo 按 Ctrl+C 停止服务
echo.
python scripts/fixed_web_service.py

pause 