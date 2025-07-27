import os
import glob

def check_and_fix_file(file_path):
    """检查并修复文件中的空字节"""
    print(f"检查文件: {file_path}")
    
    # 读取文件内容
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # 检查是否有空字节
    null_positions = [i for i, byte in enumerate(content) if byte == 0]
    
    if null_positions:
        print(f"  ❌ 发现 {len(null_positions)} 个空字节位置: {null_positions[:10]}...")
        
        # 清理空字节
        cleaned_content = content.replace(b'\x00', b'')
        
        # 备份原文件
        backup_path = file_path + '.backup'
        with open(backup_path, 'wb') as f:
            f.write(content)
        print(f"  📁 原文件已备份为: {backup_path}")
        
        # 写入清理后的内容
        with open(file_path, 'wb') as f:
            f.write(cleaned_content)
        print(f"  ✅ 已清理空字节")
        
        return True
    else:
        print(f"  ✅ 文件正常，没有空字节")
        return False

def main():
    # 检查所有Python文件
    python_files = []
    python_files.extend(glob.glob("app/**/*.py", recursive=True))
    python_files.extend(glob.glob("scripts/**/*.py", recursive=True))
    python_files.extend(glob.glob("*.py"))
    
    print("🔍 开始检查Python文件中的空字节...")
    print("=" * 50)
    
    fixed_files = []
    for file_path in python_files:
        if os.path.exists(file_path):
            if check_and_fix_file(file_path):
                fixed_files.append(file_path)
        print()
    
    print("=" * 50)
    if fixed_files:
        print(f"✅ 已修复 {len(fixed_files)} 个文件:")
        for file_path in fixed_files:
            print(f"  - {file_path}")
    else:
        print("✅ 所有文件都正常，没有发现空字节")

if __name__ == "__main__":
    main() 