#!/usr/bin/env python3
"""
一键设置 Stability AI 主要服务 + Gemini Fallback 机制
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

def print_banner():
    """打印欢迎横幅"""
    print("🎨 Stability AI 主要服务 + Gemini Fallback 设置向导")
    print("=" * 60)
    print("这个脚本将帮助你设置 Stability AI 作为主要图片生成服务")
    print("当 Stability AI 失败时，系统会自动切换到 Gemini 作为备用")
    print()

def check_python_dependencies():
    """检查Python依赖"""
    print("🔧 检查Python依赖...")
    
    required_packages = ['requests', 'PIL', 'fastapi']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖已安装")
    return True

def setup_stability_api_key():
    """设置 Stability AI API Key"""
    print("\n🔧 设置 Stability AI API Key...")
    
    # 检查是否已有API key
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'STABILITY_API_KEY' in content:
                print("✅ 检测到已配置的 STABILITY_API_KEY")
                return True
    
    print("📝 需要设置 Stability AI API Key")
    print("请访问: https://platform.stability.ai/account/keys")
    print("获取API Key后，运行: python set_stability_key.py")
    
    # 询问是否现在设置
    response = input("\n是否现在设置API Key? (y/N): ").lower().strip()
    if response == 'y':
        try:
            subprocess.run([sys.executable, "set_stability_key.py"], check=True)
            return True
        except subprocess.CalledProcessError:
            print("❌ 设置失败，请手动运行: python set_stability_key.py")
            return False
    else:
        print("⚠️  请稍后手动设置API Key")
        return False

async def test_stability_integration():
    """测试 Stability AI 集成"""
    print("\n🔧 测试 Stability AI 集成...")
    
    try:
        # 测试 Stability AI 直接调用
        from app.services.stability_image_service import stability_image_service
        
        if not stability_image_service.api_key:
            print("❌ Stability AI API Key 未配置")
            return False
        
        print("✅ API Key 已配置")
        
        # 测试图片生成
        test_description = "A peaceful forest with gentle sunlight"
        result = await stability_image_service.generate_background(test_description)
        
        if result:
            print(f"✅ Stability AI 测试成功: {result}")
            return True
        else:
            print("❌ Stability AI 测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def test_fallback_mechanism():
    """测试 fallback 机制"""
    print("\n🔧 测试 Fallback 机制...")
    
    try:
        from app.services.image_service import image_service
        
        test_description = "A serene mountain lake at sunset"
        result = await image_service.generate_background(test_description)
        
        if result:
            print(f"✅ Fallback 机制测试成功: {result}")
            return True
        else:
            print("❌ Fallback 机制测试失败")
            return False
            
    except Exception as e:
        print(f"❌ Fallback 测试失败: {e}")
        return False

def print_success_message():
    """打印成功消息"""
    print("\n🎉 设置完成！")
    print("=" * 50)
    print("✅ Stability AI 主要服务 + Gemini Fallback 机制已配置")
    print("✅ 系统现在支持智能切换:")
    print("   - 优先使用 Stability AI (主要服务)")
    print("   - Stability AI 失败时自动切换到 Gemini (备用)")
    print("   - 两个服务都失败时返回 None")
    print()
    print("📝 使用方法:")
    print("   1. 启动服务: uvicorn app.main:app --reload --port 8000")
    print("   2. 图片生成会自动使用 Stability AI 优先策略")
    print("   3. 查看日志了解使用了哪个服务")
    print()
    print("🔧 故障排除:")
    print("   - 运行 python test_stability_ai.py 进行详细测试")
    print("   - 检查 .env 文件中的 API Key 配置")
    print("   - 查看控制台日志了解错误详情")

async def main():
    """主函数"""
    print_banner()
    
    # 检查依赖
    if not check_python_dependencies():
        return
    
    # 设置API Key
    if not setup_stability_api_key():
        print("\n❌ 设置未完成，请手动配置API Key后重新运行")
        return
    
    # 测试 Stability AI 集成
    stability_test = await test_stability_integration()
    if not stability_test:
        print("\n❌ Stability AI 集成测试失败")
        return
    
    # 测试 fallback 机制
    fallback_test = await test_fallback_mechanism()
    if not fallback_test:
        print("\n❌ Fallback 机制测试失败")
        return
    
    # 打印成功消息
    print_success_message()

if __name__ == "__main__":
    asyncio.run(main()) 