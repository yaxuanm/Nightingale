# Gemini服务启动脚本
# 使用方法: .\start_gemini_service.ps1

Write-Host "🚀 启动Gemini API服务..." -ForegroundColor Green

# 检查虚拟环境
if (-not (Test-Path "venv_gemini\Scripts\Activate.ps1")) {
    Write-Host "❌ 错误: 未找到venv_gemini虚拟环境" -ForegroundColor Red
    Write-Host "请先运行: py -3.11 -m venv venv_gemini" -ForegroundColor Yellow
    exit 1
}

# 激活虚拟环境
Write-Host "📦 激活虚拟环境..." -ForegroundColor Cyan
& ".\venv_gemini\Scripts\Activate.ps1"

# 检查Python版本
$pythonVersion = python --version
Write-Host "✓ Python版本: $pythonVersion" -ForegroundColor Green

# 设置API密钥
$env:GEMINI_API_KEY = "AIzaSyAqeUjWY_u59F_Tbxm3FfE9JTJqoGMdZAI"
$env:GOOGLE_API_KEY = "AIzaSyAqeUjWY_u59F_Tbxm3FfE9JTJqoGMdZAI"
Write-Host "✓ API密钥已设置" -ForegroundColor Green

# 检查必要的包
Write-Host "🔍 检查必要的包..." -ForegroundColor Cyan
try {
    python -c "import google.generativeai; print('✓ google.generativeai')"
} catch {
    Write-Host "❌ google.generativeai未安装，正在安装..." -ForegroundColor Yellow
    pip install google-generativeai
}

try {
    python -c "import fastapi; print('✓ fastapi')"
} catch {
    Write-Host "❌ fastapi未安装，正在安装..." -ForegroundColor Yellow
    pip install fastapi uvicorn
}

# 启动服务
Write-Host "🌐 启动Gemini API服务..." -ForegroundColor Green
Write-Host "服务地址: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "API文档: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow

# 启动uvicorn服务器
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 