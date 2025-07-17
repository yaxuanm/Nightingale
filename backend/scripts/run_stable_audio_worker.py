import argparse
import os
import sys

# 将 backend 目录加入 sys.path，便于绝对导入 app.services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.services.stable_audio_service import stable_audio_service

# 兼容 Windows 控制台中文输出，Python 3.7+ 支持 reconfigure
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
try:
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

def main():
    parser = argparse.ArgumentParser(description="Stable Audio Worker")
    parser.add_argument("--prompt", type=str, required=True, help="Prompt for soundscape generation")
    parser.add_argument("--duration", type=float, default=11.0, help="Duration in seconds (max 11)")
    parser.add_argument("--out", type=str, required=True, help="Output wav file path")
    args = parser.parse_args()

    # 生成音频
    audio_path = stable_audio_service.generate_audio(args.prompt, duration=args.duration)
    # 移动/重命名到指定输出
    if audio_path != args.out:
        os.replace(audio_path, args.out)
    print(f"[STABLE_AUDIO_WORKER] Done: {args.out}")

if __name__ == "__main__":
    main() 