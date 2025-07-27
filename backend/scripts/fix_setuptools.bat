@echo off
echo ========================================
echo 修复 setuptools 问题
echo ========================================

echo.
echo 正在升级 setuptools...

cd backend

echo 1. 激活 Stable Audio 环境...
call venv_stableaudio\Scripts\activate.bat
python -m pip install --upgrade setuptools wheel
python -m pip install --upgrade pip

echo 2. 激活 Gemini 环境...
call venv_stableaudio\Scripts\deactivate.bat
call venv_gemini\Scripts\activate.bat
python -m pip install --upgrade setuptools wheel
python -m pip install --upgrade pip

echo 3. 重新安装依赖...
echo 安装 Stable Audio 依赖...
call venv_stableaudio\Scripts\activate.bat
pip install -r requirements-stable-audio.txt

echo 安装 Gemini 依赖...
call venv_stableaudio\Scripts\deactivate.bat
call venv_gemini\Scripts\activate.bat
pip install -r requirements-gemini-utf8.txt

echo.
echo ========================================
echo ✓ setuptools 问题修复完成！
echo ========================================
echo.
echo 现在可以正常启动服务了
pause 