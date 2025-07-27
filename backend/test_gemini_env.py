#!/usr/bin/env python3
"""
Gemini虚拟环境测试脚本
测试Python版本、基本包安装和Gemini相关功能
"""

import sys
import os
import subprocess
import importlib

def test_python_version():
    """测试Python版本"""
    print("=" * 50)
    print("1. Python版本测试")
    print("=" * 50)
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print(f"虚拟环境: {'是' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else '否'}")
    return True

def test_basic_imports():
    """测试基本包导入"""
    print("\n" + "=" * 50)
    print("2. 基本包导入测试")
    print("=" * 50)
    
    basic_packages = [
        'os', 'sys', 'json', 'requests', 'urllib', 'datetime',
        'logging', 'pathlib', 'typing', 'asyncio'
    ]
    
    failed_imports = []
    for package in basic_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package}")
        except ImportError as e:
            print(f"✗ {package}: {e}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0

def test_gemini_packages():
    """测试Gemini相关包"""
    print("\n" + "=" * 50)
    print("3. Gemini相关包测试")
    print("=" * 50)
    
    gemini_packages = [
        'google.generativeai',
        'google.ai.generativelanguage',
        'google.cloud.aiplatform'
    ]
    
    failed_imports = []
    for package in gemini_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package}")
        except ImportError as e:
            print(f"✗ {package}: {e}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0

def test_web_frameworks():
    """测试Web框架"""
    print("\n" + "=" * 50)
    print("4. Web框架测试")
    print("=" * 50)
    
    web_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'starlette'
    ]
    
    failed_imports = []
    for package in web_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package}")
        except ImportError as e:
            print(f"✗ {package}: {e}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0

def test_audio_packages():
    """测试音频处理包"""
    print("\n" + "=" * 50)
    print("5. 音频处理包测试")
    print("=" * 50)
    
    audio_packages = [
        'pydub',
        'librosa',
        'soundfile',
        'numpy',
        'scipy'
    ]
    
    failed_imports = []
    for package in audio_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package}")
        except ImportError as e:
            print(f"✗ {package}: {e}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0

def test_environment_variables():
    """测试环境变量"""
    print("\n" + "=" * 50)
    print("6. 环境变量测试")
    print("=" * 50)
    
    required_vars = [
        'GOOGLE_API_KEY',
        'GEMINI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {'*' * len(value)} (已设置)")
        else:
            print(f"✗ {var}: 未设置")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def test_simple_gemini_call():
    """测试简单的Gemini API调用"""
    print("\n" + "=" * 50)
    print("7. Gemini API测试")
    print("=" * 50)
    
    try:
        import google.generativeai as genai
        
        # 检查API密钥
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("✗ 未找到Gemini API密钥")
            return False
        
        # 配置API
        genai.configure(api_key=api_key)
        
        # 创建模型
        model = genai.GenerativeModel('gemini-pro')
        
        # 简单测试
        response = model.generate_content("Hello, say 'Gemini test successful' in Chinese")
        
        if response.text:
            print(f"✓ Gemini API调用成功")
            print(f"响应: {response.text}")
            return True
        else:
            print("✗ Gemini API调用失败: 无响应")
            return False
            
    except Exception as e:
        print(f"✗ Gemini API测试失败: {e}")
        return False

def test_pip_list():
    """显示已安装的包"""
    print("\n" + "=" * 50)
    print("8. 已安装包列表")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("已安装的包:")
            print(result.stdout)
        else:
            print(f"获取包列表失败: {result.stderr}")
    except Exception as e:
        print(f"获取包列表时出错: {e}")

def main():
    """主测试函数"""
    print("🚀 Gemini虚拟环境测试开始")
    print(f"测试时间: {__import__('datetime').datetime.now()}")
    
    # 运行所有测试
    tests = [
        test_python_version,
        test_basic_imports,
        test_gemini_packages,
        test_web_frameworks,
        test_audio_packages,
        test_environment_variables,
        test_simple_gemini_call
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"测试 {test.__name__} 时出错: {e}")
            results.append(False)
    
    # 显示包列表
    test_pip_list()
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    
    test_names = [
        "Python版本",
        "基本包导入",
        "Gemini相关包",
        "Web框架",
        "音频处理包",
        "环境变量",
        "Gemini API调用"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{i+1}. {name}: {status}")
    
    passed = sum(results)
    total = len(results)
    print(f"\n总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！Gemini虚拟环境配置正确。")
    else:
        print("⚠️  部分测试失败，请检查相关配置。")

if __name__ == "__main__":
    main() 