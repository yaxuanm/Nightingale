import os

def fix_file_encoding(file_path):
    """修复文件编码，移除BOM并转换为UTF-8"""
    print(f"修复文件编码: {file_path}")
    
    # 读取文件内容
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # 检查是否有UTF-16 BOM
    if content.startswith(b'\xff\xfe'):  # UTF-16 LE BOM
        print("  ❌ 发现UTF-16 LE BOM，正在转换...")
        # 移除BOM并解码为UTF-16
        content_without_bom = content[2:]
        try:
            decoded_content = content_without_bom.decode('utf-16le')
            # 重新编码为UTF-8
            utf8_content = decoded_content.encode('utf-8')
            
            # 备份原文件
            backup_path = file_path + '.encoding_backup'
            with open(backup_path, 'wb') as f:
                f.write(content)
            print(f"  📁 原文件已备份为: {backup_path}")
            
            # 写入UTF-8内容
            with open(file_path, 'wb') as f:
                f.write(utf8_content)
            print(f"  ✅ 已转换为UTF-8编码")
            return True
            
        except Exception as e:
            print(f"  ❌ 转换失败: {e}")
            return False
    
    elif content.startswith(b'\xfe\xff'):  # UTF-16 BE BOM
        print("  ❌ 发现UTF-16 BE BOM，正在转换...")
        content_without_bom = content[2:]
        try:
            decoded_content = content_without_bom.decode('utf-16be')
            utf8_content = decoded_content.encode('utf-8')
            
            backup_path = file_path + '.encoding_backup'
            with open(backup_path, 'wb') as f:
                f.write(content)
            print(f"  📁 原文件已备份为: {backup_path}")
            
            with open(file_path, 'wb') as f:
                f.write(utf8_content)
            print(f"  ✅ 已转换为UTF-8编码")
            return True
            
        except Exception as e:
            print(f"  ❌ 转换失败: {e}")
            return False
    
    else:
        print(f"  ✅ 文件编码正常")
        return False

def main():
    # 需要修复的文件列表
    files_to_fix = [
        "app/services/ai_service.py",
        "app/services/ai_service_backup.py", 
        "app/services/ai_service_old.py",
        "app/services/ai_service_working.py"
    ]
    
    print("🔧 开始修复文件编码...")
    print("=" * 50)
    
    fixed_files = []
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_file_encoding(file_path):
                fixed_files.append(file_path)
        print()
    
    print("=" * 50)
    if fixed_files:
        print(f"✅ 已修复 {len(fixed_files)} 个文件的编码:")
        for file_path in fixed_files:
            print(f"  - {file_path}")
    else:
        print("✅ 所有文件编码都正常")

if __name__ == "__main__":
    main() 