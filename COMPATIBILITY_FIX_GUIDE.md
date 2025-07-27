# Python 3.13 兼容性修复指南

## 问题背景

你的项目有两个虚拟环境，它们有严重的依赖版本冲突：

### Stable Audio 环境
- `protobuf==3.19.6` (必需，兼容 Stable Audio)
- `numpy==1.23.5` (修复 int32 溢出问题)
- 其他特定版本的依赖

### Gemini 环境
- `protobuf==4.25.8` (必需，兼容 Gemini API)
- `numpy==2.2.6` (最新版本)
- 其他特定版本的依赖

## 修复方案对比

### 方案1：兼容性修复（推荐）
**选项 9: Compatibility Fix (Keep original versions)**

**特点**：
- ✅ 保持所有原有包版本不变
- ✅ 只修复 Python 3.13 兼容性问题
- ✅ 解决 `pkgutil.ImpImporter` 错误
- ✅ 不影响现有功能
- ✅ 最小化风险

**适用场景**：
- 你的现有环境已经工作正常
- 只需要解决 Python 3.13 兼容性问题
- 不想改变任何包版本

### 方案2：智能安装
**选项 8: Smart Install**

**特点**：
- ⚠️ 会重新安装所有依赖
- ⚠️ 可能改变某些包版本
- ✅ 彻底解决所有兼容性问题
- ✅ 创建全局兼容性补丁

**适用场景**：
- 环境损坏严重
- 需要彻底重建环境
- 可以接受版本变化

### 方案3：紧急修复
**选项 7: Emergency Fix**

**特点**：
- ⚠️ 删除并重建虚拟环境
- ⚠️ 重新安装所有依赖
- ✅ 快速解决当前问题
- ⚠️ 可能改变包版本

**适用场景**：
- 环境完全无法使用
- 需要快速恢复功能
- 可以接受版本变化

## 推荐使用方案

**对于你的情况，强烈推荐使用方案1**：

```bash
./start_clean.bat
# 选择 9 (Compatibility Fix)
```

## 方案1 的工作原理

### 1. 兼容性补丁
```python
# 只修复兼容性问题，不改变版本
if not hasattr(pkgutil, 'ImpImporter'):
    class ImpImporter:
        def __init__(self):
            pass
        def find_module(self, fullname, path=None):
            return None  # 不处理任何模块
        def load_module(self, fullname):
            return None  # 不加载任何模块
    pkgutil.ImpImporter = ImpImporter
```

### 2. setuptools 修复
```python
# 只修复兼容性，保持版本
if hasattr(setuptools, '_distutils') and setuptools._distutils is not None:
    old_distutils = setuptools._distutils
    setuptools._distutils = None  # 临时禁用
    # 保留恢复机制
    setuptools._restore_distutils = lambda: setattr(setuptools, '_distutils', old_distutils)
```

### 3. 版本保持验证
```python
# 验证版本保持不变
import protobuf
print(f"protobuf 版本: {protobuf.__version__}")  # 应该保持原版本

import numpy
print(f"numpy 版本: {numpy.__version__}")  # 应该保持原版本
```

## 执行步骤

### 1. 运行兼容性修复
```bash
./start_clean.bat
# 选择 9 (Compatibility Fix)
```

### 2. 验证修复结果
脚本会自动验证：
- ✅ 兼容性补丁是否加载
- ✅ setuptools 是否正常
- ✅ pkg_resources 是否正常
- ✅ protobuf 版本是否保持
- ✅ numpy 版本是否保持

### 3. 启动服务
```bash
./start_clean.bat
# 选择 4 (Start All Services)
```

## 预期结果

修复后，你应该看到：

### Stable Audio 环境
```
✓ 兼容性补丁加载成功
✓ setuptools 导入成功
✓ pkg_resources 导入成功
✓ protobuf 3.19.6 正常
✓ numpy 1.23.5 正常
```

### Gemini 环境
```
✓ 兼容性补丁加载成功
✓ setuptools 导入成功
✓ pkg_resources 导入成功
✓ protobuf 4.25.8 正常
✓ numpy 2.2.6 正常
```

## 如果仍有问题

### 1. 检查网络连接
```bash
ping pypi.org
```

### 2. 使用管理员权限
以管理员身份运行命令提示符

### 3. 检查防火墙
确保 Python 可以访问网络

### 4. 清理缓存
```bash
python -m pip cache purge
```

## 故障排除

### 问题：版本被改变了
**解决方案**：
1. 重新运行兼容性修复
2. 检查 requirements 文件是否正确
3. 手动恢复特定版本

### 问题：兼容性补丁未加载
**解决方案**：
1. 检查 `compatibility_patch.py` 文件是否存在
2. 重新运行修复脚本
3. 手动导入补丁

### 问题：服务启动失败
**解决方案**：
1. 检查虚拟环境是否正确激活
2. 验证依赖是否完整
3. 查看错误日志

## 总结

**推荐使用方案1（兼容性修复）**，因为：
1. 最小化风险
2. 保持现有功能
3. 只解决兼容性问题
4. 不影响版本依赖

这样可以确保你的 Gemini 和 Stable Audio 环境继续正常工作，同时解决 Python 3.13 的兼容性问题。 