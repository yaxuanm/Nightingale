#!/usr/bin/env python3
"""
Prompt生成脚本 - 在Gemini虚拟环境中批量生成prompt
- 调用Gemini API生成inspiration chips, atmosphere, elements
- 随机选择选项组合成prompt
- 保存prompt到JSON文件供测试脚本使用
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

class PromptGenerator:
    """Prompt生成器"""
    
    def __init__(self):
        self.output_dir = Path("generated_prompts")
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化AI服务
        self.ai_service = AIService()
        
    def create_test_cases(self) -> List[Dict[str, Any]]:
        """创建5个非music测试用例，随机分配focus、relax、story"""
        modes = ["focus", "relax", "story"]
        test_cases = []
        for i in range(5):
            mode = random.choice(modes)
            test_cases.append({"id": f"test_{i+1}", "mode": mode})
        return test_cases
    
    async def generate_single_prompt(self, mode: str) -> Dict[str, Any]:
        """生成单个prompt"""
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
    
    async def generate_batch_prompts(self) -> List[Dict[str, Any]]:
        """批量生成prompt"""
        test_cases = self.create_test_cases()
        
        print(f"🚀 开始批量生成prompt - 共 {len(test_cases)} 个测试用例")
        print("模式包括: focus, relax, story, music")
        
        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] 生成prompt")
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
    
    def save_prompts(self, prompts: List[Dict[str, Any]]):
        """保存prompt到JSON文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_prompts_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 Prompt已保存: {filepath}")
        print(f"共生成 {len(prompts)} 个prompt")
        
        # 打印所有prompt
        print("\n📋 生成的prompt列表:")
        for i, prompt in enumerate(prompts, 1):
            print(f"  {i}. [{prompt['mode']}] {prompt['final_prompt']}")
        
        return filepath

async def main():
    """主函数"""
    print("🎵 Prompt生成器 - Gemini环境")
    print("=" * 60)
    print("批量生成prompt供测试使用")
    
    # 创建生成器
    generator = PromptGenerator()
    
    # 批量生成prompt
    prompts = await generator.generate_batch_prompts()
    
    # 保存prompt
    filepath = generator.save_prompts(prompts)
    
    print("\n" + "=" * 60)
    print("✅ Prompt生成完成!")
    print(f"文件路径: {filepath}")
    print("现在可以运行测试脚本使用这些prompt了")

if __name__ == "__main__":
    asyncio.run(main()) 