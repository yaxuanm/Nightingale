import json
import os
import time
import uuid
from typing import Any, Dict, Optional

import requests

class StableAudioService:
    def __init__(self):
        self.provider = os.environ.get("STABLE_AUDIO_PROVIDER", "hf-space").lower()
        if self.provider == "local":
            import torch
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = "remote-api"
        self.model_name = os.environ.get(
            "STABLE_AUDIO_MODEL",
            "stabilityai/stable-audio-3-small-sfx",
        )
        self.hf_space_url = os.environ.get(
            "STABLE_AUDIO_HF_SPACE_URL",
            "https://stabilityai-stable-audio-3.hf.space",
        ).rstrip("/")
        self.hf_space_variant = os.environ.get("STABLE_AUDIO_HF_SPACE_VARIANT", "small-sfx")
        self.display_name = os.environ.get("STABLE_AUDIO_DISPLAY_NAME", "Stable Audio 3 Small SFX")
        self.max_duration = float(os.environ.get("STABLE_AUDIO_MAX_DURATION", "11.0"))
        self.model = None
        self.model_config = None
        self.sample_rate = None
        self.sample_size = None
        self.is_loaded = False
        
        # 设置输出目录
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(self.base_dir, "audio_output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 设置Hugging Face token
        hf_token = os.environ.get('HF_TOKEN') or os.environ.get('HUGGING_FACE_HUB_TOKEN')
        if hf_token:
            os.environ['HF_TOKEN'] = hf_token
            os.environ['HUGGING_FACE_HUB_TOKEN'] = hf_token
            print(f"[OK] Hugging Face token set (length: {len(hf_token)})")
            
            # 在初始化时就登录
            try:
                from huggingface_hub import login
                login(token=hf_token, write_permission=False)
                print("[OK] Hugging Face login successful")
            except Exception as e:
                print(f"[WARN] Hugging Face login failed: {e}")
        else:
            print("[WARN] Warning: HF_TOKEN environment variable not set")
        
        print(f"StableAudioService initialized on device: {self.device}")
        print(f"Stable Audio provider: {self.provider}")
        print(f"Stable Audio model: {self.model_name}")
    
    def _optimize_prompt_for_stable_audio(self, prompt: str) -> str:
        """
        Optimize prompt based on Stable Audio model weaknesses:
        1. Multi-element combination failure - simplify element count
        2. Semantic modifier understanding failure - replace abstract modifiers with concrete descriptions
        3. Low volume sound generation failure - avoid requesting low volume
        """
        import re
        
        # 1. Remove or replace abstract modifiers that the model doesn't understand
        abstract_modifiers = {
            r'\bgentle\b': 'steady',
            r'\bsoft\b': 'smooth',
            r'\bquiet\b': 'background',
            r'\bcalm\b': 'steady',
            r'\bpeaceful\b': 'steady',
            r'\bsubtle\b': 'background',
            r'\bdelicate\b': 'smooth',
            r'\bwhisper\b': 'low',
            r'\bfaint\b': 'background',
            r'\bdistant\b': 'background',
            r'\bintimate\b': 'close',
            r'\bcozy\b': 'warm',
            r'\bsoothing\b': 'smooth',
            r'\brelaxing\b': 'steady'
        }
        
        optimized = prompt
        for pattern, replacement in abstract_modifiers.items():
            optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
        
        # 2. Simplify multi-element combinations - limit to 2-3 core elements
        # Use "with" and "accompanied by" to replace comma-separated lists
        optimized = re.sub(r',\s*([^,]+),\s*([^,]+)', r' with \1, accompanied by \2', optimized)
        optimized = re.sub(r',\s*([^,]+),\s*([^,]+),\s*([^,]+)', r' with \1, accompanied by \2', optimized)
        
        # 3. Avoid requesting low volume, emphasize sound presence
        optimized = re.sub(r'\bbackground\s+noise\b', 'ambient sounds', optimized, flags=re.IGNORECASE)
        optimized = re.sub(r'\bquiet\s+atmosphere\b', 'steady atmosphere', optimized, flags=re.IGNORECASE)
        
        # 4. Ensure clear primary-secondary relationship
        if 'with' not in optimized.lower() and 'accompanied by' not in optimized.lower():
            # If there are no primary-secondary relationship words, add one
            parts = optimized.split(',')
            if len(parts) > 1:
                optimized = f"{parts[0].strip()} with {parts[1].strip()}"
        
        # 5. Remove redundant modifiers
        optimized = re.sub(r'\bvery\b', '', optimized, flags=re.IGNORECASE)
        optimized = re.sub(r'\bquite\b', '', optimized, flags=re.IGNORECASE)
        optimized = re.sub(r'\bextremely\b', '', optimized, flags=re.IGNORECASE)
        
        # 6. Clean up extra spaces and punctuation
        optimized = re.sub(r'\s+', ' ', optimized)
        optimized = optimized.strip()
        
        return optimized
    
    def load_model(self):
        """Load the configured Stable Audio model."""
        if self.provider != "local":
            raise RuntimeError("Local model loading is disabled when STABLE_AUDIO_PROVIDER is not 'local'.")

        import torch
        from stable_audio_tools import get_pretrained_model

        if self.is_loaded:
            return
            
        try:
            print(f"Loading {self.display_name} model ({self.model_name})...")
            start_time = time.time()
            
            # === Fix: Set random seed before model loading ===
            import numpy as np
            import random
            
            # Set fixed random seed to avoid int32 overflow
            np.random.seed(42)
            random.seed(42)
            torch.manual_seed(42)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(42)
            
            print("[INFO] Random seed set before model loading")
            # === END ===
            
            # Ensure Hugging Face token is set
            hf_token = os.environ.get('HF_TOKEN') or os.environ.get('HUGGING_FACE_HUB_TOKEN')
            if not hf_token:
                print("⚠️  警告: 未设置HF_TOKEN环境变量")
                print("请运行: python set_hf_token.py 来设置token")
                raise Exception("Hugging Face token not set. Please set HF_TOKEN environment variable.")
            
            # 确保环境变量设置正确
            os.environ['HF_TOKEN'] = hf_token
            os.environ['HUGGING_FACE_HUB_TOKEN'] = hf_token
            
            # 下载并加载模型
            self.model, self.model_config = get_pretrained_model(self.model_name)
            self.sample_rate = self.model_config["sample_rate"]
            self.sample_size = self.model_config["sample_size"]

            # === 关键修复：CPU 使用 float32；CUDA 上 SA3 官方示例使用 float16 以省显存 ===
            try:
                if self.device == "cuda":
                    self.model = self.model.to(torch.float16)
                    print("[INFO] CUDA detected; using float16 for lower VRAM usage")
                else:
                    self.model.pretransform.model_half = False
                    self.model = self.model.to(torch.float32)
                    print("[INFO] Using float32 for CPU compatibility")
            except Exception as e:
                print("[WARN] Failed to set model precision:", e)
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
        if self.provider in {"hf-space", "huggingface-space", "remote"}:
            return self._generate_audio_via_hf_space(prompt, duration, steps, cfg_scale, sampler_type)
        return self._generate_audio_local(prompt, duration, steps, cfg_scale, sampler_type)

    def _generate_audio_local(self,
                      prompt: str,
                      duration: float = 11.0,
                      steps: int = 8,
                      cfg_scale: float = 1.0,
                      sampler_type: str = "pingpong") -> str:
        """
        生成音频文件
        
        Args:
            prompt: 文本描述
            duration: 音频时长（秒），由 STABLE_AUDIO_MAX_DURATION 控制上限
            steps: 扩散步数
            cfg_scale: CFG缩放因子
            sampler_type: 采样器类型
            
        Returns:
            生成的音频文件路径
        """
        import random

        import numpy as np
        import torch
        import torchaudio
        from einops import rearrange
        from stable_audio_tools.inference.generation import (
            generate_diffusion_cond,
            generate_diffusion_cond_inpaint,
        )

        if not self.is_loaded:
            self.load_model()
        
        # 限制 demo 生成时长，避免误触发过长生成导致成本和等待时间变高
        duration = min(duration, self.max_duration)
        
        # 优化 prompt 以适应 Stable Audio 模型的特性
        optimized_prompt = self._optimize_prompt_for_stable_audio(prompt)
        print(f"Original prompt: '{prompt}'")
        print(f"Optimized prompt: '{optimized_prompt}'")
        
        try:
            print(f"Generating audio with prompt: '{optimized_prompt}' (duration: {duration}s)")
            start_time = time.time()
            
            # === 修复：设置 numpy 随机数生成器 ===
            # 设置固定的随机种子，避免 int32 溢出
            np.random.seed(42)
            random.seed(42)
            torch.manual_seed(42)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(42)
            
            print("[INFO] Random seed set to avoid int32 overflow error")
            # === END ===
            
            # 设置文本和时间条件
            conditioning = [{
                "prompt": optimized_prompt,
                "seconds_total": duration
            }]
            
            # 生成立体声音频
            try:
                generator = generate_diffusion_cond_inpaint if self._uses_inpaint_generation else generate_diffusion_cond
                output = generator(
                    self.model,
                    steps=steps,
                    cfg_scale=cfg_scale,
                    conditioning=conditioning,
                    sample_size=self.sample_size,
                    sampler_type=sampler_type,
                    device=self.device
                )
                print("[OK] Audio generation successful")
            except Exception as e:
                if "high is out of bounds for int32" in str(e):
                    print("[WARN] Detected int32 overflow error, attempting fix...")
                    # Reset random seed
                    np.random.seed(123)
                    random.seed(123)
                    torch.manual_seed(123)
                    if torch.cuda.is_available():
                        torch.cuda.manual_seed(123)
                    
                    # 重试生成
                    generator = generate_diffusion_cond_inpaint if self._uses_inpaint_generation else generate_diffusion_cond
                    output = generator(
                        self.model,
                        steps=steps,
                        cfg_scale=cfg_scale,
                        conditioning=conditioning,
                        sample_size=self.sample_size,
                        sampler_type=sampler_type,
                        device=self.device
                    )
                    print("[OK] Audio generation successful after fix")
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
                
                # 音量标准化：确保生成的音频音量足够大且统一
                try:
                    from pydub import AudioSegment
                    audio_segment = AudioSegment.from_file(filepath)
                    
                    # 计算目标音量（-12dB 是一个比较标准的音量水平）
                    target_dBFS = -12
                    change_in_dBFS = target_dBFS - audio_segment.dBFS
                    audio_segment = audio_segment + change_in_dBFS
                    
                    # 确保音量不会过载（限制在 -1dB 以内）
                    if audio_segment.dBFS > -1:
                        audio_segment = audio_segment + (-1 - audio_segment.dBFS)
                    
                    # 重新保存标准化后的音频
                    audio_segment.export(filepath, format="wav")
                    print(f"Volume normalized: {filepath} (dBFS: {audio_segment.dBFS:.2f})")
                except Exception as e:
                    print(f"Volume normalization failed: {e}")
                
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

    def _generate_audio_via_hf_space(
        self,
        prompt: str,
        duration: float = 11.0,
        steps: int = 8,
        cfg_scale: float = 1.0,
        sampler_type: str = "pingpong",
    ) -> str:
        duration = min(float(duration), self.max_duration)
        optimized_prompt = self._optimize_prompt_for_stable_audio(prompt)
        print(f"[HF_SPACE] Original prompt: '{prompt}'")
        print(f"[HF_SPACE] Optimized prompt: '{optimized_prompt}'")

        payload = {
            "data": [
                self.hf_space_variant,
                optimized_prompt,
                duration,
                int(steps),
                float(cfg_scale),
                sampler_type,
                0,
            ]
        }

        start_time = time.time()
        event_id = self._submit_hf_space_generation(payload)
        file_url = self._wait_for_hf_space_file(event_id)

        filename = f"stable_audio_{uuid.uuid4().hex[:8]}.wav"
        filepath = os.path.join(self.output_dir, filename)
        response = requests.get(file_url, headers=self._hf_headers(), timeout=120)
        response.raise_for_status()
        with open(filepath, "wb") as audio_file:
            audio_file.write(response.content)

        generation_time = time.time() - start_time
        print(f"[HF_SPACE] Audio generated in {generation_time:.2f} seconds")
        print(f"[HF_SPACE] Saved to: {filepath}")
        return filepath

    def _submit_hf_space_generation(self, payload: Dict[str, Any]) -> str:
        response = requests.post(
            f"{self.hf_space_url}/gradio_api/call/infer",
            json=payload,
            headers=self._hf_headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["event_id"]

    def _wait_for_hf_space_file(self, event_id: str) -> str:
        response = requests.get(
            f"{self.hf_space_url}/gradio_api/call/infer/{event_id}",
            headers=self._hf_headers(),
            stream=True,
            timeout=360,
        )
        response.raise_for_status()

        last_event = None
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            if raw_line.startswith("event:"):
                last_event = raw_line.removeprefix("event:").strip()
                continue
            if not raw_line.startswith("data:"):
                continue

            payload = raw_line.removeprefix("data:").strip()
            if last_event == "complete":
                result = json.loads(payload)
                return result[0]["url"]
            if last_event == "error":
                raise RuntimeError(payload)

        raise RuntimeError(f"Hugging Face Space did not return audio for event {event_id}")

    def _hf_headers(self) -> Dict[str, str]:
        hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
        if not hf_token:
            return {}
        return {"Authorization": f"Bearer {hf_token}"}
    
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
        # Adjust generation parameters based on effects configuration
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
            "model_name": self.display_name,
            "model_id": self.model_name,
            "provider": self.provider,
            "hf_space_url": self.hf_space_url if self.provider != "local" else None,
            "device": self.device,
            "is_loaded": self.is_loaded,
            "sample_rate": self.sample_rate,
            "sample_size": self.sample_size,
            "max_duration": self.max_duration,
            "supported_sampler_types": ["pingpong", "ddpm", "ddim"]
        }

    @property
    def _uses_inpaint_generation(self) -> bool:
        """Stable Audio 3 model cards use the inpaint generation helper."""
        return "stable-audio-3" in self.model_name.lower()

# 创建单例实例
stable_audio_service = StableAudioService() 

# 可选：主流程默认测试prompt
DEFAULT_TEST_PROMPT = "Children's laughter echoing softly and Cicada chorus with distant birdsong and Grandma's humming, a quiet melody. Relaxed warm summer breeze, cicadas chirping. For focus." 
