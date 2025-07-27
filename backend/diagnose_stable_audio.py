#!/usr/bin/env python3
"""
诊断 Stable Audio 配置和可能的问题
"""

import os
import sys
import traceback

def check_environment():
    """检查环境配置"""
    print("=== 环境检查 ===")
    
    # 检查 Python 版本
    print(f"Python 版本: {sys.version}")
    
    # 检查环境变量
    hf_token = os.environ.get('HF_TOKEN') or os.environ.get('HUGGING_FACE_HUB_TOKEN')
    if hf_token:
        print(f"✅ Hugging Face Token 已设置 (长度: {len(hf_token)})")
    else:
        print("❌ Hugging Face Token 未设置")
    
    # 检查 CUDA
    try:
        import torch
        print(f"PyTorch 版本: {torch.__version__}")
        print(f"CUDA 可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA 版本: {torch.version.cuda}")
            print(f"GPU 数量: {torch.cuda.device_count()}")
            print(f"当前 GPU: {torch.cuda.current_device()}")
    except ImportError:
        print("❌ PyTorch 未安装")
    
    # 检查必要的包
    required_packages = [
        'torch',
        'torchaudio', 
        'einops',
        'stable_audio_tools',
        'pydub'
    ]
    
    print("\n=== 包检查 ===")
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")

def test_stable_audio_import():
    """测试 Stable Audio 导入"""
    print("\n=== Stable Audio 导入测试 ===")
    
    try:
        from stable_audio_tools import get_pretrained_model
        print("✅ stable_audio_tools 导入成功")
        
        # 测试模型配置获取
        try:
            model, config = get_pretrained_model("stabilityai/stable-audio-open-small")
            print("✅ 模型加载成功")
            print(f"模型配置: {config}")
            return True
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ stable_audio_tools 导入失败: {e}")
        return False

def test_audio_service():
    """测试音频服务"""
    print("\n=== 音频服务测试 ===")
    
    try:
        # 添加路径
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        from app.services.stable_audio_service import stable_audio_service
        
        print("✅ StableAudioService 导入成功")
        
        # 测试模型加载
        try:
            stable_audio_service.load_model()
            print("✅ 模型加载成功")
            return True
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ 音频服务测试失败: {e}")
        traceback.print_exc()
        return False

def test_worker_script():
    """测试 worker 脚本"""
    print("\n=== Worker 脚本测试 ===")
    
    try:
        import subprocess
        import tempfile
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        # 测试 worker 脚本
        worker_script = os.path.join(os.path.dirname(__file__), "scripts", "run_stable_audio_worker.py")
        
        if not os.path.exists(worker_script):
            print(f"❌ Worker 脚本不存在: {worker_script}")
            return False
        
        print(f"✅ Worker 脚本存在: {worker_script}")
        
        # 测试基本参数解析
        try:
            result = subprocess.run([
                sys.executable, worker_script, 
                "--prompt", "test sound", 
                "--duration", "1.0", 
                "--out", tmp_path
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Worker 脚本执行成功")
                return True
            else:
                print(f"❌ Worker 脚本执行失败")
                print(f"返回码: {result.returncode}")
                print(f"标准输出: {result.stdout}")
                print(f"错误输出: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Worker 脚本执行超时")
            return False
        except Exception as e:
            print(f"❌ Worker 脚本执行异常: {e}")
            return False
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        print(f"❌ Worker 脚本测试失败: {e}")
        return False

def main():
    """主诊断函数"""
    print("=== Stable Audio 诊断工具 ===")
    
    # 环境检查
    check_environment()
    
    # 导入测试
    import_success = test_stable_audio_import()
    
    # 服务测试
    service_success = test_audio_service()
    
    # Worker 测试
    worker_success = test_worker_script()
    
    # 总结
    print("\n=== 诊断结果 ===")
    print(f"导入测试: {'✅ 通过' if import_success else '❌ 失败'}")
    print(f"服务测试: {'✅ 通过' if service_success else '❌ 失败'}")
    print(f"Worker测试: {'✅ 通过' if worker_success else '❌ 失败'}")
    
    if import_success and service_success and worker_success:
        print("\n🎉 所有测试通过！Stable Audio 应该可以正常工作。")
    else:
        print("\n💥 发现问题！请根据上述错误信息进行修复。")
        
        if not import_success:
            print("\n建议修复导入问题:")
            print("1. 检查 stable_audio_tools 是否正确安装")
            print("2. 检查 Hugging Face token 是否设置")
            print("3. 检查网络连接")
        
        if not service_success:
            print("\n建议修复服务问题:")
            print("1. 检查模型下载权限")
            print("2. 检查磁盘空间")
            print("3. 检查内存使用")

if __name__ == "__main__":
    main() 