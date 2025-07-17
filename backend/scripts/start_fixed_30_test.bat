@echo off
echo ========================================
echo Nightingale 固定30个测试启动脚本
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
echo 2. 启动固定测试Web服务...
echo 服务将在 http://127.0.0.1:8012/ 启动
echo 使用固定的30个prompt，无需随机生成
echo 按 Ctrl+C 停止服务
echo.
python scripts/fixed_batch_test_web.py

pause 