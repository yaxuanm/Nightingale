#!/usr/bin/env python3
"""
测试 Stability AI 配置和API调用
"""

import os
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_stability_ai():
    """测试 Stability AI 服务"""
    try:
        from app.services.stability_image_service import stability_image_service
        
        print("🔧 测试 Stability AI 配置...")
        
        # 检查API key
        if not stability_image_service.api_key:
            print("❌ STABILITY_API_KEY 未配置")
            print("请在 .env 文件中添加: STABILITY_API_KEY=your_api_key_here")
            return False
        
        print(f"✅ API Key 已配置: {stability_image_service.api_key[:10]}...")
        
        # 测试API调用
        print("🔧 测试图片生成...")
        test_description = "A peaceful forest with gentle sunlight filtering through trees"
        
        result = await stability_image_service.generate_background(test_description)
        
        if result:
            print(f"✅ 图片生成成功: {result}")
            return True
        else:
            print("❌ 图片生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def test_fallback_mechanism():
    """测试fallback机制"""
    try:
        from app.services.image_service import image_service
        
        print("🔧 测试 fallback 机制...")
        
        test_description = "A serene mountain lake at sunset"
        
        result = await image_service.generate_background(test_description)
        
        if result:
            print(f"✅ Fallback 机制工作正常: {result}")
            return True
        else:
            print("❌ Fallback 机制失败")
            return False
            
    except Exception as e:
        print(f"❌ Fallback 测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始测试 Stability AI 集成...")
    
    # 测试 Stability AI 直接调用
    stability_test = await test_stability_ai()
    
    if stability_test:
        print("\n🔧 测试 fallback 机制...")
        fallback_test = await test_fallback_mechanism()
        
        if fallback_test:
            print("\n✅ 所有测试通过！")
            print("📝 配置说明:")
            print("1. 确保在 .env 文件中设置了 STABILITY_API_KEY")
            print("2. Stability AI 失败时会自动切换到 Gemini")
            print("3. 两个服务都失败时会返回 None")
        else:
            print("\n❌ Fallback 机制测试失败")
    else:
        print("\n❌ Stability AI 配置测试失败")
        print("请检查 API key 配置")

if __name__ == "__main__":
    asyncio.run(main()) 