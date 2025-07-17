#!/usr/bin/env python3
"""
为固定测试数据生成音频文件
使用Stable Audio为30个固定prompt生成音频
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from fixed_test_data import get_fixed_prompts

def generate_audio_for_fixed_prompts():
    """为固定prompt生成音频"""
    
    # 创建输出目录
    output_dir = Path("audio_test_output/fixed_test")
    audio_dir = output_dir / "audio_files"
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取固定prompt
    prompts = get_fixed_prompts()
    
    # 保存prompt到文件
    prompt_file = output_dir / "fixed_prompts.json"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)
    
    print(f"开始为 {len(prompts)} 个固定prompt生成音频...")
    
    # 在Stable Audio虚拟环境下运行音频生成
    venv = "venv_stableaudio\\Scripts\\python.exe" if os.name == 'nt' else "venv_stableaudio/bin/python"
    script = "scripts/test_audio_generation.py"
    
    cmd = [
        venv, script,
        "--prompt", str(prompt_file),
        "--output", str(output_dir / "fixed_audio_results.json"),
        "--audio_dir", str(audio_dir),
        "--progress_file", str(output_dir / "fixed_progress.json")
    ]
    
    try:
        print("正在Stable Audio环境中生成音频...")
        subprocess.run(cmd, check=True)
        print("音频生成完成！")
        
        # 检查结果
        result_file = output_dir / "fixed_audio_results.json"
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

def create_test_web_data():
    """创建用于web测试的数据结构"""
    
    output_dir = Path("audio_test_output/fixed_test")
    result_file = output_dir / "fixed_audio_results.json"
    
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
                "description": result.get('description', ''),
                "category": result.get('category', ''),
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

def main():
    print("=== 固定音频生成工具 ===")
    print("1. 生成音频文件")
    print("2. 创建web测试数据")
    print("3. 完整流程（生成音频 + 创建web数据）")
    
    choice = input("请选择操作 (1/2/3): ").strip()
    
    if choice == "1":
        generate_audio_for_fixed_prompts()
    elif choice == "2":
        create_test_web_data()
    elif choice == "3":
        if generate_audio_for_fixed_prompts():
            create_test_web_data()
    else:
        print("无效选择")

if __name__ == "__main__":
    main() 