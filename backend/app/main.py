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
from .services.audio_service import tts_to_audio
from fastapi import APIRouter
import subprocess
import uuid
from fastapi import UploadFile
import uuid
from pydub import AudioSegment
from .services.freesound_concat_demo import generate_freesound_mix, generate_freesound_mix_with_duration
# from .services.stable_audio_service import stable_audio_service
import tempfile

def generate_long_stable_audio(prompt: str, total_duration: float = 20.0, segment_duration: float = 10.0, crossfade_ms: int = 1000) -> str:
    """
    多段 Stable Audio worker 生成音频，拼接并做淡入淡出混合，导出总时长音频
    """
    import uuid, os, subprocess
    segments = []
    remaining = total_duration
    segment_idx = 0
    with tempfile.TemporaryDirectory() as tmpdir:
        while remaining > 0:
            seg_dur = min(segment_duration, remaining, 11.0)
            seg_path = os.path.join(tmpdir, f"seg_{segment_idx}.wav")
            worker_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts/run_stable_audio_worker.py"))
            # 修正虚拟环境路径，指向 backend/venv_stableaudio/Scripts/python.exe（回退到上一级目录）
            venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "venv_stableaudio", "Scripts", "python.exe"))
            cmd = [venv_python, worker_script, "--prompt", prompt, "--duration", str(seg_dur), "--out", seg_path]
            print(f"[LONG_AUDIO] Running Stable Audio worker: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"[ERROR] Stable Audio worker failed: {result.stderr}")
                raise Exception("Stable Audio worker failed")
            print(f"[LONG_AUDIO] Segment {segment_idx} generated: {seg_path}")
            segments.append(AudioSegment.from_file(seg_path))
            remaining -= seg_dur
            segment_idx += 1
        # 拼接并做淡入淡出混合
        final_audio = segments[0]
        for seg in segments[1:]:
            final_audio = final_audio.append(seg, crossfade=crossfade_ms)
        # 截断到总时长
        final_audio = final_audio[:int(total_duration * 1000)]
        out_path = os.path.join("audio_output", f"stable_long_{uuid.uuid4().hex}.wav")
        final_audio.export(out_path, format="wav")
        print(f"[LONG_AUDIO] Final audio saved: {out_path}")
        return out_path

# Get the path to the current file's directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 在 load_dotenv 之后实例化 image_service
image_service = None
try:
    image_service = ImageGenerationService()
except ValueError as e:
    print(f"Failed to initialize ImageGenerationService: {e}")
    image_service = None

# Ensure output directories exist at the very beginning
AUDIO_SAMPLES_DIR = os.path.join(BASE_DIR, "audio_samples")
IMAGE_OUTPUT_DIR = os.path.join(BASE_DIR, "image_output")
os.makedirs(AUDIO_SAMPLES_DIR, exist_ok=True)
os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)

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
    print("[DEBUG] 收到/generate-scene请求", request.dict())
    try:
        # Analyze the scene with AI
        print("[DEBUG] 调用parse_scene前")
        scene_elements = await ai_service.parse_scene(request.prompt)
        print("[DEBUG] parse_scene后，scene_elements:", scene_elements)
        narrative_script = None
        if request.mode == "story":
            print("[DEBUG] 进入story mode，准备生成narrative script")
            story_prompt = f"""
You are a masterful storyteller. Based on the following user memory, story, or scene description, write a short, immersive, and vivid narrative script in English (3-5 sentences). Use sensory details and emotional language to help the listener feel present in the moment. Do not include sound design instructions, just the story. Make it suitable for being read aloud as an audio introduction.

User description: {request.prompt}

Narrative script:"""
            try:
                print("[DEBUG] 调用Gemini generate_content前")
                response = ai_service.client.models.generate_content(
                    model=ai_service._get_current_model(),
                    contents=story_prompt
                )
                print("[DEBUG] Gemini返回response")
                narrative_script = response.text.strip() if response and response.text else None
                print("[DEBUG] narrative_script:", narrative_script)
            except Exception as e:
                print(f"[ERROR] Failed to generate narrative script: {e}")
                narrative_script = None
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
        print("[DEBUG] 返回数据")
        return {
            "scene_description": request.prompt,
            "scene_elements": scene_elements,
            "ai_response": ai_response,
            "narrative_script": narrative_script
        }
    except Exception as e:
        print(f"[ERROR] /api/generate-scene异常: {e}")
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

@app.post("/api/tts")
async def tts_endpoint(request: dict):
    text = request.get('text')
    if not text or not isinstance(text, str):
        raise HTTPException(status_code=400, detail="Missing or invalid 'text' parameter")
    filename = f"tts_{uuid.uuid4().hex}.mp3"
    output_path = os.path.join("audio_output", filename)
    os.makedirs("audio_output", exist_ok=True)
    # 使用更柔和的 JennyNeural
    await tts_to_audio(text, output_path, voice="en-US-JennyNeural")
    # 上传到 Supabase
    from .services.storage_service import storage_service
    cloud_url = await storage_service.upload_audio(output_path, filename)
    return {"audio_url": cloud_url}

@app.post("/api/generate-audio")
async def generate_audio(request: dict):
    description = request.get("description") or request.get("userInput")
    duration = float(request.get("duration", 20))
    if not description:
        raise HTTPException(status_code=400, detail="Missing 'description' parameter")
    try:
        out_path = generate_long_stable_audio(description, total_duration=duration)
        from .services.storage_service import storage_service
        cloud_url = await storage_service.upload_audio(out_path, f"stable_{abs(hash(description))}")
        return {"audio_url": cloud_url, "duration": duration}
    except Exception as e:
        print(f"[ERROR] /api/generate-audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-music")
async def generate_music(request: dict):
    description = request.get("description") or request.get("userInput")
    duration = float(request.get("duration", 20))
    if not description:
        raise HTTPException(status_code=400, detail="Missing 'description' parameter")
    try:
        out_path = generate_long_stable_audio(description, total_duration=duration)
        from .services.storage_service import storage_service
        cloud_url = await storage_service.upload_audio(out_path, f"stable_music_{abs(hash(description))}")
        return {"audio_url": cloud_url, "duration": duration}
    except Exception as e:
        print(f"[ERROR] /api/generate-music: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/create-story")
async def create_story(request: dict):
    """
    一步生成旁白脚本、TTS音频、soundscape音频并混音，返回旁白文本和合成音频URL。
    输入: { "prompt": "完整的故事描述+soundscape选择", "original_description": "原始故事描述", "duration": 20 }
    输出: { "narrative_script": ..., "audio_url": ... }
    """
    prompt = request.get("prompt")
    original_description = request.get("original_description", "")
    duration = float(request.get("duration", 20))
    if not prompt or not isinstance(prompt, str):
        raise HTTPException(status_code=400, detail="Missing or invalid 'prompt' parameter")
    try:
        # 1. 生成旁白脚本（使用原始故事描述）
        story_prompt = f"""
You are a masterful storyteller. Based on the following user memory, story, or scene description, write a short, immersive, and vivid narrative script in English. Use sensory details and emotional language to help the listener feel present in the moment. Do not include sound design instructions, just the story. Make it suitable for being read aloud as an audio introduction.

User description: {original_description}

Requirements:
- The narration should be a complete story, not cut off in the middle.
- The narration should be about what can be read aloud in about {duration} seconds (for example, 20 seconds), but do not stop abruptly—finish the story naturally.
- 3-6 sentences is typical.

Narrative script:"""
        response = ai_service.client.models.generate_content(
            model=ai_service._get_current_model(),
            contents=story_prompt
        )
        narrative_script = response.text.strip() if response and response.text else None
        if not narrative_script:
            raise Exception("Failed to generate narrative script")
        
        # 2. TTS 生成旁白音频
        tts_filename = f"tts_{uuid.uuid4().hex}.mp3"
        tts_path = os.path.join("audio_output", tts_filename)
        await tts_to_audio(narrative_script, tts_path, voice="en-US-JennyNeural")
        
        # 3. 获取 TTS 音频长度
        from pydub import AudioSegment
        tts_audio = AudioSegment.from_file(tts_path)
        tts_duration_ms = len(tts_audio)
        tts_duration_seconds = tts_duration_ms / 1000
        print(f"[STORY] TTS duration: {tts_duration_seconds:.2f} seconds (target: {duration}s)")
        
        # 4. 用 Stable Audio worker 生成 soundscape（总时长为 duration）
        stable_audio_out = generate_long_stable_audio(prompt, total_duration=duration)
        
        # 5. 混音
        soundscape_audio = AudioSegment.from_file(stable_audio_out)
        # 确保 soundscape 长度与 TTS 匹配或稍长
        if len(soundscape_audio) < tts_duration_ms:
            repeats_needed = int(tts_duration_ms / len(soundscape_audio)) + 1
            soundscape_audio = soundscape_audio * repeats_needed
        soundscape_audio = soundscape_audio[:tts_duration_ms + 2000]  # 比 TTS 长 2 秒
        tts_audio = tts_audio - 2  # 降低 TTS 音量
        soundscape_audio = soundscape_audio - 4  # 降低 soundscape 音量
        mixed = soundscape_audio.overlay(tts_audio)
        mixed_filename = f"story_mix_{uuid.uuid4().hex}.mp3"
        mixed_path = os.path.join("audio_output", mixed_filename)
        mixed.export(mixed_path, format="mp3")
        
        # 6. 上传合成音频到 Supabase
        from .services.storage_service import storage_service
        cloud_url = await storage_service.upload_audio(mixed_path, mixed_filename)
        return {"narrative_script": narrative_script, "audio_url": cloud_url}
    except Exception as e:
        print(f"[ERROR] /api/create-story: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    print("Nightingale Gemini API 启动完成！")

app.include_router(router) 