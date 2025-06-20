from audiocraft.models import AudioGen, MusicGen
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
        self.audio_model = None
        self.music_model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
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
        if self.audio_model is None:
            try:
                print("Loading AudioGen model...")
                self.audio_model = AudioGen.get_pretrained('facebook/audiogen-medium')
                print("AudioGen model loaded successfully!")
            except Exception as e:
                print(f"AudioGen model loading failed: {str(e)}")
                raise
        return self.audio_model

    def load_music_model(self):
        if self.music_model is None:
            try:
                print("Loading MusicGen model...")
                self.music_model = MusicGen.get_pretrained('facebook/musicgen-small')
                print("MusicGen model loaded successfully!")
            except Exception as e:
                print(f"MusicGen model loading failed: {str(e)}")
                raise
        return self.music_model

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

    async def generate_audio(self, description: str, duration: int = 10, is_poem: bool = False, 
                      effects_config: Optional[Dict[str, Dict[str, Any]]] = None,
                      mode: str = "default") -> Optional[str]:
        """
        Generate ambient audio and apply effects, upload to Supabase, and save locally.
        """
        try:
            if duration > 15:
                print(f"Warning: Generating {duration} seconds of audio. Quality may vary with longer durations.")
            
            model = self.load_audio_model()
            
            # If it's a poem, first convert to a scene description
            if is_poem:
                scene_description = self.convert_to_scene_description(description)
                if scene_description:
                    description = scene_description
                    print(f"Converted scene description: {description}")
                else:
                    print("Using original description for generation.")
            
            # Apply mode-specific prompt if mode is specified
            if mode in self.mode_prompts:
                description = self.mode_prompts[mode].format(description=description)
                print(f"Applied {mode} mode prompt")
            
            # Set generation parameters
            model.set_generation_params(duration=duration)
            # Generate audio
            print(f"Generating audio for: {description}")
            wav = model.generate([description], progress=True)
            
            # Save original audio to temporary path for processing/upload and local copy
            file_name = f"audio_{abs(hash(description))}.wav"
            local_file_path = os.path.join(self.output_dir, file_name)
            audio_write(
                local_file_path.replace('.wav', ''),
                wav[0].cpu(),
                model.sample_rate,
                strategy="loudness",
                loudness_compressor=True
            )
            
            processed_audio_path = local_file_path # Default to this path if no effects or processing

            try:
                # Load audio and apply effects
                audio = AudioSegment.from_wav(local_file_path)
                
                # Apply mode-specific effects if mode is specified and no custom effects_config is provided
                if mode in self.mode_effects and not effects_config:
                    effects_config = self.mode_effects[mode]
                    print(f"Applied {mode} mode effects")
                
                if effects_config:
                    processed_audio = self.effects_service.process_audio(audio, effects_config)
                    
                    # Save processed audio to a new path (still within output_dir)
                    processed_file_name = f"processed_audio_{abs(hash(description))}.wav"
                    processed_audio_path = os.path.join(self.output_dir, processed_file_name)
                    processed_audio.export(processed_audio_path, format="wav")
                    print(f"Processed audio saved locally: {processed_audio_path}")
                    # No need to delete original local_file_path if we want to keep it too

                # Attempt to upload to Supabase
                cloud_url = await storage_service.upload_audio(processed_audio_path, description)
                
                if cloud_url:
                    # If upload successful, keep local file and return cloud URL
                    print(f"Audio uploaded to Supabase: {cloud_url}")
                    return cloud_url
                else:
                    # If upload fails, return local file path
                    print(f"Supabase upload failed, returning local file: {processed_audio_path}")
                    return f"/static/generated_audio/{os.path.basename(processed_audio_path)}"
                
            except Exception as e:
                print(f"Audio processing or upload failed: {e}")
                # If an error occurs, return local file path (either original or processed, if exists)
                print(f"Returning local file due to error: {processed_audio_path}")
                return f"/static/generated_audio/{os.path.basename(processed_audio_path)}"
                
        except Exception as e:
            print(f"Audio generation failed: {e}")
            return None

    async def generate_music(self, description: str, duration: int = 30) -> Optional[str]:
        """
        Generate gentle music using MusicGen model, upload to Supabase, and save locally.
        """
        try:
            model = self.load_music_model()
            
            # Enhance the prompt for better music generation
            enhanced_prompt = f"Gentle, peaceful background music for meditation and relaxation. {description}. Soft melodies, ambient sounds, calming atmosphere."
            
            # Set generation parameters
            model.set_generation_params(
                duration=duration,
                temperature=0.7,
                top_k=250,
                top_p=0.95,
                cfg_coef=3.0
            )
            
            # Generate music
            print(f"Generating music for: {enhanced_prompt}")
            wav = model.generate([enhanced_prompt], progress=True)
            
            # Save music to temporary path for processing/upload and local copy
            file_name = f"music_{abs(hash(description))}.wav"
            local_file_path = os.path.join(self.output_dir, file_name)
            audio_write(
                local_file_path.replace('.wav', ''),
                wav[0].cpu(),
                model.sample_rate,
                strategy="loudness",
                loudness_compressor=True
            )
            
            print(f"Music temporarily saved locally for upload: {local_file_path}")

            # Upload to cloud storage
            cloud_url = await storage_service.upload_audio(local_file_path, f"music_{description}")
            
            if cloud_url:
                print(f"Music uploaded to Supabase: {cloud_url}")
                # Keep local copy after successful upload
                return cloud_url
            else:
                print("Supabase upload failed, returning local file path.")
                return f"/static/generated_audio/{file_name}"
            
        except Exception as e:
            print(f"Music generation failed: {e}")
            return None

# Create singleton instance
audio_service = AudioGenerationService() 