from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import os
from dotenv import load_dotenv
from .services.audio_service import audio_service
from fastapi.staticfiles import StaticFiles

# 获取当前文件所在目录的路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

app = FastAPI(title="Ambiance Weaver API",
             description="AI-powered ambient sound generation API",
             version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保目录存在
os.makedirs(os.path.join(BASE_DIR, "audio_samples"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "audio_output"), exist_ok=True)

# 将 audio_samples 目录挂载为静态文件服务（用于输入样本）
app.mount("/static/audio", StaticFiles(directory=os.path.join(BASE_DIR, "audio_samples")), name="audio")

# 将 audio_output 目录挂载为静态文件服务
app.mount("/static/generated_audio", StaticFiles(directory=os.path.join(BASE_DIR, "audio_output")), name="generated_audio")

# 创建音频生成服务实例 (确保这里是正确的单例模式)
# audio_service = AudioGenerationService() # This line should be commented out or removed if audio_service is imported as an already initialized instance

class SceneRequest(BaseModel):
    prompt: str
    mode: str = "guided"  # "guided" or "free"
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
    duration: Optional[int] = 5
    is_poem: Optional[bool] = False
    effects_config: Optional[Dict[str, Dict[str, Any]]] = None

class AudioGenerationResponse(BaseModel):
    audio_url: str

@app.get("/")
async def root():
    return {"message": "Welcome to Ambiance Weaver API"}

@app.post("/api/generate-scene", response_model=SceneResponse)
async def generate_scene(request: SceneRequest):
    try:
        # 模拟 LLM 交互，根据 prompt 和 chat_history 决定 AI 响应和是否生成音频
        ai_response_text = ""
        should_generate = False

        lower_prompt = request.prompt.lower()

        if "生成音频" in lower_prompt or "create audio" in lower_prompt or "生成音景" in lower_prompt or "好了" in lower_prompt or "可以了" in lower_prompt:
            ai_response_text = "明白了！我将为您生成专属音景。请稍候..."
            should_generate = True
        elif "下雨" in lower_prompt:
            ai_response_text = "关于雨的音景，您想要小雨、中雨还是雷雨呢？"
        elif "咖啡馆" in lower_prompt:
            ai_response_text = "咖啡馆里您是想听到轻声细语、咖啡机的声音，还是舒缓的音乐？"
        elif "森林" in lower_prompt:
            ai_response_text = "森林音景很棒！您是想听鸟鸣、风声，还是潺潺溪流声？"
        elif not request.chat_history: # First message from user
            ai_response_text = f"好的！您选择了 {request.mode} 模式，并且提出了 \"{request.prompt}\" 的想法。这很有趣！现在，请告诉我您对这个音景的更多细节，例如您想要什么样的氛围、心情或具体的元素？"
        else:
            ai_response_text = "好的，我正在整合您的想法。还有其他想要加入的元素吗？如果您觉得可以了，可以说'生成音频'或'可以了'。"

        return SceneResponse(response=ai_response_text, should_generate_audio=should_generate)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-audio", response_model=AudioGenerationResponse)
async def generate_audio(request: AudioGenerationRequest):
    try:
        audio_url = await audio_service.generate_audio(
            description=request.description,
            duration=request.duration,
            is_poem=request.is_poem,
            effects_config=request.effects_config
        )
        
        if not audio_url:
            raise HTTPException(status_code=500, detail="音频生成失败")
            
        return AudioGenerationResponse(audio_url=audio_url)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    print("应用程序启动中... 正在预加载 AudioGen 模型...")
    try:
        audio_service.load_model()
        print("AudioGen 模型预加载完成。")
    except Exception as e:
        print(f"模型加载失败: {str(e)}")
        raise 