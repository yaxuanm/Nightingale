# 环境依赖安装脚本
# 自动安装所有虚拟环境的依赖

Write-Host "开始安装环境依赖..." -ForegroundColor Green

# 检查虚拟环境是否存在
$environments = @(
    @{Name="API环境"; Path="venv_api"; Requirements="requirements-api.txt"},
    @{Name="Stable Audio环境"; Path="venv_stableaudio"; Requirements="requirements-stable-audio.txt"},
    @{Name="Gemini环境"; Path="venv_gemini"; Requirements="requirements-gemini-utf8.txt"},
    @{Name="Audio环境"; Path="venv_audio"; Requirements="requirements-audio.txt"}
)

foreach ($env in $environments) {
    Write-Host "`n正在安装 $($env.Name)..." -ForegroundColor Yellow
    
    # 检查虚拟环境是否存在
    if (Test-Path $env.Path) {
        Write-Host "激活 $($env.Name)..." -ForegroundColor Cyan
        & "$($env.Path)\Scripts\Activate.ps1"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "安装依赖包..." -ForegroundColor Cyan
            pip install -r $env.Requirements
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "$($env.Name) 安装完成!" -ForegroundColor Green
            } else {
                Write-Host "$($env.Name) 安装失败!" -ForegroundColor Red
            }
        } else {
            Write-Host "无法激活 $($env.Name)!" -ForegroundColor Red
        }
    } else {
        Write-Host "$($env.Name) 虚拟环境不存在: $($env.Path)" -ForegroundColor Red
    }
}

Write-Host "`n环境依赖安装完成!" -ForegroundColor Green
Write-Host "请查看 ENVIRONMENT_COMPARISON.md 了解各环境用途" -ForegroundColor Cyan 