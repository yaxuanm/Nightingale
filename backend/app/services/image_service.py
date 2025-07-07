import os
import requests
import base64
import time
import random
from typing import Optional
from .storage_service import storage_service # Re-import storage_service

class ImageGenerationService:
    def __init__(self):
        self.api_key = os.getenv("STABILITY_API_KEY")
        if not self.api_key:
            raise ValueError("STABILITY_API_KEY environment variable is not set")
            
        self.api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        # Set local output directory for images (for local copies)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(self.base_dir, "image_output")
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate_background(self, description: str, max_retries: int = 3) -> Optional[str]:
        """
        Generate a background image using Stability AI's Stable Diffusion API, upload to Supabase, and save locally.
        Includes retry mechanism for rate limiting.
        """
        for attempt in range(max_retries):
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                # Enhance the prompt for better background images
                enhanced_prompt = f"A beautiful, artistic background image for an ambient sound app. {description}. Soft colors, abstract, peaceful atmosphere, suitable for a meditation or relaxation app."
                
                body = {
                    "text_prompts": [
                        {
                            "text": enhanced_prompt,
                            "weight": 1
                        }
                    ],
                    "cfg_scale": 7,
                    "height": 1024,
                    "width": 1024,
                    "samples": 1,
                    "steps": 30,
                    "style_preset": "digital-art"
                }
                
                print(f"[IMAGE] Attempting image generation (attempt {attempt + 1}/{max_retries})...")
                
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=body
                )
                
                if response.status_code == 401:
                    print("Error: Invalid API key for Stability AI")
                    return None
                elif response.status_code == 429:
                    print(f"Error: Rate limit exceeded for Stability AI API (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        # 指数退避策略：等待时间随重试次数增加
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        print(f"[RETRY] Waiting {wait_time:.1f} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print("Error: Max retries reached for rate limiting")
                        return None
                elif response.status_code != 200:
                    print(f"Error generating image: {response.text}")
                    return None
                    
                # 成功生成图片
                print(f"[SUCCESS] Image generation successful on attempt {attempt + 1}")
                
                # Decode image data
                image_data = response.json()["artifacts"][0]["base64"]
                image_bytes = base64.b64decode(image_data)
                
                # Generate a unique filename
                file_name = f"background_{abs(hash(description))}.png"
                temp_file_path = os.path.join(self.output_dir, file_name) # Use self.output_dir for local copy
                
                # Save to a temporary local file first
                with open(temp_file_path, "wb") as f:
                    f.write(image_bytes)
                
                print(f"[SAVE] Image temporarily saved locally for upload: {temp_file_path}")

                # Upload to cloud storage
                cloud_url = await storage_service.upload_image(temp_file_path, description)

                if cloud_url:
                    print(f"[UPLOAD] Image uploaded to Supabase: {cloud_url}")
                    # Keep local copy after successful upload
                    return cloud_url
                else:
                    print("[WARNING] Supabase upload failed, returning local file path.")
                    # If upload fails, return the local static path
                    return f"/static/generated_images/{file_name}"
                
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Network error while calling Stability AI API (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"[RETRY] Waiting {wait_time:.1f} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    return None
            except Exception as e:
                print(f"[ERROR] Image generation failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"[RETRY] Waiting {wait_time:.1f} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    return None
        
        return None

# Create singleton instance
try:
    image_service = ImageGenerationService()
except ValueError as e:
    print(f"Failed to initialize ImageGenerationService: {e}")
    image_service = None 