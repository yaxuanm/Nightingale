#!/usr/bin/env python3
"""
Test script to verify Supabase upload functionality
"""

import os
import sys
import asyncio
import wave
import struct

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.storage_service import storage_service

def create_test_audio_file():
    """Create a test audio file for upload testing"""
    test_file_path = os.path.join(os.path.dirname(__file__), "test_audio.wav")
    
    # 创建1秒的测试音频文件
    sample_rate = 44100
    duration = 1.0
    num_samples = int(sample_rate * duration)
    
    with wave.open(test_file_path, 'w') as wav_file:
        wav_file.setnchannels(1)  # 单声道
        wav_file.setsampwidth(2)   # 16位
        wav_file.setframerate(sample_rate)
        
        # 写入简单的正弦波数据
        import math
        for i in range(num_samples):
            # 生成440Hz的正弦波
            sample = int(32767 * 0.1 * math.sin(2 * math.pi * 440 * i / sample_rate))
            wav_file.writeframes(struct.pack('<h', sample))
    
    print(f"Created test audio file: {test_file_path}")
    return test_file_path

async def test_supabase_upload():
    """Test Supabase upload functionality"""
    print("Testing Supabase upload functionality...")
    
    try:
        # 创建测试音频文件
        test_file = create_test_audio_file()
        
        # 测试上传
        print(f"Attempting to upload: {test_file}")
        result = await storage_service.upload_audio(test_file, "test_audio_description")
        
        if result:
            print(f"✅ Upload successful! URL: {result}")
            return True
        else:
            print("❌ Upload failed - no URL returned")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

async def test_placeholder_upload():
    """Test upload with non-existent file (should create placeholder)"""
    print("\nTesting upload with non-existent file...")
    
    try:
        # 尝试上传一个不存在的文件
        non_existent_file = "non_existent_file.wav"
        result = await storage_service.upload_audio(non_existent_file, "placeholder_test")
        
        if result:
            print(f"✅ Placeholder upload successful! URL: {result}")
            return True
        else:
            print("❌ Placeholder upload failed")
            return False
            
    except Exception as e:
        print(f"❌ Placeholder upload error: {e}")
        return False

async def main():
    """Main test function"""
    print("=== Supabase Upload Test ===")
    
    # 测试正常上传
    success1 = await test_supabase_upload()
    
    # 测试占位符上传
    success2 = await test_placeholder_upload()
    
    print(f"\n=== Test Results ===")
    print(f"Normal upload: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Placeholder upload: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 or success2:
        print("🎉 At least one upload method is working!")
    else:
        print("💥 All upload methods failed")

if __name__ == "__main__":
    asyncio.run(main()) 