#!/usr/bin/env python3
"""
直接测试 Stable Audio 服务
"""

import os
import sys
import traceback

# 设置环境变量
os.environ['HF_TOKEN'] = 'your-huggingface-token-here'  # 替换为你的token

def test_stable_audio():
    """测试Stable Audio服务"""
    print("🔧 测试 Stable Audio 服务")
    print("=" * 50)
    
    try:
        # 导入服务
        from app.services.stable_audio_service import stable_audio_service
        
        # 测试prompt
        test_prompt = "Forest sounds with bird songs"
        print(f"测试prompt: {test_prompt}")
        
        # 生成音频
        print("开始生成音频...")
        audio_path = stable_audio_service.generate_audio(test_prompt, duration=10.0)
        
        print(f"✅ 音频生成成功: {audio_path}")
        
        # 检查文件是否存在
        if os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path)
            print(f"文件大小: {file_size} bytes")
        else:
            print("❌ 文件不存在")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("详细错误信息:")
        traceback.print_exc()

if __name__ == "__main__":
    test_stable_audio() 