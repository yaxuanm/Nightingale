@echo off
echo ========================================
echo 重新安装 Stable Audio 虚拟环境 (Python 3.11)
echo ========================================
echo.

REM 检查 Python 版本
echo 检查 Python 版本...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请确保 Python 已安装并添加到 PATH
    pause
    exit /b 1
)

echo.
echo 当前 Python 版本已确认
echo.

REM 停止可能运行的服务
echo 停止可能运行的服务...
taskkill /f /im python.exe 2>nul
taskkill /f /im uvicorn.exe 2>nul

REM 删除旧的虚拟环境
echo 删除旧的虚拟环境...
if exist "venv_audio" (
    echo 删除 venv_audio 目录...
    rmdir /s /q "venv_audio"
    echo 旧环境已删除
) else (
    echo venv_audio 目录不存在，跳过删除
)

echo.
echo 创建新的虚拟环境...
python -m venv venv_audio
if %errorlevel% neq 0 (
    echo 错误: 创建虚拟环境失败
    pause
    exit /b 1
)

echo 激活虚拟环境...
call venv_audio\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo 错误: 激活虚拟环境失败
    pause
    exit /b 1
)

echo.
echo 升级 pip...
python -m pip install --upgrade pip

echo.
echo 安装 Stable Audio 依赖...
echo 正在安装核心依赖...

REM 安装核心依赖
pip install protobuf==3.19.6
pip install numpy==1.23.5
pip install fastapi==0.116.0
pip install uvicorn==0.35.0

echo 正在安装音频处理依赖...
pip install stable-audio-tools==0.0.19
pip install pydub==0.25.1
pip install soundfile==0.13.1
pip install librosa==0.11.0

echo 正在安装 AI/ML 依赖...
pip install torch==2.7.1 torchaudio==2.7.1 torchvision==0.22.1
pip install transformers==4.53.1

echo 正在安装其他依赖...
pip install supabase==2.16.0
pip install python-dotenv==1.1.1
pip install requests==2.32.4
pip install pillow==11.3.0
pip install tqdm==4.67.1

echo.
echo 安装额外的依赖包...
pip install accelerate==1.8.1
pip install huggingface-hub==0.33.2
pip install gradio==5.35.0
pip install aiofiles==24.1.0
pip install aiohttp==3.12.13

echo.
echo 验证安装...
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python -c "import stable_audio_tools; print('Stable Audio Tools imported successfully')"
python -c "import fastapi; print('FastAPI imported successfully')"

echo.
echo ========================================
echo Stable Audio 环境重装完成！
echo ========================================
echo.
echo 使用方法:
echo 1. 激活环境: venv_audio\Scripts\activate.bat
echo 2. 启动服务: python app/main_stable_audio.py
echo.
pause 