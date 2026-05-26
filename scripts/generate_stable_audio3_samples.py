from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import requests
from dotenv import dotenv_values


SPACE_BASE_URL = "https://stabilityai-stable-audio-3.hf.space"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "ambiance-weaver-react" / "public" / "demo-audio"
BACKEND_ENV = Path(__file__).resolve().parents[1] / "backend" / ".env"
MODEL_VARIANT = "small-sfx"
MODEL_ID = "stabilityai/stable-audio-3-small-sfx"


SAMPLES = [
    {
        "slug": "warm-summer-evening",
        "title": "Warm Summer Evening",
        "duration": 8,
        "seed": 1742,
        "prompt": (
            "Warm summer evening ambience with cicadas, distant birds, soft wind "
            "through trees, nostalgic and calm."
        ),
    },
    {
        "slug": "rain-window-focus",
        "title": "Rain Window Focus",
        "duration": 8,
        "seed": 2518,
        "prompt": (
            "Steady rain tapping on a window, soft room tone, muted city distance, "
            "focused and peaceful."
        ),
    },
    {
        "slug": "ocean-breath-meditation",
        "title": "Ocean Breath Meditation",
        "duration": 8,
        "seed": 3107,
        "prompt": (
            "Slow ocean waves rolling onto sand, airy coastal wind, spacious and "
            "meditative atmosphere."
        ),
    },
    {
        "slug": "midnight-library",
        "title": "Midnight Library",
        "duration": 8,
        "seed": 4309,
        "prompt": (
            "Quiet midnight library ambience, soft page turns, faint wooden room "
            "tone, intimate and reflective."
        ),
    },
]


def auth_headers() -> dict[str, str]:
    token = os.environ.get("HF_TOKEN") or dotenv_values(BACKEND_ENV).get("HF_TOKEN")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def submit_generation(sample: dict[str, Any]) -> str:
    payload = {
        "data": [
            MODEL_VARIANT,
            sample["prompt"],
            sample["duration"],
            8,
            1.0,
            "pingpong",
            sample["seed"],
        ]
    }
    response = requests.post(
        f"{SPACE_BASE_URL}/gradio_api/call/infer",
        json=payload,
        headers=auth_headers(),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["event_id"]


def wait_for_file(event_id: str) -> str:
    response = requests.get(
        f"{SPACE_BASE_URL}/gradio_api/call/infer/{event_id}",
        headers=auth_headers(),
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
        if raw_line.startswith("data:"):
            payload = raw_line.removeprefix("data:").strip()
            if last_event == "complete":
                result = json.loads(payload)
                return result[0]["url"]
            if last_event == "error":
                raise RuntimeError(payload)

    raise RuntimeError(f"No file returned for event {event_id}")


def download_file(url: str, path: Path) -> None:
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    path.write_bytes(response.content)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []

    for sample in SAMPLES:
        output_path = OUTPUT_DIR / f"{sample['slug']}.wav"
        if output_path.exists():
            print(f"Skipping existing {output_path}")
        else:
            print(f"Generating {sample['title']}...")
            event_id = submit_generation(sample)
            file_url = wait_for_file(event_id)
            download_file(file_url, output_path)
            print(f"Wrote {output_path}")

        manifest.append(
            {
                **sample,
                "model": MODEL_ID,
                "source": "Stability AI official Stable Audio 3 Hugging Face Space",
                "file": f"/demo-audio/{sample['slug']}.wav",
            }
        )
        time.sleep(2)

    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_DIR / 'manifest.json'}")


if __name__ == "__main__":
    main()
