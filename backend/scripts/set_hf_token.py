#!/usr/bin/env python3
"""
设置 Hugging Face Token
"""

import os
import sys

def set_hf_token():
    """设置Hugging Face token"""
    print("=== 设置 Hugging Face Token ===")
    print("\n请按照以下步骤操作:")
    print("1. 访问 https://huggingface.co/settings/tokens")
    print("2. 登录你的Hugging Face账户")
    print("3. 创建新的token或复制现有token")
    print("4. 确保你有访问 stable-audio-open-small 模型的权限")
    print("5. 将token粘贴到下面:")
    
    token = input("\n请输入你的Hugging Face token: ").strip()
    
    if not token:
        print("✗ 未输入token")
        return False
    
    # 设置环境变量
    os.environ['HF_TOKEN'] = token
    os.environ['HUGGING_FACE_HUB_TOKEN'] = token
    
    print("✓ Token已设置到环境变量")
    
    # 测试token
    try:
        from huggingface_hub import HfApi
        api = HfApi(token=token)
        user = api.whoami()
        print(f"✓ 认证成功! 用户: {user['name']}")
        return True
    except Exception as e:
        print(f"✗ 认证失败: {e}")
        return False

if __name__ == "__main__":
    success = set_hf_token()
    if success:
        print("\n✓ Token设置成功! 现在可以运行测试了。")
        print("运行: python test_stable_audio_simple.py")
    else:
        print("\n✗ Token设置失败，请检查token是否正确。")
        sys.exit(1) 