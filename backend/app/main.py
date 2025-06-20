from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import os
from dotenv import load_dotenv
from .services.audio_service import audio_service
from fastapi.staticfiles import StaticFiles
from .services.ai_service import ai_service, get_instruments_from_ai, build_musicgen_prompt, build_audiogen_prompt
from .services.image_service import image_service
from fastapi import APIRouter

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

load_dotenv()

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
# audio_service = AudioGenerationService() # This line should be commented out or removed if audio_service is imported as an already initialized instance

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
    duration: int = 30

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
    duration = data.get('duration', 10)
    is_poem = data.get('is_poem', False)
    mode = data.get('mode', 'default')
    effects_config = data.get('effects_config')

    audio_url = await audio_service.generate_audio(
        description=description,
        duration=duration,
        is_poem=is_poem,
        effects_config=effects_config,
        mode=mode
    )

    return {
        'audio_url': audio_url,
        'prompt': description
    }

@router.post('/api/generate-music')
async def generate_music(request: Request):
    data = await request.json()
    atmosphere = data.get('atmosphere')
    mood = data.get('mood')
    elements = data.get('elements', [])
    user_input = data.get('userInput')
    reference_era = data.get('referenceEra')
    tempo = data.get('tempo')
    duration = data.get('duration', 30)

    # 1. AI 补全乐器
    instruments = get_instruments_from_ai(
        atmosphere, mood, elements, user_input, reference_era
    )

    # 2. 拼接结构化 prompt
    prompt = build_musicgen_prompt(
        atmosphere, mood, elements, user_input, instruments, tempo, reference_era
    )

    # 3. 调用 MusicGen 真实推理逻辑
    music_url = await audio_service.generate_music(
        description=prompt,
        duration=duration
    )

    return {
        'music_url': music_url,
        'prompt': prompt,
        'instruments': instruments
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

@app.on_event("startup")
async def startup_event():
    try:
        audio_service.load_audio_model()
    except Exception as e:
        raise 

app.include_router(router) 