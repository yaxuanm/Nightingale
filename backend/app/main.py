from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import os
from dotenv import load_dotenv
from .services.audio_service import audio_service
from fastapi.staticfiles import StaticFiles
from .services.ai_service import ai_service

# Get the path to the current file's directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

app = FastAPI(title="Ambiance Weaver API",
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

# Ensure directories exist
os.makedirs(os.path.join(BASE_DIR, "audio_samples"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "audio_output"), exist_ok=True)

# Mount audio_samples directory as a static file service (for input samples)
app.mount("/static/audio", StaticFiles(directory=os.path.join(BASE_DIR, "audio_samples")), name="audio")

# Mount audio_output directory as a static file service
app.mount("/static/generated_audio", StaticFiles(directory=os.path.join(BASE_DIR, "audio_output")), name="generated_audio")

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
    effects_config: Optional[dict] = None

class AudioGenerationResponse(BaseModel):
    audio_url: str

@app.get("/")
async def root():
    return {"message": "Welcome to Ambiance Weaver API"}

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

@app.post("/api/generate-audio")
async def generate_audio(request: AudioGenerationRequest):
    try:
        audio_url = await audio_service.generate_audio(
            description=request.description,
            duration=request.duration,
            is_poem=request.is_poem,
            mode=request.mode,
            effects_config=request.effects_config
        )
        
        if not audio_url:
            raise HTTPException(status_code=500, detail="Failed to generate audio")
            
        return {"audio_url": audio_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    try:
        audio_service.load_model()
    except Exception as e:
        raise 