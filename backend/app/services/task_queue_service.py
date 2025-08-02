import redis
import rq
import json
import uuid
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(Enum):
    AUDIO_GENERATION = "audio_generation"
    MUSIC_GENERATION = "music_generation"
    STORY_GENERATION = "story_generation"
    IMAGE_GENERATION = "image_generation"
    TTS_GENERATION = "tts_generation"

class TaskQueueService:
    def __init__(self):
        # Redis连接配置
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_db = int(os.getenv('REDIS_DB', 0))
        
        # 初始化Redis连接
        try:
            self.redis_conn = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                decode_responses=True
            )
            # 测试连接
            self.redis_conn.ping()
            print(f"[TASK_QUEUE] Redis connected successfully to {self.redis_host}:{self.redis_port}")
        except Exception as e:
            print(f"[TASK_QUEUE] Redis connection failed: {e}")
            self.redis_conn = None
        
        # 初始化RQ队列
        if self.redis_conn:
            self.queue = rq.Queue('nightingale_tasks', connection=self.redis_conn)
            self.failed_queue = rq.Queue('nightingale_failed', connection=self.redis_conn)
        else:
            self.queue = None
            self.failed_queue = None
    
    def create_task(self, task_type: TaskType, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新任务"""
        if not self.queue:
            raise Exception("Task queue not available")
        
        task_id = str(uuid.uuid4())
        task_info = {
            "id": task_id,
            "type": task_type.value,
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "data": task_data,
            "result": None,
            "error": None,
            "progress": 0
        }
        
        # 存储任务信息到Redis
        self.redis_conn.hset(f"task:{task_id}", mapping=task_info)
        
        # 将任务加入队列
        job = self.queue.enqueue(
            self._execute_task,
            task_id,
            task_type,
            task_data,
            job_timeout='10m',  # 10分钟超时
            result_ttl=3600,    # 结果保存1小时
            failure_ttl=3600    # 失败信息保存1小时
        )
        
        # 更新任务信息
        self.redis_conn.hset(f"task:{task_id}", "job_id", job.id)
        
        return {
            "task_id": task_id,
            "status": TaskStatus.PENDING.value,
            "message": "Task created successfully"
        }
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        if not self.redis_conn:
            return None
        
        task_info = self.redis_conn.hgetall(f"task:{task_id}")
        if not task_info:
            return None
        
        return {
            "task_id": task_id,
            "status": task_info.get("status", TaskStatus.PENDING.value),
            "progress": int(task_info.get("progress", 0)),
            "result": task_info.get("result"),
            "error": task_info.get("error"),
            "created_at": task_info.get("created_at"),
            "completed_at": task_info.get("completed_at")
        }
    
    def update_task_progress(self, task_id: str, progress: int, status: TaskStatus = None):
        """更新任务进度"""
        if not self.redis_conn:
            return
        
        updates = {"progress": progress}
        if status:
            updates["status"] = status.value
            if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                updates["completed_at"] = datetime.now().isoformat()
        
        self.redis_conn.hset(f"task:{task_id}", mapping=updates)
    
    def update_task_result(self, task_id: str, result: Any, status: TaskStatus = TaskStatus.COMPLETED):
        """更新任务结果"""
        if not self.redis_conn:
            return
        
        updates = {
            "result": json.dumps(result) if isinstance(result, (dict, list)) else str(result),
            "status": status.value,
            "completed_at": datetime.now().isoformat()
        }
        
        self.redis_conn.hset(f"task:{task_id}", mapping=updates)
    
    def update_task_error(self, task_id: str, error: str):
        """更新任务错误信息"""
        if not self.redis_conn:
            return
        
        updates = {
            "error": error,
            "status": TaskStatus.FAILED.value,
            "completed_at": datetime.now().isoformat()
        }
        
        self.redis_conn.hset(f"task:{task_id}", mapping=updates)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if not self.redis_conn:
            return False
        
        task_info = self.redis_conn.hgetall(f"task:{task_id}")
        if not task_info:
            return False
        
        status = task_info.get("status")
        if status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]:
            return False
        
        # 更新状态为取消
        self.redis_conn.hset(f"task:{task_id}", "status", TaskStatus.CANCELLED.value)
        
        # 尝试取消RQ任务
        job_id = task_info.get("job_id")
        if job_id and self.queue:
            job = rq.job.Job.fetch(job_id, connection=self.redis_conn)
            if job and job.get_status() in ['queued', 'started']:
                job.cancel()
        
        return True
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        if not self.queue:
            return {"error": "Queue not available"}
        
        return {
            "pending": len(self.queue),
            "failed": len(self.failed_queue) if self.failed_queue else 0,
            "workers": len(self.queue.workers),
            "total_tasks": self.redis_conn.dbsize() if self.redis_conn else 0
        }
    
    def cleanup_old_tasks(self, days: int = 7):
        """清理旧任务"""
        if not self.redis_conn:
            return
        
        cutoff_date = datetime.now() - timedelta(days=days)
        pattern = "task:*"
        
        for key in self.redis_conn.scan_iter(match=pattern):
            task_info = self.redis_conn.hgetall(key)
            created_at = task_info.get("created_at")
            if created_at:
                try:
                    task_date = datetime.fromisoformat(created_at)
                    if task_date < cutoff_date:
                        self.redis_conn.delete(key)
                        print(f"[TASK_QUEUE] Cleaned up old task: {key}")
                except:
                    pass
    
    def _execute_task(self, task_id: str, task_type: TaskType, task_data: Dict[str, Any]):
        """执行任务的具体逻辑"""
        try:
            # 更新任务状态为运行中
            self.update_task_progress(task_id, 10, TaskStatus.RUNNING)
            
            # 根据任务类型执行不同的逻辑
            if task_type == TaskType.AUDIO_GENERATION:
                result = self._execute_audio_generation(task_id, task_data)
            elif task_type == TaskType.MUSIC_GENERATION:
                result = self._execute_music_generation(task_id, task_data)
            elif task_type == TaskType.STORY_GENERATION:
                result = self._execute_story_generation(task_id, task_data)
            elif task_type == TaskType.IMAGE_GENERATION:
                result = self._execute_image_generation(task_id, task_data)
            elif task_type == TaskType.TTS_GENERATION:
                result = self._execute_tts_generation(task_id, task_data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            # 更新任务完成
            self.update_task_progress(task_id, 100, TaskStatus.COMPLETED)
            self.update_task_result(task_id, result)
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"[TASK_QUEUE] Task {task_id} failed: {error_msg}")
            self.update_task_error(task_id, error_msg)
            raise
    
    def _execute_audio_generation(self, task_id: str, task_data: Dict[str, Any]):
        """执行音频生成任务"""
        from .audio_service import AudioGenerationService
        
        self.update_task_progress(task_id, 20)
        
        audio_service = AudioGenerationService()
        description = task_data.get("description", "")
        duration = task_data.get("duration", 20)
        mode = task_data.get("mode", "default")
        
        self.update_task_progress(task_id, 40)
        
        # 调用现有的音频生成逻辑
        audio_url = await audio_service.generate_audio(description, duration, mode=mode)
        
        self.update_task_progress(task_id, 80)
        
        return {
            "audio_url": audio_url,
            "description": description,
            "duration": duration,
            "mode": mode
        }
    
    def _execute_music_generation(self, task_id: str, task_data: Dict[str, Any]):
        """执行音乐生成任务"""
        from .audio_service import AudioGenerationService
        
        self.update_task_progress(task_id, 20)
        
        audio_service = AudioGenerationService()
        description = task_data.get("description", "")
        duration = task_data.get("duration", 30)
        
        self.update_task_progress(task_id, 40)
        
        # 调用现有的音乐生成逻辑
        music_url = await audio_service.generate_music(description, duration)
        
        self.update_task_progress(task_id, 80)
        
        return {
            "music_url": music_url,
            "description": description,
            "duration": duration
        }
    
    def _execute_story_generation(self, task_id: str, task_data: Dict[str, Any]):
        """执行故事生成任务"""
        # 这里可以调用现有的故事生成逻辑
        self.update_task_progress(task_id, 50)
        
        # 模拟故事生成
        story_content = task_data.get("prompt", "")
        
        return {
            "story_content": story_content,
            "audio_url": None  # 可以后续生成
        }
    
    def _execute_image_generation(self, task_id: str, task_data: Dict[str, Any]):
        """执行图片生成任务"""
        from .image_service import ImageGenerationService
        
        self.update_task_progress(task_id, 20)
        
        image_service = ImageGenerationService()
        description = task_data.get("description", "")
        
        self.update_task_progress(task_id, 40)
        
        # 调用现有的图片生成逻辑
        image_url = await image_service.generate_background(description)
        
        self.update_task_progress(task_id, 80)
        
        return {
            "image_url": image_url,
            "description": description
        }
    
    def _execute_tts_generation(self, task_id: str, task_data: Dict[str, Any]):
        """执行TTS生成任务"""
        from .audio_service import tts_to_audio
        
        self.update_task_progress(task_id, 20)
        
        text = task_data.get("text", "")
        voice = task_data.get("voice", "en-US-AriaNeural")
        
        self.update_task_progress(task_id, 40)
        
        # 调用现有的TTS逻辑
        audio_url = await tts_to_audio(text, voice)
        
        self.update_task_progress(task_id, 80)
        
        return {
            "audio_url": audio_url,
            "text": text,
            "voice": voice
        }

# 全局任务队列服务实例
task_queue_service = TaskQueueService() 