@echo off
chcp 65001
echo ========================================
echo Python 3.13 紧急兼容性修复
echo ========================================
echo.

echo 检测到 Python 3.13 构建子进程兼容性问题...
echo 正在应用紧急修复方案...
echo.

cd backend

echo 1. 设置环境变量...
set PYTHONHASHSEED=0
set PYTHONDONTWRITEBYTECODE=1
set PYTHONUTF8=1
set PIP_NO_CACHE_DIR=1
echo ✓ 环境变量设置完成
echo.

echo 2. 升级全局工具...
python -m pip install --upgrade pip setuptools wheel --no-cache-dir
echo ✓ 全局工具升级完成
echo.

echo 3. 清理缓存...
python -m pip cache purge
echo ✓ 缓存清理完成
echo.

echo 4. 删除现有环境...
if exist "venv_stableaudio" (
    echo 删除 venv_stableaudio...
    rmdir /s /q "venv_stableaudio"
)
if exist "venv_gemini" (
    echo 删除 venv_gemini...
    rmdir /s /q "venv_gemini"
)
echo ✓ 旧环境清理完成
echo.

echo 5. 创建新环境...
echo 创建 venv_stableaudio...
python -m venv venv_stableaudio
echo 创建 venv_gemini...
python -m venv venv_gemini
echo ✓ 新环境创建完成
echo.

echo 6. 配置 Stable Audio 环境...
call venv_stableaudio\Scripts\activate.bat
echo 升级环境工具...
python -m pip install --upgrade pip setuptools wheel --no-cache-dir
echo 安装依赖（使用预编译包）...
pip install --only-binary=all -r requirements-stable-audio.txt --no-cache-dir
call venv_stableaudio\Scripts\deactivate.bat
echo ✓ Stable Audio 环境配置完成
echo.

echo 7. 配置 Gemini 环境...
call venv_gemini\Scripts\activate.bat
echo 升级环境工具...
python -m pip install --upgrade pip setuptools wheel --no-cache-dir
echo 安装依赖（使用预编译包）...
pip install --only-binary=all -r requirements-gemini-utf8.txt --no-cache-dir
call venv_gemini\Scripts\deactivate.bat
echo ✓ Gemini 环境配置完成
echo.

echo 8. 测试环境...
echo 测试 Stable Audio 环境...
call venv_stableaudio\Scripts\activate.bat
python -c "import setuptools; print('✓ setuptools 正常')"
python -c "import pkg_resources; print('✓ pkg_resources 正常')"
call venv_stableaudio\Scripts\deactivate.bat

echo 测试 Gemini 环境...
call venv_gemini\Scripts\activate.bat
python -c "import setuptools; print('✓ setuptools 正常')"
python -c "import pkg_resources; print('✓ pkg_resources 正常')"
call venv_gemini\Scripts\deactivate.bat

echo.
echo ========================================
echo ✓ Python 3.13 紧急修复完成！
echo ========================================
echo.
echo 修复内容:
echo - 使用 --only-binary=all 强制使用预编译包
echo - 升级了所有基础工具
echo - 清理了所有缓存
echo - 重新创建了虚拟环境
echo.
echo 现在可以启动服务:
echo 1. 运行 ../start_clean.bat
echo 2. 选择 4 启动所有服务
echo.
echo 如果仍有问题:
echo 1. 检查网络连接
echo 2. 使用管理员权限运行
echo 3. 确保防火墙允许 Python 访问网络
echo.
pause 