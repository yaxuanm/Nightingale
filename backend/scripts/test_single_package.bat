@echo off
chcp 65001
echo ========================================
echo 单包安装测试 - Python 3.13 兼容性
echo ========================================
echo.

echo 这个脚本将测试单个包的安装来验证兼容性修复
echo 不会影响你现有的虚拟环境
echo.

set /p package_name="请输入要测试的包名 (例如: numpy): "
if "%package_name%"=="" (
    echo 使用默认包: numpy
    set package_name=numpy
)

echo.
echo 测试包: %package_name%
echo.

cd backend

echo 1. 设置环境变量...
set PYTHONHASHSEED=0
set PYTHONDONTWRITEBYTECODE=1
set PYTHONUTF8=1
set PIP_NO_CACHE_DIR=1
echo ✓ 环境变量设置完成
echo.

echo 2. 创建临时测试环境...
python -m venv temp_test_env
echo ✓ 临时环境创建完成
echo.

echo 3. 激活环境并升级工具...
call temp_test_env\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel --no-cache-dir
echo ✓ 工具升级完成
echo.

echo 4. 测试安装 %package_name%...
echo 尝试安装 %package_name% (使用预编译包)...
pip install --only-binary=all %package_name% --no-cache-dir
if %errorlevel% equ 0 (
    echo ✓ %package_name% 安装成功！
    echo.
    echo 5. 测试导入...
    python -c "import %package_name%; print(f'✓ {package_name} 导入成功，版本: {package_name}.__version__')"
) else (
    echo ✗ %package_name% 安装失败
    echo.
    echo 尝试不使用 --only-binary=all...
    pip install %package_name% --no-cache-dir
    if %errorlevel% equ 0 (
        echo ✓ %package_name% 安装成功（不使用预编译包）
        python -c "import %package_name%; print(f'✓ {package_name} 导入成功')"
    ) else (
        echo ✗ %package_name% 安装完全失败
    )
)

call temp_test_env\Scripts\deactivate.bat

echo.
echo 6. 清理临时环境...
rmdir /s /q temp_test_env
echo ✓ 临时环境清理完成
echo.

echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 测试结果:
echo - 包名: %package_name%
echo - 环境变量: 已设置
echo - 工具升级: 已完成
echo - 预编译包: 已测试
echo.
echo 如果测试成功，说明兼容性修复有效
echo 如果测试失败，可能需要进一步调整修复方案
echo.
pause 