@echo off
chcp 65001
echo ========================================
echo Python 3.13 兼容安装脚本
echo ========================================
echo.

set ENV_NAME=%1
set REQUIREMENTS_FILE=%2

if "%ENV_NAME%"=="" (
    echo Error: Environment name not provided
    echo Usage: install_python313.bat [env_name] [requirements_file]
    exit /b 1
)

if "%REQUIREMENTS_FILE%"=="" (
    echo Error: Requirements file not provided
    echo Usage: install_python313.bat [env_name] [requirements_file]
    exit /b 1
)

echo Installing dependencies for %ENV_NAME% (Python 3.13 compatible)...
echo Requirements file: %REQUIREMENTS_FILE%
echo.

echo 1. Creating/updating virtual environment...
if exist "%ENV_NAME%" (
    echo Removing existing %ENV_NAME% environment...
    rmdir /s /q %ENV_NAME%
)

python -m venv %ENV_NAME%
echo ✓ Virtual environment created
echo.

echo 2. Activating environment and upgrading tools...
call %ENV_NAME%\Scripts\activate.bat

echo Upgrading pip, setuptools, wheel...
python -m pip install --upgrade pip setuptools wheel --no-cache-dir

echo 3. Installing dependencies with Python 3.13 compatible versions...
echo Installing from %REQUIREMENTS_FILE%...
pip install -r %REQUIREMENTS_FILE% --no-cache-dir --force-reinstall

call %ENV_NAME%\Scripts\deactivate.bat

echo.
echo ========================================
echo ✓ %ENV_NAME% environment setup completed!
echo ========================================
echo.
echo Environment: %ENV_NAME%
echo Requirements: %REQUIREMENTS_FILE%
echo Python Version: 3.13 Compatible
echo.
pause 