#!/usr/bin/env python3
"""
Web一键批量测试服务（FastAPI，子进程隔离）
- /         : 前端页面（带进度条和评测）
- /api/generate-batch-test : POST，触发子进程生成prompt和音频，返回task_id
- /api/generate-progress   : GET，查询进度和结果
- 自动打开浏览器
- 数据存 audio_test_output/web/
- 依赖隔离：Gemini和StableAudio分别在各自虚拟环境下运行
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

DATA_DIR = Path("audio_test_output/web")
AUDIO_DIR = DATA_DIR / "audio_files"
PROMPT_FILE = DATA_DIR / "web_prompts.json"
RESULT_FILE = DATA_DIR / "web_results.json"
PROGRESS_FILE = DATA_DIR / "web_progress.json"
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

# 子进程批量生成任务

def run_generate_prompts():
    """在Gemini虚拟环境下生成prompt"""
    venv = "venv_gemini\\Scripts\\python.exe" if os.name == 'nt' else "venv_gemini/bin/python"
    script = "scripts/generate_prompts.py"
    # 生成到指定文件
    cmd = [venv, script, "--output", str(PROMPT_FILE)]
    # 兼容老脚本：如果没有--output参数，则后续用文件移动
    try:
        subprocess.run(cmd, check=True)
    except Exception:
        # fallback: 直接运行脚本，后续查找最新文件
        subprocess.run([venv, script], check=True)
        # 查找最新prompt文件
        prompt_dir = Path("generated_prompts")
        files = list(prompt_dir.glob("generated_prompts_*.json"))
        if files:
            latest = max(files, key=lambda x: x.stat().st_mtime)
            with open(latest, 'r', encoding='utf-8') as f:
                data = json.load(f)
            with open(PROMPT_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)


def run_generate_audio():
    """在StableAudio虚拟环境下生成音频"""
    venv = "venv_stableaudio\\Scripts\\python.exe" if os.name == 'nt' else "venv_stableaudio/bin/python"
    script = "scripts/test_audio_generation.py"
    cmd = [venv, script, "--prompt", str(PROMPT_FILE), "--output", str(RESULT_FILE), "--audio_dir", str(AUDIO_DIR), "--progress_file", str(PROGRESS_FILE)]
    try:
        subprocess.run(cmd, check=True)
    except Exception:
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
    # 1. 生成prompt
    TASKS[task_id]["progress"] = 0.05
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_generate_prompts)
    TASKS[task_id]["progress"] = 0.3
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
                "final_prompt": r.get("final_prompt", "")
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
        resp["progress"] = 0.3 + 0.65 * (progress["current"] / max(progress["total"], 1))
        resp["current"] = progress["current"]
        resp["total"] = progress["total"]
        resp["prompts"] = progress["results"]
    return resp

def open_browser():
    url = "http://127.0.0.1:8000/"
    webbrowser.open(url)

def main():
    threading.Timer(1.0, open_browser).start()
    uvicorn.run(app, host="0.0.0.0", port=8010, reload=False)

if __name__ == "__main__":
    main() 