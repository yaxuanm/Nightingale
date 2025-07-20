#!/usr/bin/env python3
"""
设置 Stability AI API Key
"""

import os
import getpass
from pathlib import Path

def set_stability_api_key():
    """设置 Stability AI API Key"""
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    print("🔧 设置 Stability AI API Key")
    print("=" * 50)
    
    # 检查是否已有API key
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'STABILITY_API_KEY' in content:
                print("⚠️  检测到已存在的 STABILITY_API_KEY")
                overwrite = input("是否要覆盖现有的API key? (y/N): ").lower().strip()
                if overwrite != 'y':
                    print("❌ 操作已取消")
                    return
    
    # 获取API key
    print("\n📝 请输入你的 Stability AI API Key:")
    print("你可以在 https://platform.stability.ai/account/keys 获取API key")
    print()
    
    api_key = getpass.getpass("API Key: ").strip()
    
    if not api_key:
        print("❌ API Key 不能为空")
        return
    
    # 写入.env文件
    try:
        # 读取现有内容
        existing_content = ""
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # 检查是否已有STABILITY_API_KEY
        lines = existing_content.split('\n')
        new_lines = []
        stability_key_found = False
        
        for line in lines:
            if line.startswith('STABILITY_API_KEY='):
                new_lines.append(f'STABILITY_API_KEY={api_key}')
                stability_key_found = True
            else:
                new_lines.append(line)
        
        # 如果没有找到，添加新的
        if not stability_key_found:
            new_lines.append(f'STABILITY_API_KEY={api_key}')
        
        # 写入文件
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print(f"✅ API Key 已保存到 {env_file}")
        print("🔧 现在你可以运行测试脚本验证配置:")
        print("   python test_stability_ai.py")
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")

if __name__ == "__main__":
    set_stability_api_key() 