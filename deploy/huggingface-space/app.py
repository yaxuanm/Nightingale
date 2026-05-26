import os
import tempfile
import time
from functools import lru_cache

import gradio as gr
import torch
import torchaudio
from einops import rearrange
from stable_audio_tools import get_pretrained_model
from stable_audio_tools.inference.generation import generate_diffusion_cond_inpaint

try:
    import spaces
except Exception:
    class _SpacesFallback:
        def GPU(self, *args, **kwargs):
            def decorator(fn):
                return fn
            return decorator

    spaces = _SpacesFallback()


MODEL_ID = os.getenv("STABLE_AUDIO_MODEL", "stabilityai/stable-audio-3-small-sfx")
MAX_DURATION = float(os.getenv("STABLE_AUDIO_MAX_DURATION", "11.0"))
DEFAULT_STEPS = int(os.getenv("STABLE_AUDIO_STEPS", "8"))
DEFAULT_CFG = float(os.getenv("STABLE_AUDIO_CFG_SCALE", "1.0"))


def _device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


@lru_cache(maxsize=1)
def load_model():
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    if token:
        os.environ["HF_TOKEN"] = token
        os.environ["HUGGING_FACE_HUB_TOKEN"] = token

    model, model_config = get_pretrained_model(MODEL_ID)
    device = _device()
    if device == "cuda":
        model = model.to(torch.float16)
    else:
        try:
            model.pretransform.model_half = False
        except Exception:
            pass
        model = model.to(torch.float32)

    model = model.to(device)
    return model, model_config


def _normalize_prompt(prompt: str) -> str:
    prompt = (prompt or "").strip()
    if not prompt:
        raise gr.Error("Please enter a soundscape description.")
    return prompt[:600]


@spaces.GPU(duration=120)
def generate_soundscape(prompt: str, duration: float, steps: int, cfg_scale: float):
    start = time.time()
    prompt = _normalize_prompt(prompt)
    duration = min(float(duration), MAX_DURATION)

    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(42)

    model, model_config = load_model()
    sample_rate = int(model_config["sample_rate"])
    sample_size = int(model_config["sample_size"])
    device = _device()

    conditioning = [{
        "prompt": prompt,
        "seconds_total": duration,
    }]

    output = generate_diffusion_cond_inpaint(
        model,
        steps=int(steps),
        cfg_scale=float(cfg_scale),
        conditioning=conditioning,
        sample_size=sample_size,
        sampler_type="pingpong",
        device=device,
    )

    output = rearrange(output, "b d n -> d (b n)")
    peak = torch.max(torch.abs(output))
    if peak > 0:
        output = output / peak
    output = output.clamp(-1, 1).mul(32767).to(torch.int16).cpu()

    handle = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    handle.close()
    torchaudio.save(handle.name, output, sample_rate)

    elapsed = time.time() - start
    return handle.name, f"Generated in {elapsed:.1f}s with {MODEL_ID}"


with gr.Blocks(title="Nightingale Stable Audio 3 Demo") as demo:
    gr.Markdown("# Nightingale Stable Audio 3 Demo")
    gr.Markdown("Generate short ambience and soundscape clips with Stable Audio 3 Small SFX.")

    with gr.Row():
        prompt = gr.Textbox(
            label="Soundscape prompt",
            value="Warm summer evening ambience with cicadas, distant birds, soft wind through trees, nostalgic and calm.",
            lines=4,
        )

    with gr.Row():
        duration = gr.Slider(3, MAX_DURATION, value=min(8, MAX_DURATION), step=1, label="Duration")
        steps = gr.Slider(4, 16, value=DEFAULT_STEPS, step=1, label="Steps")
        cfg_scale = gr.Slider(0.5, 3.0, value=DEFAULT_CFG, step=0.1, label="CFG scale")

    generate = gr.Button("Generate", variant="primary")
    audio = gr.Audio(label="Generated audio", type="filepath")
    status = gr.Textbox(label="Status", interactive=False)

    generate.click(
        fn=generate_soundscape,
        inputs=[prompt, duration, steps, cfg_scale],
        outputs=[audio, status],
        api_name="generate",
    )


if __name__ == "__main__":
    demo.queue(max_size=8).launch()
