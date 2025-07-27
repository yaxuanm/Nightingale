@echo off
echo ========================================
echo Nightingale 部署脚本 (绕过 NVM 干扰)
echo ========================================

echo.
echo 正在临时禁用 NVM...
if exist "%APPDATA%\nvm" (
    ren "%APPDATA%\nvm" "nvm_backup"
    echo ✓ NVM 已临时禁用
) else (
    echo - NVM 未找到，继续执行
)

echo.
echo 开始环境设置...
cd backend

echo 1. 创建虚拟环境...
python -m venv venv_stableaudio
if %errorlevel% neq 0 (
    echo ❌ 创建 venv_stableaudio 失败
    goto cleanup
)

python -m venv venv_gemini
if %errorlevel% neq 0 (
    echo ❌ 创建 venv_gemini 失败
    goto cleanup
)

echo 2. 安装 Stable Audio 环境依赖...
call venv_stableaudio\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ 激活 venv_stableaudio 失败
    goto cleanup
)

python -m pip install --upgrade pip
pip install -r requirements-stable-audio.txt
if %errorlevel% neq 0 (
    echo ❌ 安装 Stable Audio 依赖失败
    goto cleanup
)

call venv_stableaudio\Scripts\deactivate.bat

echo 3. 安装 Gemini 环境依赖...
call venv_gemini\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ 激活 venv_gemini 失败
    goto cleanup
)

python -m pip install --upgrade pip
pip install -r requirements-gemini-utf8.txt
if %errorlevel% neq 0 (
    echo ❌ 安装 Gemini 依赖失败
    goto cleanup
)

call venv_gemini\Scripts\deactivate.bat

echo.
echo 4. 设置前端环境...
cd ..\ambiance-weaver-react
if exist "package.json" (
    echo 安装前端依赖...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ 安装前端依赖失败
        goto cleanup
    )
) else (
    echo ❌ package.json 未找到
    goto cleanup
)

cd ..

echo.
echo ========================================
echo ✓ 环境设置完成！
echo ========================================
echo.
echo 现在可以启动服务：
echo 1. 运行 ./start_clean.bat
echo 2. 选择 4 (Start All Services)
echo.
goto restore_nvm

:cleanup
echo.
echo ❌ 环境设置失败，正在清理...
cd ..
if exist "backend\venv_stableaudio" rmdir /s /q backend\venv_stableaudio
if exist "backend\venv_gemini" rmdir /s /q backend\venv_gemini
echo 清理完成

:restore_nvm
echo.
echo 正在恢复 NVM...
if exist "%APPDATA%\nvm_backup" (
    ren "%APPDATA%\nvm_backup" "nvm"
    echo ✓ NVM 已恢复
) else (
    echo - 没有找到 NVM 备份
)

echo.
echo 部署脚本执行完成！
pause 