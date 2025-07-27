@echo off
echo ========================================
echo Setting up environment - Creating virtual environments
echo ========================================

echo.
echo 1. Creating Stable Audio environment (venv_stableaudio)...
python -m venv venv_stableaudio
if %errorlevel% neq 0 (
    echo Error: Failed to create venv_stableaudio
    pause
    exit /b 1
)

call venv_stableaudio\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Error: Failed to activate venv_stableaudio
    pause
    exit /b 1
)

python -m pip install --upgrade pip
python -m pip install --upgrade setuptools wheel
pip install -r requirements-stable-audio.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install requirements-stable-audio.txt
    pause
    exit /b 1
)

echo ✓ Stable Audio environment setup completed

echo.
echo 2. Creating Gemini API environment (venv_gemini)...
call venv_stableaudio\Scripts\deactivate.bat

python -m venv venv_gemini
if %errorlevel% neq 0 (
    echo Error: Failed to create venv_gemini
    pause
    exit /b 1
)

call venv_gemini\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Error: Failed to activate venv_gemini
    pause
    exit /b 1
)

python -m pip install --upgrade pip
pip install -r requirements-gemini-utf8.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install requirements-gemini-utf8.txt
    pause
    exit /b 1
)

echo ✓ Gemini API environment setup completed

echo.
echo ========================================
echo Environment setup completed!
echo ========================================
echo.
echo Usage:
echo 1. Start Stable Audio service: start_stable_audio.bat
echo 2. Start Gemini API service: start_gemini.bat
echo.
echo Service URLs:
echo - Stable Audio: http://127.0.0.1:8001
echo - Gemini API: http://127.0.0.1:8000
echo ========================================

pause 