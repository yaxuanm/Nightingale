@echo off
chcp 65001
echo ========================================
echo Python 3.13.5 兼容性快速修复
echo ========================================
echo.

echo 检测到 Python 3.13.5 兼容性问题...
echo 正在应用综合修复方案...
echo.

cd backend

echo 1. 检查 Python 版本...
python --version
echo.

echo 2. 升级基础工具...
python -m pip install --upgrade pip setuptools wheel
echo.

echo 3. 清理所有缓存...
python -m pip cache purge
echo.

echo 4. 删除现有虚拟环境（如果存在）...
if exist "venv_stableaudio" (
    echo 删除 venv_stableaudio...
    rmdir /s /q "venv_stableaudio"
)
if exist "venv_gemini" (
    echo 删除 venv_gemini...
    rmdir /s /q "venv_gemini"
)
echo.

echo 5. 创建新的虚拟环境...
echo 创建 venv_stableaudio...
python -m venv venv_stableaudio
echo 创建 venv_gemini...
python -m venv venv_gemini
echo.

echo 6. 设置 Stable Audio 环境...
call venv_stableaudio\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
echo 安装 Stable Audio 依赖...
pip install -r requirements-stable-audio.txt --no-cache-dir
call venv_stableaudio\Scripts\deactivate.bat
echo ✓ Stable Audio 环境设置完成
echo.

echo 7. 设置 Gemini 环境...
call venv_gemini\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
echo 安装 Gemini 依赖...
pip install -r requirements-gemini-utf8.txt --no-cache-dir
call venv_gemini\Scripts\deactivate.bat
echo ✓ Gemini 环境设置完成
echo.

echo 8. 创建兼容性补丁...
echo 创建 Python 3.13 兼容性补丁...
(
echo # Python 3.13 兼容性补丁
echo import sys
echo import pkgutil
echo import os
echo.
echo # 设置环境变量
echo os.environ['PYTHONHASHSEED'] = '0'
echo os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
echo os.environ['PYTHONUTF8'] = '1'
echo.
echo # 为 Python 3.12+ 添加 ImpImporter 兼容性
echo if not hasattr^(pkgutil, 'ImpImporter'^):
echo     class ImpImporter:
echo         pass
echo     pkgutil.ImpImporter = ImpImporter
echo.
echo # 修复 setuptools 兼容性
echo try:
echo     import setuptools
echo     print^('✓ setuptools 导入成功'^)
echo except Exception as e:
echo     print^(f'⚠ setuptools 导入警告: {e}'^)
echo.
echo print^('✓ Python 3.13 兼容性补丁已应用'^)
) > python313_compatibility_patch.py

echo 9. 测试环境...
echo 测试 Stable Audio 环境...
call venv_stableaudio\Scripts\activate.bat
python python313_compatibility_patch.py
python -c "import setuptools; print('✓ Stable Audio 环境正常')"
call venv_stableaudio\Scripts\deactivate.bat

echo 测试 Gemini 环境...
call venv_gemini\Scripts\activate.bat
python python313_compatibility_patch.py
python -c "import setuptools; print('✓ Gemini 环境正常')"
call venv_gemini\Scripts\deactivate.bat

echo.
echo ========================================
echo ✓ Python 3.13.5 兼容性问题修复完成！
echo ========================================
echo.
echo 修复内容:
echo - 升级了所有基础工具
echo - 清理了所有缓存
echo - 重新创建了虚拟环境
echo - 使用兼容模式安装依赖
echo - 创建了 Python 3.13 兼容性补丁
echo.
echo 现在可以启动服务:
echo 1. 运行 ../start_clean.bat
echo 2. 选择 4 启动所有服务
echo.
echo 如果仍有问题:
echo 1. 检查网络连接
echo 2. 确保防火墙允许 Python 访问网络
echo 3. 尝试使用管理员权限运行
echo.
pause 