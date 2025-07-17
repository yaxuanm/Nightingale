import os
import requests
from pydub import AudioSegment, effects
from typing import List
import tempfile
from .ai_service import AIService
import asyncio
import noisereduce as nr
import numpy as np
import librosa

FREESOUND_API_KEY = os.getenv("FREESOUND_API_KEY", "your_freesound_api_key_here")
FREESOUND_SEARCH_URL = "https://freesound.org/apiv2/search/text/"

# 1. 用 Gemini 提取声音关键词（复用 ai_service）
async def extract_keywords(prompt: str, topk: int = 3) -> List[str]:
    print(f"[DEBUG] extract_keywords called with prompt: {prompt}")
    try:
        ai_service = AIService()
        print("[DEBUG] AIService instantiated.")
        elements = await ai_service.parse_scene(prompt)
        print(f"[DEBUG] parse_scene returned: {elements}")
        keywords = [e["name"] for e in elements if "name" in e][:topk]
        print(f"[KEYWORDS] Extracted: {keywords}")
        return keywords
    except Exception as e:
        print(f"[ERROR] extract_keywords failed: {e}")
        raise

# 2. 用 Freesound API 检索并下载音频

def search_and_download(keyword: str, out_dir: str) -> str:
    print(f"[DEBUG] search_and_download called with keyword: {keyword}")
    try:
        params = {
            "query": keyword,
            "fields": "id,name,previews,duration,license",
            "token": FREESOUND_API_KEY,
            "page_size": 1,
            "filter": "duration:[3 TO 60]",  # 只要3-60秒的音频
            "sort": "score"
        }
        resp = requests.get(FREESOUND_SEARCH_URL, params=params)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        print(f"[DEBUG] Freesound search results: {results}")
        if not results:
            raise Exception(f"No Freesound result for: {keyword}")
        preview_url = results[0]["previews"]["preview-hq-mp3"]
        audio_name = f"{keyword.replace(' ', '_')}.mp3"
        audio_path = os.path.join(out_dir, audio_name)
        audio_data = requests.get(preview_url)
        with open(audio_path, "wb") as f:
            f.write(audio_data.content)
        print(f"[FREESOUND] Downloaded: {audio_path}")
        return audio_path
    except Exception as e:
        print(f"[ERROR] search_and_download failed for '{keyword}': {e}")
        raise

# 3. 拼接音频

def reduce_noise(audio: AudioSegment, prop_decrease=0.5) -> AudioSegment:
    y = np.array(audio.get_array_of_samples()).astype(np.float32)
    sr = audio.frame_rate
    # librosa 只支持单声道，若多声道需转换
    if audio.channels > 1:
        y = y.reshape((-1, audio.channels))
        y = y.mean(axis=1)
    reduced = nr.reduce_noise(y=y, sr=sr, prop_decrease=prop_decrease)
    reduced = np.clip(reduced, -32768, 32767).astype(np.int16)
    return AudioSegment(
        reduced.tobytes(),
        frame_rate=sr,
        sample_width=2,
        channels=1
    )

def extract_middle(audio, segment_ms=8000, skip_start_ms=2000):
    try:
        audio = effects.strip_silence(audio, silence_len=500, silence_thresh=-40)
    except Exception as e:
        print(f"[WARN] strip_silence failed: {e}")
    # 跳过开头2秒
    if len(audio) > skip_start_ms:
        audio = audio[skip_start_ms:]
    # 降噪
    try:
        audio = reduce_noise(audio, prop_decrease=0.5)
    except Exception as e:
        print(f"[WARN] reduce_noise failed: {e}")
    # 取中间 segment_ms 毫秒
    if len(audio) > segment_ms:
        start = (len(audio) - segment_ms) // 2
        return audio[start:start+segment_ms]
    return audio

def concat_audios(audio_paths: List[str], out_path: str) -> str:
    print(f"[DEBUG] concat_audios (错峰混音+降噪) called with: {audio_paths}")
    try:
        segment_ms = 8000
        mix_segments = []
        for path in audio_paths:
            seg = AudioSegment.from_file(path)
            seg = extract_middle(seg, segment_ms)
            mix_segments.append(seg)
        base = AudioSegment.silent(duration=20000)  # 20秒静音底
        positions = [0, 6000, 12000]  # 错峰叠加
        for seg, pos in zip(mix_segments, positions):
            base = base.overlay(seg, position=pos)
        base = base.fade_in(1000).fade_out(1000)
        base = base[:20000]  # 截取前20秒
        base.export(out_path, format="mp3")
        print(f"[AUDIO] Mixed audio saved: {out_path}")
        return out_path
    except Exception as e:
        print(f"[ERROR] concat_audios (错峰混音+降噪) failed: {e}")
        raise

# 4. main 测试入口

async def generate_freesound_mix(prompt: str) -> str:
    keywords = await extract_keywords(prompt)
    audio_paths = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for kw in keywords:
            try:
                path = search_and_download(kw, tmpdir)
                audio_paths.append(path)
            except Exception as e:
                print(f"[WARN] Failed to get audio for '{kw}': {e}")
        if not audio_paths:
            print("[ERROR] No audio files downloaded.")
            return None
        # 输出到 backend/audio_output/（修正为 ../../audio_output）
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../audio_output"))
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, f"freesound_{abs(hash(prompt))}.mp3")
        try:
            concat_audios(audio_paths, out_path)
        except Exception as e:
            print(f"[ERROR] Failed to concatenate audios: {e}")
            return None
        print(f"[DONE] Output: {out_path}")
        # 返回静态文件URL
        return f"/static/generated_audio/{os.path.basename(out_path)}"

async def generate_freesound_mix_with_duration(prompt: str, target_duration_seconds: float) -> str:
    """
    生成指定时长的 soundscape，与 TTS 旁白长度匹配
    """
    print(f"[STORY] Generating soundscape with target duration: {target_duration_seconds:.2f} seconds")
    keywords = await extract_keywords(prompt)
    audio_paths = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for kw in keywords:
            try:
                path = search_and_download(kw, tmpdir)
                audio_paths.append(path)
            except Exception as e:
                print(f"[WARN] Failed to get audio for '{kw}': {e}")
        if not audio_paths:
            print("[ERROR] No audio files downloaded.")
            return None
        
        # 输出到 backend/audio_output/
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../audio_output"))
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, f"freesound_story_{abs(hash(prompt))}.mp3")
        
        try:
            # 使用新的动态长度拼接函数
            concat_audios_with_duration(audio_paths, out_path, target_duration_seconds)
        except Exception as e:
            print(f"[ERROR] Failed to concatenate audios: {e}")
            return None
        print(f"[STORY] Output: {out_path}")
        # 返回静态文件URL
        return f"/static/generated_audio/{os.path.basename(out_path)}"

def concat_audios_with_duration(audio_paths: List[str], out_path: str, target_duration_seconds: float) -> str:
    """
    拼接音频到指定时长，用于 Story Mode
    """
    print(f"[STORY] concat_audios_with_duration called with target duration: {target_duration_seconds:.2f}s")
    try:
        target_duration_ms = int(target_duration_seconds * 1000)
        segment_ms = min(8000, target_duration_ms // 3)  # 动态调整片段长度
        
        mix_segments = []
        for path in audio_paths:
            seg = AudioSegment.from_file(path)
            seg = extract_middle(seg, segment_ms)
            mix_segments.append(seg)
        
        # 创建目标时长的静音底
        base = AudioSegment.silent(duration=target_duration_ms)
        
        # 错峰叠加音频片段
        positions = []
        for i in range(len(mix_segments)):
            pos = i * (target_duration_ms // len(mix_segments))
            positions.append(pos)
        
        for seg, pos in zip(mix_segments, positions):
            if pos + len(seg) <= target_duration_ms:
                base = base.overlay(seg, position=pos)
        
        # 添加淡入淡出效果
        base = base.fade_in(1000).fade_out(1000)
        
        # 确保最终长度正确
        base = base[:target_duration_ms]
        
        base.export(out_path, format="mp3")
        print(f"[STORY] Mixed audio saved: {out_path} (duration: {len(base)/1000:.2f}s)")
        return out_path
    except Exception as e:
        print(f"[ERROR] concat_audios_with_duration failed: {e}")
        raise

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python freesound_concat_demo.py '<your prompt>'")
        exit(1)
    prompt = sys.argv[1]
    asyncio.run(generate_freesound_mix(prompt)) 