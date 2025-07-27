@echo off
chcp 65001
echo ========================================
echo 带补丁的依赖安装脚本
echo ========================================
echo.

set ENV_NAME=%1
set REQUIREMENTS_FILE=%2

if "%ENV_NAME%"=="" (
    echo Error: Environment name not provided
    echo Usage: install_with_patch.bat [env_name] [requirements_file]
    exit /b 1
)

if "%REQUIREMENTS_FILE%"=="" (
    echo Error: Requirements file not provided
    echo Usage: install_with_patch.bat [env_name] [requirements_file]
    exit /b 1
)

echo Installing dependencies for %ENV_NAME% with compatibility patch...
echo Requirements file: %REQUIREMENTS_FILE%
echo.

echo 1. Creating compatibility patch...
echo import sys > python312_compatibility_patch.py
echo import os >> python312_compatibility_patch.py
echo. >> python312_compatibility_patch.py
echo # Python 3.12+ compatibility patch >> python312_compatibility_patch.py
echo def apply_compatibility_patch(): >> python312_compatibility_patch.py
echo     try: >> python312_compatibility_patch.py
echo         import pkgutil >> python312_compatibility_patch.py
echo         if not hasattr(pkgutil, 'ImpImporter'): >> python312_compatibility_patch.py
echo             class ImpImporter: >> python312_compatibility_patch.py
echo                 pass >> python312_compatibility_patch.py
echo             pkgutil.ImpImporter = ImpImporter >> python312_compatibility_patch.py
echo             print("✓ ImpImporter patch applied") >> python312_compatibility_patch.py
echo     except Exception as e: >> python312_compatibility_patch.py
echo         print(f"Patch failed: {e}") >> python312_compatibility_patch.py
echo. >> python312_compatibility_patch.py
echo # Set compatibility environment variables >> python312_compatibility_patch.py
echo os.environ['PYTHONHASHSEED'] = '0' >> python312_compatibility_patch.py
echo os.environ['PYTHONDONTWRITEBYTECODE'] = '1' >> python312_compatibility_patch.py
echo os.environ['PYTHONUTF8'] = '1' >> python312_compatibility_patch.py
echo os.environ['PIP_NO_CACHE_DIR'] = '1' >> python312_compatibility_patch.py
echo. >> python312_compatibility_patch.py
echo # Apply patch >> python312_compatibility_patch.py
echo apply_compatibility_patch() >> python312_compatibility_patch.py
echo print("✓ Compatibility setup completed") >> python312_compatibility_patch.py

echo ✓ Compatibility patch created
echo.

echo 2. Creating/updating virtual environment...
if exist "%ENV_NAME%" (
    echo Removing existing %ENV_NAME% environment...
    rmdir /s /q %ENV_NAME%
)

python -m venv %ENV_NAME%
echo ✓ Virtual environment created
echo.

echo 3. Activating environment and applying patch...
call %ENV_NAME%\Scripts\activate.bat

echo Upgrading pip, setuptools, wheel...
python -m pip install --upgrade pip setuptools wheel --no-cache-dir

echo Applying compatibility patch...
python python312_compatibility_patch.py

echo 4. Installing dependencies with patch...
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
echo Compatibility patch: Applied
echo.
pause 