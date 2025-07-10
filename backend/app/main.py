import os
from dotenv import load_dotenv
# 指定 .env 路径，始终加载 backend/.env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    print(f"Warning: .env file not found at {env_path}")

from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from fastapi.staticfiles import StaticFiles
from .services.ai_service import ai_service, get_instruments_from_ai, build_musicgen_prompt, build_audiogen_prompt
from .services.image_service import ImageGenerationService
from fastapi import APIRouter
import subprocess

# Get the path to the current file's directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print(f"DEBUG: BASE_DIR is {BASE_DIR}")

# Ensure output directories exist at the very beginning
AUDIO_SAMPLES_DIR = os.path.join(BASE_DIR, "audio_samples")
IMAGE_OUTPUT_DIR = os.path.join(BASE_DIR, "image_output")

print(f"DEBUG: Ensuring AUDIO_SAMPLES_DIR {AUDIO_SAMPLES_DIR} exists.")
os.makedirs(AUDIO_SAMPLES_DIR, exist_ok=True)
print(f"DEBUG: Ensuring IMAGE_OUTPUT_DIR {IMAGE_OUTPUT_DIR} exists.")
os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)

print("DEBUG: SUPABASE_URL =", os.environ.get("SUPABASE_URL"))
print("DEBUG: SUPABASE_KEY =", os.environ.get("SUPABASE_KEY"))

# 在 load_dotenv 之后实例化 image_service
image_service = None
try:
    image_service = ImageGenerationService()
except ValueError as e:
    print(f"Failed to initialize ImageGenerationService: {e}")
    image_service = None

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
app.mount("/static/audio", StaticFiles(directory=AUDIO_SAMPLES_DIR), name="audio")
# Mount image_output directory as a static file service
app.mount("/static/generated_images", StaticFiles(directory=IMAGE_OUTPUT_DIR), name="generated_images")

class SceneRequest(BaseModel):
    prompt: str
    mode: str = "default"
    chat_history: List[str] = []

class SceneResponse(BaseModel):
    response: str
    should_generate_audio: bool

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

class InspirationChipsRequest(BaseModel):
    mode: str = "default"
    user_input: str = ""

class InspirationChipsResponse(BaseModel):
    chips: list[str]

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
    print("[DEBUG] /api/generate-options 收到请求:", request.dict())
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
        ai_options = await ai_service.generate_options(
            mode=request.mode,
            user_input=request.input,
            stage=request.stage
        )
        print("[DEBUG] AI options:", ai_options)
        if ai_options and isinstance(ai_options, list) and all(isinstance(opt, str) for opt in ai_options):
            print("[DEBUG] 返回 AI 生成选项:", ai_options)
            return {"options": ai_options}
    except Exception as e:
        print(f"[DEBUG] AI option generation failed: {e}")
    fallback = default_options.get(request.stage, [])
    print("[DEBUG] 返回 fallback 选项:", fallback)
    return {"options": fallback}

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
        if options and isinstance(options, list) and all(isinstance(opt, str) for opt in options):
            return {"options": options}
    except Exception as e:
        print(f"MusicGen option generation failed: {e}")
    return {"options": []}

@app.post("/api/generate-inspiration-chips", response_model=InspirationChipsResponse)
async def generate_inspiration_chips(request: InspirationChipsRequest):
    """
    生成随机的inspiration chips，用于MainScreen的提示选项
    """
    try:
        chips = await ai_service.generate_inspiration_chips(
            mode=request.mode,
            user_input=request.user_input
        )
        if chips and isinstance(chips, list) and all(isinstance(chip, str) for chip in chips):
            return {"chips": chips}
    except Exception as e:
        print(f"Inspiration chips generation failed: {e}")
    
    # Fallback options
    fallback_chips = [
        "A cozy cafe on a rainy afternoon",
        "Gentle forest sounds with a distant waterfall",
        "The calm before a thunderstorm",
        "A quiet library with turning pages",
        "Meditative ocean waves",
        "Lively city street during rush hour",
    ]
    return {"chips": fallback_chips}

@app.on_event("startup")
async def startup_event():
    print("Nightingale Gemini API 启动完成！")

app.include_router(router) 