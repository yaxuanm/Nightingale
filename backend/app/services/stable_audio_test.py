import torch
import torchaudio
from einops import rearrange
from stable_audio_tools import get_pretrained_model
from stable_audio_tools.inference.generation import generate_diffusion_cond
import numpy as np
import soundfile as sf

# 1. 选择设备
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# 2. 下载并加载模型
print("Loading Stable Audio Open Small model...")
model, model_config = get_pretrained_model("stabilityai/stable-audio-open-small")
sample_rate = model_config["sample_rate"]
sample_size = model_config["sample_size"]
model = model.to(DEVICE)

# 3. 设置prompt和生成参数
PROMPT = "crackling fireplace"  # 你可以修改为任意SFX描述
DURATION = 2  # 生成音频时长（秒），减小输出体积

conditioning = [{
    "prompt": PROMPT,
    "seconds_total": DURATION
}]

print(f"Generating audio for prompt: '{PROMPT}' ({DURATION}s)...")
output = generate_diffusion_cond(
    model,
    steps=8,
    cfg_scale=1.0,
    conditioning=conditioning,
    sample_size=sample_size,
    sampler_type="pingpong",
    device=DEVICE,
    seed=int(np.random.randint(0, 2**31 - 1))
)
print("Inference finished!")
print("Raw output type:", type(output))
print("Raw output shape:", output.shape)
print("Raw output dtype:", output.dtype)
print("Done!") 