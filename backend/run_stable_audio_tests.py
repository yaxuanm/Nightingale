#!/usr/bin/env python3
"""
Stable Audio Open Small 模型测试运行脚本
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def install_dependencies():
    """安装必要的依赖"""
    print("=== 安装依赖 ===")
    
    # 检查是否在虚拟环境中
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠ 建议在虚拟环境中运行测试")
    
    # 安装 stable-audio-tools
    try:
        print("安装 stable-audio-tools...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "stable-audio-tools"])
        print("✓ stable-audio-tools 安装成功")
    except subprocess.CalledProcessError as e:
        print(f"✗ stable-audio-tools 安装失败: {e}")
        return False
    
    # 安装 einops
    try:
        print("安装 einops...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "einops"])
        print("✓ einops 安装成功")
    except subprocess.CalledProcessError as e:
        print(f"✗ einops 安装失败: {e}")
        return False
    
    # 安装 psutil (用于资源监控)
    try:
        print("安装 psutil...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        print("✓ psutil 安装成功")
    except subprocess.CalledProcessError as e:
        print(f"✗ psutil 安装失败: {e}")
        return False
    
    return True

def check_environment():
    """检查环境"""
    print("=== 环境检查 ===")
    
    # 检查 Python 版本
    python_version = sys.version_info
    print(f"Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("⚠ 建议使用 Python 3.8 或更高版本")
    
    # 检查 CUDA 可用性
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print(f"✓ CUDA 可用: {torch.cuda.get_device_name(0)}")
        else:
            print("⚠ CUDA 不可用，将使用 CPU")
    except ImportError:
        print("⚠ PyTorch 未安装")
    
    # 检查工作目录
    current_dir = Path.cwd()
    print(f"当前工作目录: {current_dir}")
    
    # 检查必要的目录
    required_dirs = ["audio_output", "tests"]
    for dir_name in required_dirs:
        dir_path = current_dir / dir_name
        if dir_path.exists():
            print(f"✓ 目录存在: {dir_name}")
        else:
            print(f"⚠ 目录不存在: {dir_name}")
            dir_path.mkdir(exist_ok=True)
            print(f"  已创建目录: {dir_name}")

def run_basic_test():
    """运行基础测试"""
    print("\n=== 基础功能测试 ===")
    
    try:
        # 导入服务
        sys.path.append(str(Path.cwd()))
        from app.services.stable_audio_service import stable_audio_service
        
        # 测试模型信息
        print("获取模型信息...")
        info = stable_audio_service.get_model_info()
        print(f"模型名称: {info['model_name']}")
        print(f"最大时长: {info['max_duration']}秒")
        print(f"设备: {info['device']}")
        
        # 测试模型加载
        print("\n加载模型...")
        start_time = time.time()
        stable_audio_service.load_model()
        load_time = time.time() - start_time
        print(f"模型加载完成，耗时: {load_time:.2f}秒")
        
        # 测试音频生成
        print("\n生成测试音频...")
        test_prompt = "128 BPM tech house drum loop"
        start_time = time.time()
        audio_path = stable_audio_service.generate_audio(test_prompt, duration=3.0)
        generation_time = time.time() - start_time
        
        if os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path)
            print(f"✓ 音频生成成功!")
            print(f"  文件路径: {audio_path}")
            print(f"  文件大小: {file_size} bytes")
            print(f"  生成时间: {generation_time:.2f}秒")
        else:
            print("✗ 音频文件未生成")
            return False
        
        return True
        
    except ImportError as e:
        print(f"✗ 导入错误: {e}")
        print("请确保已安装所有依赖")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def run_performance_test():
    """运行性能测试"""
    print("\n=== 性能测试 ===")
    
    try:
        from app.services.stable_audio_service import stable_audio_service
        import psutil
        
        process = psutil.Process()
        
        # 记录基础资源使用
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"基础内存使用: {baseline_memory:.2f} MB")
        
        # 测试不同提示词的生成时间
        test_prompts = [
            "128 BPM tech house drum loop",
            "peaceful rain sounds with distant thunder",
            "gentle ocean waves crashing on the shore"
        ]
        
        total_time = 0
        total_size = 0
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n测试 {i}/{len(test_prompts)}: {prompt}")
            
            start_time = time.time()
            audio_path = stable_audio_service.generate_audio(prompt, duration=3.0)
            generation_time = time.time() - start_time
            
            file_size = os.path.getsize(audio_path) if os.path.exists(audio_path) else 0
            
            total_time += generation_time
            total_size += file_size
            
            print(f"  生成时间: {generation_time:.2f}秒")
            print(f"  文件大小: {file_size} bytes")
        
        # 计算平均值
        avg_time = total_time / len(test_prompts)
        avg_size = total_size / len(test_prompts)
        
        print(f"\n性能统计:")
        print(f"  平均生成时间: {avg_time:.2f}秒")
        print(f"  平均文件大小: {avg_size:.0f} bytes")
        
        # 记录最终资源使用
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - baseline_memory
        print(f"  内存增加: {memory_increase:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"✗ 性能测试失败: {e}")
        return False

def main():
    """主函数"""
    print("Stable Audio Open Small 模型测试")
    print("=" * 50)
    
    # 检查环境
    check_environment()
    
    # 询问是否安装依赖
    install_choice = input("\n是否安装/更新依赖? (y/n): ").lower().strip()
    if install_choice in ['y', 'yes']:
        if not install_dependencies():
            print("依赖安装失败，退出测试")
            return
    
    # 运行基础测试
    if not run_basic_test():
        print("基础测试失败，退出")
        return
    
    # 询问是否运行性能测试
    perf_choice = input("\n是否运行性能测试? (y/n): ").lower().strip()
    if perf_choice in ['y', 'yes']:
        run_performance_test()
    
    print("\n=== 测试完成 ===")
    print("生成的音频文件保存在 audio_output 目录中")

if __name__ == "__main__":
    main() 