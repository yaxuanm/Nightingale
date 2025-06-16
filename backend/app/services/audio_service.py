from audiocraft.models import AudioGen
from audiocraft.data.audio import audio_write
import os
import torch
import google.generativeai as genai
from typing import Optional, Dict, Any
from pydub import AudioSegment
from .audio_effects import AudioEffectsService
from .storage_service import storage_service

class AudioGenerationService:
    def __init__(self):
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        # 初始化 Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        # 初始化音频效果服务
        self.effects_service = AudioEffectsService()
        # 设置输出目录
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.output_dir = os.path.join(self.base_dir, "audio_output")
        os.makedirs(self.output_dir, exist_ok=True)

    def load_model(self):
        if self.model is None:
            try:
                print("正在加载 AudioGen 模型...")
                self.model = AudioGen.get_pretrained('facebook/audiogen-medium')
                self.model.to(self.device)
                print("AudioGen 模型加载成功！")
            except Exception as e:
                print(f"模型加载失败: {str(e)}")
                raise
        return self.model

    def convert_to_scene_description(self, text: str) -> Optional[str]:
        """使用 Gemini 将诗句或文学描述转换为场景描述"""
        try:
            prompt = """你是一个专业的音频场景描述专家。
            你的任务是将诗句或文学描述转换为具体的场景描述，包含声音元素。
            例如：
            - 输入："小楼一夜听春雨"
            - 输出："轻柔的春雨声，滴落在木质屋檐上，远处偶尔传来几声鸟鸣，营造出宁静的夜晚氛围"
            
            请确保输出包含具体的环境声音描述，而不是抽象的诗意表达。
            
            现在，请将以下文本转换为场景描述：
            """
            
            response = self.gemini_model.generate_content(prompt + text)
            return response.text
        except Exception as e:
            print(f"Gemini 转换失败: {e}")
            return None

    async def generate_audio(self, description: str, duration: int = 5, is_poem: bool = False, 
                      effects_config: Optional[Dict[str, Dict[str, Any]]] = None) -> Optional[str]:
        """
        生成音频并应用效果
        effects_config: {
            'reverb': {'room_size': 0.5, 'damping': 0.5},
            'echo': {'delay': 300, 'decay': 0.5},
            'fade': {'fade_in': 1000, 'fade_out': 1000},
            'volume': {'volume_db': 0}
        }
        """
        try:
            model = self.load_model()
            
            # 如果是诗句，先转换为场景描述
            if is_poem:
                scene_description = self.convert_to_scene_description(description)
                if scene_description:
                    description = scene_description
                    print(f"转换后的场景描述: {description}")
                else:
                    print("使用原始描述继续生成")

            # 设置生成参数
            model.set_generation_params(duration=duration)
            
            # 生成音频
            print(f"正在生成音频: {description}")
            wav = model.generate([description], progress=True)
            
            # 保存原始音频
            temp_path = os.path.join(self.output_dir, f"temp_{hash(description)}.wav")
            audio_write(
                temp_path.replace('.wav', ''),
                wav.cpu(),
                model.sample_rate,
                strategy="loudness",
                loudness_compressor=True
            )
            
            try:
                # 加载音频并应用效果
                if effects_config:
                    audio = AudioSegment.from_wav(temp_path)
                    processed_audio = self.effects_service.process_audio(audio, effects_config)
                    
                    # 保存处理后的音频
                    output_path = os.path.join(self.output_dir, f"processed_{hash(description)}.wav")
                    processed_audio.export(output_path, format="wav")
                    
                    # 删除临时文件
                    os.remove(temp_path)
                    
                    # 上传到 Supabase
                    cloud_url = await storage_service.upload_audio(output_path, description)
                    
                    # 删除本地文件
                    os.remove(output_path)
                    
                    return cloud_url
                
                # 如果没有效果配置，直接上传原始文件
                cloud_url = await storage_service.upload_audio(temp_path, description)
                
                # 删除本地文件
                os.remove(temp_path)
                
                return cloud_url
                
            except Exception as e:
                print(f"音频处理或上传失败: {e}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise
                
        except Exception as e:
            print(f"音频生成失败: {e}")
            return None

# 创建单例实例
audio_service = AudioGenerationService() 