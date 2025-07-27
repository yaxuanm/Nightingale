# Python 3.13 兼容性问题修复指南

## 问题原因

你遇到的 `pkgutil.ImpImporter` 错误是因为：

1. **Python 3.12+ 的变化**：`pkgutil.ImpImporter` 在 Python 3.12 中被完全移除
2. **旧版本 setuptools**：某些依赖包仍在使用旧版本的 setuptools，它们尝试导入已被移除的功能
3. **依赖包版本冲突**：不同包之间的版本不兼容

## 快速解决方案

### 方案1：使用紧急修复脚本（推荐）

```bash
# 运行主启动脚本
./start_clean.bat

# 选择 7 (Emergency Fix)
```

### 方案2：手动运行修复脚本

```bash
# 直接运行紧急修复脚本
cd backend
scripts/emergency_fix.bat
```

### 方案3：手动修复步骤

```bash
# 1. 设置环境变量
set PYTHONHASHSEED=0
set PYTHONDONTWRITEBYTECODE=1
set PYTHONUTF8=1
set PIP_NO_CACHE_DIR=1

# 2. 升级基础工具
python -m pip install --upgrade pip setuptools wheel --no-cache-dir

# 3. 清理缓存
python -m pip cache purge

# 4. 删除现有虚拟环境
rmdir /s /q venv_stableaudio
rmdir /s /q venv_gemini

# 5. 重新创建环境
python -m venv venv_stableaudio
python -m venv venv_gemini

# 6. 安装依赖
call venv_stableaudio\Scripts\activate.bat
pip install -r requirements-stable-audio.txt --no-cache-dir --force-reinstall
call venv_stableaudio\Scripts\deactivate.bat

call venv_gemini\Scripts\activate.bat
pip install -r requirements-gemini-utf8.txt --no-cache-dir --force-reinstall
call venv_gemini\Scripts\deactivate.bat
```

## 为什么会出现这个问题？

1. **Python 版本更新**：Python 3.12+ 移除了旧的导入机制
2. **包管理器变化**：pip 和 setuptools 的更新导致兼容性问题
3. **依赖包滞后**：某些包还没有完全适配 Python 3.13

## 预防措施

1. **使用虚拟环境**：每个项目使用独立的虚拟环境
2. **固定版本**：在 requirements 文件中固定关键包的版本
3. **定期更新**：定期更新依赖包到兼容版本

## 验证修复

修复完成后，运行以下命令验证：

```bash
# 测试 Stable Audio 环境
call venv_stableaudio\Scripts\activate.bat
python -c "import setuptools; print('✓ Stable Audio 环境正常')"
call venv_stableaudio\Scripts\deactivate.bat

# 测试 Gemini 环境
call venv_gemini\Scripts\activate.bat
python -c "import setuptools; print('✓ Gemini 环境正常')"
call venv_gemini\Scripts\deactivate.bat
```

## 如果问题仍然存在

1. **使用管理员权限**：以管理员身份运行命令提示符
2. **检查网络**：确保可以访问 PyPI
3. **降级 Python**：如果问题持续，考虑使用 Python 3.11
4. **清理系统**：删除所有 Python 缓存和临时文件

## 相关文件

- `backend/scripts/emergency_fix.bat` - 紧急修复脚本
- `backend/scripts/fix_python313.bat` - 完整修复脚本
- `start_clean.bat` - 主启动脚本（包含修复选项） 