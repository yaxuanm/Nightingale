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
            
            # === 修复：在模型加载前设置随机种子 ===
            import numpy as np
            import random
            
            # 设置固定的随机种子，避免 int32 溢出
            np.random.seed(42)
            random.seed(42)
            torch.manual_seed(42)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(42)
            
            print("[INFO] 模型加载前已设置随机种子")
            # === END ===
            
            # 下载并加载模型
            self.model, self.model_config = get_pretrained_model("stabilityai/stable-audio-open-small")
            self.sample_rate = self.model_config["sample_rate"]
            self.sample_size = self.model_config["sample_size"]

            # === 关键修复：强制float32，避免CPU卡死 ===
            try:
                self.model.pretransform.model_half = False
                self.model = self.model.to(torch.float32)
                print("[INFO] 强制模型为float32 (CPU友好)")
            except Exception as e:
                print("[WARN] 设置float32失败:", e)
            # === END ===

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
            
            # === 修复：设置 numpy 随机数生成器 ===
            import numpy as np
            import random
            
            # 设置固定的随机种子，避免 int32 溢出
            np.random.seed(42)
            random.seed(42)
            torch.manual_seed(42)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(42)
            
            print("[INFO] 已设置随机种子，避免 int32 溢出错误")
            # === END ===
            
            # 设置文本和时间条件
            conditioning = [{
                "prompt": prompt,
                "seconds_total": duration
            }]
            
            # 生成立体声音频
            try:
                output = generate_diffusion_cond(
                    self.model,
                    steps=steps,
                    cfg_scale=cfg_scale,
                    conditioning=conditioning,
                    sample_size=self.sample_size,
                    sampler_type=sampler_type,
                    device=self.device
                )
                print("✅ 音频生成成功")
            except Exception as e:
                if "high is out of bounds for int32" in str(e):
                    print("⚠️  检测到 int32 溢出错误，尝试修复...")
                    # 重新设置随机种子
                    np.random.seed(123)
                    random.seed(123)
                    torch.manual_seed(123)
                    if torch.cuda.is_available():
                        torch.cuda.manual_seed(123)
                    
                    # 重试生成
                    output = generate_diffusion_cond(
                        self.model,
                        steps=steps,
                        cfg_scale=cfg_scale,
                        conditioning=conditioning,
                        sample_size=self.sample_size,
                        sampler_type=sampler_type,
                        device=self.device
                    )
                    print("✅ 修复后音频生成成功")
                else:
                    raise e
            
            # 重新排列音频批次为单个序列
            output = rearrange(output, "b d n -> d (b n)")
            
            # 峰值归一化、裁剪、转换为int16并保存到文件
            try:
                print(f"Output shape before processing: {output.shape}")
                print(f"Output dtype: {output.dtype}")
                print(f"Output device: {output.device}")
                print(f"Output min: {output.min()}, max: {output.max()}")
                
                output = (output.to(torch.float32)
                         .div(torch.max(torch.abs(output)))
                         .clamp(-1, 1)
                         .mul(32767)
                         .to(torch.int16)
                         .cpu())
                
                print(f"Output shape after processing: {output.shape}")
                print(f"Output dtype after processing: {output.dtype}")
                print(f"Output device after processing: {output.device}")
                print(f"Output min after: {output.min()}, max after: {output.max()}")
                print(f"Output has NaN: {torch.isnan(output).any().item()}, has inf: {torch.isinf(output).any().item()}")
                print(f"Output first 10 samples: {output.flatten()[:10]}")
                
                # 生成唯一文件名
                filename = f"stable_audio_{uuid.uuid4().hex[:8]}.wav"
                filepath = os.path.join(self.output_dir, filename)
                
                # 确保sample_rate是整数
                sample_rate = int(self.sample_rate)
                print(f"Sample rate: {sample_rate}")
                print(f"即将保存: path={filepath}, shape={output.shape}, dtype={output.dtype}, min={output.min()}, max={output.max()}")
                
                # 保存音频文件
                torchaudio.save(filepath, output, sample_rate)
                print(f"Audio saved successfully: {filepath}")
                
            except Exception as e:
                print(f"Error in audio processing/saving: {e}")
                print(f"Output tensor info - shape: {output.shape}, dtype: {output.dtype}, device: {output.device}, min: {output.min()}, max: {output.max()}")
                import traceback
                traceback.print_exc()
                raise
            
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

# 可选：主流程默认测试prompt
DEFAULT_TEST_PROMPT = "Children's laughter echoing softly and Cicada chorus with distant birdsong and Grandma's humming, a quiet melody. Relaxed warm summer breeze, cicadas chirping. For focus." 