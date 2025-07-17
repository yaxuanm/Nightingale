#!/usr/bin/env python3
"""
固定Web测试服务 - 使用预设的30个prompt
基于原有的batch_test_web.py，但使用固定的prompt列表
- /         : 前端页面（带进度条和评测）
- /api/generate-batch-test : POST，触发子进程生成音频，返回task_id
- /api/generate-progress   : GET，查询进度和结果
- 自动打开浏览器
- 数据存 audio_test_output/fixed_web/
- 依赖隔离：StableAudio在虚拟环境下运行
"""
import os
import sys
import time
import json
import random
import asyncio
import threading
import subprocess
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import webbrowser
from typing import Dict, Any

DATA_DIR = Path("audio_test_output/fixed_web")
AUDIO_DIR = DATA_DIR / "audio_files"
PROMPT_FILE = DATA_DIR / "fixed_prompts.json"
RESULT_FILE = DATA_DIR / "fixed_results.json"
PROGRESS_FILE = DATA_DIR / "fixed_progress.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/audio_files", StaticFiles(directory=AUDIO_DIR), name="audio_files")

TASKS: Dict[str, Dict[str, Any]] = {}

def create_fixed_prompts():
    """创建固定的30个prompt"""
    from fixed_prompts_generator import FIXED_PROMPTS
    
    prompts = []
    for prompt_data in FIXED_PROMPTS:
        prompt = {
            "id": prompt_data["id"],
            "mode": prompt_data["mode"],
            "user_input": prompt_data["final_prompt"],
            "inspiration_chip": prompt_data["final_prompt"],
            "atmosphere": prompt_data["final_prompt"],
            "elements": [prompt_data["final_prompt"]],
            "final_prompt": prompt_data["final_prompt"],
            "description": prompt_data["description"],
            "generation_time": time.time()
        }
        prompts.append(prompt)
    
    # 保存到文件
    with open(PROMPT_FILE, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)
    
    print(f"已创建 {len(prompts)} 个固定prompt")
    return prompts

def run_generate_audio():
    """在StableAudio虚拟环境下生成音频"""
    venv = "venv_stableaudio\\Scripts\\python.exe" if os.name == 'nt' else "venv_stableaudio/bin/python"
    script = "scripts/test_audio_generation.py"
    cmd = [venv, script, "--prompt", str(PROMPT_FILE), "--output", str(RESULT_FILE), "--audio_dir", str(AUDIO_DIR), "--progress_file", str(PROGRESS_FILE)]
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"音频生成失败: {e}")
        # fallback: 直接运行脚本
        subprocess.run([venv, script], check=True)
        report_dir = Path("audio_test_output/reports")
        files = list(report_dir.glob("audio_test_results_*.json"))
        if files:
            latest = max(files, key=lambda x: x.stat().st_mtime)
            with open(latest, 'r', encoding='utf-8') as f:
                data = json.load(f)
            with open(RESULT_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

async def batch_task(task_id: str):
    TASKS[task_id]["progress"] = 0.0
    TASKS[task_id]["done"] = False
    TASKS[task_id]["results"] = None
    
    # 1. 创建固定prompt
    TASKS[task_id]["progress"] = 0.1
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, create_fixed_prompts)
    TASKS[task_id]["progress"] = 0.2
    
    # 2. 生成音频
    await loop.run_in_executor(None, run_generate_audio)
    TASKS[task_id]["progress"] = 0.95
    
    # 3. 读取结果
    if RESULT_FILE.exists():
        with open(RESULT_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
        frontend_results = []
        for i, r in enumerate(results):
            frontend_results.append({
                "id": r.get("id", f"test_{i+1}"),
                "metrics": r.get("metrics", {}),
                "cloud_url": r.get("cloud_url", ""),
                "final_prompt": r.get("final_prompt", ""),
                "description": r.get("description", "")
            })
        TASKS[task_id]["results"] = frontend_results
    TASKS[task_id]["progress"] = 1.0
    TASKS[task_id]["done"] = True

@app.get("/", response_class=HTMLResponse)
async def index():
    with open(Path(__file__).parent / "batch_test_web_frontend.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.post("/api/generate-batch-test")
async def api_generate_batch_test():
    task_id = str(int(time.time()*1000)) + str(random.randint(1000,9999))
    TASKS[task_id] = {"progress": 0.0, "done": False, "results": None}
    threading.Thread(target=lambda: asyncio.run(batch_task(task_id))).start()
    return {"task_id": task_id}

@app.get("/api/generate-progress")
async def api_generate_progress(task_id: str):
    task = TASKS.get(task_id)
    progress = None
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                progress = json.load(f)
        except Exception:
            progress = None
    if not task:
        return JSONResponse({"error": "Task not found"}, status_code=404)
    resp = {
        "progress": task["progress"],
        "done": task["done"],
        "results": task["results"] if task["done"] else None
    }
    if progress:
        # 用更细粒度的进度覆盖
        resp["progress"] = 0.2 + 0.75 * (progress["current"] / max(progress["total"], 1))
        resp["current"] = progress["current"]
        resp["total"] = progress["total"]
        resp["prompts"] = progress["results"]
    return resp

def open_browser():
    url = "http://127.0.0.1:8012/"
    webbrowser.open(url)

def main():
    print("=== Nightingale 固定测试服务 ===")
    print("服务地址: http://127.0.0.1:8012/")
    print("使用固定的30个prompt")
    
    threading.Timer(1.0, open_browser).start()
    uvicorn.run(app, host="0.0.0.0", port=8012, reload=False)

if __name__ == "__main__":
    main() 