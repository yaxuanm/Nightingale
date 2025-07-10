import os
import base64
import time
import random
from typing import Optional
from .storage_service import storage_service
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

class ImageGenerationService:
    def __init__(self):
        self.client = genai.Client()
        self.model = "gemini-2.0-flash-preview-image-generation"  # 使用图片生成专用模型
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(self.base_dir, "image_output")
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate_background(self, description: str, max_retries: int = 3) -> Optional[str]:
        """
        用 Gemini 生成背景图，上传到 Supabase，并本地保存。
        保持原有的 prompt 生成和上传逻辑不变。
        """
        enhanced_prompt = f"A beautiful, artistic background image for an ambient sound app. {description}. Soft colors, abstract, peaceful atmosphere, suitable for a meditation or relaxation app."
        for attempt in range(max_retries):
            try:
                print(f"[IMAGE] [GENAI] Attempting image generation (attempt {attempt + 1}/{max_retries})...")
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=enhanced_prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT', 'IMAGE']
                    )
                )
                
                # 解析图片内容 - 使用新的标准格式
                image_data = None
                for part in response.candidates[0].content.parts:
                    if getattr(part, "inline_data", None) is not None:
                        image_data = part.inline_data.data
                        break
                
                if not image_data:
                    print("[ERROR] GenAI did not return any images.")
                    return None
                
                # 生成唯一文件名
                file_name = f"background_{abs(hash(description))}.png"
                temp_file_path = os.path.join(self.output_dir, file_name)
                
                # 保存本地 - 使用 PIL 处理图片
                image = Image.open(BytesIO(image_data))
                image.save(temp_file_path)
                print(f"[SAVE] [GENAI] Image temporarily saved locally for upload: {temp_file_path}")
                
                # 上传到云存储 - 保持原有逻辑不变
                cloud_url = await storage_service.upload_image(temp_file_path, description)
                if cloud_url:
                    print(f"[UPLOAD] [GENAI] Image uploaded to Supabase: {cloud_url}")
                    return cloud_url
                else:
                    print("[WARNING] Supabase upload failed, returning local file path.")
                    return f"/static/generated_images/{file_name}"
                    
            except Exception as e:
                print(f"[ERROR] [GENAI] Image generation failed (attempt {attempt + 1}): {e}")
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