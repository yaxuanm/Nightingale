#!/usr/bin/env python3
"""
Gemini虚拟环境快速测试脚本
"""

import sys
import os

def quick_test():
    print("🚀 Gemini虚拟环境快速测试")
    print("=" * 40)
    
    # 1. 检查Python版本
    print(f"1. Python版本: {sys.version}")
    print(f"   Python路径: {sys.executable}")
    
    # 2. 检查虚拟环境
    is_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print(f"2. 虚拟环境: {'✓ 是' if is_venv else '✗ 否'}")
    
    # 3. 测试基本导入
    print("3. 基本包导入测试:")
    basic_packages = ['os', 'sys', 'json', 'requests']
    for package in basic_packages:
        try:
            __import__(package)
            print(f"   ✓ {package}")
        except ImportError:
            print(f"   ✗ {package}")
    
    # 4. 测试Gemini包
    print("4. Gemini包测试:")
    try:
        import google.generativeai
        print("   ✓ google.generativeai")
    except ImportError:
        print("   ✗ google.generativeai")
    
    # 5. 测试Web框架
    print("5. Web框架测试:")
    web_packages = ['fastapi', 'uvicorn']
    for package in web_packages:
        try:
            __import__(package)
            print(f"   ✓ {package}")
        except ImportError:
            print(f"   ✗ {package}")
    
    # 6. 检查环境变量
    print("6. 环境变量检查:")
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"   ✓ API密钥已设置 ({'*' * len(api_key)})")
    else:
        print("   ✗ API密钥未设置")
    
    print("\n" + "=" * 40)
    print("快速测试完成！")

if __name__ == "__main__":
    quick_test() 