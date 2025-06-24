import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import json

class SupabaseStorageService:
    def __init__(self):
        load_dotenv()
        
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
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
            
        try:
            # 生成唯一的文件名
            file_name = f"{hash(description)}.wav"
            
            # 读取文件内容
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            print(f"Attempting to upload file: {file_name}")
            
            # 上传到 Supabase Storage
            try:
                result = self.supabase.storage.from_(self.bucket_name).upload(
                    file_name,
                    file_data,
                    {"content-type": "audio/wav"}
                )
                print(f"Upload successful: {file_name}") # 简单的成功信息
            except Exception as upload_error:
                print(f"Upload error details: {str(upload_error)}")
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
                print(f"File uploaded successfully: {url}")
                return url
            except Exception as url_error:
                print(f"Error getting public URL: {url_error}")
                return None
            
        except Exception as e:
            print(f"Error uploading to Supabase: {e}")
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