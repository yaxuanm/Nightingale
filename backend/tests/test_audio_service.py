import asyncio
import os
from app.services.audio_service import audio_service

async def test_audio_generation():
    # 测试普通场景描述
    description = "雨滴落在树叶上的声音，伴随着远处传来的鸟鸣"
    print("测试1: 普通场景描述")
    result = await audio_service.generate_audio(description, duration=5)
    print(f"生成结果: {result}")

    # 测试诗句转换
    poem = "小楼一夜听春雨"
    print("\n测试2: 诗句转换")
    result = await audio_service.generate_audio(poem, duration=5, is_poem=True)
    print(f"生成结果: {result}")

    # 测试带音效的生成
    effects_config = {
        'reverb': {'room_size': 0.5, 'damping': 0.5},
        'fade': {'fade_in': 1000, 'fade_out': 1000}
    }
    print("\n测试3: 带音效的生成")
    result = await audio_service.generate_audio(description, duration=5, effects_config=effects_config)
    print(f"生成结果: {result}")

if __name__ == "__main__":
    asyncio.run(test_audio_generation()) 