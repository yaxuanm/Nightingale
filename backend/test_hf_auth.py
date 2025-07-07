#!/usr/bin/env python3
"""
Hugging Face 认证测试脚本
"""

import os
import sys
from huggingface_hub import HfApi, login
import getpass

def test_hf_auth():
    """测试Hugging Face认证"""
    print("=== Hugging Face 认证测试 ===")
    
    # 方法1: 检查环境变量
    token = os.getenv('HF_TOKEN')
    if token:
        print("✓ 找到环境变量 HF_TOKEN")
        try:
            api = HfApi(token=token)
            user = api.whoami()
            print(f"✓ 认证成功! 用户: {user['name']}")
            return True
        except Exception as e:
            print(f"✗ 环境变量token无效: {e}")
    
    # 方法2: 手动输入token
    print("\n请输入你的Hugging Face token:")
    print("1. 访问 https://huggingface.co/settings/tokens")
    print("2. 创建新的token或复制现有token")
    print("3. 粘贴到下面:")
    
    try:
        token = getpass.getpass("Token: ")
        if token:
            api = HfApi(token=token)
            user = api.whoami()
            print(f"✓ 认证成功! 用户: {user['name']}")
            
            # 保存到环境变量
            os.environ['HF_TOKEN'] = token
            print("✓ Token已保存到环境变量")
            return True
        else:
            print("✗ 未输入token")
            return False
    except Exception as e:
        print(f"✗ 认证失败: {e}")
        return False

def test_model_access():
    """测试模型访问权限"""
    print("\n=== 测试模型访问权限 ===")
    
    try:
        from stable_audio_tools.models.pretrained import get_pretrained_model
        
        print("尝试访问 Stable Audio Open Small 模型...")
        model, config = get_pretrained_model("stabilityai/stable-audio-open-small")
        print("✓ 成功访问模型!")
        print(f"模型配置: {config}")
        return True
    except Exception as e:
        print(f"✗ 模型访问失败: {e}")
        return False

if __name__ == "__main__":
    print("Hugging Face 认证测试")
    print("=" * 50)
    
    # 测试认证
    auth_success = test_hf_auth()
    
    if auth_success:
        # 测试模型访问
        test_model_access()
    else:
        print("\n请先完成认证，然后重新运行此脚本")
        sys.exit(1) 