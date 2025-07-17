@echo off
echo Starting Nightingale Fixed Test Web Service...
echo.

cd /d "%~dp0"

REM 设置正确的参数
set DATA_FILE=../audio_test_output/fixed_test/web_test_data.json
set AUDIO_DIR=../audio_test_output/fixed_test/audio_files
set PORT=8010

echo Data file: %DATA_FILE%
echo Audio directory: %AUDIO_DIR%
echo Port: %PORT%
echo.

REM 检查文件是否存在
if not exist "%DATA_FILE%" (
    echo ERROR: Data file not found: %DATA_FILE%
    pause
    exit /b 1
)

if not exist "%AUDIO_DIR%" (
    echo ERROR: Audio directory not found: %AUDIO_DIR%
    pause
    exit /b 1
)

echo Starting web service...
python fixed_test_web.py --data_file "%DATA_FILE%" --audio_dir "%AUDIO_DIR%" --port %PORT%

pause 