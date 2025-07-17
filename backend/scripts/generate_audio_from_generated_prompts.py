#!/usr/bin/env python3
"""
使用生成的prompt文件生成音频
从generated_prompts目录读取最新的prompt文件，生成音频并上传到前端
"""

import argparse
import os
import sys
import json
import time
import shutil
from pathlib import Path
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt_file', type=str, required=True, help='Prompt文件路径')
    parser.add_argument('--output_dir', type=str, required=True, help='输出目录')
    return parser.parse_args()

def load_prompts_from_file(prompt_file):
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompts = json.load(f)
    return prompts

def generate_audio_for_prompts(prompts, output_dir):
    output_dir = Path(output_dir)
    audio_dir = output_dir / "audio_files"
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    # 保存prompt到文件
    prompt_file = output_dir / "generated_prompts.json"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)
    print(f"开始为 {len(prompts)} 个prompt生成音频...")
    sys.path.append(str(Path("app")))
    from services.stable_audio_service import StableAudioService
    audio_service = StableAudioService()
    results = []
    for idx, prompt in enumerate(prompts, 1):
        print(f"\n[{idx}/{len(prompts)}] 生成音频: {prompt.get('id', f'test_{idx:03d}')}")
        try:
            result_path = audio_service.generate_audio(
                prompt=prompt.get('final_prompt', prompt.get('prompt', '')),
                duration=11.0
            )
            if result_path and os.path.exists(result_path):
                audio_filename = f"test_{idx:03d}.wav"
                audio_path = audio_dir / audio_filename
                shutil.copy2(result_path, audio_path)
                file_size = audio_path.stat().st_size
                metrics = {
                    'duration': 11.0,
                    'file_size': file_size,
                    'format': 'wav'
                }
                results.append({
                    'id': prompt.get('id', f'test_{idx:03d}'),
                    'final_prompt': prompt.get('final_prompt', ''),
                    'user_input': prompt.get('user_input', ''),
                    'mode': prompt.get('mode', ''),
                    'success': True,
                    'local_file': str(audio_path),
                    'metrics': metrics,
                    'generation_time': time.time()
                })
                print(f"✓ 完成: {audio_filename}")
            else:
                results.append({
                    'id': prompt.get('id', f'test_{idx:03d}'),
                    'final_prompt': prompt.get('final_prompt', ''),
                    'user_input': prompt.get('user_input', ''),
                    'mode': prompt.get('mode', ''),
                    'success': False,
                    'error': 'Audio generation failed',
                    'generation_time': time.time()
                })
                print(f"✗ 失败: {prompt.get('id', f'test_{idx:03d}')}")
        except Exception as e:
            results.append({
                'id': prompt.get('id', f'test_{idx:03d}'),
                'final_prompt': prompt.get('final_prompt', ''),
                'user_input': prompt.get('user_input', ''),
                'mode': prompt.get('mode', ''),
                'success': False,
                'error': str(e),
                'generation_time': time.time()
            })
            print(f"✗ 失败: {prompt.get('id', f'test_{idx:03d}')} - {e}")
    # 保存结果
    result_file = output_dir / "audio_results.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n音频生成完成！")
    print(f"成功生成: {len([r for r in results if r['success']])} 个")
    print(f"失败: {len([r for r in results if not r['success']])} 个")
    return output_dir

def create_web_data(output_dir):
    from pathlib import Path
    result_file = Path(output_dir) / "audio_results.json"
    if not result_file.exists():
        print("错误：音频结果文件不存在")
        return False
    with open(result_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    web_data = []
    for result in results:
        audio_file = result.get('local_file', '')
        if result.get('success') and audio_file and Path(audio_file).exists():
            web_data.append({
                "id": result.get('id', 'unknown'),
                "prompt": result.get('final_prompt', ''),
                "user_input": result.get('user_input', ''),
                "mode": result.get('mode', ''),
                "audio_url": f"/audio_files/{Path(audio_file).name}",
                "local_file": str(audio_file),
                "metrics": result.get('metrics', {}),
            })
    web_data_file = Path(output_dir) / "web_test_data.json"
    with open(web_data_file, 'w', encoding='utf-8') as f:
        json.dump(web_data, f, ensure_ascii=False, indent=2)
    print(f"已创建web测试数据，包含 {len(web_data)} 个音频文件")
    return web_data_file

def main():
    args = parse_args()
    prompts = load_prompts_from_file(args.prompt_file)
    output_dir = args.output_dir
    output_dir = generate_audio_for_prompts(prompts, output_dir)
    create_web_data(output_dir)
    print(f"\n全部完成！输出目录: {output_dir}")

if __name__ == "__main__":
    main() 