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
echo 6. Fix Python 3.13 Compatibility Issues
echo 7. Test Python 3.13 Compatibility (Safe)
echo 8. Test Single Package Installation
echo 9. Exit
echo.

set /p choice="Please select (1-9): "

if "%choice%"=="1" goto start_gemini
if "%choice%"=="2" goto start_stable_audio
if "%choice%"=="3" goto start_frontend
if "%choice%"=="4" goto start_all
if "%choice%"=="5" goto setup_env
if "%choice%"=="6" goto fix_python313
if "%choice%"=="7" goto test_compatibility_safe
if "%choice%"=="8" goto test_single_package
if "%choice%"=="9" goto exit
goto invalid_choice

:start_gemini
echo.
echo Starting Gemini API Service...
cd backend
echo Current directory: %CD%
echo Checking for venv_gemini environment...
if exist "venv_gemini\Scripts\activate.bat" (
    echo Found venv_gemini environment (batch)
    start cmd /k "cd /d %CD% && call venv_gemini\Scripts\activate.bat && set GEMINI_API_KEY=AIzaSyAqeUjWY_u59F_Tbxm3FfE9JTJqoGMdZAI && set GOOGLE_API_KEY=AIzaSyAqeUjWY_u59F_Tbxm3FfE9JTJqoGMdZAI && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    echo Gemini API Service started in new window (http://127.0.0.1:8000)
    echo API Keys have been set automatically
) else if exist "venv_gemini\Scripts\activate.ps1" (
    echo Found venv_gemini environment (powershell)
    start powershell -Command "cd '%CD%'; .\venv_gemini\Scripts\Activate.ps1; $env:GEMINI_API_KEY='AIzaSyAqeUjWY_u59F_Tbxm3FfE9JTJqoGMdZAI'; $env:GOOGLE_API_KEY='AIzaSyAqeUjWY_u59F_Tbxm3FfE9JTJqoGMdZAI'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    echo Gemini API Service started in new window (http://127.0.0.1:8000)
    echo API Keys have been set automatically
) else (
    echo Error: venv_gemini environment not found at %CD%\venv_gemini\Scripts\
    echo Please run option 5 to setup environment first
)
cd ..
goto end

:start_stable_audio
echo.
echo Starting Stable Audio Service...
cd backend
echo Current directory: %CD%
echo Checking for venv_stableaudio environment...
if exist "venv_stableaudio\Scripts\activate.bat" (
    echo Found venv_stableaudio environment (batch)
    start cmd /k "cd /d %CD% && call venv_stableaudio\Scripts\activate.bat && python app/main_stable_audio.py"
    echo Stable Audio Service started in new window (http://127.0.0.1:8001)
    echo Environment variables will be loaded from .env file
) else if exist "venv_stableaudio\Scripts\activate.ps1" (
    echo Found venv_stableaudio environment (powershell)
    start powershell -Command "cd '%CD%'; .\venv_stableaudio\Scripts\Activate.ps1; python app/main_stable_audio.py"
    echo Stable Audio Service started in new window (http://127.0.0.1:8001)
    echo Environment variables will be loaded from .env file
) else (
    echo Error: venv_stableaudio environment not found at %CD%\venv_stableaudio\Scripts\
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
echo Checking for venv_gemini environment...
if exist "venv_gemini\Scripts\activate.bat" (
    echo Found venv_gemini environment (batch)
    start cmd /k "cd /d %CD% && call venv_gemini\Scripts\activate.bat && set GEMINI_API_KEY=AIzaSyAqeUjWY_u59F_Tbxm3FfE9JTJqoGMdZAI && set GOOGLE_API_KEY=AIzaSyAqeUjWY_u59F_Tbxm3FfE9JTJqoGMdZAI && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    echo Gemini API Service started in new window (http://127.0.0.1:8000)
    echo API Keys have been set automatically
) else if exist "venv_gemini\Scripts\activate.ps1" (
    echo Found venv_gemini environment (powershell)
    start powershell -Command "cd '%CD%'; .\venv_gemini\Scripts\Activate.ps1; $env:GEMINI_API_KEY='AIzaSyAqeUjWY_u59F_Tbxm3FfE9JTJqoGMdZAI'; $env:GOOGLE_API_KEY='AIzaSyAqeUjWY_u59F_Tbxm3FfE9JTJqoGMdZAI'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    echo Gemini API Service started in new window (http://127.0.0.1:8000)
    echo API Keys have been set automatically
) else (
    echo Warning: venv_gemini environment not found at %CD%\venv_gemini\Scripts\, skipping Gemini service
)
cd ..

REM Stable Audio Service
cd backend
echo Current directory: %CD%
echo Checking for venv_stableaudio\Scripts\activate.bat...
if exist "venv_stableaudio\Scripts\activate.bat" (
    echo Found venv_stableaudio environment
    start cmd /k "cd /d %CD% && call venv_stableaudio\Scripts\activate.bat && python app/main_stable_audio.py"
    echo Stable Audio Service started in new window (http://127.0.0.1:8001)
    echo Environment variables will be loaded from .env file
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
echo Setting up environment (preserving existing virtual environments)...
echo.
echo 1. Applying compatibility fix to existing environments...
cd backend

echo Creating compatibility patch...
(
echo import sys
echo import os
echo.
echo # Python 3.12+ 兼容性补丁
echo def apply_compatibility_patch^(^):
echo     try:
echo         import pkgutil
echo         if not hasattr^(pkgutil, 'ImpImporter'^):
echo             # 添加缺失的 ImpImporter
echo             class ImpImporter:
echo                 pass
echo             pkgutil.ImpImporter = ImpImporter
echo             print^("✓ 已应用 ImpImporter 补丁"^)
echo     except Exception as e:
echo         print^(f"补丁应用失败: {e}"^)
echo.
echo # 设置兼容性环境变量
echo os.environ['PYTHONHASHSEED'] = '0'
echo os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
echo os.environ['PYTHONUTF8'] = '1'
echo os.environ['PIP_NO_CACHE_DIR'] = '1'
echo.
echo # 应用补丁
echo apply_compatibility_patch^(^)
echo print^("✓ 兼容性设置完成"^)
) > python312_compatibility_patch.py

echo ✓ 兼容性补丁已创建
echo.

echo 2. Upgrading tools in existing environments...
if exist "venv_stableaudio\Scripts\activate.bat" (
    echo Upgrading Stable Audio environment tools...
    call venv_stableaudio\Scripts\activate.bat
    python -m pip install --upgrade pip setuptools wheel --no-cache-dir
    python python312_compatibility_patch.py
    call venv_stableaudio\Scripts\deactivate.bat
    echo ✓ Stable Audio environment updated
) else (
    echo Warning: venv_stableaudio not found
)

if exist "venv_gemini\Scripts\activate.bat" (
    echo Upgrading Gemini environment tools...
    call venv_gemini\Scripts\activate.bat
    python -m pip install --upgrade pip setuptools wheel --no-cache-dir
    python python312_compatibility_patch.py
    call venv_gemini\Scripts\deactivate.bat
    echo ✓ Gemini environment updated
) else (
    echo Warning: venv_gemini not found
)

cd ..

echo.
echo 3. Setting up frontend environment...
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
echo ✓ Environment setup completed!
echo ========================================
echo.
echo Your existing virtual environments have been preserved and updated:
echo - Compatibility patch applied
echo - Tools upgraded
echo - No environments deleted
echo.
echo If you encounter pkgutil.ImpImporter errors, run option 6
echo.
echo Now you can run option 4 to start all services
goto end



:fix_python313
echo.
echo Fixing Python 3.13 compatibility issues...
echo.
cd backend
if exist "scripts\fix_python313.bat" (
    call scripts\fix_python313.bat
    echo Python 3.13 compatibility fix completed
) else (
    echo Error: scripts\fix_python313.bat not found
    echo Please check if the file exists
)
cd ..
echo.
echo Fix completed! You can now try running the services again
goto end

:test_compatibility_safe
echo.
echo Running safe Python 3.13 compatibility test...
echo.
cd backend
if exist "scripts\test_install_safe.bat" (
    call scripts\test_install_safe.bat
    echo Safe compatibility test completed
) else (
    echo Error: scripts\test_install_safe.bat not found
    echo Please check if the file exists
)
cd ..
echo.
echo Test completed! Check the results above
goto end

:test_single_package
echo.
echo Running single package installation test...
echo.
cd backend
if exist "scripts\test_single_package.bat" (
    call scripts\test_single_package.bat
    echo Single package test completed
) else (
    echo Error: scripts\test_single_package.bat not found
    echo Please check if the file exists
)
cd ..
echo.
echo Test completed! Check the results above
goto end

:fix_python312
echo.
echo Fixing Python 3.12 compatibility issues...
echo.
cd backend
if exist "scripts\fix_python312_compatibility.bat" (
    call scripts\fix_python312_compatibility.bat
    echo Python 3.12 compatibility fix completed
) else (
    echo Error: scripts\fix_python312_compatibility.bat not found
    echo Please check if the file exists
)
cd ..
echo.
echo Fix completed! You can now try running the services again
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