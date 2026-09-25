import base64
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Optional

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from google import genai
from google.genai import types


APP_BASE_URL = os.getenv("APP_BASE_URL", "").rstrip("/")
OUTPUT_DIR = Path(os.getenv("AUDIO_OUTPUT_DIR", "/tmp/nightingale-audio"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HF_SPACE_URL = os.getenv("STABLE_AUDIO_HF_SPACE_URL", "https://stabilityai-stable-audio-3.hf.space").rstrip("/")
HF_SPACE_VARIANT = os.getenv("STABLE_AUDIO_HF_SPACE_VARIANT", "small-sfx")
STABLE_AUDIO_MODEL = os.getenv("STABLE_AUDIO_MODEL", "stabilityai/stable-audio-3-small-sfx")
MAX_DURATION = float(os.getenv("STABLE_AUDIO_MAX_DURATION", "11.0"))
DEFAULT_STEPS = int(os.getenv("STABLE_AUDIO_STEPS", "8"))
DEFAULT_CFG_SCALE = float(os.getenv("STABLE_AUDIO_CFG_SCALE", "1.0"))

# The Stability key belongs only in the backend's secret manager. It is never
# accepted from, stored in, or returned to the browser.
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_AUDIO_API_URL = os.getenv(
    "STABILITY_AUDIO_API_URL",
    "https://api.stability.ai/v2beta/audio/stable-audio-2/text-to-audio",
)
# Keep this separate from the legacy STABLE_AUDIO_MODEL setting used by the
# Hugging Face proxy fallback. Existing Spaces can retain that old setting
# without changing which model the direct Stability API uses.
STABILITY_API_MODEL = os.getenv("STABILITY_API_MODEL", "stable-audio-2.5")
STABILITY_AUDIO_MAX_DURATION = float(os.getenv("STABILITY_AUDIO_MAX_DURATION", "180"))
STABILITY_AUDIO_STEPS = int(os.getenv("STABILITY_AUDIO_STEPS", "8"))
STABILITY_AUDIO_CFG_SCALE = float(os.getenv("STABILITY_AUDIO_CFG_SCALE", "1.0"))

# This is an owner-configured backend secret for the Gemini-guided demo. It is
# intentionally never read from the browser and is never returned by an API.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")
GEMINI_INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"


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


def gemini_client() -> Optional[genai.Client]:
    if not GEMINI_API_KEY:
        return None
    return genai.Client(api_key=GEMINI_API_KEY)


def gemini_text(prompt: str) -> Optional[str]:
    client = gemini_client()
    if not client:
        return None
    try:
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return response.text.strip() if response.text else None
    except Exception:
        # The demo remains usable on a quota/provider error without exposing
        # provider details or owner credentials to visitors.
        return None


def gemini_json(prompt: str) -> Optional[Any]:
    client = gemini_client()
    if not client:
        return None
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        return json.loads(response.text) if response.text else None
    except Exception:
        return None


def gemini_background_image(description: str) -> Optional[bytes]:
    """Create a player background with the owner-managed Gemini key only."""
    if not GEMINI_API_KEY:
        return None
    prompt = (
        "Create a serene, cinematic 16:9 background image for an ambient-audio player. "
        "No people, text, logos, watermarks, interface elements, or borders. "
        f"Scene: {optimize_prompt(description)}"
    )
    try:
        response = requests.post(
            GEMINI_INTERACTIONS_URL,
            headers={
                "x-goog-api-key": GEMINI_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "model": GEMINI_IMAGE_MODEL,
                "input": prompt,
                "response_format": {
                    "type": "image",
                    "mime_type": "image/jpeg",
                    "aspect_ratio": "16:9",
                    "image_size": "1K",
                },
            },
            timeout=120,
        )
        if not response.ok:
            return None
        payload = response.json()
        image = payload.get("output_image") or payload.get("outputImage") or {}
        image_data = image.get("data") if isinstance(image, dict) else None
        if isinstance(image_data, str):
            return base64.b64decode(image_data)
        if isinstance(image_data, (bytes, bytearray)):
            return bytes(image_data)
    except Exception:
        # A missing image entitlement, quota issue, or model error should not
        # prevent the audio experience from using its local visual fallback.
        return None
    return None


class AudioProviderError(RuntimeError):
    """A safe, user-facing audio provider error without credentials or response bodies."""


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


def generate_audio_file_via_stability_api(
    api_key: str,
    prompt: str,
    duration: float,
) -> tuple[Path, float]:
    """Generate with the owner-managed Stability secret without exposing it."""
    requested_duration = min(max(float(duration), 1.0), STABILITY_AUDIO_MAX_DURATION)
    try:
        response = requests.post(
            STABILITY_AUDIO_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "audio/*",
            },
            # The official Stability example uses multipart form data for this endpoint.
            files={"image": None},
            data={
                "prompt": optimize_prompt(prompt),
                "duration": requested_duration,
                "seed": 0,
                "steps": STABILITY_AUDIO_STEPS,
                "cfg_scale": STABILITY_AUDIO_CFG_SCALE,
                "output_format": "wav",
                "model": STABILITY_API_MODEL,
            },
            timeout=120,
        )
    except requests.RequestException as exc:
        raise AudioProviderError("The Stability Audio API could not be reached. Please try again.") from exc

    if not response.ok:
        raise AudioProviderError(
            f"The Stability Audio API rejected this generation (HTTP {response.status_code}). "
            "Please try a shorter prompt or try again later."
        )
    if not response.content:
        raise AudioProviderError("The Stability Audio API returned an empty audio file. Please try again.")

    output_path = OUTPUT_DIR / f"stability_audio_{uuid.uuid4().hex[:10]}.wav"
    output_path.write_bytes(response.content)
    return output_path, requested_duration


@app.get("/")
async def root():
    return {
        "service": "nightingale-backend",
        "stable_audio_model": STABLE_AUDIO_MODEL,
        "stable_audio_provider": "stability-api" if STABILITY_API_KEY else "official-huggingface-space-proxy",
        "stable_audio_enabled": bool(STABILITY_API_KEY),
        "gemini_demo_enabled": bool(GEMINI_API_KEY),
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "nightingale-backend",
        "gemini_demo_enabled": bool(GEMINI_API_KEY),
        "stable_audio_enabled": bool(STABILITY_API_KEY),
    }


async def generate_audio_response(request: Request):
    started = time.time()
    try:
        data = await request.json()
        prompt = data.get("description") or data.get("userInput") or data.get("prompt") or ""
        duration = float(data.get("duration") or 8)
        if STABILITY_API_KEY:
            output_path, actual_duration = generate_audio_file_via_stability_api(STABILITY_API_KEY, prompt, duration)
            provider = "stability-api"
            model = STABILITY_API_MODEL
        else:
            output_path = generate_audio_file(prompt, duration, DEFAULT_STEPS, DEFAULT_CFG_SCALE, "pingpong")
            actual_duration = min(float(duration), MAX_DURATION)
            provider = "stable-audio-3-hf-space"
            model = STABLE_AUDIO_MODEL
        audio_url = f"{public_base_url(request)}/static/generated_audio/{output_path.name}"
        return {
            "audio_url": audio_url,
            "prompt": prompt,
            "service": provider,
            "model": model,
            "duration": actual_duration,
            "generation_time": round(time.time() - started, 2),
        }
    except AudioProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/generate-audio")
async def generate_audio(request: Request):
    return await generate_audio_response(request)


@app.post("/api/generate-stable-audio")
async def generate_stable_audio(request: Request):
    return await generate_audio_response(request)


@app.post("/api/generate-prompt")
async def generate_prompt(request: Request):
    data = await request.json()
    user_input = data.get("user_input") or data.get("description") or "a personal soundscape"
    mood = data.get("mood") or "calm"
    elements = data.get("elements") or []
    element_text = ", ".join(elements[:4]) if isinstance(elements, list) else str(elements)
    prompt = gemini_text(
        "Write one concise English Stable Audio prompt for this soundscape. "
        "Return only the prompt, with no title, markup, or explanation. "
        f"Scene: {user_input}\nMood: {mood}\nSound elements: {element_text}"
    ) or f"{user_input}. Mood: {mood}. Key sound elements: {element_text}. Immersive ambient soundscape."
    return {"prompt": prompt}


@app.post("/api/generate-options")
async def generate_options(request: Request):
    data = await request.json()
    stage = data.get("stage") or data.get("type", "")
    user_input = data.get("input") or data.get("user_input") or "a personal soundscape"
    if stage in {"mood", "audio_mood"}:
        fallback = ["Relaxed", "Focused", "Dreamy", "Uplifting", "Reflective"]
        goal = "moods"
    else:
        fallback = ["Rain", "Wind", "Ocean waves", "Birds chirping", "Night crickets", "City hum"]
        goal = "concrete sound elements"
    generated = gemini_json(
        f"Return exactly a JSON array of five short English {goal} for this soundscape. "
        f"No explanation. Scene: {user_input}"
    )
    options = generated if isinstance(generated, list) and all(isinstance(item, str) for item in generated) else fallback
    return {"options": options[:5]}


@app.post("/api/generate-inspiration-chips")
async def generate_inspiration_chips(request: Request):
    data = await request.json()
    mode = data.get("mode") or "ambient"
    user_input = data.get("user_input") or ""
    fallback = [
        "A rainy window for deep focus",
        "A summer evening from childhood",
        "A quiet library after midnight",
        "Ocean air for meditation",
    ]
    generated = gemini_json(
        "Return exactly a JSON array of four concise English soundscape ideas. "
        "They must be vivid, approachable, and suitable for Stable Audio. "
        f"Mode: {mode}\nOptional user context: {user_input}"
    )
    chips = generated if isinstance(generated, list) and all(isinstance(item, str) for item in generated) else fallback
    return {"chips": chips[:4]}


@app.post("/api/generate-background")
async def generate_background(request: Request):
    data = await request.json()
    description = data.get("description") or "a calm ambient soundscape"
    image_bytes = gemini_background_image(description)
    if not image_bytes:
        return {"image_url": None}
    output_path = OUTPUT_DIR / f"background_{uuid.uuid4().hex[:10]}.jpg"
    output_path.write_bytes(image_bytes)
    return {"image_url": f"{public_base_url(request)}/static/generated_audio/{output_path.name}"}


@app.post("/api/generate-scene")
async def generate_scene(request: Request):
    data = await request.json()
    prompt = data.get("prompt") or data.get("description") or "A Nightingale soundscape"
    if data.get("mode") == "story":
        narrative_script = gemini_text(
            "Write a short, immersive English narrative for a soundscape experience. "
            "Use three or four sentences with sensory detail; do not include headings or production notes. "
            f"Scene: {prompt}"
        ) or prompt
        return {"scene": prompt, "prompt": prompt, "narrative_script": narrative_script}
    return {"scene": prompt, "prompt": prompt}


@app.post("/api/edit-prompt")
async def edit_prompt(request: Request):
    data = await request.json()
    current_prompt = data.get("current_prompt") or data.get("prompt") or data.get("text") or ""
    edit_instruction = data.get("edit_instruction") or ""
    edited_prompt = gemini_text(
        "Revise the following English audio prompt according to the instruction. "
        "Return only the revised prompt, with no explanation.\n"
        f"Prompt: {current_prompt}\nInstruction: {edit_instruction}"
    ) or current_prompt
    return {"edited_prompt": edited_prompt}


@app.post("/api/music-prompt")
async def music_prompt(request: Request):
    data = await request.json()
    genre = data.get("genre") or "Ambient"
    instruments = data.get("instruments") or []
    tempo = data.get("tempo") or "Slow"
    usage = data.get("usage") or "relaxation"
    source = data.get("input") or "a calm, immersive scene"
    instrument_text = ", ".join(instruments[:4]) if isinstance(instruments, list) else str(instruments)
    prompt = gemini_text(
        "Write one concise English Stable Audio music prompt. Return only the prompt. "
        f"Genre: {genre}\nInstruments: {instrument_text}\nTempo: {tempo}\nUse: {usage}\nInspiration: {source}"
    ) or f"{genre} music for {usage}, {tempo} tempo, featuring {instrument_text or 'soft synthesizer textures'}, inspired by {source}."
    return {"prompt": prompt}
