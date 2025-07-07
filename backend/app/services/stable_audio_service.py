import os
import torch
import torchaudio
from einops import rearrange
from stable_audio_tools import get_pretrained_model
from stable_audio_tools.inference.generation import generate_diffusion_cond
from typing import Optional, Dict, Any
import time
import uuid

class StableAudioService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.model_config = None
        self.sample_rate = None
        self.sample_size = None
        self.is_loaded = False
        
        # 设置输出目录
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(self.base_dir, "audio_output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"StableAudioService initialized on device: {self.device}")
    
    def load_model(self):
        """加载 Stable Audio Open Small 模型"""
        if self.is_loaded:
            return
            
        try:
            print("Loading Stable Audio Open Small model...")
            start_time = time.time()
            
            # 下载并加载模型
            self.model, self.model_config = get_pretrained_model("stabilityai/stable-audio-open-small")
            self.sample_rate = self.model_config["sample_rate"]
            self.sample_size = self.model_config["sample_size"]
            
            # 将模型移动到指定设备
            self.model = self.model.to(self.device)
            
            load_time = time.time() - start_time
            print(f"Model loaded successfully in {load_time:.2f} seconds")
            print(f"Sample rate: {self.sample_rate}")
            print(f"Sample size: {self.sample_size}")
            
            self.is_loaded = True
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise
    
    def generate_audio(self, 
                      prompt: str, 
                      duration: float = 11.0,
                      steps: int = 8,
                      cfg_scale: float = 1.0,
                      sampler_type: str = "pingpong") -> str:
        """
        生成音频文件
        
        Args:
            prompt: 文本描述
            duration: 音频时长（秒），最大11秒
            steps: 扩散步数
            cfg_scale: CFG缩放因子
            sampler_type: 采样器类型
            
        Returns:
            生成的音频文件路径
        """
        if not self.is_loaded:
            self.load_model()
        
        # 限制时长在模型范围内
        duration = min(duration, 11.0)
        
        try:
            print(f"Generating audio with prompt: '{prompt}' (duration: {duration}s)")
            start_time = time.time()
            
            # 设置文本和时间条件
            conditioning = [{
                "prompt": prompt,
                "seconds_total": duration
            }]
            
            # 生成立体声音频
            output = generate_diffusion_cond(
                self.model,
                steps=steps,
                cfg_scale=cfg_scale,
                conditioning=conditioning,
                sample_size=self.sample_size,
                sampler_type=sampler_type,
                device=self.device
            )
            
            # 重新排列音频批次为单个序列
            output = rearrange(output, "b d n -> d (b n)")
            
            # 峰值归一化、裁剪、转换为int16并保存到文件
            output = (output.to(torch.float32)
                     .div(torch.max(torch.abs(output)))
                     .clamp(-1, 1)
                     .mul(32767)
                     .to(torch.int16)
                     .cpu())
            
            # 生成唯一文件名
            filename = f"stable_audio_{uuid.uuid4().hex[:8]}.wav"
            filepath = os.path.join(self.output_dir, filename)
            
            # 保存音频文件
            torchaudio.save(filepath, output, self.sample_rate)
            
            generation_time = time.time() - start_time
            print(f"Audio generated successfully in {generation_time:.2f} seconds")
            print(f"Saved to: {filepath}")
            
            return filepath
            
        except Exception as e:
            print(f"Error generating audio: {str(e)}")
            raise
    
    def generate_audio_with_effects(self, 
                                  prompt: str, 
                                  duration: float = 11.0,
                                  effects_config: Optional[Dict[str, Any]] = None) -> str:
        """
        生成带音效的音频
        
        Args:
            prompt: 文本描述
            duration: 音频时长
            effects_config: 音效配置
            
        Returns:
            生成的音频文件路径
        """
        # 根据音效配置调整生成参数
        steps = 8
        cfg_scale = 1.0
        sampler_type = "pingpong"
        
        if effects_config:
            if "steps" in effects_config:
                steps = effects_config["steps"]
            if "cfg_scale" in effects_config:
                cfg_scale = effects_config["cfg_scale"]
            if "sampler_type" in effects_config:
                sampler_type = effects_config["sampler_type"]
        
        return self.generate_audio(prompt, duration, steps, cfg_scale, sampler_type)
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "model_name": "Stable Audio Open Small",
            "device": self.device,
            "is_loaded": self.is_loaded,
            "sample_rate": self.sample_rate,
            "sample_size": self.sample_size,
            "max_duration": 11.0,
            "supported_sampler_types": ["pingpong", "ddpm", "ddim"]
        }

# 创建单例实例
stable_audio_service = StableAudioService() 