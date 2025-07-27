"""
Stable Audio 专用服务
只包含音频生成相关功能，不包含 Google Generative AI
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import sys
from pathlib import Path

# 加载 .env 文件
from dotenv import load_dotenv

# 获取项目根目录
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"

# 加载环境变量
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ 已加载环境变量文件: {env_path}")
else:
    print(f"⚠️  环境变量文件不存在: {env_path}")

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.stable_audio_service import stable_audio_service
from app.services.storage_service import storage_service

app = FastAPI(title="Stable Audio Service", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载音频输出目录为静态文件服务
audio_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_output")
os.makedirs(audio_output_dir, exist_ok=True)
app.mount("/static/generated_audio", StaticFiles(directory=audio_output_dir), name="generated_audio")

@app.get("/")
async def root():
    return {"message": "Stable Audio Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "stable-audio"}

@app.post('/api/generate-audio')
async def generate_audio(request: Request):
    """使用 Stable Audio 模型生成音频"""
    try:
        data = await request.json()
        description = data.get('userInput') or data.get('description', '')
        
        print(f"[STABLE_AUDIO] 开始生成音频 - 描述: {description[:50]}...")
        
        # 使用 Stable Audio 服务生成音频
        local_audio_path = stable_audio_service.generate_audio(description)
        
        print(f"[STABLE_AUDIO] 音频生成完成: {local_audio_path}")
        
        # 上传到云存储
        print(f"[STABLE_AUDIO] 开始上传到云存储...")
        cloud_url = await storage_service.upload_audio(local_audio_path, description)
        
        if cloud_url:
            print(f"[STABLE_AUDIO] 上传成功: {cloud_url}")
            return {
                'audio_url': cloud_url,
                'prompt': description,
                'service': 'stable-audio'
            }
        else:
            print(f"[STABLE_AUDIO] 上传失败，返回静态文件URL")
            static_url = f"/static/generated_audio/{os.path.basename(local_audio_path)}"
            return {
                'audio_url': static_url,
                'prompt': description,
                'service': 'stable-audio'
            }
        
    except Exception as e:
        print(f"[STABLE_AUDIO] 错误: {str(e)}")
        return {
            'error': str(e),
            'service': 'stable-audio'
        }

@app.post('/api/generate-stable-audio')
async def generate_stable_audio(request: Request):
    """专门的 Stable Audio 生成接口"""
    try:
        data = await request.json()
        description = data.get('prompt', '')
        duration = data.get('duration', 10.0)
        
        print(f"[STABLE_AUDIO] 开始生成音频 - 描述: {description[:50]}... 时长: {duration}秒")
        
        # 使用 Stable Audio 服务生成音频
        local_audio_path = stable_audio_service.generate_audio(description, duration)
        
        print(f"[STABLE_AUDIO] 音频生成完成: {local_audio_path}")
        
        # 上传到云存储
        print(f"[STABLE_AUDIO] 开始上传到云存储...")
        cloud_url = await storage_service.upload_audio(local_audio_path, description)
        
        if cloud_url:
            print(f"[STABLE_AUDIO] 上传成功: {cloud_url}")
            return {
                'audio_url': cloud_url,
                'prompt': description,
                'duration': duration,
                'service': 'stable-audio'
            }
        else:
            print(f"[STABLE_AUDIO] 上传失败，返回静态文件URL")
            static_url = f"/static/generated_audio/{os.path.basename(local_audio_path)}"
            return {
                'audio_url': static_url,
                'prompt': description,
                'duration': duration,
                'service': 'stable-audio'
            }
        
    except Exception as e:
        print(f"[STABLE_AUDIO] 错误: {str(e)}")
        return {
            'error': str(e),
            'service': 'stable-audio'
        }

if __name__ == "__main__":
    import uvicorn
    
    # 从环境变量获取配置
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8001))
    reload = os.getenv("RELOAD", "True").lower() == "true"
    
    print(f"🚀 启动 Stable Audio 服务...")
    print(f"📍 地址: http://{host}:{port}")
    print(f"🔄 热重载: {reload}")
    
    uvicorn.run(app, host=host, port=port, reload=reload) 