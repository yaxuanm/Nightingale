#!/usr/bin/env python3
"""
启动脚本 - 包含 Stability AI 配置检查
"""

import os
import sys
import asyncio
from pathlib import Path

def check_stability_config():
    """检查 Stability AI 配置"""
    print("🔧 检查 Stability AI 配置...")
    
    # 检查 .env 文件
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        print("❌ .env 文件不存在")
        return False
    
    # 检查 STABILITY_API_KEY
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'STABILITY_API_KEY' not in content:
            print("❌ STABILITY_API_KEY 未配置")
            print("请运行: python set_stability_key.py")
            return False
    
    print("✅ Stability AI 配置检查通过")
    return True

async def test_image_generation():
    """测试图片生成功能"""
    try:
        from app.services.image_service import image_service
        
        print("🔧 测试图片生成功能...")
        
        test_description = "A peaceful forest with gentle sunlight"
        result = await image_service.generate_background(test_description)
        
        if result:
            print(f"✅ 图片生成成功: {result}")
            return True
        else:
            print("❌ 图片生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 启动 Nightingale 后端服务")
    print("=" * 50)
    
    # 检查配置
    if not check_stability_config():
        print("\n📝 配置说明:")
        print("1. 运行 python set_stability_key.py 设置 API key")
        print("2. 运行 python test_stability_ai.py 测试配置")
        print("3. 然后重新运行此脚本")
        return
    
    # 测试图片生成
    print("\n🔧 测试图片生成功能...")
    test_result = asyncio.run(test_image_generation())
    
    if test_result:
        print("\n✅ 所有检查通过！")
        print("🎉 系统已准备好使用 Gemini + Stability AI fallback 机制")
        print("\n📝 启动服务:")
        print("   uvicorn app.main:app --reload --port 8000")
    else:
        print("\n❌ 图片生成测试失败")
        print("请检查网络连接和API配置")

if __name__ == "__main__":
    main() 