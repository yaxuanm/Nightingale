# Stable Audio Open Small 模型测试启动脚本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Stable Audio Open Small 模型测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 检查Python是否安装
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python版本: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ 错误: 未找到Python，请先安装Python 3.8+" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

# 检查是否在虚拟环境中
Write-Host "`n检查虚拟环境..." -ForegroundColor Yellow
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠ 警告: 建议在虚拟环境中运行测试" -ForegroundColor Yellow
    Write-Host "如果遇到依赖问题，请先创建虚拟环境:" -ForegroundColor Yellow
    Write-Host "python -m venv venv_stable_audio" -ForegroundColor White
    Write-Host "venv_stable_audio\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host ""
}

# 安装依赖
Write-Host "安装依赖包..." -ForegroundColor Yellow
$dependencies = @("stable-audio-tools", "einops", "psutil", "pytest", "requests")

foreach ($dep in $dependencies) {
    Write-Host "安装 $dep..." -ForegroundColor White
    try {
        pip install $dep
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ $dep 安装成功" -ForegroundColor Green
        } else {
            Write-Host "✗ $dep 安装失败" -ForegroundColor Red
            Read-Host "按任意键退出"
            exit 1
        }
    } catch {
        Write-Host "✗ $dep 安装失败: $_" -ForegroundColor Red
        Read-Host "按任意键退出"
        exit 1
    }
}

Write-Host "`n✓ 依赖安装完成！" -ForegroundColor Green
Write-Host ""

# 检查必要目录
Write-Host "检查必要目录..." -ForegroundColor Yellow
$audioOutputDir = "audio_output"
if (-not (Test-Path $audioOutputDir)) {
    New-Item -ItemType Directory -Path $audioOutputDir -Force | Out-Null
    Write-Host "✓ 创建目录: $audioOutputDir" -ForegroundColor Green
} else {
    Write-Host "✓ 目录已存在: $audioOutputDir" -ForegroundColor Green
}

# 运行简单测试
Write-Host "`n开始运行简单测试..." -ForegroundColor Yellow
try {
    python test_stable_audio_simple.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✓ 测试完成！" -ForegroundColor Green
    } else {
        Write-Host "`n✗ 测试失败！" -ForegroundColor Red
    }
} catch {
    Write-Host "`n✗ 测试运行失败: $_" -ForegroundColor Red
}

Write-Host "`n生成的音频文件保存在 audio_output 目录中" -ForegroundColor Cyan
Write-Host ""

# 询问是否运行完整测试
$runFullTest = Read-Host "是否运行完整测试套件? (y/n)"
if ($runFullTest -eq "y" -or $runFullTest -eq "yes") {
    Write-Host "`n运行完整测试套件..." -ForegroundColor Yellow
    try {
        python run_stable_audio_tests.py
    } catch {
        Write-Host "完整测试运行失败: $_" -ForegroundColor Red
    }
}

# 询问是否运行pytest
$runPytest = Read-Host "`n是否运行pytest测试? (y/n)"
if ($runPytest -eq "y" -or $runPytest -eq "yes") {
    Write-Host "`n运行pytest测试..." -ForegroundColor Yellow
    try {
        pytest tests/ -v
    } catch {
        Write-Host "pytest测试运行失败: $_" -ForegroundColor Red
    }
}

Write-Host "`n所有测试完成！" -ForegroundColor Green
Read-Host "按任意键退出" 