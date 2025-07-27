#!/usr/bin/env python3
"""
测试 Hugging Face Token 设置
"""

import os
import sys

def test_hf_token():
    """测试Hugging Face token是否设置正确"""
    print("=== 测试 Hugging Face Token ===")
    
    # 检查环境变量
    token = os.environ.get('HF_TOKEN') or os.environ.get('HUGGING_FACE_HUB_TOKEN')
    if not token:
        print("❌ 未找到 Hugging Face token")
        print("请运行: python scripts/set_hf_token.py")
        return False
    
    print(f"✓ 找到 token: {token[:10]}...")
    
    # 测试token有效性
    try:
        from huggingface_hub import HfApi
        api = HfApi(token=token)
        user = api.whoami()
        print(f"✓ 认证成功! 用户: {user['name']}")
        
        # 测试模型访问权限
        try:
            from huggingface_hub import model_info
            info = model_info("stabilityai/stable-audio-open-small", token=token)
            print(f"✓ 可以访问模型: {info.modelId}")
            return True
        except Exception as e:
            print(f"❌ 无法访问模型: {e}")
            print("请确保你的账户有访问 stable-audio-open-small 模型的权限")
            return False
            
    except Exception as e:
        print(f"❌ 认证失败: {e}")
        return False

if __name__ == "__main__":
    success = test_hf_token()
    if success:
        print("\n✓ Token 设置正确! 可以运行 Stable Audio 了。")
    else:
        print("\n✗ Token 设置有问题，请检查。")
        sys.exit(1) 