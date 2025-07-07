import argparse
import os
import sys
from audiocraft.models import AudioGen, MusicGen
from audiocraft.data.audio import audio_write

# 设置环境变量以确保进度条显示
os.environ['TQDM_DISABLE'] = '0'
os.environ['TQDM_MININTERVAL'] = '0.1'

def generate_audio(description, duration, output_path, model_type="audiogen"):
    print(f"[MODEL] Starting to load {model_type.upper()} model...")
    
    if model_type == "audiogen":
        print("[DOWNLOAD] Downloading AudioGen model (facebook/audiogen-medium)...")
        model = AudioGen.get_pretrained('facebook/audiogen-medium')
        print("[SUCCESS] AudioGen model loaded successfully!")
    else:
        print("[DOWNLOAD] Downloading MusicGen model (facebook/musicgen-small)...")
        model = MusicGen.get_pretrained('facebook/musicgen-small')
        print("[SUCCESS] MusicGen model loaded successfully!")
    
    print(f"[CONFIG] Setting generation parameters: duration {duration} seconds")
    model.set_generation_params(duration=duration)
    
    print(f"[GENERATE] Starting audio generation...")
    print(f"[PROMPT] Description: {description}")
    print(f"[TIME] Expected generation time: {duration} seconds")
    print("[PROGRESS] Model generation in progress (this may take a while)...")
    
    # 强制刷新输出缓冲区
    sys.stdout.flush()
    
    wav = model.generate([description], progress=True)
    
    print(f"[SAVE] Saving audio file to: {output_path}")
    audio_write(
        output_path.replace('.wav', ''),
        wav[0].cpu(),
        model.sample_rate,
        strategy="loudness",
        loudness_compressor=True
    )
    print(f"[SUCCESS] Audio file saved successfully: {output_path}")
    print(f"[INFO] Audio info: Sample rate {model.sample_rate}Hz, Duration {duration} seconds")

if __name__ == "__main__":
    # 确保输出不被缓冲
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    
    parser = argparse.ArgumentParser(description="Generate audio using AudioCraft.")
    parser.add_argument('--desc', type=str, required=True, help='Text description for audio generation')
    parser.add_argument('--duration', type=int, default=10, help='Duration in seconds')
    parser.add_argument('--out', type=str, required=True, help='Output wav file path')
    parser.add_argument('--model', type=str, choices=['audiogen', 'musicgen'], default='audiogen', help='Model type')
    args = parser.parse_args()
    
    print("[START] AudioCraft Worker starting")
    print(f"[MODEL] Model type: {args.model}")
    print(f"[TIME] Generation duration: {args.duration} seconds")
    print(f"[FILE] Output file: {args.out}")
    
    generate_audio(args.desc, args.duration, args.out, args.model)
    
    print("[COMPLETE] AudioCraft Worker completed!") 