#!/usr/bin/env python3
"""
使用 Supabase 的 Stable Audio 测试脚本
- 生成音频并上传到 Supabase
- 创建可访问的评估界面
"""

import os
import sys
import time
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.stable_audio_service import stable_audio_service
from app.services.storage_service import storage_service

class SupabaseTester:
    """使用 Supabase 的测试器"""
    
    def __init__(self):
        self.output_dir = Path("supabase_test_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # 创建子目录
        (self.output_dir / "evaluation").mkdir(exist_ok=True)
        
    async def run_single_test(self) -> Dict[str, Any]:
        """运行单个测试并上传到 Supabase"""
        print("🎵 使用 Supabase 的 Stable Audio 测试")
        print("=" * 50)
        
        # 使用一个简单的测试用例
        test_case = {
            "id": "supabase_test",
            "user_input": "cozy cafe",
            "mode": "focus",
            "final_prompt": "cozy cafe, rainy afternoon with coffee machine steaming",
            "duration": 8.0
        }
        
        print(f"测试用例: {test_case['user_input']}")
        print(f"最终prompt: {test_case['final_prompt']}")
        print(f"时长: {test_case['duration']}秒")
        
        start_time = time.time()
        
        try:
            # 生成音频
            print("\n🔄 正在生成音频...")
            local_audio_path = stable_audio_service.generate_audio(
                prompt=test_case['final_prompt'],
                duration=test_case['duration']
            )
            
            generation_time = time.time() - start_time
            
            # 上传到 Supabase
            print("\n☁️ 正在上传到 Supabase...")
            cloud_url = await storage_service.upload_audio(local_audio_path, test_case['final_prompt'])
            
            if cloud_url:
                print(f"✅ 上传成功: {cloud_url}")
            else:
                print("❌ 上传失败，使用本地文件")
                cloud_url = None
            
            result = {
                "id": test_case['id'],
                "user_input": test_case['user_input'],
                "mode": test_case['mode'],
                "final_prompt": test_case['final_prompt'],
                "duration": test_case['duration'],
                "success": True,
                "local_audio_path": local_audio_path,
                "cloud_url": cloud_url,
                "generation_time": generation_time,
                "error": None
            }
            
            print(f"✅ 音频生成成功!")
            print(f"  耗时: {generation_time:.2f}秒")
            print(f"  本地文件: {local_audio_path}")
            print(f"  云存储URL: {cloud_url}")
            print(f"  文件大小: {os.path.getsize(local_audio_path)} bytes")
            
            return result
            
        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = str(e)
            
            result = {
                "id": test_case['id'],
                "user_input": test_case['user_input'],
                "mode": test_case['mode'],
                "final_prompt": test_case['final_prompt'],
                "duration": test_case['duration'],
                "success": False,
                "local_audio_path": None,
                "cloud_url": None,
                "generation_time": generation_time,
                "error": error_msg
            }
            
            print(f"❌ 生成失败: {error_msg}")
            return result
    
    def generate_evaluation_interface(self, result: Dict[str, Any]):
        """生成人工评估界面"""
        if not result['success']:
            print("没有成功的测试结果可评估")
            return
        
        # 生成HTML评估界面
        html_content = self.create_evaluation_html(result)
        
        evaluation_file = self.output_dir / "evaluation" / "human_evaluation.html"
        with open(evaluation_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n🎯 人工评估界面已生成: {evaluation_file}")
        print("请在浏览器中打开此文件进行人工评估")
        
        # 尝试自动打开浏览器
        try:
            import webbrowser
            webbrowser.open(f"file://{evaluation_file.absolute()}")
        except:
            print("无法自动打开浏览器，请手动打开评估文件")
    
    def create_evaluation_html(self, result: Dict[str, Any]) -> str:
        """创建HTML评估界面 - 使用 Supabase URL"""
        audio_url = result.get('cloud_url') or f"/static/generated_audio/{os.path.basename(result['local_audio_path'])}"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Stable Audio 人工评估界面</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
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
        .download-link {{ color: #3498db; text-decoration: none; }}
        .download-link:hover {{ text-decoration: underline; }}
        .audio-error {{ color: #e74c3c; font-weight: bold; }}
        .url-info {{ background: #ecf0f1; padding: 10px; border-radius: 3px; margin: 10px 0; font-family: monospace; word-break: break-all; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 Stable Audio 人工评估界面</h1>
            <p>请为音频样本进行质量评估。评估完成后点击"保存评估结果"。</p>
            <p><strong>音频来源:</strong> {'Supabase 云存储' if result.get('cloud_url') else '本地文件'}</p>
        </div>
        
        <form id="evaluation-form">
            <div class="test-item">
                <div class="test-info">
                    <h3>测试: {result['id']}</h3>
                    <p><strong>用户输入:</strong> {result['user_input']}</p>
                    <p><strong>模式:</strong> {result['mode']}</p>
                    <p><strong>最终Prompt:</strong> {result['final_prompt']}</p>
                    <p><strong>生成时间:</strong> {result['generation_time']:.2f}秒</p>
                    <div class="url-info">
                        <strong>音频URL:</strong><br>
                        {audio_url}
                    </div>
                </div>
                
                <div class="audio-player">
                    <p><strong>音频播放:</strong></p>
                    <audio controls style="width: 100%;">
                        <source src="{audio_url}" type="audio/wav">
                        您的浏览器不支持音频播放。
                    </audio>
                    <p class="audio-error" id="audio-error" style="display: none;">
                        ⚠️ 音频无法播放，请检查网络连接或URL
                    </p>
                    <p>
                        <a href="{audio_url}" target="_blank" class="download-link">
                            📥 在新窗口打开音频
                        </a>
                    </p>
                </div>
                
                <div class="evaluation-form">
                    <div class="rating-group">
                        <label for="relevance">相关性 (1-5):</label>
                        <select name="relevance" id="relevance" required>
                            <option value="">请选择</option>
                            <option value="1">1 - 完全不相关</option>
                            <option value="2">2 - 部分相关</option>
                            <option value="3">3 - 一般相关</option>
                            <option value="4">4 - 高度相关</option>
                            <option value="5">5 - 完全相关</option>
                        </select>
                    </div>
                    
                    <div class="rating-group">
                        <label for="quality">音频质量 (1-5):</label>
                        <select name="quality" id="quality" required>
                            <option value="">请选择</option>
                            <option value="1">1 - 质量很差</option>
                            <option value="2">2 - 质量较差</option>
                            <option value="3">3 - 质量一般</option>
                            <option value="4">4 - 质量较好</option>
                            <option value="5">5 - 质量很好</option>
                        </select>
                    </div>
                    
                    <div class="rating-group">
                        <label for="enjoyment">听觉享受 (1-5):</label>
                        <select name="enjoyment" id="enjoyment" required>
                            <option value="">请选择</option>
                            <option value="1">1 - 很不享受</option>
                            <option value="2">2 - 不太享受</option>
                            <option value="3">3 - 一般享受</option>
                            <option value="4">4 - 比较享受</option>
                            <option value="5">5 - 非常享受</option>
                        </select>
                    </div>
                    
                    <div class="rating-group">
                        <label for="usability">实用性 (1-5):</label>
                        <select name="usability" id="usability" required>
                            <option value="">请选择</option>
                            <option value="1">1 - 完全不可用</option>
                            <option value="2">2 - 基本不可用</option>
                            <option value="3">3 - 勉强可用</option>
                            <option value="4">4 - 比较可用</option>
                            <option value="5">5 - 非常可用</option>
                        </select>
                    </div>
                </div>
                
                <div>
                    <label for="comments">详细评论:</label>
                    <textarea name="comments" id="comments" class="comments" placeholder="请详细描述您的感受和建议..."></textarea>
                </div>
            </div>
            
            <div style="text-align: center; margin: 20px 0;">
                <button type="submit" class="submit-btn">💾 保存评估结果</button>
            </div>
        </form>
    </div>
    
    <script>
        // 检查音频文件是否存在
        function checkAudioFile() {{
            const audio = document.querySelector('audio');
            const errorElement = document.getElementById('audio-error');
            
            audio.addEventListener('error', function() {{
                if (errorElement) {{
                    errorElement.style.display = 'block';
                    console.log('Audio loading error');
                }}
            }});
            
            audio.addEventListener('loadstart', function() {{
                if (errorElement) {{
                    errorElement.style.display = 'none';
                }}
                console.log('Audio loading started');
            }});
            
            audio.addEventListener('canplay', function() {{
                console.log('Audio can play');
            }});
        }}
        
        // 表单提交
        document.getElementById('evaluation-form').addEventListener('submit', function(e) {{
            e.preventDefault();
            
            const formData = new FormData(this);
            const evaluationData = {{
                relevance: formData.get('relevance'),
                quality: formData.get('quality'),
                enjoyment: formData.get('enjoyment'),
                usability: formData.get('usability'),
                comments: formData.get('comments'),
                audio_url: '{audio_url}',
                timestamp: new Date().toISOString()
            }};
            
            // 创建下载链接
            const dataStr = JSON.stringify(evaluationData, null, 2);
            const dataBlob = new Blob([dataStr], {{type: 'application/json'}});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'evaluation_result.json';
            link.click();
            
            alert('评估结果已保存！');
        }});
        
        // 初始化
        checkAudioFile();
    </script>
</body>
</html>
        """
        
        return html_content

async def main():
    """主函数"""
    # 创建测试器
    tester = SupabaseTester()
    
    # 运行单个测试
    result = await tester.run_single_test()
    
    # 生成评估界面
    tester.generate_evaluation_interface(result)
    
    print("\n" + "=" * 50)
    print("✅ 测试完成!")
    print("请打开生成的评估界面进行人工评估")

if __name__ == "__main__":
    asyncio.run(main()) 