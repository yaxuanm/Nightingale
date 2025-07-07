#!/usr/bin/env python3
"""
简单的 Stable Audio Open Small 测试脚本
"""

import os
import sys
import time
from pathlib import Path

def test_stable_audio_basic():
    """基础测试"""
    print("=== Stable Audio Open Small 基础测试 ===")
    
    try:
        # 添加当前目录到Python路径
        current_dir = Path.cwd()
        sys.path.insert(0, str(current_dir))
        
        # 尝试导入服务
        print("导入 Stable Audio 服务...")
        from app.services.stable_audio_service import stable_audio_service
        
        # 获取模型信息
        print("获取模型信息...")
        info = stable_audio_service.get_model_info()
        print(f"模型名称: {info['model_name']}")
        print(f"设备: {info['device']}")
        print(f"最大时长: {info['max_duration']}秒")
        print(f"已加载: {info['is_loaded']}")
        
        # 加载模型
        print("\n加载模型...")
        start_time = time.time()
        stable_audio_service.load_model()
        load_time = time.time() - start_time
        print(f"模型加载完成，耗时: {load_time:.2f}秒")
        
        # 测试音频生成
        print("\n生成测试音频...")
        test_prompts = [
            "128 BPM tech house drum loop",
            "peaceful rain sounds with distant thunder",
            "gentle ocean waves crashing on the shore"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n测试 {i}: {prompt}")
            
            start_time = time.time()
            audio_path = stable_audio_service.generate_audio(prompt, duration=3.0)
            generation_time = time.time() - start_time
            
            if os.path.exists(audio_path):
                file_size = os.path.getsize(audio_path)
                print(f"✓ 生成成功!")
                print(f"  文件: {audio_path}")
                print(f"  大小: {file_size} bytes")
                print(f"  时间: {generation_time:.2f}秒")
            else:
                print("✗ 生成失败")
                return False
        
        print("\n=== 所有测试通过! ===")
        return True
        
    except ImportError as e:
        print(f"✗ 导入错误: {e}")
        print("请确保已安装 stable-audio-tools 和 einops:")
        print("pip install stable-audio-tools einops")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_integration():
    """测试API集成"""
    print("\n=== API集成测试 ===")
    
    try:
        import requests
        import json
        
        # 测试模型信息API
        print("测试模型信息API...")
        response = requests.get("http://localhost:8000/api/stable-audio-info")
        if response.status_code == 200:
            info = response.json()
            print(f"✓ API响应: {json.dumps(info, indent=2, ensure_ascii=False)}")
        else:
            print(f"✗ API请求失败: {response.status_code}")
            return False
        
        # 测试音频生成API
        print("\n测试音频生成API...")
        test_data = {
            "prompt": "128 BPM tech house drum loop",
            "duration": 3.0,
            "steps": 8,
            "cfg_scale": 1.0,
            "sampler_type": "pingpong"
        }
        
        response = requests.post(
            "http://localhost:8000/api/generate-stable-audio",
            json=test_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 生成成功!")
            print(f"  音频URL: {result['audio_url']}")
            print(f"  生成时间: {result['generation_time']:.2f}秒")
            print(f"  文件大小: {result['file_size']} bytes")
        else:
            print(f"✗ 生成失败: {response.status_code}")
            print(f"  错误: {response.text}")
            return False
        
        print("\n=== API集成测试通过! ===")
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到API服务器")
        print("请确保后端服务器正在运行: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"✗ API测试失败: {e}")
        return False

def main():
    """主函数"""
    print("Stable Audio Open Small 简单测试")
    print("=" * 40)
    
    # 检查工作目录
    current_dir = Path.cwd()
    print(f"工作目录: {current_dir}")
    
    # 检查必要目录
    audio_output_dir = current_dir / "audio_output"
    if not audio_output_dir.exists():
        audio_output_dir.mkdir(exist_ok=True)
        print(f"创建目录: {audio_output_dir}")
    
    # 运行基础测试
    if test_stable_audio_basic():
        print("\n基础测试通过!")
        
        # 询问是否测试API
        api_choice = input("\n是否测试API集成? (y/n): ").lower().strip()
        if api_choice in ['y', 'yes']:
            test_api_integration()
    else:
        print("\n基础测试失败!")
        print("\n可能的解决方案:")
        print("1. 安装依赖: pip install stable-audio-tools einops")
        print("2. 确保在正确的虚拟环境中")
        print("3. 检查Python版本 (建议3.8+)")
        print("4. 检查CUDA环境 (如果使用GPU)")

if __name__ == "__main__":
    main() 