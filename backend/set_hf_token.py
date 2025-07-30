#!/usr/bin/env python3
"""
设置 Hugging Face Token
"""

import os
import getpass
from pathlib import Path

def set_hf_token():
    """设置Hugging Face token"""
    print("🔧 设置 Hugging Face Token")
    print("=" * 50)
    
    # 获取项目根目录
    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    
    # 检查是否已有HF_TOKEN
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'HF_TOKEN' in content:
                print("⚠️  检测到已存在的 HF_TOKEN")
                overwrite = input("是否要覆盖现有的token? (y/N): ").lower().strip()
                if overwrite != 'y':
                    print("❌ 操作已取消")
                    return
    
    print("\n📝 请按照以下步骤获取 Hugging Face Token:")
    print("1. 访问 https://huggingface.co/settings/tokens")
    print("2. 登录你的Hugging Face账户")
    print("3. 创建新的token或复制现有token")
    print("4. 确保你有访问 stable-audio-open-small 模型的权限")
    print()
    
    token = getpass.getpass("请输入你的Hugging Face token: ").strip()
    
    if not token:
        print("❌ Token 不能为空")
        return
    
    # 测试token
    try:
        # 尝试导入 huggingface_hub
        try:
            from huggingface_hub import HfApi
        except ImportError:
            print("⚠️  huggingface_hub 模块未安装，正在尝试安装...")
            import subprocess
            import sys
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub"])
                from huggingface_hub import HfApi
                print("✅ huggingface_hub 安装成功")
            except Exception as install_error:
                print(f"❌ 安装失败: {install_error}")
                print("请手动安装: pip install huggingface_hub")
                return
        
        api = HfApi(token=token)
        user = api.whoami()
        print(f"✅ 认证成功! 用户: {user['name']}")
    except Exception as e:
        print(f"❌ 认证失败: {e}")
        print("请检查token是否正确，并确保有访问模型的权限。")
        return
    
    # 写入.env文件
    try:
        # 读取现有内容
        existing_content = ""
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # 检查是否已有HF_TOKEN
        lines = existing_content.split('\n')
        new_lines = []
        hf_token_found = False
        
        for line in lines:
            if line.startswith('HF_TOKEN='):
                new_lines.append(f'HF_TOKEN={token}')
                hf_token_found = True
            else:
                new_lines.append(line)
        
        # 如果没有找到，添加新的
        if not hf_token_found:
            new_lines.append(f'HF_TOKEN={token}')
        
        # 写入文件
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print(f"✅ Token 已保存到 {env_file}")
        print("🔧 现在你可以运行Stable Audio服务了!")
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")

if __name__ == "__main__":
    set_hf_token() 