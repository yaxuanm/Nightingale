import os
import warnings
from dotenv import load_dotenv

# 忽略 ffmpeg 警告
warnings.filterwarnings("ignore", message="Couldn't find ffprobe or avprobe")
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
import json
from datetime import datetime

def generate_long_stable_audio(prompt: str, total_duration: float = 20.0, segment_duration: float = 10.0, crossfade_ms: int = 1000) -> str:
    """
    生成单段音频，然后循环播放达到目标时长
    """
    import uuid, os, subprocess
    print(f"[LONG_AUDIO] Starting generate_long_stable_audio with prompt: {prompt[:50]}...")
    print(f"[LONG_AUDIO] Current working directory: {os.getcwd()}")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 只生成一次10秒的音频
        seg_dur = min(segment_duration, 11.0)  # 最大11秒
        seg_path = os.path.join(tmpdir, "single_segment.wav")
        
        # 使用动态路径 - 指向 backend 目录的虚拟环境
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(current_dir)  # backend 目录
        worker_script = os.path.join(base_dir, "scripts", "run_stable_audio_worker.py")
        venv_python = os.path.join(base_dir, "venv_stableaudio", "Scripts", "python.exe")
        
        # 检查文件是否存在
        if not os.path.exists(worker_script):
            raise Exception(f"Worker script not found: {worker_script}")
        if not os.path.exists(venv_python):
            raise Exception(f"Python executable not found: {venv_python}")
        
        # 设置环境变量
        env = os.environ.copy()
        env['PYTHONPATH'] = base_dir
        
        cmd = [venv_python, worker_script, "--prompt", prompt, "--duration", str(seg_dur), "--out", seg_path]
        print(f"[LONG_AUDIO] Running Stable Audio worker: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', env=env, cwd=base_dir)
        if result.returncode != 0:
            print(f"[ERROR] Stable Audio worker failed: {result.stderr}")
            print(f"[ERROR] Command was: {' '.join(cmd)}")
            print(f"[ERROR] Return code: {result.returncode}")
            raise Exception(f"Stable Audio worker failed: {result.stderr}")
        print(f"[LONG_AUDIO] Single segment generated: {seg_path}")
        
        # 加载音频并循环播放达到目标时长
        segment_audio = AudioSegment.from_file(seg_path)
        segment_duration_ms = len(segment_audio)
        target_duration_ms = int(total_duration * 1000)
        
        # 计算需要重复多少次
        repeats_needed = int(target_duration_ms / segment_duration_ms) + 1
        print(f"[LONG_AUDIO] Segment duration: {segment_duration_ms}ms, target: {target_duration_ms}ms, repeats: {repeats_needed}")
        
        # 重复音频片段
        final_audio = segment_audio * repeats_needed
        
        # 截断到目标时长
        final_audio = final_audio[:target_duration_ms]
        
        # 使用绝对路径保存
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        audio_output_dir = os.path.join(current_file_dir, "..", "audio_output")
        audio_output_dir = os.path.abspath(audio_output_dir)  # 解析绝对路径
        os.makedirs(audio_output_dir, exist_ok=True)
        out_path = os.path.join(audio_output_dir, f"stable_long_{uuid.uuid4().hex}.wav")
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
    # 使用绝对路径
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    audio_output_dir = os.path.join(current_file_dir, "..", "audio_output")
    audio_output_dir = os.path.abspath(audio_output_dir)  # 解析绝对路径
    os.makedirs(audio_output_dir, exist_ok=True)
    output_path = os.path.join(audio_output_dir, filename)
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
        print(f"[AUDIO] 开始生成音频 - 描述: {description[:50]}...")
        print(f"[AUDIO] 调用 generate_long_stable_audio...")
        out_path = generate_long_stable_audio(description, total_duration=duration)
        print(f"[AUDIO] 音频生成完成: {out_path}")
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
        print(f"[MUSIC] 开始生成音乐 - 描述: {description[:50]}...")
        print(f"[MUSIC] 调用 generate_long_stable_audio...")
        out_path = generate_long_stable_audio(description, total_duration=duration)
        print(f"[MUSIC] 音乐生成完成: {out_path}")
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
    # 路径测试
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    audio_output_dir = os.path.join(current_file_dir, "..", "audio_output")
    audio_output_dir = os.path.abspath(audio_output_dir)
    print(f"[PATH_TEST] Current file dir: {current_file_dir}")
    print(f"[PATH_TEST] Audio output dir: {audio_output_dir}")
    print(f"[PATH_TEST] Audio output exists: {os.path.exists(audio_output_dir)}")
    
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
        print(f"[STORY] Starting TTS generation...")
        tts_filename = f"tts_{uuid.uuid4().hex}.mp3"
        # 使用更可靠的绝对路径
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        audio_output_dir = os.path.join(current_file_dir, "..", "audio_output")
        audio_output_dir = os.path.abspath(audio_output_dir)  # 解析绝对路径
        print(f"[STORY] audio_output_dir: {audio_output_dir}")
        print(f"[STORY] audio_output_dir exists: {os.path.exists(audio_output_dir)}")
        os.makedirs(audio_output_dir, exist_ok=True)
        tts_path = os.path.join(audio_output_dir, tts_filename)
        print(f"[STORY] tts_path: {tts_path}")
        print(f"[STORY] tts_path absolute: {os.path.abspath(tts_path)}")
        await tts_to_audio(narrative_script, tts_path, voice="en-US-JennyNeural")
        print(f"[STORY] TTS generation completed")
        
        # 检查文件是否存在
        print(f"[DEBUG] Checking if TTS file exists: {os.path.exists(tts_path)}")
        if os.path.exists(tts_path):
            print(f"[DEBUG] TTS file size: {os.path.getsize(tts_path)} bytes")
            print(f"[DEBUG] TTS file absolute path: {os.path.abspath(tts_path)}")
        else:
            print(f"[ERROR] TTS file does not exist!")
            print(f"[DEBUG] Directory contents: {os.listdir(audio_output_dir)}")
        
        # 3. 获取 TTS 音频长度
        print(f"[DEBUG] About to import AudioSegment...")
        from pydub import AudioSegment
        print(f"[DEBUG] AudioSegment imported successfully")

        print(f"[DEBUG] About to load TTS file: {tts_path}")
        try:
            tts_audio = AudioSegment.from_file(tts_path)
            print(f"[DEBUG] TTS file loaded successfully")
        except Exception as e:
            print(f"[ERROR] Failed to load TTS file: {e}")
            import traceback
            traceback.print_exc()
            raise

        tts_duration_ms = len(tts_audio)
        tts_duration_seconds = tts_duration_ms / 1000
        print(f"[STORY] TTS duration: {tts_duration_seconds:.2f} seconds (target: {duration}s)")
        
        # 4. 用 Stable Audio worker 生成 soundscape（总时长为 duration）
        print(f"[STORY] About to call generate_long_stable_audio with prompt: {prompt[:50]}...")
        try:
            stable_audio_out = generate_long_stable_audio(prompt, total_duration=duration)
            print(f"[STORY] generate_long_stable_audio completed: {stable_audio_out}")
        except Exception as e:
            print(f"[STORY] generate_long_stable_audio failed: {e}")
            raise e
        
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
        mixed_path = os.path.join(audio_output_dir, mixed_filename)
        mixed.export(mixed_path, format="mp3")
        
        # 6. 上传合成音频到 Supabase
        from .services.storage_service import storage_service
        cloud_url = await storage_service.upload_audio(mixed_path, mixed_filename)
        return {"narrative_script": narrative_script, "audio_url": cloud_url}
    except Exception as e:
        print(f"[ERROR] /api/create-story: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/create-story-music")
async def create_story_music(request: dict):
    """
    生成旁白+音乐混音（音乐用Stable Audio生成）
    输入: { "narrative": "...", "music_prompt": "...", "duration": 30 }
    输出: { "narrative_script": "...", "audio_url": "..." }
    """
    narrative = request.get("narrative")
    music_prompt = request.get("music_prompt")
    duration = float(request.get("duration", 30))

    if not narrative or not music_prompt:
        raise HTTPException(status_code=400, detail="Missing narrative or music_prompt")

    try:
        # 1. 生成旁白音频
        tts_filename = f"tts_{uuid.uuid4().hex}.mp3"
        # 使用绝对路径
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        audio_output_dir = os.path.join(current_file_dir, "..", "audio_output")
        audio_output_dir = os.path.abspath(audio_output_dir)  # 解析绝对路径
        os.makedirs(audio_output_dir, exist_ok=True)
        tts_path = os.path.join(audio_output_dir, tts_filename)
        await tts_to_audio(narrative, tts_path, voice="en-US-JennyNeural")

        # 2. 用Stable Audio生成音乐
        music_path = generate_long_stable_audio(music_prompt, total_duration=duration)

        # 3. 混音
        tts_audio = AudioSegment.from_file(tts_path)
        music_audio = AudioSegment.from_file(music_path)
        # 如果音乐比旁白短，循环补齐
        if len(music_audio) < len(tts_audio):
            repeats = int(len(tts_audio) / len(music_audio)) + 1
            music_audio = music_audio * repeats
        music_audio = music_audio[:len(tts_audio) + 2000]  # 比旁白长2秒
        tts_audio = tts_audio - 2  # 旁白音量降低
        music_audio = music_audio - 4  # 音乐音量降低
        mixed = music_audio.overlay(tts_audio)
        mixed_filename = f"story_music_mix_{uuid.uuid4().hex}.mp3"
        mixed_path = os.path.join(audio_output_dir, mixed_filename)
        mixed.export(mixed_path, format="mp3")

        # 4. 上传合成音频
        from .services.storage_service import storage_service
        cloud_url = await storage_service.upload_audio(mixed_path, mixed_filename)
        return {
            "narrative_script": narrative,
            "audio_url": cloud_url
        }
    except Exception as e:
        print(f"[ERROR] /api/create-story-music: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/music-prompt")
async def music_prompt(request: dict):
    """
    生成适合Stable Audio的音乐描述prompt。
    输入: { "genre": ..., "tempo": ..., "usage": ..., "instruments": [...], "input": ... }
    输出: { "prompt": "..." }
    """
    genre = request.get("genre")
    tempo = request.get("tempo")
    usage = request.get("usage")
    instruments = request.get("instruments", [])
    user_input = request.get("input", "")
    try:
        # 1. 让Gemini根据Stable Audio需求生成自然语言描述
        gemini_prompt = f"""
You are a world-class music prompt engineer. Given the following user selections, write a single, vivid, natural English sentence describing the music to be generated. The description should be suitable for input to a generative AI music model (Stable Audio) and should include genre, tempo, usage, and instruments, as well as the user's inspiration or idea. Do not use list format, just a single flowing sentence. Be concise but evocative.

Selections:
- Genre: {genre}
- Tempo: {tempo}
- Usage: {usage}
- Instruments: {', '.join(instruments)}
- User input: {user_input}

Example output:
"A slow ambient piece for background use, featuring synth and violin, inspired by whispers of forgotten lore in a moonlit ancient ruin."

Now write the prompt:
"""
        response = ai_service.client.models.generate_content(
            model=ai_service._get_current_model(),
            contents=gemini_prompt
        )
        text = response.text.strip() if response and response.text else None
        # 只取第一行或第一个句号前内容，去除多余解释
        if text:
            text = text.split('\n')[0].strip('"')
        if not text:
            raise Exception("Failed to generate music prompt")
        return {"prompt": text}
    except Exception as e:
        print(f"[ERROR] /api/music-prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-prompt")
async def generate_prompt(request: dict):
    """
    根据用户输入、mood、elements、mode生成自然语言音频描述prompt。
    输入: { "user_input": ..., "mood": ..., "elements": [...], "mode": ... }
    输出: { "prompt": "..." }
    """
    user_input = request.get("user_input", "")
    mood = request.get("mood", "")
    elements = request.get("elements", [])
    mode = request.get("mode", "default")
    try:
        # 构建LLM prompt
        if mode == "asmr":
            llm_prompt = f"""
You are an expert in ASMR soundscape design. Given the user's idea and selected sound elements, write a single, vivid, natural English sentence describing the ASMR soundscape to be generated. Focus on tactile, soothing, and immersive triggers. 80% of the content should be classic ASMR triggers (e.g. Tapping, Brushing, Page turning, Ear cleaning, Crinkling, Hand movements, Water sounds, Glove sounds, Typing, Spray sounds, Personal attention, Hair brushing, Face touching, Light triggers, Scalp massage, Whispering, Scratching, Plastic crinkling, Mic brushing, Roleplay: doctor, Roleplay: haircut, Roleplay: spa). 20% can be gentle, relaxing environmental sounds (e.g. Gentle rain, Soft wind, Distant thunder, Footsteps on carpet, Water dripping, Fire crackling, Pages turning in a quiet library). Do not generate poetic lines, abstract moods, or pure nature scenes without a tactile or ASMR element. Do not use list format, just a single flowing sentence. Be concise but evocative.

User input: {user_input}
Selected elements: {', '.join(elements)}
Mode: asmr

Example chips: Tapping, Brushing, Page turning, Ear cleaning, Gentle rain, Soft wind, Distant thunder, Footsteps on carpet, Water dripping, Fire crackling, Whispering, Scalp massage

Example output:
"A soothing ASMR soundscape with gentle rain tapping on the window, soft brushing sounds, and the subtle footsteps in a quiet room."
"""
        else:
            llm_prompt = f"""
You are an expert in soundscape design. Given the user's idea, mood, and selected sound elements, write a single, vivid, natural English sentence describing the soundscape to be generated. The description should be suitable for input to a generative AI audio model. Do not use list format, just a single flowing sentence. Be concise but evocative.

User input: {user_input}
Mood: {mood}
Selected elements: {', '.join(elements)}
Mode: {mode}

Example output:
"A peaceful soundscape for deep focus, featuring gentle rain, soft wind, and distant thunder."
"""
        response = ai_service.client.models.generate_content(
            model=ai_service._get_current_model(),
            contents=llm_prompt
        )
        text = response.text.strip() if response and response.text else None
        # 只取第一行或第一个句号前内容，去除多余解释
        if text:
            text = text.split('\n')[0].strip('"')
        if not text:
            raise Exception("Failed to generate prompt")
        return {"prompt": text}
    except Exception as e:
        print(f"[ERROR] /api/generate-prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 获取分享基础URL
SHARE_BASE_URL = os.getenv("SHARE_BASE_URL", "http://localhost:3000")

@app.post("/api/create-share")
async def create_share(request: dict):
    """
    创建分享链接，包含音频和背景数据
    输入: { "audio_url": "...", "background_url": "...", "description": "...", "title": "..." }
    输出: { "share_id": "...", "share_url": "..." }
    """
    audio_url = request.get("audio_url")
    background_url = request.get("background_url")
    description = request.get("description", "")
    title = request.get("title", "My Soundscape")
    
    if not audio_url:
        raise HTTPException(status_code=400, detail="Missing 'audio_url' parameter")
    
    try:
        # 生成唯一的分享ID
        share_id = str(uuid.uuid4())
        
        # 创建分享数据
        share_data = {
            "id": share_id,
            "audio_url": audio_url,
            "background_url": background_url,
            "description": description,
            "title": title,
            "created_at": str(datetime.now()),
            "views": 0
        }
        
        # 保存到数据库或文件系统（这里简化处理，实际应该用数据库）
        shares_dir = os.path.join(BASE_DIR, "shares")
        os.makedirs(shares_dir, exist_ok=True)
        
        share_file = os.path.join(shares_dir, f"{share_id}.json")
        with open(share_file, 'w', encoding='utf-8') as f:
            json.dump(share_data, f, ensure_ascii=False, indent=2)
        
        # 使用环境变量中的域名生成分享URL
        share_url = f"{SHARE_BASE_URL}/share/{share_id}"
        
        return {
            "share_id": share_id,
            "share_url": share_url,
            "message": "Share created successfully"
        }
        
    except Exception as e:
        print(f"[ERROR] /api/create-share: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/edit-prompt")
async def edit_prompt(request: dict):
    """
    AI编辑prompt或narrative
    输入: { "current_prompt": "...", "edit_instruction": "...", "mode": "...", "is_story": true/false }
    输出: { "edited_prompt": "..." }
    """
    current_prompt = request.get("current_prompt", "")
    edit_instruction = request.get("edit_instruction", "")
    mode = request.get("mode", "default")
    is_story = request.get("is_story", False)
    
    if not current_prompt or not edit_instruction:
        raise HTTPException(status_code=400, detail="Missing 'current_prompt' or 'edit_instruction' parameter")
    
    try:
        # 使用AI服务编辑prompt或narrative
        edited_prompt = await ai_service.edit_prompt(current_prompt, edit_instruction, mode, is_story)
        
        return {
            "edited_prompt": edited_prompt,
            "message": "Prompt edited successfully"
        }
        
    except Exception as e:
        print(f"[ERROR] /api/edit-prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/share/{share_id}")
async def get_share(share_id: str):
    """
    获取分享数据
    """
    try:
        shares_dir = os.path.join(BASE_DIR, "shares")
        share_file = os.path.join(shares_dir, f"{share_id}.json")
        
        if not os.path.exists(share_file):
            raise HTTPException(status_code=404, detail="Share not found")
        
        with open(share_file, 'r', encoding='utf-8') as f:
            share_data = json.load(f)
        
        # 增加访问计数
        share_data["views"] += 1
        with open(share_file, 'w', encoding='utf-8') as f:
            json.dump(share_data, f, ensure_ascii=False, indent=2)
        
        return share_data
        
    except Exception as e:
        print(f"[ERROR] /api/share/{share_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    print("Nightingale Gemini API 启动完成！")

app.include_router(router) 