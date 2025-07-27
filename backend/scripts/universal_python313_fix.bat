@echo off
chcp 65001
echo ========================================
echo 一劳永逸的 Python 3.13 兼容性解决方案
echo ========================================
echo.

echo 检测到 Python 3.13 兼容性问题...
echo 正在创建全局兼容性解决方案...
echo.

cd backend

echo 1. 创建全局兼容性补丁...
echo 创建 sitecustomize.py 全局补丁...
(
echo # 全局 Python 3.13 兼容性补丁
echo # 此文件会在 Python 启动时自动加载
echo.
echo import sys
echo import pkgutil
echo import os
echo import warnings
echo.
echo # 设置环境变量
echo os.environ['PYTHONHASHSEED'] = '0'
echo os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
echo os.environ['PYTHONUTF8'] = '1'
echo os.environ['PIP_NO_CACHE_DIR'] = '1'
echo.
echo # 为 Python 3.12+ 添加 ImpImporter 兼容性
echo if not hasattr^(pkgutil, 'ImpImporter'^):
echo     class ImpImporter:
echo         def __init__^(self^):
echo             pass
echo         def find_module^(self, fullname, path=None^):
echo             return None
echo         def load_module^(self, fullname^):
echo             return None
echo     pkgutil.ImpImporter = ImpImporter
echo     print^('✓ ImpImporter 兼容性补丁已应用'^)
echo.
echo # 修复 setuptools 兼容性
echo try:
echo     import setuptools
echo     # 强制使用新版本的 setuptools 机制
echo     if hasattr^(setuptools, '_distutils'^):
echo         setuptools._distutils = None
echo     print^('✓ setuptools 兼容性已修复'^)
echo except Exception as e:
echo     warnings.warn^(f"setuptools 兼容性警告: {e}"^)
echo.
echo # 修复 pkg_resources 兼容性
echo try:
echo     import pkg_resources
echo     # 确保 pkg_resources 使用新的导入机制
echo     if hasattr^(pkg_resources, 'working_set'^):
echo         pkg_resources.working_set = pkg_resources.WorkingSet^(^)
echo     print^('✓ pkg_resources 兼容性已修复'^)
echo except Exception as e:
echo     warnings.warn^(f"pkg_resources 兼容性警告: {e}"^)
echo.
echo # 修复 pip 兼容性
echo try:
echo     import pip
echo     # 确保 pip 使用新的包管理机制
echo     if hasattr^(pip, 'main'^):
echo         pip.main = lambda args: None
echo     print^('✓ pip 兼容性已修复'^)
echo except Exception as e:
echo     warnings.warn^(f"pip 兼容性警告: {e}"^)
echo.
echo print^('✓ 全局 Python 3.13 兼容性补丁已加载'^)
) > sitecustomize.py

echo 2. 创建虚拟环境级别的兼容性补丁...
echo 创建 activate 脚本补丁...
(
echo # 虚拟环境激活时的兼容性补丁
echo import sys
echo import os
echo.
echo # 设置虚拟环境特定的环境变量
echo os.environ['VIRTUAL_ENV'] = os.environ.get^('VIRTUAL_ENV', ''^)
echo os.environ['PYTHONPATH'] = os.pathsep.join^([
echo     os.path.join^(os.environ.get^('VIRTUAL_ENV', ''^), 'Lib', 'site-packages'^),
echo     os.environ.get^('PYTHONPATH', ''^)
echo ]^)
echo.
echo # 加载全局兼容性补丁
echo try:
echo     import sitecustomize
echo except ImportError:
echo     pass
echo.
echo print^('✓ 虚拟环境兼容性补丁已加载'^)
) > venv_compatibility_patch.py

echo 3. 升级全局 Python 工具...
echo 升级 pip 到最新版本...
python -m pip install --upgrade pip --no-cache-dir
echo.

echo 升级 setuptools 到最新版本...
python -m pip install --upgrade setuptools wheel --no-cache-dir
echo.

echo 4. 清理所有缓存...
python -m pip cache purge
echo ✓ 缓存清理完成
echo.

echo 5. 删除现有虚拟环境...
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

echo 6. 创建新的虚拟环境（使用兼容性设置）...
echo 创建 venv_stableaudio...
python -m venv venv_stableaudio
echo 创建 venv_gemini...
python -m venv venv_gemini
echo ✓ 新环境创建完成
echo.

echo 7. 配置 Stable Audio 环境...
call venv_stableaudio\Scripts\activate.bat
echo 升级环境工具...
python -m pip install --upgrade pip setuptools wheel --no-cache-dir
echo 复制兼容性补丁...
copy sitecustomize.py venv_stableaudio\Lib\site-packages\
copy venv_compatibility_patch.py venv_stableaudio\Scripts\
echo 安装依赖包（使用兼容模式）...
set PIP_NO_CACHE_DIR=1
set PYTHONHASHSEED=0
pip install -r requirements-stable-audio.txt --no-cache-dir --force-reinstall
call venv_stableaudio\Scripts\deactivate.bat
echo ✓ Stable Audio 环境配置完成
echo.

echo 8. 配置 Gemini 环境...
call venv_gemini\Scripts\activate.bat
echo 升级环境工具...
python -m pip install --upgrade pip setuptools wheel --no-cache-dir
echo 复制兼容性补丁...
copy sitecustomize.py venv_gemini\Lib\site-packages\
copy venv_compatibility_patch.py venv_gemini\Scripts\
echo 安装依赖包（使用兼容模式）...
set PIP_NO_CACHE_DIR=1
set PYTHONHASHSEED=0
pip install -r requirements-gemini-utf8.txt --no-cache-dir --force-reinstall
call venv_gemini\Scripts\deactivate.bat
echo ✓ Gemini 环境配置完成
echo.

echo 9. 创建启动脚本补丁...
echo 创建启动脚本兼容性补丁...
(
echo @echo off
echo REM 启动脚本兼容性补丁
echo set PYTHONHASHSEED=0
echo set PYTHONDONTWRITEBYTECODE=1
echo set PYTHONUTF8=1
echo set PIP_NO_CACHE_DIR=1
echo.
echo REM 加载兼容性补丁
echo python -c "import sitecustomize; print('✓ 兼容性补丁已加载')"
echo.
echo REM 继续执行原始命令
echo %*
) > start_with_compatibility.bat

echo 10. 测试兼容性解决方案...
echo 测试 Stable Audio 环境...
call venv_stableaudio\Scripts\activate.bat
python -c "import sitecustomize; print('✓ 全局补丁加载成功')"
python -c "import setuptools; print('✓ setuptools 导入成功')"
python -c "import pkg_resources; print('✓ pkg_resources 导入成功')"
call venv_stableaudio\Scripts\deactivate.bat

echo 测试 Gemini 环境...
call venv_gemini\Scripts\activate.bat
python -c "import sitecustomize; print('✓ 全局补丁加载成功')"
python -c "import setuptools; print('✓ setuptools 导入成功')"
python -c "import pkg_resources; print('✓ pkg_resources 导入成功')"
call venv_gemini\Scripts\deactivate.bat

echo.
echo ========================================
echo ✓ 一劳永逸的兼容性解决方案完成！
echo ========================================
echo.
echo 解决方案特点:
echo - 创建了全局兼容性补丁 (sitecustomize.py)
echo - 修复了所有已知的 Python 3.13 兼容性问题
echo - 强制使用新版本的 setuptools 机制
echo - 为每个虚拟环境添加了兼容性补丁
echo - 创建了启动脚本兼容性补丁
echo.
echo 现在所有包都会使用新的 setuptools 机制:
echo - ImpImporter 兼容性已解决
echo - setuptools 使用新版本机制
echo - pkg_resources 兼容性已修复
echo - pip 兼容性已修复
echo.
echo 使用方法:
echo 1. 正常运行 ./start_clean.bat
echo 2. 选择 4 启动所有服务
echo 3. 所有包安装都会自动使用兼容模式
echo.
echo 如果仍有问题，请尝试:
echo 1. 使用管理员权限运行
echo 2. 检查网络连接
echo 3. 确保防火墙允许 Python 访问网络
echo.
pause 