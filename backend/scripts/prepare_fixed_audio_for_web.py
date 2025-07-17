#!/usr/bin/env python3
"""
准备固定音频文件用于web评测
1. 使用已生成的prompt文件
2. 使用Stable Audio生成对应的音频文件
3. 准备web评测数据
"""

import os
import sys
import json
import time
import subprocess
import asyncio
from pathlib import Path
from fixed_prompts_generator import FixedPromptGenerator

def find_latest_prompt_file():
    """找到最新的prompt文件"""
    prompt_dir = Path("generated_prompts")
    if not prompt_dir.exists():
        return None
    
    # 查找所有fixed_prompts文件
    files = list(prompt_dir.glob("fixed_prompts_*.json"))
    if not files:
        return None
    
    # 返回最新的文件
    latest = max(files, key=lambda x: x.stat().st_mtime)
    return latest

def load_existing_prompts():
    """加载已存在的prompt文件"""
    prompt_file = find_latest_prompt_file()
    if not prompt_file:
        print("未找到已生成的prompt文件，需要重新生成...")
        return None
    
    print(f"使用已生成的prompt文件: {prompt_file}")
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompts = json.load(f)
    
    print(f"加载了 {len(prompts)} 个prompt")
    return prompts

async def generate_fixed_audio():
    """生成30个固定音频文件"""
    
    # 创建输出目录
    output_dir = Path("audio_test_output/fixed_web")
    audio_dir = output_dir / "audio_files"
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    # 尝试加载已存在的prompt文件
    prompts = load_existing_prompts()
    
    # 如果没有找到已存在的文件，则重新生成
    if prompts is None:
        print("使用Gemini API生成30个固定prompt...")
        generator = FixedPromptGenerator()
        prompts = await generator.generate_fixed_prompts()
    
    # 保存prompt文件到web目录
    prompt_file = output_dir / "fixed_prompts.json"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)
    
    print(f"已准备 {len(prompts)} 个固定prompt")
    
    # 使用Stable Audio生成音频
    print("开始生成音频文件...")
    venv = "venv_stableaudio\\Scripts\\python.exe" if os.name == 'nt' else "venv_stableaudio/bin/python"
    script = "scripts/test_audio_generation.py"
    
    result_file = output_dir / "fixed_results.json"
    progress_file = output_dir / "fixed_progress.json"
    
    cmd = [
        venv, script,
        "--prompt", str(prompt_file),
        "--output", str(result_file),
        "--audio_dir", str(audio_dir),
        "--progress_file", str(progress_file)
    ]
    
    try:
        print("正在Stable Audio环境中生成音频...")
        subprocess.run(cmd, check=True)
        print("音频生成完成！")
        
        # 检查结果
        if result_file.exists():
            with open(result_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            print(f"成功生成 {len(results)} 个音频文件")
            
            # 显示生成的音频文件
            for result in results:
                audio_file = result.get('local_file', '')
                if audio_file and Path(audio_file).exists():
                    print(f"✓ {result.get('id', 'unknown')}: {result.get('final_prompt', '')[:50]}...")
                else:
                    print(f"✗ {result.get('id', 'unknown')}: 音频文件未找到")
        else:
            print("警告：结果文件未生成")
            
    except subprocess.CalledProcessError as e:
        print(f"音频生成失败: {e}")
        return False
    except Exception as e:
        print(f"发生错误: {e}")
        return False
    
    return True

def create_web_test_data():
    """创建用于web测试的数据"""
    
    output_dir = Path("audio_test_output/fixed_web")
    result_file = output_dir / "fixed_results.json"
    
    if not result_file.exists():
        print("错误：音频结果文件不存在，请先运行音频生成")
        return False
    
    with open(result_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # 创建web测试数据
    web_data = []
    for result in results:
        audio_file = result.get('local_file', '')
        if audio_file and Path(audio_file).exists():
            # 获取相对路径用于web访问
            rel_path = Path(audio_file).relative_to(Path.cwd())
            web_data.append({
                "id": result.get('id', 'unknown'),
                "prompt": result.get('final_prompt', ''),
                "mode": result.get('mode', ''),
                "audio_url": f"/audio_files/{Path(audio_file).name}",
                "local_file": str(audio_file),
                "metrics": result.get('metrics', {})
            })
    
    # 保存web数据
    web_data_file = output_dir / "web_test_data.json"
    with open(web_data_file, 'w', encoding='utf-8') as f:
        json.dump(web_data, f, ensure_ascii=False, indent=2)
    
    print(f"已创建web测试数据，包含 {len(web_data)} 个音频文件")
    return True

async def main():
    print("=== 准备固定音频文件用于web评测 ===")
    print("1. 生成音频文件")
    print("2. 创建web测试数据")
    print("3. 完整流程（生成音频 + 创建web数据）")
    
    choice = input("请选择操作 (1/2/3): ").strip()
    
    if choice == "1":
        await generate_fixed_audio()
    elif choice == "2":
        create_web_test_data()
    elif choice == "3":
        if await generate_fixed_audio():
            create_web_test_data()
    else:
        print("无效选择")

if __name__ == "__main__":
    asyncio.run(main()) 