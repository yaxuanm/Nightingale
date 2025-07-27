import sys 
import os 
 
# Python 3.12+ compatibility patch 
def apply_compatibility_patch(): 
    try: 
        import pkgutil 
        if not hasattr(pkgutil, 'ImpImporter'): 
            class ImpImporter: 
                pass 
            pkgutil.ImpImporter = ImpImporter 
            print("✓ ImpImporter patch applied") 
    except Exception as e: 
        print(f"Patch failed: {e}") 
 
# Set compatibility environment variables 
os.environ['PYTHONHASHSEED'] = '0' 
os.environ['PYTHONDONTWRITEBYTECODE'] = '1' 
os.environ['PYTHONUTF8'] = '1' 
os.environ['PIP_NO_CACHE_DIR'] = '1' 
 
# Apply patch 
apply_compatibility_patch() 
print("✓ Compatibility setup completed") 
