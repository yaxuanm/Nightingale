# Python 3.13 兼容性测试指南

## 问题背景

你遇到的 `pkgutil.ImpImporter` 错误是因为 Python 3.13 移除了旧的导入机制，但某些依赖包仍在使用这些已移除的功能。

## 安全测试方案

为了保护你现有的虚拟环境，我们提供了以下**安全的测试方案**：

### 方案1：完整环境测试（推荐）

**特点**：
- ✅ 创建新的测试环境（`test_venv_stableaudio`, `test_venv_gemini`）
- ✅ 完全不影响你现有的虚拟环境
- ✅ 测试完整的依赖安装流程
- ✅ 验证所有关键包的兼容性

**使用方法**：
```bash
./start_clean.bat
# 选择 7 (Test Python 3.13 Compatibility - Safe)
```

### 方案2：单包测试

**特点**：
- ✅ 创建临时测试环境
- ✅ 测试单个包的安装
- ✅ 快速验证修复方案
- ✅ 不影响现有环境

**使用方法**：
```bash
./start_clean.bat
# 选择 8 (Test Single Package Installation)
# 输入要测试的包名（如：numpy, protobuf）
```

## 测试内容

### 环境变量设置
```bash
set PYTHONHASHSEED=0
set PYTHONDONTWRITEBYTECODE=1
set PYTHONUTF8=1
set PIP_NO_CACHE_DIR=1
```

### 工具升级
```bash
python -m pip install --upgrade pip setuptools wheel --no-cache-dir
```

### 预编译包安装
```bash
pip install --only-binary=all package_name --no-cache-dir
```

## 预期结果

### 成功情况
```
✓ setuptools 正常
✓ pkg_resources 正常
✓ numpy 1.23.5 正常
✓ protobuf 3.19.6 正常
```

### 失败情况
如果仍然出现 `pkgutil.ImpImporter` 错误，说明需要进一步调整修复方案。

## 测试后的操作

### 如果测试成功
1. **保留测试环境**：可以作为备份使用
2. **删除测试环境**：`rmdir /s /q test_venv_stableaudio test_venv_gemini`
3. **应用到生产环境**：使用相同的修复方案更新你的实际环境

### 如果测试失败
1. **分析错误信息**：查看具体的错误原因
2. **调整修复方案**：根据错误信息修改修复脚本
3. **重新测试**：使用调整后的方案再次测试

## 故障排除

### 网络问题
```bash
# 检查网络连接
ping pypi.org
```

### 权限问题
```bash
# 使用管理员权限运行
# 右键点击命令提示符 -> 以管理员身份运行
```

### 缓存问题
```bash
# 清理 pip 缓存
python -m pip cache purge
```

## 修复方案说明

### 核心问题
Python 3.13 移除了 `pkgutil.ImpImporter`，但某些旧版本的 setuptools 和 pkg_resources 仍在使用它。

### 解决方案
1. **使用预编译包**：`--only-binary=all` 避免从源码编译
2. **升级工具**：使用最新版本的 pip, setuptools, wheel
3. **设置环境变量**：确保兼容性设置生效
4. **清理缓存**：避免使用缓存的旧版本包

## 安全保证

- ✅ 所有测试脚本都不会修改你现有的虚拟环境
- ✅ 测试环境使用不同的名称（`test_venv_*`）
- ✅ 临时环境会自动清理
- ✅ 可以随时取消测试

## 下一步

1. 运行测试脚本验证修复方案
2. 根据测试结果调整修复策略
3. 如果测试成功，可以安全地应用到生产环境
4. 如果测试失败，分析错误并改进修复方案

这样你就可以安全地测试兼容性修复，而不用担心影响你现有的工作环境！ 