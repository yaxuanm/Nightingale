# Gemini服务启动脚本
# 使用方法: .\start_gemini_simple.ps1

Write-Host "🚀 启动Gemini API服务..." -ForegroundColor Green
Write-Host "=" * 50

# 检查并进入backend目录
if (Test-Path "backend") {
    Set-Location "backend"
    Write-Host "✓ 进入backend目录" -ForegroundColor Green
} else {
    Write-Host "❌ 错误: 未找到backend目录" -ForegroundColor Red
    exit 1
}

# 检查虚拟环境
if (Test-Path "venv_gemini\Scripts\Activate.ps1") {
    Write-Host "✓ 找到venv_gemini虚拟环境" -ForegroundColor Green
} else {
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
$packages = @("google.generativeai", "fastapi", "uvicorn")
foreach ($package in $packages) {
    try {
        python -c "import $package; print('✓ $package')"
    } catch {
        Write-Host "❌ $package 未安装" -ForegroundColor Red
    }
}

# 启动服务
Write-Host "🌐 启动Gemini API服务..." -ForegroundColor Green
Write-Host "服务地址: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "API文档: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host "=" * 50

# 启动uvicorn服务器
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 