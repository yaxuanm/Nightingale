#!/usr/bin/env python3
"""
简化的音频生成脚本
使用生成的prompt文件生成音频，避免异步问题
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

def find_latest_prompt_file():
    """找到最新的prompt文件"""
    prompt_dir = Path("generated_prompts")
    if not prompt_dir.exists():
        print("错误：generated_prompts目录不存在")
        return None
    
    # 查找所有fixed_prompts文件
    prompt_files = list(prompt_dir.glob("fixed_prompts_*.json"))
    if not prompt_files:
        print("错误：未找到fixed_prompts文件")
        return None
    
    # 按修改时间排序，返回最新的
    latest_file = max(prompt_files, key=lambda x: x.stat().st_mtime)
    print(f"使用prompt文件: {latest_file}")
    return latest_file

def load_prompts_from_file(prompt_file):
    """从文件加载prompt数据"""
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompts = json.load(f)
    
    # 转换为音频生成脚本需要的格式
    formatted_prompts = []
    for prompt in prompts:
        formatted_prompts.append({
            "id": prompt.get("id", "unknown"),
            "prompt": prompt.get("final_prompt", ""),
            "category": prompt.get("mode", "relax"),
            "description": prompt.get("user_input", ""),
            "mode": prompt.get("mode", "relax"),
            "atmosphere": prompt.get("atmosphere", ""),
            "elements": prompt.get("elements", [])
        })
    
    return formatted_prompts

def generate_single_audio(prompt_data, output_dir, audio_dir):
    """生成单个音频文件"""
    
    # 导入Stable Audio服务
    sys.path.append(str(Path("app")))
    from services.stable_audio_service import StableAudioService
    
    # 初始化服务
    audio_service = StableAudioService()
    
    try:
        print(f"正在生成音频: {prompt_data['id']} - {prompt_data['prompt'][:50]}...")
        
        # 生成音频
        result = audio_service.generate_audio(
            prompt=prompt_data['prompt'],
            duration=11.0  # 最大11秒
        )
        
        if result:
            # 复制生成的音频文件到目标目录
            audio_filename = f"{prompt_data['id']}.wav"
            audio_path = audio_dir / audio_filename
            
            # 复制文件
            import shutil
            shutil.copy2(result, audio_path)
            
            # 分析音频
            file_size = audio_path.stat().st_size
            metrics = {
                'duration': 11.0,
                'file_size': file_size,
                'format': 'wav'
            }
            
            return {
                'id': prompt_data['id'],
                'prompt': prompt_data['prompt'],
                'description': prompt_data['description'],
                'category': prompt_data['category'],
                'mode': prompt_data['mode'],
                'success': True,
                'local_file': str(audio_path),
                'metrics': metrics,
                'generation_time': time.time()
            }
        else:
            return {
                'id': prompt_data['id'],
                'prompt': prompt_data['prompt'],
                'description': prompt_data['description'],
                'category': prompt_data['category'],
                'mode': prompt_data['mode'],
                'success': False,
                'error': 'Audio generation failed',
                'generation_time': time.time()
            }
            
    except Exception as e:
        print(f"生成音频时出错: {e}")
        return {
            'id': prompt_data['id'],
            'prompt': prompt_data['prompt'],
            'description': prompt_data['description'],
            'category': prompt_data['category'],
            'mode': prompt_data['mode'],
            'success': False,
            'error': str(e),
            'generation_time': time.time()
        }

def generate_audio_for_prompts(prompts):
    """为prompt生成音频"""
    
    # 创建输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"audio_test_output/generated_{timestamp}")
    audio_dir = output_dir / "audio_files"
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存prompt到文件
    prompt_file = output_dir / "generated_prompts.json"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)
    
    print(f"开始为 {len(prompts)} 个prompt生成音频...")
    
    results = []
    
    # 逐个生成音频
    for i, prompt in enumerate(prompts, 1):
        print(f"\n[{i}/{len(prompts)}] 生成音频: {prompt['id']}")
        
        result = generate_single_audio(prompt, output_dir, audio_dir)
        results.append(result)
        
        # 更新进度
        progress = {
            'current': i,
            'total': len(prompts),
            'percentage': (i / len(prompts)) * 100,
            'current_id': prompt['id']
        }
        
        progress_file = output_dir / "progress.json"
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 完成: {prompt['id']}")
    
    # 保存结果
    result_file = output_dir / "audio_results.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n音频生成完成！")
    print(f"成功生成: {len([r for r in results if r['success']])} 个")
    print(f"失败: {len([r for r in results if not r['success']])} 个")
    
    return output_dir

def create_web_data(output_dir):
    """创建用于web测试的数据结构"""
    
    result_file = output_dir / "audio_results.json"
    
    if not result_file.exists():
        print("错误：音频结果文件不存在")
        return False
    
    with open(result_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # 创建web测试数据
    web_data = []
    for result in results:
        if result.get('success') and result.get('local_file'):
            audio_file = result['local_file']
            if Path(audio_file).exists():
                web_data.append({
                    "id": result.get('id', 'unknown'),
                    "prompt": result.get('prompt', ''),
                    "description": result.get('description', ''),
                    "category": result.get('category', ''),
                    "audio_url": f"/audio_files/{Path(audio_file).name}",
                    "local_file": str(audio_file),
                    "metrics": result.get('metrics', {}),
                    "mode": result.get('mode', 'relax'),
                    "atmosphere": result.get('atmosphere', ''),
                    "elements": result.get('elements', [])
                })
    
    # 保存web数据
    web_data_file = output_dir / "web_test_data.json"
    with open(web_data_file, 'w', encoding='utf-8') as f:
        json.dump(web_data, f, ensure_ascii=False, indent=2)
    
    print(f"已创建web测试数据，包含 {len(web_data)} 个音频文件")
    return web_data_file

def main():
    print("=== 简化的音频生成工具 ===")
    
    # 1. 找到最新的prompt文件
    prompt_file = find_latest_prompt_file()
    if not prompt_file:
        return
    
    # 2. 加载prompt数据
    prompts = load_prompts_from_file(prompt_file)
    print(f"加载了 {len(prompts)} 个prompt")
    
    # 3. 生成音频
    output_dir = generate_audio_for_prompts(prompts)
    if not output_dir:
        return
    
    # 4. 创建web数据
    web_data_file = create_web_data(output_dir)
    if not web_data_file:
        return
    
    print(f"\n音频生成完成！")
    print(f"输出目录: {output_dir}")
    print(f"Web数据文件: {web_data_file}")
    print(f"音频文件目录: {output_dir / 'audio_files'}")
    
    print("\n要启动web服务，请运行:")
    print(f"venv_api\\Scripts\\python.exe scripts/fixed_test_web.py --data_file {web_data_file} --audio_dir {output_dir / 'audio_files'} --port 8010")

if __name__ == "__main__":
    main() 