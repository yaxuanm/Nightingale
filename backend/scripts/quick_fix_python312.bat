@echo off
echo 快速修复 Python 3.12 兼容性问题...
echo.

echo 正在升级 pip 和 setuptools...
python -m pip install --upgrade pip setuptools wheel

echo.
echo 正在清理并重新安装依赖包...
echo.

echo 修复 venv_stableaudio...
call venv_stableaudio\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements-stable-audio.txt --no-cache-dir --force-reinstall
call venv_stableaudio\Scripts\deactivate.bat

echo.
echo 修复 venv_gemini...
call venv_gemini\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements-gemini-utf8.txt --no-cache-dir --force-reinstall
call venv_gemini\Scripts\deactivate.bat

echo.
echo 修复 venv_audio...
call venv_audio\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements-audio.txt --no-cache-dir --force-reinstall
call venv_audio\Scripts\deactivate.bat

echo.
echo 修复完成！现在可以重新运行环境设置或启动服务
pause 