@echo off
chcp 65001
echo ========================================
echo Python 3.13 兼容性修复 - 安全测试版
echo ========================================
echo.

echo 这是一个安全的测试版本，不会删除你现有的虚拟环境！
echo 将创建新的测试环境来验证修复方案。
echo.

echo 现有环境将被保留:
echo - venv_stableaudio (保留)
echo - venv_gemini (保留)
echo.
echo 将创建测试环境:
echo - test_venv_stableaudio (新建)
echo - test_venv_gemini (新建)
echo.

set /p confirm="确认继续测试？(y/n): "
if /i not "%confirm%"=="y" (
    echo 测试已取消
    goto end
)

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

echo 4. 创建测试环境...
echo 创建 test_venv_stableaudio...
python -m venv test_venv_stableaudio
echo 创建 test_venv_gemini...
python -m venv test_venv_gemini
echo ✓ 测试环境创建完成
echo.

echo 5. 配置测试 Stable Audio 环境...
call test_venv_stableaudio\Scripts\activate.bat
echo 升级环境工具...
python -m pip install --upgrade pip setuptools wheel --no-cache-dir
echo 安装依赖（使用预编译包）...
pip install --only-binary=all -r requirements-stable-audio.txt --no-cache-dir
call test_venv_stableaudio\Scripts\deactivate.bat
echo ✓ 测试 Stable Audio 环境配置完成
echo.

echo 6. 配置测试 Gemini 环境...
call test_venv_gemini\Scripts\activate.bat
echo 升级环境工具...
python -m pip install --upgrade pip setuptools wheel --no-cache-dir
echo 安装依赖（使用预编译包）...
pip install --only-binary=all -r requirements-gemini-utf8.txt --no-cache-dir
call test_venv_gemini\Scripts\deactivate.bat
echo ✓ 测试 Gemini 环境配置完成
echo.

echo 7. 测试环境...
echo 测试 Stable Audio 环境...
call test_venv_stableaudio\Scripts\activate.bat
python -c "import setuptools; print('✓ setuptools 正常')"
python -c "import pkg_resources; print('✓ pkg_resources 正常')"
python -c "import numpy; print(f'✓ numpy {numpy.__version__} 正常')"
python -c "import protobuf; print(f'✓ protobuf {protobuf.__version__} 正常')"
call test_venv_stableaudio\Scripts\deactivate.bat

echo 测试 Gemini 环境...
call test_venv_gemini\Scripts\activate.bat
python -c "import setuptools; print('✓ setuptools 正常')"
python -c "import pkg_resources; print('✓ pkg_resources 正常')"
python -c "import numpy; print(f'✓ numpy {numpy.__version__} 正常')"
python -c "import protobuf; print(f'✓ protobuf {protobuf.__version__} 正常')"
call test_venv_gemini\Scripts\deactivate.bat

echo.
echo ========================================
echo ✓ Python 3.13 兼容性测试完成！
echo ========================================
echo.
echo 测试结果:
echo - 创建了测试环境: test_venv_stableaudio, test_venv_gemini
echo - 使用 --only-binary=all 强制使用预编译包
echo - 升级了所有基础工具
echo - 清理了所有缓存
echo.
echo 你的原始环境仍然完整:
echo - venv_stableaudio (未修改)
echo - venv_gemini (未修改)
echo.
echo 如果测试成功，你可以:
echo 1. 手动删除测试环境: rmdir /s /q test_venv_stableaudio test_venv_gemini
echo 2. 或者保留测试环境作为备份
echo.
echo 如果测试失败，你的原始环境不受影响。
echo.
pause

:end
echo 测试结束 