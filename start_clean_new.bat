@echo off
chcp 65001 >nul
cls

:menu
echo ========================================
echo Nightingale Project Startup Script
echo ========================================
echo.
echo Select service to start:
echo.
echo 1. Start Gemini API Service (Port 8000)
echo 2. Start Stable Audio Service (Port 8001)
echo 3. Start Frontend React App
echo 4. Start All Services (Recommended)
echo 5. Setup Environment (First Time)
echo 6. Test Gemini Environment
echo 7. Exit
echo.

set /p choice="Please select (1-7): "

if "%choice%"=="1" goto start_gemini
if "%choice%"=="2" goto start_stable_audio
if "%choice%"=="3" goto start_frontend
if "%choice%"=="4" goto start_all
if "%choice%"=="5" goto setup_env
if "%choice%"=="6" goto test_gemini
if "%choice%"=="7" goto exit
goto invalid_choice

:start_gemini
echo.
echo Starting Gemini API Service...
if exist "backend\venv_gemini\Scripts\Activate.ps1" (
    echo Found venv_gemini environment (powershell)
    echo Starting Gemini API Service in new window...
    start powershell -NoExit -Command "cd '%CD%\backend'; .\venv_gemini\Scripts\Activate.ps1; $env:GEMINI_API_KEY='%GEMINI_API_KEY%'; $env:GOOGLE_API_KEY='%GOOGLE_API_KEY%'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    echo Gemini API Service started in new window (http://127.0.0.1:8000)
) else (
    echo Error: venv_gemini environment not found
    echo Please run option 5 to setup environment first
)
goto end

:start_stable_audio
echo.
echo Starting Stable Audio Service...
if exist "backend\venv_stableaudio\Scripts\Activate.ps1" (
    echo Found venv_stableaudio environment (powershell)
    start powershell -NoExit -Command "cd '%CD%\backend'; .\venv_stableaudio\Scripts\Activate.ps1; $env:HF_TOKEN='%HF_TOKEN%'; $env:HUGGING_FACE_HUB_TOKEN='%HF_TOKEN%'; python -m uvicorn app.main_stable_audio:app --host 0.0.0.0 --port 8001 --reload"
    echo Stable Audio Service started in new window (http://127.0.0.1:8001)
) else (
    echo Error: venv_stableaudio environment not found
    echo Please run option 5 to setup environment first
)
goto end

:start_frontend
echo.
echo Starting Frontend React App...
cd ambiance-weaver-react
if exist "node_modules" (
    start cmd /k "npm start"
    echo Frontend App started in new window (http://localhost:3000)
) else (
    echo Error: node_modules not found
    echo Please run npm install first
)
cd ..
goto end

:start_all
echo.
echo Starting All Services...
echo.

REM Check if required environment variables are set
if "%GEMINI_API_KEY%"=="" (
    echo Warning: GEMINI_API_KEY environment variable not set
    echo Please set it before starting Gemini service
)
if "%HF_TOKEN%"=="" (
    echo Warning: HF_TOKEN environment variable not set
    echo Please set it before starting Stable Audio service
)

REM Gemini API Service
if exist "backend\venv_gemini\Scripts\Activate.ps1" (
    echo Found venv_gemini environment (powershell)
    echo Starting Gemini API Service with PowerShell...
    start powershell -NoExit -Command "cd '%CD%\backend'; .\venv_gemini\Scripts\Activate.ps1; $env:GEMINI_API_KEY='%GEMINI_API_KEY%'; $env:GOOGLE_API_KEY='%GOOGLE_API_KEY%'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    echo Gemini API Service started in new window (http://127.0.0.1:8000)
) else (
    echo Warning: venv_gemini environment not found, skipping Gemini service
)

REM Stable Audio Service
if exist "backend\venv_stableaudio\Scripts\Activate.ps1" (
    echo Found venv_stableaudio environment (powershell)
    start powershell -NoExit -Command "cd '%CD%\backend'; .\venv_stableaudio\Scripts\Activate.ps1; $env:HF_TOKEN='%HF_TOKEN%'; $env:HUGGING_FACE_HUB_TOKEN='%HF_TOKEN%'; python -m uvicorn app.main_stable_audio:app --host 0.0.0.0 --port 8001 --reload"
    echo Stable Audio Service started in new window (http://127.0.0.1:8001)
) else (
    echo Warning: venv_stableaudio environment not found, skipping Stable Audio service
)

REM Frontend React App
cd ambiance-weaver-react
if exist "node_modules" (
    start cmd /k "npm start"
    echo Frontend App started in new window (http://localhost:3000)
) else (
    echo Warning: node_modules not found, please run npm install first
)
cd ..

echo.
echo All services started in new windows!
echo Frontend: http://localhost:3000
echo Gemini API: http://127.0.0.1:8000
echo Stable Audio: http://127.0.0.1:8001
goto end

:setup_env
echo.
echo Setting up environment...
echo.

echo Creating virtual environments in backend directory...
cd backend

if not exist "venv_gemini" (
    echo Creating venv_gemini...
    py -3.11 -m venv venv_gemini
)

if not exist "venv_stableaudio" (
    echo Creating venv_stableaudio...
    py -3.11 -m venv venv_stableaudio
)

echo.
echo Upgrading tools in virtual environments...
if exist "venv_gemini\Scripts\Activate.ps1" (
    echo Upgrading Gemini environment tools...
    powershell -Command "cd '%CD%'; .\venv_gemini\Scripts\Activate.ps1; python -m pip install --upgrade pip setuptools wheel"
    echo Installing Gemini environment dependencies...
    powershell -Command "cd '%CD%'; .\venv_gemini\Scripts\Activate.ps1; pip install -r requirements-gemini-working.txt"
    echo Gemini environment updated
)

if exist "venv_stableaudio\Scripts\activate.bat" (
    echo Upgrading Stable Audio environment tools...
    call venv_stableaudio\Scripts\activate.bat
    python -m pip install --upgrade pip setuptools wheel
    echo Installing Stable Audio environment dependencies...
    pip install -r requirements-stable-audio.txt
    call venv_stableaudio\Scripts\deactivate.bat
    echo Stable Audio environment updated
)

cd ..

echo.
echo Setting up frontend environment...
cd ambiance-weaver-react
if exist "package.json" (
    echo Installing frontend dependencies...
    npm install
    echo Frontend environment setup completed
) else (
    echo Error: package.json not found
)
cd ..

echo.
echo ========================================
echo Environment setup completed!
echo ========================================
echo.
echo Virtual environments created and updated
echo Now you can run option 4 to start all services
echo.
echo IMPORTANT: Set environment variables before starting services:
echo set GEMINI_API_KEY=your_gemini_api_key
echo set HF_TOKEN=your_huggingface_token
goto end

:test_gemini
echo.
echo Testing Gemini Environment...
cd backend
if exist "test_gemini_startup.ps1" (
    powershell -ExecutionPolicy Bypass -File "test_gemini_startup.ps1"
) else (
    echo Error: test_gemini_startup.ps1 not found
)
cd ..
goto end

:invalid_choice
echo Invalid choice, please try again
goto end

:end
echo.
echo Press any key to return to main menu...
pause >nul
goto menu

:exit
echo Exiting startup script