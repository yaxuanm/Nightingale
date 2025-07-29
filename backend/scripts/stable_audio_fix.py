#!/usr/bin/env python3
"""
修复 stable-audio-tools 中的 int32 溢出问题
在 Windows 64位系统上，numpy.random.randint 默认使用 int32 类型，
当 high 值超过 int32 范围时会报错。
"""

import os
import shutil
import re

def fix_stable_audio_tools():
    """修复 stable-audio-tools 中的 int32 溢出问题"""
    
    # 找到 stable-audio-tools 的安装路径
    import stable_audio_tools
    package_path = os.path.dirname(stable_audio_tools.__file__)
    generation_file = os.path.join(package_path, "inference", "generation.py")
    
    print(f"找到 stable-audio-tools 路径: {package_path}")
    print(f"修复文件: {generation_file}")
    
    # 备份原文件
    backup_file = generation_file + ".backup"
    if not os.path.exists(backup_file):
        shutil.copy2(generation_file, backup_file)
        print(f"已备份原文件到: {backup_file}")
    
    # 读取文件内容
    with open(generation_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复第33行：添加 dtype=np.int64
    content = re.sub(
        r'seed = seed if seed != -1 else np\\.random\\.randint\\(0, 2\\*\\*32 - 1, dtype=np\\.uint32\\)',
        'seed = seed if seed != -1 else np.random.randint(0, 2**32 - 1, dtype=np.int64)',
        content
    )
    
    # 修复第137行：添加 dtype=np.int64
    content = re.sub(
        r'seed = seed if seed != -1 else np\\.random\\.randint\\(0, 2\\*\\*32 - 1\\)',
        'seed = seed if seed != -1 else np.random.randint(0, 2**32 - 1, dtype=np.int64)',
        content
    )
    
    # 修复第271行：添加 dtype=np.int64
    content = re.sub(
        r'seed = seed if seed != -1 else np\\.random\\.randint\\(0, 2\\*\\*32 - 1\\)',
        'seed = seed if seed != -1 else np.random.randint(0, 2**32 - 1, dtype=np.int64)',
        content
    )
    
    # 写入修复后的文件
    with open(generation_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("修复完成！")
    print("修复内容:")
    print("1. 第33行: 添加 dtype=np.int64")
    print("2. 第137行: 添加 dtype=np.int64") 
    print("3. 第271行: 添加 dtype=np.int64")
    print("\n现在可以重新测试 Stable Audio 功能了。")

def test_fix():
    """测试修复是否有效"""
    print("\n测试修复效果...")
    
    try:
        import numpy as np
        # 测试修复后的 randint 调用
        test_seed = np.random.randint(0, 2**32 - 1, dtype=np.int64)
        print(f"✅ 测试成功: {test_seed}")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=== Stable Audio Tools Int32 溢出修复 ===")
    
    try:
        fix_stable_audio_tools()
        test_fix()
        print("\n🎉 修复完成！现在可以正常使用 Stable Audio 功能了。")
    except Exception as e:
        print(f"❌ 修复过程中出现错误: {e}")
        print("请检查文件权限或手动修复。") 