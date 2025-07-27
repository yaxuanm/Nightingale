# Gemini服务启动测试脚本
# 使用方法: .\test_gemini_startup.ps1

Write-Host "🧪 Gemini服务启动测试" -ForegroundColor Green
Write-Host "=" * 50

# 1. 检查虚拟环境
Write-Host "1. 检查虚拟环境..." -ForegroundColor Cyan
if (Test-Path "venv_gemini\Scripts\Activate.ps1") {
    Write-Host "✓ 找到venv_gemini虚拟环境" -ForegroundColor Green
} else {
    Write-Host "❌ 未找到venv_gemini虚拟环境" -ForegroundColor Red
    exit 1
}

# 2. 激活虚拟环境
Write-Host "2. 激活虚拟环境..." -ForegroundColor Cyan
& ".\venv_gemini\Scripts\Activate.ps1"

# 3. 检查Python版本
Write-Host "3. 检查Python版本..." -ForegroundColor Cyan
$pythonVersion = python --version
Write-Host "✓ $pythonVersion" -ForegroundColor Green

# 4. 检查关键包
Write-Host "4. 检查关键包..." -ForegroundColor Cyan
$packages = @("google.generativeai", "fastapi", "uvicorn", "requests")
foreach ($package in $packages) {
    try {
        python -c "import $package; print('✓ $package')"
    } catch {
        Write-Host "❌ $package 未安装" -ForegroundColor Red
    }
}

# 5. 设置环境变量
Write-Host "5. 设置环境变量..." -ForegroundColor Cyan
$env:GEMINI_API_KEY = "AIzaSyAqeUjWY_u59F_Tbxm3FfE9JTJqoGMdZAI"
$env:GOOGLE_API_KEY = "AIzaSyAqeUjWY_u59F_Tbxm3FfE9JTJqoGMdZAI"
Write-Host "✓ API密钥已设置" -ForegroundColor Green

# 6. 测试Gemini API连接
Write-Host "6. 测试Gemini API连接..." -ForegroundColor Cyan
try {
    python -c "
import google.generativeai as genai
genai.configure(api_key='AIzaSyAqeUjWY_u59F_Tbxm3FfE9JTJqoGMdZAI')
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content('Hello, test connection')
print('✓ Gemini API连接成功')
print(f'响应: {response.text}')
"
} catch {
    Write-Host "❌ Gemini API连接失败" -ForegroundColor Red
}

# 7. 检查FastAPI应用
Write-Host "7. 检查FastAPI应用..." -ForegroundColor Cyan
if (Test-Path "app\main.py") {
    Write-Host "✓ 找到app\main.py" -ForegroundColor Green
} else {
    Write-Host "❌ 未找到app\main.py" -ForegroundColor Red
}

Write-Host "=" * 50
Write-Host "✅ 测试完成！如果所有项目都显示✓，则可以启动服务" -ForegroundColor Green
Write-Host "启动命令: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" -ForegroundColor Cyan 