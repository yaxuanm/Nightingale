#!/usr/bin/env python3
"""
音频生成测试脚本 - 在Stable Audio环境中
- 读取生成的prompt文件
- 生成音频并上传到Supabase
- 创建英文评估界面
"""

import os
import sys
import time
import json
import torchaudio
import numpy as np
import webbrowser
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import torch
import argparse

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.stable_audio_service import stable_audio_service
from app.services.storage_service import storage_service

class AudioTester:
    """音频测试器"""
    
    def __init__(self):
        self.results = []
        self.output_dir = Path("audio_test_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # 创建子目录
        (self.output_dir / "audio_files").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
        (self.output_dir / "evaluation").mkdir(exist_ok=True)
        
    def load_prompts(self, prompt_file: str = None) -> List[Dict[str, Any]]:
        """加载prompt文件"""
        if prompt_file is None:
            # 自动查找最新的prompt文件
            prompt_dir = Path("generated_prompts")
            if not prompt_dir.exists():
                print("❌ 未找到generated_prompts目录")
                return []
            
            prompt_files = list(prompt_dir.glob("generated_prompts_*.json"))
            if not prompt_files:
                print("❌ 未找到prompt文件")
                return []
            
            # 选择最新的文件
            prompt_file = max(prompt_files, key=lambda x: x.stat().st_mtime)
            print(f"📁 自动选择prompt文件: {prompt_file}")
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompts = json.load(f)
            print(f"✅ 成功加载 {len(prompts)} 个prompt")
            return prompts
        except Exception as e:
            print(f"❌ 加载prompt文件失败: {str(e)}")
            return []
    
    def analyze_audio_comprehensive(self, audio_path: str) -> Dict[str, Any]:
        """简化的音频分析 - 只保留基础指标"""
        try:
            # 检查文件是否存在
            if not os.path.exists(audio_path):
                return {"error": f"Audio file not found: {audio_path}"}
            
            # 检查文件大小
            file_size = os.path.getsize(audio_path)
            if file_size == 0:
                return {"error": f"Audio file is empty: {audio_path}"}
            
            # 加载音频
            waveform, sample_rate = torchaudio.load(audio_path)
            
            # 转换为float32进行计算
            waveform = waveform.float()
            
            duration = waveform.shape[1] / sample_rate
            channels = waveform.shape[0]
            
            # 基础指标
            dynamic_range = torch.max(waveform) - torch.min(waveform)
            rms = torch.sqrt(torch.mean(waveform ** 2))
            silence_ratio = torch.sum(torch.abs(waveform) < 0.01) / waveform.numel()
            
            # 频谱分析
            if channels == 2:  # 立体声
                left_channel = waveform[0]
                right_channel = waveform[1]
                stereo_correlation = torch.corrcoef(torch.stack([left_channel, right_channel]))[0, 1]
            else:
                stereo_correlation = 1.0
            
            # 峰值检测
            peak_ratio = torch.sum(torch.abs(waveform) > 0.9) / waveform.numel()
            
            # 频谱密度分析
            fft = torch.fft.fft(waveform.mean(dim=0))
            spectral_density = torch.abs(fft)
            spectral_centroid = torch.sum(spectral_density * torch.arange(len(spectral_density))) / torch.sum(spectral_density)
            
            # 过零率 (Zero Crossing Rate) - 衡量音频的复杂度
            zero_crossings = torch.sum(torch.sign(waveform[:, 1:]) != torch.sign(waveform[:, :-1]))
            zero_crossing_rate = zero_crossings / (waveform.shape[0] * (waveform.shape[1] - 1))
            
            return {
                "duration": float(duration),
                "channels": int(channels),
                "sample_rate": int(sample_rate),
                "dynamic_range": float(dynamic_range),
                "rms": float(rms),
                "silence_ratio": float(silence_ratio),
                "stereo_correlation": float(stereo_correlation) if isinstance(stereo_correlation, (float, int)) else stereo_correlation.item(),
                "peak_ratio": float(peak_ratio),
                "spectral_centroid": float(spectral_centroid),
                "zero_crossing_rate": float(zero_crossing_rate),
                "file_size": file_size
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def run_single_test(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个测试"""
        print(f"\n=== 测试: {prompt_data['id']} ===")
        print(f"模式: {prompt_data['mode']}")
        print(f"用户输入: {prompt_data['user_input']}")
        print(f"最终prompt: {prompt_data['final_prompt']}")
        
        start_time = time.time()
        
        try:
            # 设置默认时长
            duration = 8.0
            
            # 生成音频
            print(f"🔄 正在生成音频...")
            audio_path = stable_audio_service.generate_audio(
                prompt=prompt_data['final_prompt'],
                duration=duration
            )
            
            generation_time = time.time() - start_time
            
            # 上传到 Supabase
            print(f"☁️ 正在上传到 Supabase...")
            cloud_url = await storage_service.upload_audio(audio_path, prompt_data['final_prompt'])
            
            if cloud_url:
                print(f"✅ 上传成功: {cloud_url}")
            else:
                print("❌ 上传失败，使用本地文件")
                cloud_url = None
            
            # 分析音频
            metrics = self.analyze_audio_comprehensive(audio_path)
            
            result = {
                "id": prompt_data['id'],
                "user_input": prompt_data['user_input'],
                "mode": prompt_data['mode'],
                "inspiration_chip": prompt_data['inspiration_chip'],
                "atmosphere": prompt_data['atmosphere'],
                "elements": prompt_data['elements'],
                "final_prompt": prompt_data['final_prompt'],
                "duration": duration,
                "category": prompt_data['mode'],
                "success": True,
                "local_audio_path": audio_path,
                "cloud_url": cloud_url,
                "generation_time": generation_time,
                "metrics": metrics,
                "error": None,
                "human_evaluation": None
            }
            
            print(f"✓ 成功 (耗时: {generation_time:.2f}秒)")
            print(f"  文件大小: {metrics.get('file_size', 0)} bytes")
            print(f"  实际时长: {metrics.get('duration', 0):.2f}秒")
            
            return result
            
        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = str(e)
            
            result = {
                "id": prompt_data['id'],
                "user_input": prompt_data['user_input'],
                "mode": prompt_data['mode'],
                "inspiration_chip": prompt_data['inspiration_chip'],
                "atmosphere": prompt_data['atmosphere'],
                "elements": prompt_data['elements'],
                "final_prompt": prompt_data['final_prompt'],
                "duration": 8.0,
                "category": prompt_data['mode'],
                "success": False,
                "local_audio_path": None,
                "cloud_url": None,
                "generation_time": generation_time,
                "metrics": {},
                "error": error_msg,
                "human_evaluation": None
            }
            
            print(f"✗ 失败: {error_msg}")
            return result
    
    async def run_batch_test(self, prompt_file: str = None, progress_file: str = None) -> List[Dict[str, Any]]:
        """运行批量测试"""
        # 加载prompt
        prompts = self.load_prompts(prompt_file)
        if not prompts:
            print("❌ 没有可用的prompt，退出测试")
            return []
        
        print(f"🚀 开始批量测试 - 共 {len(prompts)} 个prompt")
        print("流程: 加载prompt → 生成音频 → 上传云存储 → 测评")
        
        start_time = time.time()
        
        results = []
        total = len(prompts)
        for i, prompt_data in enumerate(prompts, 1):
            print(f"\n[{i}/{total}] 进度")
            result = await self.run_single_test(prompt_data)
            results.append(result)
            # 写入进度文件
            if progress_file:
                progress = {
                    "current": i,
                    "total": total,
                    "results": [
                        {"id": r["id"], "final_prompt": r["final_prompt"]} for r in results
                    ]
                }
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(progress, f, ensure_ascii=False)
        
        total_time = time.time() - start_time
        
        # 统计结果
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"\n" + "="*60)
        print(f"✅ 测试完成!")
        print(f"总耗时: {total_time:.2f}秒")
        print(f"成功: {len(successful)}/{len(results)}")
        print(f"失败: {len(failed)}/{len(results)}")
        
        if successful:
            avg_time = np.mean([r['generation_time'] for r in successful])
            print(f"平均生成时间: {avg_time:.2f}秒")
        
        self.results = results
        return results
    
    def generate_evaluation_interface(self):
        """生成人工评估界面"""
        if not self.results:
            print("没有测试结果可评估")
            return
        
        successful_results = [r for r in self.results if r['success']]
        if not successful_results:
            print("没有成功的测试结果可评估")
            return
        
        # 生成HTML评估界面
        html_content = self.create_evaluation_html(successful_results)
        
        evaluation_file = self.output_dir / "evaluation" / "human_evaluation.html"
        with open(evaluation_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n🎯 人工评估界面已生成: {evaluation_file}")
        print("请在浏览器中打开此文件进行人工评估")
        
        # 尝试自动打开浏览器
        try:
            webbrowser.open(f"file://{evaluation_file.absolute()}")
        except:
            print("无法自动打开浏览器，请手动打开评估文件")
    
    def create_evaluation_html(self, results: List[Dict[str, Any]]) -> str:
        """创建HTML评估界面 - 精简版"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Stable Audio Evaluation Interface</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .test-item {{ background: white; margin: 10px 0; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .test-info {{ margin-bottom: 15px; }}
        .audio-player {{ margin: 10px 0; }}
        .evaluation-form {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 15px 0; }}
        .rating-group {{ display: flex; flex-direction: column; }}
        .rating-group label {{ font-weight: bold; margin-bottom: 5px; }}
        .rating-group select {{ padding: 8px; border: 1px solid #ddd; border-radius: 3px; }}
        .comments {{ width: 100%; height: 80px; padding: 8px; border: 1px solid #ddd; border-radius: 3px; resize: vertical; }}
        .submit-btn {{ background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }}
        .submit-btn:hover {{ background: #2980b9; }}
        .progress {{ background: #ecf0f1; padding: 10px; border-radius: 3px; margin: 10px 0; }}
        .url-info {{ background: #ecf0f1; padding: 10px; border-radius: 3px; margin: 10px 0; font-family: monospace; word-break: break-all; font-size: 12px; }}
        .audio-error {{ color: #e74c3c; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 Stable Audio Evaluation Interface</h1>
            <p>Please evaluate the quality of each audio sample. Click "Save Evaluation Results" when finished.</p>
            <p><strong>Audio Source:</strong> Supabase Cloud Storage</p>
        </div>
        
        <div class="progress">
            <span id="progress-text">Evaluation Progress: 0/{len(results)}</span>
            <div style="width: 100%; background: #ddd; height: 20px; border-radius: 10px; overflow: hidden;">
                <div id="progress-bar" style="width: 0%; background: #3498db; height: 100%; transition: width 0.3s;"></div>
            </div>
        </div>
        
        <form id="evaluation-form">
"""
        for i, result in enumerate(results):
            audio_url = result.get('cloud_url') or f"/static/generated_audio/{os.path.basename(result['local_audio_path'])}"
            html_content += f"""
            <div class="test-item" data-id="{result['id']}">
                <div class="test-info">
                    <h3>Test {i+1}: {result['id']}</h3>
                    <p><strong>Duration:</strong> {result.get('metrics', {}).get('duration', 0):.2f} seconds</p>
                    <p><strong>File Size:</strong> {result.get('metrics', {}).get('file_size', 0)} bytes</p>
                    <div class="url-info">
                        <strong>Audio URL:</strong><br>
                        {audio_url}
                    </div>
                </div>
                <div class="audio-player">
                    <p><strong>Audio Player:</strong></p>
                    <audio controls style="width: 100%;">
                        <source src="{audio_url}" type="audio/wav">
                        Your browser does not support audio playback.
                    </audio>
                    <p class="audio-error" id="audio-error-{i}" style="display: none;">
                        ⚠️ Audio cannot be played, please check network connection or URL
                    </p>
                </div>
                <div class="evaluation-form">
                    <div class="rating-group">
                        <label for="relevance_{i}">Relevance (1-5):</label>
                        <select name="relevance_{i}" id="relevance_{i}" required>
                            <option value="">Please select</option>
                            <option value="1">1 - Completely irrelevant</option>
                            <option value="2">2 - Partially relevant</option>
                            <option value="3">3 - Moderately relevant</option>
                            <option value="4">4 - Highly relevant</option>
                            <option value="5">5 - Perfectly relevant</option>
                        </select>
                    </div>
                    <div class="rating-group">
                        <label for="quality_{i}">Audio Quality (1-5):</label>
                        <select name="quality_{i}" id="quality_{i}" required>
                            <option value="">Please select</option>
                            <option value="1">1 - Very poor quality</option>
                            <option value="2">2 - Poor quality</option>
                            <option value="3">3 - Average quality</option>
                            <option value="4">4 - Good quality</option>
                            <option value="5">5 - Excellent quality</option>
                        </select>
                    </div>
                    <div class="rating-group">
                        <label for="enjoyment_{i}">Listening Enjoyment (1-5):</label>
                        <select name="enjoyment_{i}" id="enjoyment_{i}" required>
                            <option value="">Please select</option>
                            <option value="1">1 - Not enjoyable at all</option>
                            <option value="2">2 - Slightly enjoyable</option>
                            <option value="3">3 - Moderately enjoyable</option>
                            <option value="4">4 - Quite enjoyable</option>
                            <option value="5">5 - Very enjoyable</option>
                        </select>
                    </div>
                    <div class="rating-group">
                        <label for="usability_{i}">Usability (1-5):</label>
                        <select name="usability_{i}" id="usability_{i}" required>
                            <option value="">Please select</option>
                            <option value="1">1 - Completely unusable</option>
                            <option value="2">2 - Mostly unusable</option>
                            <option value="3">3 - Barely usable</option>
                            <option value="4">4 - Quite usable</option>
                            <option value="5">5 - Highly usable</option>
                        </select>
                    </div>
                </div>
                <div>
                    <label for="comments_{i}">Detailed Comments:</label>
                    <textarea name="comments_{i}" id="comments_{i}" class="comments" placeholder="Please describe your experience and suggestions in detail..."></textarea>
                </div>
            </div>
        """
        html_content += f"""
            <div style="text-align: center; margin: 20px 0;">
                <button type="submit" class="submit-btn">💾 Save Evaluation Results</button>
            </div>
        </form>
    </div>
    <script>
        // Check if audio files exist
        function checkAudioFiles() {{
            const audioElements = document.querySelectorAll('audio');
            audioElements.forEach((audio, index) => {{
                audio.addEventListener('error', function() {{
                    const errorElement = document.getElementById(`audio-error-${{index}}`);
                    if (errorElement) {{
                        errorElement.style.display = 'block';
                    }}
                }});
                audio.addEventListener('loadstart', function() {{
                    const errorElement = document.getElementById(`audio-error-${{index}}`);
                    if (errorElement) {{
                        errorElement.style.display = 'none';
                    }}
                }});
            }});
        }}
        function updateProgress() {{
            const form = document.getElementById('evaluation-form');
            const selects = form.querySelectorAll('select[required]');
            const totalRequired = selects.length;
            let completed = 0;
            selects.forEach(select => {{
                if (select.value !== '') {{
                    completed++;
                }}
            }});
            const progressText = document.getElementById('progress-text');
            const progressBar = document.getElementById('progress-bar');
            const percentage = (completed / totalRequired) * 100;
            progressText.textContent = `Evaluation Progress: ${{completed}}/${{totalRequired}}`;
            progressBar.style.width = percentage + '%';
        }}
        document.querySelectorAll('select').forEach(select => {{
            select.addEventListener('change', updateProgress);
        }});
        document.getElementById('evaluation-form').addEventListener('submit', function(e) {{
            e.preventDefault();
            const formData = new FormData(this);
            const evaluationData = {{}};
            for (let i = 0; i < {len(results)}; i++) {{
                evaluationData[i] = {{
                    relevance: formData.get(`relevance_${{i}}`),
                    quality: formData.get(`quality_${{i}}`),
                    enjoyment: formData.get(`enjoyment_${{i}}`),
                    usability: formData.get(`usability_${{i}}`),
                    comments: formData.get(`comments_${{i}}`)
                }};
            }}
            const dataStr = JSON.stringify(evaluationData, null, 2);
            const dataBlob = new Blob([dataStr], {{type: 'application/json'}});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'human_evaluation_results.json';
            link.click();
            alert('Evaluation results saved!');
        }});
        updateProgress();
        checkAudioFiles();
    </script>
</body>
</html>
        """
        return html_content
    
    def save_results(self):
        """保存测试结果"""
        if not self.results:
            print("没有测试结果可保存")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存详细JSON结果
        json_file = self.output_dir / "reports" / f"audio_test_results_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        # 生成简化的CSV报告
        csv_data = []
        for result in self.results:
            csv_data.append({
                "id": result['id'],
                "user_input": result['user_input'],
                "mode": result['mode'],
                "category": result['category'],
                "final_prompt": result['final_prompt'],
                "success": result['success'],
                "generation_time": result['generation_time'],
                "duration": result.get('metrics', {}).get('duration', 0),
                "file_size": result.get('metrics', {}).get('file_size', 0),
                "cloud_url": result.get('cloud_url', ''),
                "error": result.get('error', '')
            })
        
        df = pd.DataFrame(csv_data)
        csv_file = self.output_dir / "reports" / f"audio_test_results_{timestamp}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        # 生成基础统计报告
        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]
        
        report = {
            "summary": {
                "total_tests": len(self.results),
                "successful": len(successful),
                "failed": len(failed),
                "success_rate": len(successful) / len(self.results) * 100 if self.results else 0
            },
            "performance": {
                "avg_generation_time": np.mean([r['generation_time'] for r in successful]) if successful else 0,
                "avg_duration": np.mean([r.get('metrics', {}).get('duration', 0) for r in successful]) if successful else 0,
                "avg_file_size": np.mean([r.get('metrics', {}).get('file_size', 0) for r in successful]) if successful else 0
            },
            "failed_tests": [
                {"id": r['id'], "user_input": r['user_input'], "error": r['error']} 
                for r in failed
            ]
        }
        
        report_file = self.output_dir / "reports" / f"audio_test_report_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 结果已保存:")
        print(f"  详细结果: {json_file}")
        print(f"  CSV数据: {csv_file}")
        print(f"  统计报告: {report_file}")
        
        # 打印基础统计
        if successful:
            print(f"\n📈 基础统计:")
            print(f"  成功率: {len(successful)/len(self.results)*100:.1f}%")
            print(f"  平均生成时间: {np.mean([r['generation_time'] for r in successful]):.2f}秒")
            print(f"  平均时长: {np.mean([r.get('metrics', {}).get('duration', 0) for r in successful]):.2f}秒")
            print(f"  平均文件大小: {np.mean([r.get('metrics', {}).get('file_size', 0) for r in successful]):.0f} bytes")

async def main():
    """主函数"""
    print("🎵 音频生成测试工具")
    print("=" * 60)
    print("读取prompt文件，生成音频，创建评估界面")
    
    # 创建测试器
    tester = AudioTester()
    
    # 运行批量测试
    results = await tester.run_batch_test()
    
    # 保存结果
    tester.save_results()
    
    # 生成评估界面
    tester.generate_evaluation_interface()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成!")
    print("请打开生成的评估界面进行人工评估")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', type=str, default=None, help='Prompt文件路径')
    parser.add_argument('--output', type=str, default=None, help='结果输出文件路径')
    parser.add_argument('--audio_dir', type=str, default=None, help='音频输出目录')
    parser.add_argument('--progress_file', type=str, default=None, help='进度文件路径')
    args = parser.parse_args()
    tester = AudioTester()
    results = asyncio.run(tester.run_batch_test(prompt_file=args.prompt, progress_file=args.progress_file))
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2) 