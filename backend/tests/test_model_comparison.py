import pytest
import asyncio
import os
import time
import json
from typing import List, Dict, Any
from datetime import datetime

# 导入不同的音频服务
from app.services.stable_audio_service import stable_audio_service
from app.services.audio_service import audio_service

class TestModelComparison:
    """模型对比测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前的设置"""
        self.test_prompts = [
            "128 BPM tech house drum loop",
            "peaceful rain sounds with distant thunder", 
            "gentle ocean waves crashing on the shore",
            "forest ambience with birds chirping",
            "cozy fireplace crackling sounds"
        ]
        
        # 创建结果目录
        self.results_dir = os.path.join(os.path.dirname(__file__), "comparison_results")
        os.makedirs(self.results_dir, exist_ok=True)
        
    def test_stable_audio_basic(self):
        """测试 Stable Audio Open Small 基础功能"""
        print("\n=== Stable Audio Open Small 基础测试 ===")
        
        try:
            # 导入服务
            from app.services.stable_audio_service import stable_audio_service
            
            # 测试模型信息
            info = stable_audio_service.get_model_info()
            print(f"模型信息: {info}")
            
            # 测试基本生成
            audio_path = stable_audio_service.generate_audio("test prompt", duration=3.0)
            print(f"生成的音频文件: {audio_path}")
            
            assert os.path.exists(audio_path), "音频文件应该存在"
            print("✓ 基础功能测试通过")
            
        except ImportError as e:
            print(f"⚠ 无法导入 Stable Audio 服务: {e}")
            pytest.skip("Stable Audio 服务不可用")
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            raise
        
    def test_model_loading_time(self):
        """测试模型加载时间"""
        print("\n=== 模型加载时间测试 ===")
        
        try:
            from app.services.stable_audio_service import stable_audio_service
            
            start_time = time.time()
            stable_audio_service.load_model()
            load_time = time.time() - start_time
            
            print(f"Stable Audio Open Small 加载时间: {load_time:.2f}秒")
            
            # 保存结果
            results = {
                "model": "Stable Audio Open Small",
                "load_time_seconds": load_time,
                "timestamp": datetime.now().isoformat()
            }
            
            self._save_results("loading_time", results)
            
        except Exception as e:
            print(f"✗ 加载时间测试失败: {e}")
            raise
        
    def test_generation_speed(self):
        """测试生成速度"""
        print("\n=== 生成速度测试 ===")
        
        try:
            from app.services.stable_audio_service import stable_audio_service
            
            test_prompts = [
                "128 BPM tech house drum loop",
                "peaceful rain sounds",
                "ocean waves"
            ]
            
            results = {}
            
            for i, prompt in enumerate(test_prompts):
                print(f"测试提示词 {i+1}: {prompt}")
                
                start_time = time.time()
                audio_path = stable_audio_service.generate_audio(prompt, duration=3.0)
                generation_time = time.time() - start_time
                
                file_size = os.path.getsize(audio_path) if os.path.exists(audio_path) else 0
                
                results[f"prompt_{i+1}"] = {
                    "prompt": prompt,
                    "generation_time_seconds": generation_time,
                    "file_size_bytes": file_size,
                    "audio_path": audio_path
                }
                
                print(f"  ✓ 生成时间: {generation_time:.2f}秒, 文件大小: {file_size} bytes")
            
            # 计算平均时间
            avg_time = sum(r["generation_time_seconds"] for r in results.values()) / len(results)
            print(f"\n平均生成时间: {avg_time:.2f}秒")
            
            # 保存结果
            self._save_results("generation_speed", results)
            
        except Exception as e:
            print(f"✗ 生成速度测试失败: {e}")
            raise
        
    def test_audio_quality_metrics(self):
        """测试音频质量指标"""
        print("\n=== 音频质量测试 ===")
        
        try:
            import torchaudio
            from app.services.stable_audio_service import stable_audio_service
            
            test_prompt = "peaceful rain sounds with distant thunder"
            duration = 5.0
            
            # 生成音频
            audio_path = stable_audio_service.generate_audio(test_prompt, duration)
            
            # 分析音频文件
            waveform, sample_rate = torchaudio.load(audio_path)
            
            # 计算质量指标
            actual_duration = waveform.shape[1] / sample_rate
            channels = waveform.shape[0]
            file_size = os.path.getsize(audio_path)
            bitrate = (file_size * 8) / actual_duration if actual_duration > 0 else 0
            
            # 计算音频统计信息
            mean_amplitude = torch.mean(torch.abs(waveform)).item()
            max_amplitude = torch.max(torch.abs(waveform)).item()
            rms = torch.sqrt(torch.mean(waveform**2)).item()
            
            results = {
                "prompt": test_prompt,
                "requested_duration": duration,
                "actual_duration": actual_duration,
                "sample_rate": sample_rate,
                "channels": channels,
                "file_size_bytes": file_size,
                "bitrate_bps": bitrate,
                "mean_amplitude": mean_amplitude,
                "max_amplitude": max_amplitude,
                "rms": rms,
                "audio_path": audio_path
            }
            
            print("音频质量指标:")
            print(f"  采样率: {sample_rate} Hz")
            print(f"  声道数: {channels}")
            print(f"  实际时长: {actual_duration:.2f}秒")
            print(f"  文件大小: {file_size} bytes")
            print(f"  比特率: {bitrate:.0f} bps")
            print(f"  平均振幅: {mean_amplitude:.4f}")
            print(f"  最大振幅: {max_amplitude:.4f}")
            print(f"  RMS: {rms:.4f}")
            
            # 保存结果
            self._save_results("audio_quality", results)
            
        except Exception as e:
            print(f"✗ 音频质量测试失败: {e}")
            raise
        
    def test_resource_usage(self):
        """测试资源使用情况"""
        print("\n=== 资源使用测试 ===")
        
        try:
            import psutil
            from app.services.stable_audio_service import stable_audio_service
            
            process = psutil.Process()
            
            # 基础资源使用
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
            baseline_cpu = process.cpu_percent()
            
            print(f"基础内存使用: {baseline_memory:.2f} MB")
            print(f"基础CPU使用: {baseline_cpu:.2f}%")
            
            # 加载模型后
            stable_audio_service.load_model()
            after_load_memory = process.memory_info().rss / 1024 / 1024
            after_load_cpu = process.cpu_percent()
            
            # 生成音频时
            start_time = time.time()
            audio_path = stable_audio_service.generate_audio("test resource usage", duration=3.0)
            generation_time = time.time() - start_time
            
            after_gen_memory = process.memory_info().rss / 1024 / 1024
            after_gen_cpu = process.cpu_percent()
            
            results = {
                "baseline_memory_mb": baseline_memory,
                "after_load_memory_mb": after_load_memory,
                "after_gen_memory_mb": after_gen_memory,
                "memory_increase_mb": after_load_memory - baseline_memory,
                "baseline_cpu_percent": baseline_cpu,
                "after_load_cpu_percent": after_load_cpu,
                "after_gen_cpu_percent": after_gen_cpu,
                "generation_time_seconds": generation_time
            }
            
            print(f"模型加载后内存增加: {results['memory_increase_mb']:.2f} MB")
            print(f"生成时间: {generation_time:.2f}秒")
            
            # 保存结果
            self._save_results("resource_usage", results)
            
        except Exception as e:
            print(f"✗ 资源使用测试失败: {e}")
            raise
        
    def _save_results(self, test_name: str, results: Dict[str, Any]):
        """保存测试结果到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"结果已保存到: {filepath}")

def test_stable_audio_integration():
    """测试 Stable Audio Open Small 集成"""
    print("\n=== 集成测试 ===")
    
    try:
        from app.services.stable_audio_service import stable_audio_service
        
        # 测试模型信息
        info = stable_audio_service.get_model_info()
        assert info["model_name"] == "Stable Audio Open Small"
        assert info["max_duration"] == 11.0
        
        print("✓ 模型信息正确")
        
        # 测试基本生成
        audio_path = stable_audio_service.generate_audio("test integration", duration=3.0)
        assert os.path.exists(audio_path)
        
        print("✓ 基本生成功能正常")
        
        # 测试音效配置
        effects_config = {
            "steps": 6,
            "cfg_scale": 1.5
        }
        audio_path_with_effects = stable_audio_service.generate_audio_with_effects(
            "test with effects", 
            duration=3.0, 
            effects_config=effects_config
        )
        assert os.path.exists(audio_path_with_effects)
        
        print("✓ 音效配置功能正常")
        
    except Exception as e:
        print(f"✗ 集成测试失败: {e}")
        raise

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"]) 