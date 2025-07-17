#!/usr/bin/env python3
"""
固定Prompt生成器 - 使用Gemini API生成30个固定prompt
基于原有的Gemini逻辑，但生成固定的30个prompt而不是随机生成
"""

import os
import sys
import time
import json
import random
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ai_service import AIService

# 固定的30个测试用例
FIXED_TEST_CASES = [
    {"id": "test_001", "mode": "relax"},
    {"id": "test_002", "mode": "relax"},
    {"id": "test_003", "mode": "focus"},
    {"id": "test_004", "mode": "focus"},
    {"id": "test_005", "mode": "relax"},
    {"id": "test_006", "mode": "relax"},
    {"id": "test_007", "mode": "focus"},
    {"id": "test_008", "mode": "story"},
    {"id": "test_009", "mode": "relax"},
    {"id": "test_010", "mode": "story"},
    {"id": "test_011", "mode": "relax"},
    {"id": "test_012", "mode": "relax"},
    {"id": "test_013", "mode": "relax"},
    {"id": "test_014", "mode": "story"},
    {"id": "test_015", "mode": "relax"},
    {"id": "test_016", "mode": "relax"},
    {"id": "test_017", "mode": "story"},
    {"id": "test_018", "mode": "story"},
    {"id": "test_019", "mode": "focus"},
    {"id": "test_020", "mode": "relax"},
    {"id": "test_021", "mode": "story"},
    {"id": "test_022", "mode": "relax"},
    {"id": "test_023", "mode": "story"},
    {"id": "test_024", "mode": "focus"},
    {"id": "test_025", "mode": "relax"},
    {"id": "test_026", "mode": "story"},
    {"id": "test_027", "mode": "relax"},
    {"id": "test_028", "mode": "relax"},
    {"id": "test_029", "mode": "focus"},
    {"id": "test_030", "mode": "relax"}
]

class FixedPromptGenerator:
    """固定Prompt生成器 - 使用Gemini API"""
    
    def __init__(self):
        self.output_dir = Path("generated_prompts")
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化AI服务
        self.ai_service = AIService()
        
    async def generate_single_prompt(self, mode: str) -> Dict[str, Any]:
        """生成单个prompt - 使用原有的Gemini逻辑"""
        print(f"🤖 生成prompt (模式: {mode})...")
        
        try:
            # 1. 生成inspiration chips
            print("  📝 生成inspiration chips...")
            inspiration_chips = await self.ai_service.generate_inspiration_chips(mode, "")
            selected_chip = random.choice(inspiration_chips) if inspiration_chips else "cozy cafe"
            print(f"    选中chip: {selected_chip}")
            
            # 2. 生成atmosphere选项
            print("  🌍 生成atmosphere选项...")
            atmosphere_options = await self.ai_service.generate_options(mode, selected_chip, "audio_atmosphere")
            selected_atmosphere = random.choice(atmosphere_options) if atmosphere_options else f"{selected_chip} environment"
            print(f"    选中atmosphere: {selected_atmosphere}")
            
            # 3. 生成elements选项
            print("  🔊 生成elements选项...")
            element_options = await self.ai_service.generate_options(mode, selected_chip, "audio_elements")
            # 随机选择1-3个elements
            num_elements = random.randint(1, min(3, len(element_options) if element_options else 1))
            selected_elements = random.sample(element_options, num_elements) if element_options and len(element_options) >= num_elements else ["ambient sound"]
            print(f"    选中elements: {selected_elements}")
            
            # 4. 拼接成final prompt
            elements_str = ", ".join(selected_elements)
            final_prompt = f"{selected_atmosphere} with {elements_str}"
            print(f"  🎯 最终prompt: {final_prompt}")
            
            return {
                "user_input": selected_chip,
                "inspiration_chip": selected_chip,
                "atmosphere": selected_atmosphere,
                "elements": selected_elements,
                "final_prompt": final_prompt,
                "mode": mode
            }
            
        except Exception as e:
            print(f"  ❌ 生成失败: {str(e)}")
            # 使用fallback
            fallback_chip = "cozy cafe"
            return {
                "user_input": fallback_chip,
                "inspiration_chip": fallback_chip,
                "atmosphere": f"{fallback_chip} environment",
                "elements": ["ambient sound"],
                "final_prompt": f"{fallback_chip} with ambient sound",
                "mode": mode
            }
    
    async def generate_fixed_prompts(self) -> List[Dict[str, Any]]:
        """生成固定的30个prompt - 使用Gemini API"""
        print(f"🚀 开始生成固定prompt - 共 {len(FIXED_TEST_CASES)} 个测试用例")
        print("模式包括: focus, relax, story")
        
        results = []
        for i, test_case in enumerate(FIXED_TEST_CASES, 1):
            print(f"\n[{i}/{len(FIXED_TEST_CASES)}] 生成prompt")
            prompt_data = await self.generate_single_prompt(test_case['mode'])
            
            result = {
                "id": test_case['id'],
                "mode": test_case['mode'],
                "user_input": prompt_data['user_input'],
                "inspiration_chip": prompt_data['inspiration_chip'],
                "atmosphere": prompt_data['atmosphere'],
                "elements": prompt_data['elements'],
                "final_prompt": prompt_data['final_prompt'],
                "generation_time": time.time()
            }
            
            results.append(result)
            print(f"✓ 完成: {prompt_data['final_prompt']}")
        
        return results
    
    def save_prompts(self, prompts: List[Dict[str, Any]], output_file: str = None):
        """保存prompt到JSON文件"""
        if output_file:
            filepath = Path(output_file)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fixed_prompts_{timestamp}.json"
            filepath = self.output_dir / filename
        
        # 确保目录存在
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 固定prompt已保存: {filepath}")
        print(f"共生成 {len(prompts)} 个prompt")
        
        # 打印所有prompt
        print("\n📋 生成的prompt列表:")
        for i, prompt in enumerate(prompts, 1):
            print(f"  {i}. [{prompt['mode']}] {prompt['final_prompt']}")
        
        return filepath

async def main():
    """主函数"""
    print("🎵 固定Prompt生成器 - Gemini环境")
    print("=" * 60)
    print("使用Gemini API生成固定的30个prompt供测试使用")
    
    # 创建生成器
    generator = FixedPromptGenerator()
    
    # 生成固定prompt
    prompts = await generator.generate_fixed_prompts()
    
    # 保存prompt
    filepath = generator.save_prompts(prompts)
    
    print("\n" + "=" * 60)
    print("✅ 固定prompt生成完成!")
    print(f"文件路径: {filepath}")
    print("现在可以运行测试脚本使用这些prompt了")

if __name__ == "__main__":
    asyncio.run(main()) 