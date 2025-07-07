import os
import google.generativeai as genai
from typing import Optional, Dict, Any
from pydub import AudioSegment
import subprocess
from .audio_effects import AudioEffectsService
from .storage_service import storage_service
from .freesound_concat_demo import generate_freesound_mix

class AudioGenerationService:
    def __init__(self):
        self.audio_model = None
        self.music_model = None
        self.device = "cpu"  # Audio generation is now handled by worker script
        # Initialize Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
        # Initialize audio effects service
        self.effects_service = AudioEffectsService()
        # Set output directory for audio (for local copies)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(self.base_dir, "audio_output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Mode-specific configurations
        self.mode_prompts = {
            "focus": """A quiet workspace with {description}. The sounds are clear and consistent, with gentle background elements that don't distract.""",
            
            "relax": """A peaceful environment with {description}. The sounds are soft and natural, creating a calming atmosphere with gentle transitions.""",
            
            "story": """An immersive scene with {description}. The sounds create a rich environment with distinct elements that tell a story through audio.""",
            
            "music": """A musical atmosphere with {description}. The sounds blend together in a harmonious way, creating a melodic and rhythmic experience."""
        }
        
        self.mode_effects = {
            "focus": {
                "volume": {"volume_db": -3},  # Slightly lower volume
                "fade": {"fade_in": 2000, "fade_out": 2000}  # Longer fade
            },
            "relax": {
                "reverb": {"room_size": 0.7, "damping": 0.5},  # More reverb
                "fade": {"fade_in": 3000, "fade_out": 3000}  # Longer fade
            },
            "story": {
                "echo": {"delay": 200, "decay": 0.3},  # Slight echo
                "volume": {"volume_db": 0}  # Original volume
            },
            "music": {
                "reverb": {"room_size": 0.5, "damping": 0.7},  # Moderate reverb
                "echo": {"delay": 150, "decay": 0.2}  # Slight echo
            }
        }

    def load_audio_model(self):
        # AudioGen model loading is now handled by the worker script
        return "audiogen"

    def load_music_model(self):
        # MusicGen model loading is now handled by the worker script
        return "musicgen"

    def convert_to_scene_description(self, text: str) -> Optional[str]:
        """Use Gemini to convert poetic or literary descriptions into scene descriptions"""
        try:
            prompt = """You are an expert in audio scene description.
            Your task is to convert poetic or literary descriptions into concrete scene descriptions, including sound elements.
            For example:
            - Input: "小楼一夜听春雨"
            - Output: "Soft spring rain drops on a wooden roof, with occasional distant bird chirps, creating a peaceful night ambiance."
            
            Please ensure the output contains concrete environmental sound descriptions, not abstract poetic expressions.
            Keep the description concise and focused on sound elements, ideally under 50 words.
            
            Now, please convert the following text into a scene description:
            """
            
            generation_config = {
                "max_output_tokens": 100, # Limit output length to around 50 words
            }
            
            response = self.gemini_model.generate_content(prompt + text, generation_config=generation_config)
            return response.text
        except Exception as e:
            print(f"Gemini conversion failed: {e}")
            return None

    async def generate_audio(self, description, duration=20, output_path=None, model_type="audiogen"):
        print("[INFO] Using Freesound混音方案作为主音频生成逻辑")
        audio_path = await generate_freesound_mix(description)
        # 上传到 Supabase
        try:
            cloud_url = await storage_service.upload_audio(audio_path, f"freesound_{abs(hash(description))}")
            if cloud_url:
                print(f"[SUCCESS] Uploaded to Supabase: {cloud_url}")
                return cloud_url
            else:
                print("[WARNING] Supabase upload failed, using local static path")
                return f"/static/generated_audio/{os.path.basename(audio_path)}"
        except Exception as e:
            print(f"[ERROR] Supabase upload exception: {e}")
            return f"/static/generated_audio/{os.path.basename(audio_path)}"

    async def generate_music(self, description: str, duration: int = 30) -> Optional[str]:
        """
        Generate gentle music using MusicGen model, upload to Supabase, and save locally.
        """
        try:
            print(f"[MUSIC] Starting music generation process...")
            
            # Enhance the prompt for better music generation
            enhanced_prompt = f"Gentle, peaceful background music for meditation and relaxation. {description}. Soft melodies, ambient sounds, calming atmosphere."
            print(f"[PROMPT] Enhanced prompt: {enhanced_prompt[:100]}...")
            
            # Generate music using worker script
            file_name = f"music_{abs(hash(description))}.wav"
            local_file_path = os.path.join(self.output_dir, file_name)
            print(f"[PATH] Local file path: {local_file_path}")
            
            # Call the worker script
            worker_script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "audio_generate_worker.py")
            # Use the audio virtual environment Python interpreter
            audio_venv_python = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "venv_audio", "Scripts", "python.exe")
            cmd = [
                audio_venv_python, worker_script_path,
                "--desc", enhanced_prompt,
                "--duration", str(duration),
                "--out", local_file_path,
                "--model", "musicgen"
            ]
            
            # Set working directory to backend folder to ensure proper path resolution
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
            print(f"[MODEL] Starting MusicGen model generation (expected {duration} seconds)...")
            print(f"[WORKDIR] Working directory: {backend_dir}")
            
            # 使用实时输出，确保进度条能显示
            result = subprocess.run(
                cmd, 
                capture_output=False,  # 不使用capture_output，让输出实时显示
                text=True, 
                cwd=backend_dir,
                bufsize=1,  # 行缓冲
                env=dict(os.environ, PYTHONUNBUFFERED="1")  # 确保Python输出不被缓冲
            )
            
            # 由于不使用capture_output，我们需要手动检查返回码
            if result.returncode != 0:
                print(f"[FAILED] Music generation failed, return code: {result.returncode}")
                return None
            
            print(f"[SUCCESS] Music generation completed! Temporarily saved to: {local_file_path}")

            # Upload to cloud storage
            print("[UPLOAD] Starting music upload to cloud storage...")
            cloud_url = await storage_service.upload_audio(local_file_path, f"music_{description}")
            
            if cloud_url:
                print(f"[SUCCESS] Music uploaded to Supabase successfully: {cloud_url}")
                # Keep local copy after successful upload
                return cloud_url
            else:
                print("[WARNING] Supabase upload failed, returning local file path")
                return f"/static/generated_audio/{file_name}"
            
        except Exception as e:
            print(f"[ERROR] Music generation failed: {e}")
            return None

# Create singleton instance
audio_service = AudioGenerationService() 