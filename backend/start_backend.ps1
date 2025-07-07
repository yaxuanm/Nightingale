# Nightingale Backend Startup Script
# Usage: .\start_backend.ps1

Write-Host "=== Nightingale Backend Startup Script ===" -ForegroundColor Green

# Check if in correct directory
if (-not (Test-Path "venv_api")) {
    Write-Host "Error: Please run this script in the backend directory" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv_api\Scripts\activate"

# Check if virtual environment activation was successful
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Error: Virtual environment activation failed" -ForegroundColor Red
    exit 1
}

Write-Host "Virtual environment activated: $env:VIRTUAL_ENV" -ForegroundColor Green

# Check dependencies
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import uvicorn, fastapi, numpy, pydub, google.generativeai; print('All dependencies installed')"
} catch {
    Write-Host "Installing missing dependencies..." -ForegroundColor Yellow
    pip install -r requirements-api.txt
    pip install numpy pydub google-generativeai ffmpeg-python
}

# Start service
Write-Host "Starting FastAPI service..." -ForegroundColor Green
Write-Host "Service URL: http://localhost:8000/" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Audio Generation: Using worker script (audiocraft)" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop service" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 