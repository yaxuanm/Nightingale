@echo off
echo 修复 Python 3.12 兼容性问题...
echo.

echo 正在修复 venv_stableaudio 环境...
cd /d "%~dp0.."
call venv_stableaudio\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade pkg_resources
echo.

echo 正在修复 venv_gemini 环境...
call venv_gemini\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade pkg_resources
echo.

echo 正在修复 venv_audio 环境...
call venv_audio\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade pkg_resources
echo.

echo 重新安装依赖包...
echo.

echo 重新安装 venv_stableaudio 依赖...
call venv_stableaudio\Scripts\activate.bat
pip install -r requirements-stable-audio.txt --no-cache-dir
echo.

echo 重新安装 venv_gemini 依赖...
call venv_gemini\Scripts\activate.bat
pip install -r requirements-gemini-utf8.txt --no-cache-dir
echo.

echo 重新安装 venv_audio 依赖...
call venv_audio\Scripts\activate.bat
pip install -r requirements-audio.txt --no-cache-dir
echo.

echo 修复完成！
echo 现在可以重新运行 setup_environments.bat 或 start_clean.bat
pause 