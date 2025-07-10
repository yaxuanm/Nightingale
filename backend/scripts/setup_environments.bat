@echo off
echo ========================================
echo 设置分环境部署 - 创建两个虚拟环境
echo ========================================

echo.
echo 1. 创建 Stable Audio 环境 (venv_stableaudio)...
python -m venv venv_stableaudio
call venv_stableaudio\Scripts\activate
pip install --upgrade pip
pip install -r requirements-stable-audio.txt
echo ✓ Stable Audio 环境设置完成

echo.
echo 2. 创建 Gemini API 环境 (venv_gemini)...
call venv_stableaudio\Scripts\deactivate
python -m venv venv_gemini
call venv_gemini\Scripts\activate
pip install --upgrade pip
pip install -r requirements-gemini-utf8.txt
echo ✓ Gemini API 环境设置完成

echo.
echo ========================================
echo 环境设置完成！
echo ========================================
echo.
echo 使用方法：
echo 1. 启动 Stable Audio 服务: start_stable_audio.bat
echo 2. 启动 Gemini API 服务: start_gemini.bat
echo.
echo 服务地址：
echo - Stable Audio: http://127.0.0.1:8001
echo - Gemini API: http://127.0.0.1:8000
echo ========================================

pause 