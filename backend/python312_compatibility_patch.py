import sys
import os

# Python 3.12+ 兼容性补丁
def apply_compatibility_patch():
    try:
        import pkgutil
        if not hasattr(pkgutil, 'ImpImporter'):
            # 添加缺失的 ImpImporter
            class ImpImporter:
                pass
            pkgutil.ImpImporter = ImpImporter
            print("✓ 已应用 ImpImporter 补丁")
    except Exception as e:
        print(f"补丁应用失败: {e}")

# 设置兼容性环境变量
os.environ['PYTHONHASHSEED'] = '0'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['PYTHONUTF8'] = '1'
os.environ['PIP_NO_CACHE_DIR'] = '1'

# 应用补丁
apply_compatibility_patch()
print("✓ 兼容性设置完成")
