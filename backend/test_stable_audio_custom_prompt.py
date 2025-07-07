#!/usr/bin/env python3
"""
Stable Audio Open Small 自定义prompt测试脚本
"""

from app.services.stable_audio_service import stable_audio_service

if __name__ == "__main__":
    prompt = "A quiet workspace with Subtle wind chimes tinkling Calm Gentle Spring Rain on Roof Tiles, for focus. The sounds are clear and consistent, with gentle background elements that don't distract."
    duration = 10.0
    print("开始生成 Stable Audio ...")
    audio_path = stable_audio_service.generate_audio(prompt, duration=duration)
    print("音频已生成，文件路径：", audio_path) 