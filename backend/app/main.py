import os
from dotenv import load_dotenv
# 指定 .env 路径，始终加载 backend/.env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
# 只在 .env 文件存在时加载
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    print(f"Warning: .env file not found at {env_path}")

from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from .services.storage_service import SupabaseStorageService
from .services.audio_service import audio_service, AudioGenerationService
from fastapi.staticfiles import StaticFiles
from .services.ai_service import ai_service, get_instruments_from_ai, build_musicgen_prompt, build_audiogen_prompt
from .services.image_service import ImageGenerationService
from .services.stable_audio_service import stable_audio_service
from fastapi import APIRouter
import subprocess

# Get the path to the current file's directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print(f"DEBUG: BASE_DIR is {BASE_DIR}")

# Ensure output directories exist at the very beginning
AUDIO_SAMPLES_DIR = os.path.join(BASE_DIR, "audio_samples")
AUDIO_OUTPUT_DIR = os.path.join(BASE_DIR, "audio_output")
IMAGE_OUTPUT_DIR = os.path.join(BASE_DIR, "image_output")

print(f"DEBUG: Ensuring AUDIO_SAMPLES_DIR {AUDIO_SAMPLES_DIR} exists.")
os.makedirs(AUDIO_SAMPLES_DIR, exist_ok=True)
print(f"DEBUG: Ensuring AUDIO_OUTPUT_DIR {AUDIO_OUTPUT_DIR} exists.")
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)
print(f"DEBUG: Ensuring IMAGE_OUTPUT_DIR {IMAGE_OUTPUT_DIR} exists.")
os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)

print("DEBUG: SUPABASE_URL =", os.environ.get("SUPABASE_URL"))
print("DEBUG: SUPABASE_KEY =", os.environ.get("SUPABASE_KEY"))

storage_service = SupabaseStorageService()

app = FastAPI(title="Nightingale API",
             description="AI-powered ambient sound generation API",
             version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specific origins should be set
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount audio_samples directory as a static file service (for input samples)
app.mount("/static/audio", StaticFiles(directory=os.path.join(BASE_DIR, "audio_samples")), name="audio")

# Mount audio_output directory as a static file service
app.mount("/static/generated_audio", StaticFiles(directory=os.path.join(BASE_DIR, "audio_output")), name="generated_audio")

# Mount image_output directory as a static file service
app.mount("/static/generated_images", StaticFiles(directory=os.path.join(BASE_DIR, "image_output")), name="generated_images")

# Create audio generation service instance (ensure this is the correct singleton pattern)
audio_service = AudioGenerationService()

# 在 load_dotenv 之后实例化 image_service
image_service = None
try:
    image_service = ImageGenerationService()
except ValueError as e:
    print(f"Failed to initialize ImageGenerationService: {e}")
    image_service = None

class SceneRequest(BaseModel):
    prompt: str
    mode: str = "default"
    chat_history: List[str] = []

class SceneResponse(BaseModel):
    response: str
    should_generate_audio: bool

# Removed: These models are no longer needed for the new /api/generate-scene endpoint
# class AudioElement(BaseModel):
#     name: str
#     volume: float
#     position: str  # "foreground", "background"
#     duration: float

# class SceneResponse(BaseModel):
#     audio_url: str
#     elements: List[AudioElement]
#     duration: float

class AudioGenerationRequest(BaseModel):
    description: str
    duration: int = 10
    is_poem: bool = False
    mode: str = "default"
    effects_config: Optional[Dict[str, Dict[str, Any]]] = None

class AudioGenerationResponse(BaseModel):
    audio_url: str

class MusicGenerationRequest(BaseModel):
    description: str
    duration: int = 15

class ImageGenerationRequest(BaseModel):
    description: str

class OptionGenerationRequest(BaseModel):
    mode: str
    input: str
    stage: str  # 'atmosphere' | 'mood' | 'elements'

class OptionGenerationResponse(BaseModel):
    options: list[str]

class MusicGenOptionRequest(BaseModel):
    stage: str  # 'genre' | 'instruments' | 'tempo' | 'usage'
    user_input: str = ""

class MusicGenOptionResponse(BaseModel):
    options: list[str]

class StableAudioGenerationRequest(BaseModel):
    prompt: str
    duration: float = 11.0
    steps: int = 8
    cfg_scale: float = 1.0
    sampler_type: str = "pingpong"

class StableAudioGenerationResponse(BaseModel):
    audio_url: str
    generation_time: float
    file_size: int
    model_info: Dict[str, Any]

router = APIRouter()

@app.get("/")
async def root():
    return {"message": "Welcome to Nightingale API"}

@app.post("/api/generate-scene")
async def generate_scene(request: SceneRequest):
    try:
        # Analyze the scene with AI
        scene_elements = await ai_service.parse_scene(request.prompt)
        
        # Generate AI response based on mode
        if request.mode == "focus":
            ai_response = "I'll create a focused soundscape that helps you concentrate. The sounds will be clear and non-distracting."
        elif request.mode == "relax":
            ai_response = "I'll create a relaxing soundscape to help you unwind. The sounds will be gentle and soothing."
        elif request.mode == "story":
            ai_response = "I'll create a rich narrative soundscape that brings your scene to life with detailed environmental sounds."
        elif request.mode == "music":
            ai_response = "I'll create a musical soundscape with melodic elements and rhythmic patterns."
        else:
            ai_response = "I'll create a soundscape based on your description."
        
        return {
            "scene_description": request.prompt,
            "scene_elements": scene_elements,
            "ai_response": ai_response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/generate-audio')
async def generate_audio(request: Request):
    data = await request.json()
    description = data.get('userInput') or data.get('description', '')
    print(f"[AUDIO] [FREESOUND] Starting Freesound混音音频生成 - Description: {description[:50]}...")
    audio_url = await audio_service.generate_audio(description)
    return {
        'audio_url': audio_url,
        'prompt': description
    }

@router.post('/api/generate-music')
async def generate_music(request: Request):
    data = await request.json()
    # 优先使用 userInput 字段作为原始描述
    user_text = data.get('userInput') or data.get('description', '')
    duration = data.get('duration', 30)
    # 收集结构化字段
    extra_fields = {
        'genre': data.get('genre'),
        'instruments': data.get('instruments'),
        'tempo': data.get('tempo'),
        'usage': data.get('usage'),
    }
    
    print(f"[MUSIC] Starting music generation - Description: {user_text[:50]}...")
    print(f"[PARAMS] Structured parameters: {extra_fields}")
    
    # 1. LLM 分层分析，优先合并结构化字段
    print("[AI] Starting AI layered analysis of music prompt...")
    layers = ai_service.analyze_music_prompt_layers(user_text, extra_fields)
    print(f"[SUCCESS] AI analysis completed, extracted layers: {list(layers.keys())}")
    
    # 2. 构建高保真分层 prompt
    print("[BUILD] Building high-fidelity music generation prompt...")
    prompt = ai_service.build_high_fidelity_musicgen_prompt(
        genre=layers.get('genre', ''),
        style=layers.get('style', ''),
        mood=layers.get('mood', ''),
        feeling=layers.get('feeling', ''),
        instrumentation=layers.get('instrumentation', []),
        tempo=layers.get('tempo', ''),
        bpm=layers.get('bpm', 0),
        production_quality=layers.get('production_quality', ''),
        artist_style=layers.get('artist_style', '')
    )
    print(f"[PROMPT] Final prompt: {prompt[:100]}...")
    
    # 3. 生成音乐
    print(f"[MODEL] Starting music generation (expected {duration} seconds)...")
    music_url = await audio_service.generate_music(
        description=prompt,
        duration=duration
    )
    
    if music_url:
        print(f"[SUCCESS] Music generation completed: {music_url}")
    else:
        print("[FAILED] Music generation failed")
    
    # 4. 生成背景图片
    print("[IMAGE] Starting background image generation...")
    background_url = None
    try:
        # 构建图片生成的 prompt
        image_prompt = f"Abstract visualization of {prompt}. Artistic, atmospheric, minimal design."
        background_url = await image_service.generate_background(description=image_prompt)
        if background_url:
            print(f"[SUCCESS] Background image generation completed: {background_url}")
        else:
            print("[WARNING] Background image generation failed - this is optional")
    except Exception as e:
        print(f"[ERROR] Background image generation failed: {e} - this is optional")

    print("[COMPLETE] Music generation process completed!")
    return {
        'music_url': music_url,
        'prompt': prompt,
        'layers': layers,
        'background_url': background_url  # 可能为 None，前端需要处理
    }

@app.post("/api/generate-background")
async def generate_background(request: ImageGenerationRequest):
    try:
        image_url = await image_service.generate_background(
            description=request.description
        )
        
        if not image_url:
            raise HTTPException(status_code=500, detail="Failed to generate background image")
            
        return {"image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-options")
async def generate_options(request: OptionGenerationRequest):
    """
    根据 mode、input、stage 生成 atmosphere/mood/elements 选项，AI 失败时返回默认。
    """
    # 默认选项
    default_options = {
        'atmosphere': [
            "Cozy and intimate",
            "Spacious and airy",
            "Lively and energetic",
            "Calm and serene",
            "Mysterious and intriguing",
        ],
        'mood': [
            "Relaxed",
            "Focused",
            "Inspired",
            "Dreamy",
            "Uplifting",
            "Melancholic",
        ],
        'elements': [
            "Rain", "Wind", "Birds chirping", "Ocean waves", "Fire crackling",
            "Coffee machine sounds", "Distant chatter", "Footsteps", "Gentle music",
            "Thunderstorm", "Night crickets", "City hum", "Train passing",
        ],
    }
    try:
        # 这里假设有 ai_service.generate_options 方法，实际可用 openai/gemini/其他大模型
        ai_options = await ai_service.generate_options(
            mode=request.mode,
            user_input=request.input,
            stage=request.stage
        )
        if ai_options and isinstance(ai_options, list) and all(isinstance(opt, str) for opt in ai_options):
            return {"options": ai_options}
    except Exception as e:
        print(f"AI option generation failed: {e}")
    # fallback
    return {"options": default_options.get(request.stage, [])}

@app.post("/api/generate-musicgen-options", response_model=MusicGenOptionResponse)
async def generate_musicgen_options(request: MusicGenOptionRequest):
    """
    动态生成 MusicGen 分支多级选项，支持中英文输入，输出英文选项。
    """
    try:
        options = await ai_service.generate_musicgen_options(
            stage=request.stage,
            user_input=request.user_input or ""
        )
        if not options:
            raise HTTPException(status_code=500, detail="AI failed to generate options")
        return {"options": options}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-stable-audio", response_model=StableAudioGenerationResponse)
async def generate_stable_audio(request: StableAudioGenerationRequest):
    """使用 Stable Audio Open Small 模型生成音频"""
    try:
        import time
        
        print(f"[STABLE_AUDIO] 开始生成音频 - 提示词: {request.prompt[:50]}...")
        print(f"[PARAMS] 时长: {request.duration}s, 步数: {request.steps}, CFG: {request.cfg_scale}")
        
        start_time = time.time()
        
        # 生成音频
        audio_path = stable_audio_service.generate_audio(
            prompt=request.prompt,
            duration=request.duration,
            steps=request.steps,
            cfg_scale=request.cfg_scale,
            sampler_type=request.sampler_type
        )
        
        generation_time = time.time() - start_time
        
        # 获取文件信息
        file_size = os.path.getsize(audio_path) if os.path.exists(audio_path) else 0
        
        # 构建音频URL
        audio_filename = os.path.basename(audio_path)
        audio_url = f"/static/generated_audio/{audio_filename}"
        
        # 获取模型信息
        model_info = stable_audio_service.get_model_info()
        
        print(f"[SUCCESS] Stable Audio 生成完成 - 耗时: {generation_time:.2f}秒, 大小: {file_size} bytes")
        
        return StableAudioGenerationResponse(
            audio_url=audio_url,
            generation_time=generation_time,
            file_size=file_size,
            model_info=model_info
        )
        
    except Exception as e:
        print(f"[ERROR] Stable Audio 生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"音频生成失败: {str(e)}")

@app.get("/api/stable-audio-info")
async def get_stable_audio_info():
    """获取 Stable Audio Open Small 模型信息"""
    try:
        info = stable_audio_service.get_model_info()
        return {
            "model_info": info,
            "status": "ready" if info["is_loaded"] else "not_loaded"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型信息失败: {str(e)}")

@app.on_event("startup")
async def startup_event():
    try:
        print("=== Nightingale Backend Startup ===")
        print("✅ FastAPI server started successfully")
        print("✅ Audio generation service ready (using worker script)")
        print("✅ Supabase storage service configured")
        print("✅ Gemini AI service configured")
        if os.environ.get("STABILITY_API_KEY"):
            print("✅ Image generation service: STABILITY_API_KEY is set")
        else:
            print("⚠️  Image generation service: STABILITY_API_KEY not set (optional)")
        # 检查ffmpeg
        import shutil
        if shutil.which("ffmpeg"):
            print("✅ Audio processing: ffmpeg found")
        else:
            print("⚠️  Audio processing: ffmpeg not found (optional)")
        print("🚀 Server ready at http://localhost:8000")
        print("📚 API docs at http://localhost:8000/docs")
        print("=====================================")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        raise 

app.include_router(router) 