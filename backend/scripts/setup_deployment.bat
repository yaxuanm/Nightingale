@echo off
echo ========================================
echo    Nightingale 部署设置向导
echo ========================================
echo.

echo 正在检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到 Python
    echo 请先安装 Python 3.8+
    pause
    exit /b 1
)
echo ✓ Python 环境正常

echo.
echo 正在检查 Hugging Face Token...
set "token_exists="
if defined HF_TOKEN set "token_exists=1"
if defined HUGGING_FACE_HUB_TOKEN set "token_exists=1"

if not defined token_exists (
    echo ❌ 未设置 Hugging Face Token
    echo.
    echo 正在启动 Token 设置向导...
    python scripts/set_hf_token.py
    if %errorlevel% neq 0 (
        echo.
        echo ❌ Token 设置失败
        echo 请检查网络连接和 Hugging Face 账户
        pause
        exit /b 1
    )
) else (
    echo ✓ 找到 Hugging Face Token
)

echo.
echo 正在验证 Token...
python scripts/test_hf_token.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Token 验证失败
    echo 请重新设置 Token
    pause
    exit /b 1
)

echo.
echo 正在修复 Stable Audio 兼容性问题...
python scripts/stable_audio_fix.py
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Stable Audio 修复失败，但可以继续尝试
    echo 如果后续遇到 int32 溢出错误，请手动运行：
    echo   python scripts/stable_audio_fix.py
) else (
    echo ✓ Stable Audio 兼容性修复完成
)

echo.
echo ========================================
echo ✓ 部署设置完成！
echo ========================================
echo.
echo 现在可以运行 Stable Audio 了：
echo   python scripts/run_stable_audio_worker.py --prompt "your prompt" --out output.wav
echo.
pause 