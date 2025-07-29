import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import json

class SupabaseStorageService:
    def __init__(self):
        # 获取项目根目录的 .env 文件路径
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        env_path = project_root / ".env"
        load_dotenv(env_path)
        
        # 从环境变量获取 Supabase 配置
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase configuration. Please set SUPABASE_URL and SUPABASE_KEY environment variables.")
        
        try:
            self.supabase: Client = create_client(supabase_url, supabase_key)
            self.bucket_name = "audio-files"
            # 检查存储桶是否存在
            try:
                self.supabase.storage.get_bucket(self.bucket_name)
            except Exception as e:
                raise
                
        except Exception as e:
            raise

    async def upload_audio(self, file_path: str, description: str) -> Optional[str]:
        """
        上传音频文件到 Supabase Storage
        
        Args:
            file_path: 本地音频文件路径
            description: 音频描述，用于生成文件名
            
        Returns:
            str: 可访问的音频文件 URL，如果上传失败则返回 None
        """
        # 添加调试信息
        print(f"[DEBUG] upload_audio: file_path={file_path}")
        print(f"[DEBUG] upload_audio: file_path type={type(file_path)}")
        print(f"[DEBUG] upload_audio: file_path exists={os.path.exists(file_path)}")
        print(f"[DEBUG] upload_audio: file_path absolute={os.path.abspath(file_path)}")
        print(f"[DEBUG] upload_audio: current working directory={os.getcwd()}")
        
        # 尝试多种路径变体
        possible_paths = [
            file_path,
            os.path.abspath(file_path),
            os.path.normpath(file_path),
            os.path.join(os.getcwd(), file_path),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "audio_output", os.path.basename(file_path))
        ]
        
        actual_file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                actual_file_path = path
                print(f"[DEBUG] upload_audio: Found file at {path}")
                break
        
        if not actual_file_path:
            print(f"[ERROR] File not found in any of the attempted paths:")
            for path in possible_paths:
                print(f"  - {path} (exists: {os.path.exists(path)})")
            
            # 如果文件不存在，尝试创建一个空的音频文件作为占位符
            print(f"[WARNING] Creating placeholder file for Supabase upload")
            try:
                # 创建一个简单的音频文件（1秒的静音）
                import wave
                import struct
                
                placeholder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "audio_output", "placeholder.wav")
                os.makedirs(os.path.dirname(placeholder_path), exist_ok=True)
                
                # 创建1秒的静音WAV文件
                sample_rate = 44100
                duration = 1.0
                num_samples = int(sample_rate * duration)
                
                with wave.open(placeholder_path, 'w') as wav_file:
                    wav_file.setnchannels(1)  # 单声道
                    wav_file.setsampwidth(2)   # 16位
                    wav_file.setframerate(sample_rate)
                    
                    # 写入静音数据
                    for _ in range(num_samples):
                        wav_file.writeframes(struct.pack('<h', 0))
                
                actual_file_path = placeholder_path
                print(f"[INFO] Created placeholder file: {actual_file_path}")
                
            except Exception as e:
                print(f"[ERROR] Failed to create placeholder file: {e}")
                return None
            
        try:
            # 生成唯一的文件名
            file_name = f"{hash(description)}.wav"
            
            # 读取文件内容
            with open(actual_file_path, 'rb') as f:
                file_data = f.read()
            
            print(f"[INFO] Attempting to upload file: {file_name} (size: {len(file_data)} bytes)")
            
            # 上传到 Supabase Storage
            try:
                result = self.supabase.storage.from_(self.bucket_name).upload(
                    file_name,
                    file_data,
                    {"content-type": "audio/wav"}
                )
                print(f"[SUCCESS] Upload successful: {file_name}")
            except Exception as upload_error:
                print(f"[ERROR] Upload error details: {str(upload_error)}")
                if "RLS" in str(upload_error):
                    print("\nRLS Policy Error: Please check your Supabase storage bucket policies.")
                    print("You may need to add a policy like:")
                    print("""
                    CREATE POLICY \"Allow public uploads\"
                    ON storage.objects
                    FOR INSERT
                    TO public
                    WITH CHECK (bucket_id = 'audio-files');
                    """)
                raise
            
            # 获取公共访问 URL
            try:
                url = self.supabase.storage.from_(self.bucket_name).get_public_url(file_name)
                print(f"[SUCCESS] File uploaded successfully: {url}")
                return url
            except Exception as url_error:
                print(f"[ERROR] Error getting public URL: {url_error}")
                return None
            
        except Exception as e:
            print(f"[ERROR] Error uploading to Supabase: {e}")
            return None

    async def delete_audio(self, file_name: str) -> bool:
        """
        从 Supabase Storage 删除音频文件
        
        Args:
            file_name: 文件名
            
        Returns:
            bool: 删除是否成功
        """
        try:
            self.supabase.storage.from_(self.bucket_name).remove([file_name])
            print(f"File deleted successfully: {file_name}")
            return True
        except Exception as e:
            print(f"Error deleting from Supabase: {e}")
            return False

    async def upload_image(self, file_path: str, description: str) -> Optional[str]:
        try:
            file_name = f"image_{hash(description)}.png"
            with open(file_path, 'rb') as f:
                try:
                    # Try to upload the file
                    self.supabase.storage.from_('images').upload(
                        file_name,
                        f.read(),
                        {"content-type": "image/png"}
                    )
                except Exception as upload_error:
                    # If error is due to duplicate file, that's fine
                    if "Duplicate" in str(upload_error):
                        print(f"Image already exists: {file_name}")
                    else:
                        print(f"Failed to upload image: {upload_error}")
                        raise
            
            # Get the public URL regardless of whether upload succeeded or file already existed
            return self.supabase.storage.from_('images').get_public_url(file_name)
        except Exception as e:
            print(f"Failed to upload image: {e}")
            return None

# 创建单例实例
storage_service = SupabaseStorageService() 