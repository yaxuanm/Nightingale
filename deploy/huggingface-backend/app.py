import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


APP_BASE_URL = os.getenv("APP_BASE_URL", "").rstrip("/")
OUTPUT_DIR = Path(os.getenv("AUDIO_OUTPUT_DIR", "/tmp/nightingale-audio"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HF_SPACE_URL = os.getenv("STABLE_AUDIO_HF_SPACE_URL", "https://stabilityai-stable-audio-3.hf.space").rstrip("/")
HF_SPACE_VARIANT = os.getenv("STABLE_AUDIO_HF_SPACE_VARIANT", "small-sfx")
STABLE_AUDIO_MODEL = os.getenv("STABLE_AUDIO_MODEL", "stabilityai/stable-audio-3-small-sfx")
MAX_DURATION = float(os.getenv("STABLE_AUDIO_MAX_DURATION", "11.0"))
DEFAULT_STEPS = int(os.getenv("STABLE_AUDIO_STEPS", "8"))
DEFAULT_CFG_SCALE = float(os.getenv("STABLE_AUDIO_CFG_SCALE", "1.0"))


app = FastAPI(title="Nightingale Backend", version="1.0.0")

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "https://yaxuanm.github.io,http://localhost:3000").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static/generated_audio", StaticFiles(directory=str(OUTPUT_DIR)), name="generated_audio")


def hf_headers() -> dict[str, str]:
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def public_base_url(request: Request) -> str:
    if APP_BASE_URL:
        return APP_BASE_URL
    return str(request.base_url).rstrip("/")


def optimize_prompt(prompt: str) -> str:
    prompt = " ".join((prompt or "").split())
    if not prompt:
        return "A calm, immersive ambient soundscape with gentle natural texture."
    return prompt[:600]


def submit_stable_audio(prompt: str, duration: float, steps: int, cfg_scale: float, sampler: str) -> str:
    payload = {
        "data": [
            HF_SPACE_VARIANT,
            optimize_prompt(prompt),
            min(float(duration), MAX_DURATION),
            int(steps),
            float(cfg_scale),
            sampler,
            0,
        ]
    }
    response = requests.post(
        f"{HF_SPACE_URL}/gradio_api/call/infer",
        json=payload,
        headers=hf_headers(),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["event_id"]


def wait_for_stable_audio_file(event_id: str) -> str:
    response = requests.get(
        f"{HF_SPACE_URL}/gradio_api/call/infer/{event_id}",
        headers=hf_headers(),
        stream=True,
        timeout=360,
    )
    response.raise_for_status()

    last_event = None
    for raw_line in response.iter_lines(decode_unicode=True):
        if not raw_line:
            continue
        if raw_line.startswith("event:"):
            last_event = raw_line.removeprefix("event:").strip()
            continue
        if not raw_line.startswith("data:"):
            continue

        payload = raw_line.removeprefix("data:").strip()
        if last_event == "complete":
            result = json.loads(payload)
            return result[0]["url"]
        if last_event == "error":
            raise RuntimeError(payload)

    raise RuntimeError(f"Stable Audio Space did not return audio for event {event_id}")


def generate_audio_file(prompt: str, duration: float, steps: int, cfg_scale: float, sampler: str) -> Path:
    event_id = submit_stable_audio(prompt, duration, steps, cfg_scale, sampler)
    file_url = wait_for_stable_audio_file(event_id)
    response = requests.get(file_url, headers=hf_headers(), timeout=120)
    response.raise_for_status()

    output_path = OUTPUT_DIR / f"stable_audio_{uuid.uuid4().hex[:10]}.wav"
    output_path.write_bytes(response.content)
    return output_path


@app.get("/")
async def root():
    return {
        "service": "nightingale-backend",
        "stable_audio_model": STABLE_AUDIO_MODEL,
        "stable_audio_provider": "official-huggingface-space-proxy",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nightingale-backend"}


@app.post("/api/generate-audio")
async def generate_audio(request: Request):
    started = time.time()
    try:
        data = await request.json()
        prompt = data.get("description") or data.get("userInput") or data.get("prompt") or ""
        duration = float(data.get("duration") or 8)
        output_path = generate_audio_file(prompt, duration, DEFAULT_STEPS, DEFAULT_CFG_SCALE, "pingpong")
        audio_url = f"{public_base_url(request)}/static/generated_audio/{output_path.name}"
        return {
            "audio_url": audio_url,
            "prompt": prompt,
            "service": "stable-audio-3-hf-space",
            "model": STABLE_AUDIO_MODEL,
            "duration": duration,
            "generation_time": round(time.time() - started, 2),
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/generate-stable-audio")
async def generate_stable_audio(request: Request):
    started = time.time()
    try:
        data = await request.json()
        prompt = data.get("prompt") or data.get("description") or ""
        duration = float(data.get("duration") or 8)
        output_path = generate_audio_file(prompt, duration, DEFAULT_STEPS, DEFAULT_CFG_SCALE, "pingpong")
        audio_url = f"{public_base_url(request)}/static/generated_audio/{output_path.name}"
        return {
            "audio_url": audio_url,
            "prompt": prompt,
            "service": "stable-audio-3-hf-space",
            "model": STABLE_AUDIO_MODEL,
            "duration": duration,
            "generation_time": round(time.time() - started, 2),
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/generate-prompt")
async def generate_prompt(request: Request):
    data = await request.json()
    user_input = data.get("user_input") or data.get("description") or "a personal soundscape"
    mood = data.get("mood") or "calm"
    elements = data.get("elements") or []
    element_text = ", ".join(elements[:4]) if isinstance(elements, list) else str(elements)
    prompt = f"{user_input}. Mood: {mood}. Key sound elements: {element_text}. Immersive ambient soundscape."
    return {"prompt": prompt}


@app.post("/api/generate-options")
async def generate_options(request: Request):
    data = await request.json()
    option_type = data.get("type", "")
    if option_type == "audio_mood":
        return {"options": ["Relaxed", "Focused", "Dreamy", "Uplifting", "Reflective"]}
    return {"options": ["Rain", "Wind", "Ocean waves", "Birds chirping", "Night crickets", "City hum"]}


@app.post("/api/generate-inspiration-chips")
async def generate_inspiration_chips():
    return {
        "chips": [
            "A rainy window for deep focus",
            "A summer evening from childhood",
            "A quiet library after midnight",
            "Ocean air for meditation",
        ]
    }


@app.post("/api/generate-background")
async def generate_background():
    return {"image_url": None}


@app.post("/api/generate-scene")
async def generate_scene(request: Request):
    data = await request.json()
    prompt = data.get("prompt") or data.get("description") or "A Nightingale soundscape"
    return {"scene": prompt, "prompt": prompt}


@app.post("/api/edit-prompt")
async def edit_prompt(request: Request):
    data = await request.json()
    return {"prompt": data.get("prompt") or data.get("text") or ""}
