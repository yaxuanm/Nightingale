@echo off
chcp 65001
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
echo 6. Exit
echo.

set /p choice="Please select (1-6): "

if "%choice%"=="1" goto start_gemini
if "%choice%"=="2" goto start_stable_audio
if "%choice%"=="3" goto start_frontend
if "%choice%"=="4" goto start_all
if "%choice%"=="5" goto setup_env
if "%choice%"=="6" goto exit
goto invalid_choice

:start_gemini
echo.
echo Starting Gemini API Service...
cd backend
echo Current directory: %CD%
echo Checking for venv_gemini\Scripts\activate.bat...
if exist "venv_gemini\Scripts\activate.bat" (
    echo Found venv_gemini environment
    start cmd /k "cd /d %CD% && call venv_gemini\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    echo Gemini API Service started in new window (http://127.0.0.1:8000)
) else (
    echo Error: venv_gemini environment not found at %CD%\venv_gemini\Scripts\activate.bat
    echo Please run option 5 to setup environment first
)
cd ..
goto end

:start_stable_audio
echo.
echo Starting Stable Audio Service...
cd backend
echo Current directory: %CD%
echo Checking for venv_stableaudio\Scripts\activate.bat...
if exist "venv_stableaudio\Scripts\activate.bat" (
    echo Found venv_stableaudio environment
    start cmd /k "cd /d %CD% && call venv_stableaudio\Scripts\activate.bat && python -m uvicorn app.main_stable_audio:app --host 0.0.0.0 --port 8001"
    echo Stable Audio Service started in new window (http://127.0.0.1:8001)
) else (
    echo Error: venv_stableaudio environment not found at %CD%\venv_stableaudio\Scripts\activate.bat
    echo Please run option 5 to setup environment first
)
cd ..
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

REM Gemini API Service
cd backend
echo Current directory: %CD%
echo Checking for venv_gemini\Scripts\activate.bat...
if exist "venv_gemini\Scripts\activate.bat" (
    echo Found venv_gemini environment
    start cmd /k "cd /d %CD% && call venv_gemini\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    echo Gemini API Service started in new window (http://127.0.0.1:8000)
) else (
    echo Warning: venv_gemini environment not found at %CD%\venv_gemini\Scripts\activate.bat, skipping Gemini service
)
cd ..

REM Stable Audio Service
cd backend
echo Current directory: %CD%
echo Checking for venv_stableaudio\Scripts\activate.bat...
if exist "venv_stableaudio\Scripts\activate.bat" (
    echo Found venv_stableaudio environment
    start cmd /k "cd /d %CD% && call venv_stableaudio\Scripts\activate.bat && python -m uvicorn app.main_stable_audio:app --host 0.0.0.0 --port 8001"
    echo Stable Audio Service started in new window (http://127.0.0.1:8001)
) else (
    echo Warning: venv_stableaudio environment not found at %CD%\venv_stableaudio\Scripts\activate.bat, skipping Stable Audio service
)
cd ..

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
echo 1. Setting up backend environment...
cd backend
if exist "setup_environments.bat" (
    call setup_environments.bat
    echo Backend environment setup completed
) else (
    echo Error: setup_environments.bat not found
)
cd ..

echo.
echo 2. Setting up frontend environment...
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
echo Environment setup completed!
echo Now you can run option 4 to start all services
goto end

:invalid_choice
echo Invalid choice, please try again
goto end

:end
echo.
echo Press any key to return to main menu...
pause >nul
goto start

:exit
echo Exiting startup script 