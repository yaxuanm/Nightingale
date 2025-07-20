import os
import requests
import base64
import time
import random
from typing import Optional
from PIL import Image
from io import BytesIO
from .storage_service import storage_service

class StabilityImageService:
    def __init__(self):
        self.api_key = os.getenv("STABILITY_API_KEY")
        self.api_host = "https://api.stability.ai"
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(self.base_dir, "image_output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        if not self.api_key:
            print("[WARNING] STABILITY_API_KEY not found in environment variables")
    
    async def generate_background(self, description: str, max_retries: int = 3) -> Optional[str]:
        """
        使用 Stability AI 生成背景图片，使用和 Gemini 相同的 prompt 格式
        """
        if not self.api_key:
            print("[ERROR] Stability AI API key not configured")
            return None
            
        # 使用和 Gemini 相同的 prompt 格式
        enhanced_prompt = (
            "Create a stunning, high-quality background image for an ambient sound app. "
            f"The scene should depict: {description}. "
            "Style: Photorealistic, cinematic, with soft lighting and atmospheric depth. "
            "Colors: Rich, vibrant but calming palette with subtle gradients. "
            "Composition: Wide landscape or atmospheric scene with depth of field. "
            "Quality: Ultra-high resolution, professional photography style, suitable for premium app backgrounds. "
            "Mood: Peaceful, meditative, and immersive."
        )
        
        for attempt in range(max_retries):
            try:
                print(f"[IMAGE] [STABILITY] Attempting image generation (attempt {attempt + 1}/{max_retries})...")
                
                # 调用 Stability AI API
                image_data = await self._call_stability_api(enhanced_prompt)
                
                if not image_data:
                    print("[ERROR] Stability AI did not return any images.")
                    return None
                
                # 生成唯一文件名
                file_name = f"stability_background_{abs(hash(description))}.png"
                temp_file_path = os.path.join(self.output_dir, file_name)
                
                # 保存本地
                image = Image.open(BytesIO(image_data))
                image.save(temp_file_path)
                print(f"[SAVE] [STABILITY] Image temporarily saved locally for upload: {temp_file_path}")
                
                # 上传到云存储
                cloud_url = await storage_service.upload_image(temp_file_path, description)
                if cloud_url:
                    print(f"[UPLOAD] [STABILITY] Image uploaded to Supabase: {cloud_url}")
                    return cloud_url
                else:
                    print("[WARNING] Supabase upload failed, returning local file path.")
                    return f"/static/generated_images/{file_name}"
                    
            except Exception as e:
                error_msg = str(e).lower()
                if "rate limit" in error_msg:
                    print(f"[ERROR] [STABILITY] Rate limit exceeded: {e}")
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(5, 10)  # 更长的等待时间
                        print(f"[RETRY] Waiting {wait_time:.1f} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return None
                elif "quota" in error_msg or "balance" in error_msg or "payment" in error_msg:
                    print(f"[ERROR] [STABILITY] Quota/Balance issue: {e}")
                    return None  # 直接返回None，让fallback处理
                else:
                    print(f"[ERROR] [STABILITY] Image generation failed (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        print(f"[RETRY] Waiting {wait_time:.1f} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return None
                    
        return None
    
    async def _call_stability_api(self, prompt: str) -> Optional[bytes]:
        """
        调用 Stability AI API 生成图片，使用和 Gemini 相同的尺寸
        """
        try:
            url = f"{self.api_host}/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1
                    }
                ],
                "cfg_scale": 7,
                "height": 1024,  # 和 Gemini 相同的尺寸
                "width": 1024,   # 和 Gemini 相同的尺寸
                "samples": 1,
                "steps": 30,
            }
            
            print(f"[STABILITY] Calling API with prompt: {prompt[:100]}...")
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if "artifacts" in result and len(result["artifacts"]) > 0:
                    image_data = base64.b64decode(result["artifacts"][0]["base64"])
                    print("[STABILITY] Image generated successfully")
                    return image_data
                else:
                    print("[ERROR] No artifacts returned from Stability AI")
                    return None
            elif response.status_code == 402:
                print("[ERROR] Stability AI: Payment required - insufficient balance")
                raise Exception("Insufficient balance")
            elif response.status_code == 429:
                print("[ERROR] Stability AI: Rate limit exceeded")
                raise Exception("Rate limit exceeded")
            else:
                print(f"[ERROR] Stability AI API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Network error calling Stability AI: {e}")
            return None
        except Exception as e:
            print(f"[ERROR] Unexpected error calling Stability AI: {e}")
            return None

# 创建全局实例
stability_image_service = StabilityImageService() 