#!/usr/bin/env python3
"""
简单测试 Stability AI 图片生成
"""

import asyncio
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_image_generation():
    """测试图片生成"""
    try:
        from app.services.image_service import image_service
        
        print("🔧 测试图片生成...")
        
        # 测试描述
        test_description = "A peaceful forest with gentle sunlight"
        
        print(f"📝 测试描述: {test_description}")
        result = await image_service.generate_background(test_description)
        
        if result:
            print(f"✅ 图片生成成功: {result}")
            return True
        else:
            print("❌ 图片生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("🚀 开始测试...")
    
    # 检查API key
    api_key = os.getenv("STABILITY_API_KEY")
    if not api_key:
        print("❌ STABILITY_API_KEY 未配置")
        return
    
    print(f"✅ API Key 已配置: {api_key[:10]}...")
    
    # 测试图片生成
    success = await test_image_generation()
    
    if success:
        print("\n🎉 测试成功！")
        print("📝 系统现在使用 Stability AI 作为主要服务，Gemini 作为备用")
    else:
        print("\n❌ 测试失败")

if __name__ == "__main__":
    asyncio.run(main()) 