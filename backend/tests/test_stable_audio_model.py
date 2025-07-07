import pytest
import asyncio
import os
import time
import torch
import torchaudio
from typing import List, Dict, Any

# 导入我们的服务
from app.services.stable_audio_service import StableAudioService, stable_audio_service

class TestStableAudioModel:
    """Stable Audio Open Small 模型测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前的设置"""
        self.service = StableAudioService()
        self.test_prompts = [
            "128 BPM tech house drum loop",
            "peaceful rain sounds with distant thunder",
            "gentle ocean waves crashing on the shore",
            "forest ambience with birds chirping",
            "cozy fireplace crackling sounds"
        ]
        
    def test_model_initialization(self):
        """测试模型初始化"""
        print("\n=== 测试模型初始化 ===")
        
        # 检查设备
        assert self.service.device in ["cuda", "cpu"], f"Unexpected device: {self.service.device}"
        print(f"✓ 设备检测: {self.service.device}")
        
        # 检查输出目录
        assert os.path.exists(self.service.output_dir), f"Output directory not found: {self.service.output_dir}"
        print(f"✓ 输出目录: {self.service.output_dir}")
        
        # 检查模型状态
        assert not self.service.is_loaded, "Model should not be loaded initially"
        print("✓ 初始状态: 模型未加载")
        
    def test_model_loading(self):
        """测试模型加载"""
        print("\n=== 测试模型加载 ===")
        
        start_time = time.time()
        self.service.load_model()
        load_time = time.time() - start_time
        
        # 验证模型已加载
        assert self.service.is_loaded, "Model should be loaded after load_model()"
        assert self.service.model is not None, "Model should not be None"
        assert self.service.model_config is not None, "Model config should not be None"
        
        print(f"✓ 模型加载成功 (耗时: {load_time:.2f}秒)")
        print(f"✓ 采样率: {self.service.sample_rate}")
        print(f"✓ 样本大小: {self.service.sample_size}")
        
    def test_basic_audio_generation(self):
        """测试基础音频生成"""
        print("\n=== 测试基础音频生成 ===")
        
        # 确保模型已加载
        if not self.service.is_loaded:
            self.service.load_model()
        
        prompt = "128 BPM tech house drum loop"
        duration = 5.0
        
        start_time = time.time()
        audio_path = self.service.generate_audio(prompt, duration)
        generation_time = time.time() - start_time
        
        # 验证生成结果
        assert audio_path is not None, "Audio path should not be None"
        assert os.path.exists(audio_path), f"Generated audio file not found: {audio_path}"
        assert audio_path.endswith('.wav'), "Generated file should be WAV format"
        
        # 验证音频文件属性
        waveform, sample_rate = torchaudio.load(audio_path)
        assert sample_rate == self.service.sample_rate, f"Sample rate mismatch: {sample_rate} vs {self.service.sample_rate}"
        assert waveform.shape[0] == 2, "Should be stereo audio (2 channels)"
        
        print(f"✓ 音频生成成功 (耗时: {generation_time:.2f}秒)")
        print(f"✓ 文件路径: {audio_path}")
        print(f"✓ 音频时长: {waveform.shape[1] / sample_rate:.2f}秒")
        print(f"✓ 声道数: {waveform.shape[0]}")
        
    def test_duration_limits(self):
        """测试时长限制"""
        print("\n=== 测试时长限制 ===")
        
        if not self.service.is_loaded:
            self.service.load_model()
        
        # 测试超过最大时长的处理
        long_duration = 15.0  # 超过11秒限制
        prompt = "test prompt"
        
        audio_path = self.service.generate_audio(prompt, long_duration)
        
        # 验证实际生成的时长
        waveform, sample_rate = torchaudio.load(audio_path)
        actual_duration = waveform.shape[1] / sample_rate
        
        assert actual_duration <= 11.0, f"Generated duration {actual_duration}s exceeds limit"
        print(f"✓ 时长限制生效: 请求{long_duration}s, 实际{actual_duration:.2f}s")
        
    def test_different_prompts(self):
        """测试不同提示词的效果"""
        print("\n=== 测试不同提示词 ===")
        
        if not self.service.is_loaded:
            self.service.load_model()
        
        results = []
        for i, prompt in enumerate(self.test_prompts[:3]):  # 只测试前3个
            print(f"测试提示词 {i+1}: {prompt}")
            
            start_time = time.time()
            audio_path = self.service.generate_audio(prompt, duration=3.0)
            generation_time = time.time() - start_time
            
            # 验证生成结果
            assert os.path.exists(audio_path), f"Audio file not generated for prompt: {prompt}"
            
            # 检查音频文件大小
            file_size = os.path.getsize(audio_path)
            assert file_size > 0, f"Generated file is empty: {audio_path}"
            
            results.append({
                'prompt': prompt,
                'path': audio_path,
                'time': generation_time,
                'size': file_size
            })
            
            print(f"  ✓ 生成成功 (耗时: {generation_time:.2f}秒, 大小: {file_size} bytes)")
        
        print(f"✓ 所有提示词测试完成，共生成 {len(results)} 个音频文件")
        
    def test_generation_parameters(self):
        """测试不同生成参数的效果"""
        print("\n=== 测试生成参数 ===")
        
        if not self.service.is_loaded:
            self.service.load_model()
        
        base_prompt = "128 BPM tech house drum loop"
        
        # 测试不同的steps参数
        for steps in [4, 8, 12]:
            print(f"测试 steps={steps}")
            start_time = time.time()
            audio_path = self.service.generate_audio(
                base_prompt, 
                duration=3.0, 
                steps=steps,
                cfg_scale=1.0
            )
            generation_time = time.time() - start_time
            
            assert os.path.exists(audio_path), f"Audio not generated with steps={steps}"
            print(f"  ✓ steps={steps} 生成成功 (耗时: {generation_time:.2f}秒)")
        
        # 测试不同的cfg_scale参数
        for cfg_scale in [0.5, 1.0, 2.0]:
            print(f"测试 cfg_scale={cfg_scale}")
            start_time = time.time()
            audio_path = self.service.generate_audio(
                base_prompt, 
                duration=3.0, 
                steps=8,
                cfg_scale=cfg_scale
            )
            generation_time = time.time() - start_time
            
            assert os.path.exists(audio_path), f"Audio not generated with cfg_scale={cfg_scale}"
            print(f"  ✓ cfg_scale={cfg_scale} 生成成功 (耗时: {generation_time:.2f}秒)")
        
    def test_model_info(self):
        """测试模型信息获取"""
        print("\n=== 测试模型信息 ===")
        
        info = self.service.get_model_info()
        
        # 验证信息完整性
        required_keys = ["model_name", "device", "is_loaded", "sample_rate", "sample_size", "max_duration"]
        for key in required_keys:
            assert key in info, f"Missing key in model info: {key}"
        
        assert info["model_name"] == "Stable Audio Open Small"
        assert info["max_duration"] == 11.0
        assert info["device"] in ["cuda", "cpu"]
        
        print("✓ 模型信息获取成功:")
        for key, value in info.items():
            print(f"  {key}: {value}")
            
    def test_error_handling(self):
        """测试错误处理"""
        print("\n=== 测试错误处理 ===")
        
        # 测试空提示词
        with pytest.raises(Exception):
            self.service.generate_audio("", duration=5.0)
        print("✓ 空提示词错误处理正常")
        
        # 测试负时长
        with pytest.raises(Exception):
            self.service.generate_audio("test", duration=-1.0)
        print("✓ 负时长错误处理正常")

def test_stable_audio_service_singleton():
    """测试单例模式"""
    print("\n=== 测试单例模式 ===")
    
    # 验证单例实例
    assert stable_audio_service is not None
    assert isinstance(stable_audio_service, StableAudioService)
    
    # 验证多次获取是同一个实例
    service1 = stable_audio_service
    service2 = stable_audio_service
    assert service1 is service2
    
    print("✓ 单例模式工作正常")

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"]) 