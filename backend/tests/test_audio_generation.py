import pytest
from app.services.audio_service import AudioGenerationService

def test_audio_generation():
    """测试音频生成功能"""
    service = AudioGenerationService()
    
    # 测试场景描述
    description = "A peaceful summer night in a countryside courtyard, with cicadas chirping and distant frog sounds"
    
    # 生成音频
    audio_path = service.generate_audio(description, duration=10)
    
    # 验证结果
    assert audio_path is not None, "音频生成失败"
    assert audio_path.endswith('.wav'), "生成的文件不是 WAV 格式"
    
    # 验证文件是否存在
    import os
    assert os.path.exists(audio_path), "生成的音频文件不存在" 