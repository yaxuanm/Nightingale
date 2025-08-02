import asyncio
import threading
import time
import uuid
import json
import os
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from collections import deque
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

class AsyncTaskService:
    def __init__(self, max_concurrent_tasks: int = 3, max_queue_size: int = 50):
        # 内存中的任务存储（可以后续改为Redis）
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.task_handlers: Dict[TaskType, Callable] = {}
        
        # 队列管理
        self.task_queue = deque()  # 待处理任务队列
        self.running_tasks: Dict[str, Dict[str, Any]] = {}  # 正在运行的任务
        self.max_concurrent_tasks = max_concurrent_tasks
        self.max_queue_size = max_queue_size
        
        # 用户会话管理
        self.user_sessions: Dict[str, List[str]] = {}  # 用户ID -> 任务ID列表
        
        # 队列锁
        self.queue_lock = threading.Lock()
        self.running_lock = threading.Lock()
        
        # 注册任务处理器
        self._register_handlers()
        
        # 启动队列处理器
        self._start_queue_processor()
        
        # 清理旧任务的定时器
        self._start_cleanup_timer()
        
        logger.info(f"AsyncTaskService initialized with max_concurrent_tasks={max_concurrent_tasks}")
    
    def _register_handlers(self):
        """注册各种任务类型的处理器"""
        self.task_handlers[TaskType.AUDIO_GENERATION] = self._handle_audio_generation
        self.task_handlers[TaskType.MUSIC_GENERATION] = self._handle_music_generation
        self.task_handlers[TaskType.STORY_GENERATION] = self._handle_story_generation
        self.task_handlers[TaskType.IMAGE_GENERATION] = self._handle_image_generation
        self.task_handlers[TaskType.TTS_GENERATION] = self._handle_tts_generation
    
    def create_task(self, task_type: TaskType, task_data: Dict[str, Any], 
                   user_id: str = None, priority: TaskPriority = TaskPriority.NORMAL) -> Dict[str, Any]:
        """创建新任务并加入队列"""
        task_id = str(uuid.uuid4())
        user_id = user_id or "anonymous"
        
        # 检查队列是否已满
        with self.queue_lock:
            if len(self.task_queue) >= self.max_queue_size:
                return {
                    "error": "Queue is full. Please try again later.",
                    "queue_size": len(self.task_queue),
                    "max_queue_size": self.max_queue_size
                }
        
        task_info = {
            "id": task_id,
            "type": task_type.value,
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "data": task_data,
            "result": None,
            "error": None,
            "progress": 0,
            "done": False,
            "user_id": user_id,
            "priority": priority.value,
            "queue_position": 0
        }
        
        # 存储任务信息
        self.tasks[task_id] = task_info
        
        # 添加到用户会话
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
        self.user_sessions[user_id].append(task_id)
        
        # 加入队列
        with self.queue_lock:
            self.task_queue.append({
                "task_id": task_id,
                "priority": priority.value,
                "created_at": datetime.now()
            })
            # 更新队列位置
            task_info["queue_position"] = len(self.task_queue)
        
        logger.info(f"Task {task_id} created for user {user_id}, queue position: {task_info['queue_position']}")
        
        return {
            "task_id": task_id,
            "status": TaskStatus.PENDING.value,
            "message": "Task created successfully",
            "queue_position": task_info["queue_position"],
            "estimated_wait_time": self._estimate_wait_time()
        }
    
    def get_task_status(self, task_id: str, user_id: str = None) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        task_info = self.tasks.get(task_id)
        if not task_info:
            return None
        
        # 检查用户权限（如果指定了用户ID）
        if user_id and task_info.get("user_id") != user_id:
            return {"error": "Access denied"}
        
        # 计算队列位置
        queue_position = 0
        with self.queue_lock:
            for i, queue_item in enumerate(self.task_queue):
                if queue_item["task_id"] == task_id:
                    queue_position = i + 1
                    break
        
        return {
            "task_id": task_id,
            "status": task_info.get("status", TaskStatus.PENDING.value),
            "progress": task_info.get("progress", 0),
            "result": task_info.get("result"),
            "error": task_info.get("error"),
            "created_at": task_info.get("created_at"),
            "completed_at": task_info.get("completed_at"),
            "done": task_info.get("done", False),
            "queue_position": queue_position,
            "user_id": task_info.get("user_id")
        }
    
    def get_user_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户的所有任务"""
        user_task_ids = self.user_sessions.get(user_id, [])
        tasks = []
        
        for task_id in user_task_ids:
            task_status = self.get_task_status(task_id, user_id)
            if task_status and "error" not in task_status:
                tasks.append(task_status)
        
        return tasks
    
    def cancel_task(self, task_id: str, user_id: str = None) -> Dict[str, Any]:
        """取消任务"""
        task_info = self.tasks.get(task_id)
        if not task_info:
            return {"success": False, "error": "Task not found"}
        
        # 检查用户权限
        if user_id and task_info.get("user_id") != user_id:
            return {"success": False, "error": "Access denied"}
        
        status = task_info.get("status")
        if status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value, TaskStatus.CANCELLED.value]:
            return {"success": False, "error": f"Task is already {status}"}
        
        # 更新任务状态
        task_info["status"] = TaskStatus.CANCELLED.value
        task_info["completed_at"] = datetime.now().isoformat()
        task_info["done"] = True
        
        # 从队列中移除
        with self.queue_lock:
            self.task_queue = deque([item for item in self.task_queue if item["task_id"] != task_id])
        
        # 从运行中移除
        with self.running_lock:
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
        
        logger.info(f"Task {task_id} cancelled by user {user_id}")
        
        return {"success": True, "message": "Task cancelled successfully"}
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        with self.queue_lock:
            queue_size = len(self.task_queue)
        
        with self.running_lock:
            running_count = len(self.running_tasks)
        
        # 统计各状态的任务数量
        status_counts = {
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0
        }
        
        for task_info in self.tasks.values():
            status = task_info.get("status", "pending")
            if status in status_counts:
                status_counts[status] += 1
        
        return {
            "total": len(self.tasks),
            "pending": status_counts["pending"],
            "running": status_counts["running"],
            "completed": status_counts["completed"],
            "failed": status_counts["failed"],
            "cancelled": status_counts["cancelled"],
            "queue_size": queue_size,
            "running_count": running_count,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "max_queue_size": self.max_queue_size,
            "estimated_wait_time": self._estimate_wait_time()
        }
    
    def _estimate_wait_time(self) -> int:
        """估算等待时间（分钟）"""
        with self.queue_lock:
            queue_size = len(self.task_queue)
        
        # 假设每个任务平均需要2分钟
        avg_task_time = 2  # 分钟
        return queue_size * avg_task_time
    
    def _start_queue_processor(self):
        """启动队列处理器"""
        def process_queue():
            while True:
                try:
                    # 检查是否可以启动新任务
                    with self.running_lock:
                        if len(self.running_tasks) >= self.max_concurrent_tasks:
                            time.sleep(0.5)
                            continue
                    
                    # 获取下一个任务
                    with self.queue_lock:
                        if not self.task_queue:
                            time.sleep(0.5)
                            continue
                        
                        # 按优先级排序，先进先出
                        queue_item = self.task_queue.popleft()
                        task_id = queue_item["task_id"]
                    
                    # 获取任务信息
                    task_info = self.tasks.get(task_id)
                    if not task_info:
                        continue
                    
                    # 检查任务是否已被取消
                    if task_info.get("status") == TaskStatus.CANCELLED.value:
                        continue
                    
                    # 启动任务
                    with self.running_lock:
                        self.running_tasks[task_id] = task_info
                    
                    # 异步执行任务
                    threading.Thread(
                        target=lambda: asyncio.run(self._execute_task(task_id, TaskType(task_info["type"]), task_info["data"])),
                        daemon=True
                    ).start()
                    
                    logger.info(f"Started task {task_id} from queue")
                    
                except Exception as e:
                    logger.error(f"Error in queue processor: {e}")
                    time.sleep(0.5)
        
        # 启动队列处理器线程
        threading.Thread(target=process_queue, daemon=True).start()
        logger.info("Queue processor started")
    
    async def _execute_task(self, task_id: str, task_type: TaskType, task_data: Dict[str, Any]):
        """执行任务"""
        task_info = self.tasks.get(task_id)
        if not task_info:
            return
        
        try:
            # 更新状态为运行中
            task_info["status"] = TaskStatus.RUNNING.value
            task_info["progress"] = 0
            
            logger.info(f"Executing task {task_id} of type {task_type.value}")
            
            # 获取对应的处理器
            handler = self.task_handlers.get(task_type)
            if not handler:
                raise Exception(f"No handler found for task type: {task_type.value}")
            
            # 执行任务
            result = await handler(task_id, task_data)
            
            # 更新任务完成状态
            task_info["status"] = TaskStatus.COMPLETED.value
            task_info["result"] = result
            task_info["progress"] = 100
            task_info["completed_at"] = datetime.now().isoformat()
            task_info["done"] = True
            
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            # 更新任务失败状态
            task_info["status"] = TaskStatus.FAILED.value
            task_info["error"] = str(e)
            task_info["completed_at"] = datetime.now().isoformat()
            task_info["done"] = True
            
            logger.error(f"Task {task_id} failed: {e}")
        
        finally:
            # 从运行中移除
            with self.running_lock:
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
    
    async def _handle_audio_generation(self, task_id: str, task_data: Dict[str, Any]):
        """处理音频生成任务"""
        try:
            # 模拟进度更新
            task_info = self.tasks.get(task_id)
            if task_info:
                task_info["progress"] = 20
            
            # 调用8001端口的Stable Audio服务
            import aiohttp
            
            description = task_data.get("description", "")
            duration = task_data.get("duration", 20)
            mode = task_data.get("mode", "default")
            
            # 更新进度
            if task_info:
                task_info["progress"] = 40
            
            # 调用8001端口的音频生成API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'http://localhost:8001/api/generate-audio',
                    json={
                        "description": description,
                        "duration": duration,
                        "mode": mode
                    }
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Audio generation API failed: {error_text}")
                    
                    audio_result = await response.json()
                    audio_url = audio_result.get("audio_url")
                    
                    if not audio_url:
                        raise Exception("No audio URL returned from API")
                    
                    # 更新进度
                    if task_info:
                        task_info["progress"] = 80
                    
                    return {
                        "audio_url": audio_url,
                        "description": description,
                        "duration": duration,
                        "mode": mode
                    }
            
        except Exception as e:
            logger.error(f"Audio generation failed for task {task_id}: {e}")
            raise
    
    async def _handle_music_generation(self, task_id: str, task_data: Dict[str, Any]):
        """处理音乐生成任务"""
        try:
            # 模拟进度更新
            task_info = self.tasks.get(task_id)
            if task_info:
                task_info["progress"] = 30
            
            # 调用8001端口的Stable Audio服务
            import aiohttp
            
            description = task_data.get("description", "")
            duration = task_data.get("duration", 20)
            mode = task_data.get("mode", "default")
            
            # 更新进度
            if task_info:
                task_info["progress"] = 60
            
            # 调用8001端口的音频生成API（音乐也用音频生成）
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'http://localhost:8001/api/generate-audio',
                    json={
                        "description": description,
                        "duration": duration,
                        "mode": mode
                    }
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Music generation API failed: {error_text}")
                    
                    music_result = await response.json()
                    music_url = music_result.get("audio_url")
                    
                    if not music_url:
                        raise Exception("No music URL returned from API")
                    
                    return {
                        "music_url": music_url,
                        "description": description,
                        "duration": duration,
                        "mode": mode
                    }
            
        except Exception as e:
            logger.error(f"Music generation failed for task {task_id}: {e}")
            raise
    
    async def _handle_story_generation(self, task_id: str, task_data: Dict[str, Any]):
        """处理故事生成任务"""
        try:
            # 模拟进度更新
            task_info = self.tasks.get(task_id)
            if task_info:
                task_info["progress"] = 20
            
            # 直接调用8000端口的create-story API，但确保它调用8001端口的音频生成
            import aiohttp
            
            prompt = task_data.get("prompt", "")
            original_description = task_data.get("original_description", "")
            duration = task_data.get("duration", 20)
            
            # 更新进度
            if task_info:
                task_info["progress"] = 40
            
            # 调用8000端口的create-story API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'http://localhost:8000/api/create-story',
                    json={
                        "prompt": prompt,
                        "original_description": original_description,
                        "duration": duration
                    }
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Story generation API failed: {error_text}")
                    
                    story_result = await response.json()
                    
                    # 更新进度
                    if task_info:
                        task_info["progress"] = 60
                    
                    # 同时生成图片
                    from app.services.image_service import image_service
                    image_url = await image_service.generate_background(original_description)
                    
                    # 更新进度
                    if task_info:
                        task_info["progress"] = 80
                    
                    # 生成背景音乐（使用Stable Audio）
                    async with session.post(
                        'http://localhost:8001/api/generate-audio',
                        json={
                            "description": f"Background music for story: {original_description}",
                            "duration": duration,
                            "mode": "music"
                        }
                    ) as music_response:
                        if music_response.status != 200:
                            print(f"Warning: Music generation failed, continuing without music")
                            music_url = None
                        else:
                            music_result = await music_response.json()
                            music_url = music_result.get("audio_url")
                    
                    return {
                        "audio_url": story_result.get("audio_url"),
                        "background_image_url": image_url,
                        "music_url": music_url,
                        "narrative_script": story_result.get("narrative_script"),
                        "description": original_description
                    }
            
        except Exception as e:
            logger.error(f"Story generation failed for task {task_id}: {e}")
            raise
    
    async def _handle_image_generation(self, task_id: str, task_data: Dict[str, Any]):
        """处理图片生成任务"""
        try:
            # 模拟进度更新
            task_info = self.tasks.get(task_id)
            if task_info:
                task_info["progress"] = 35
            
            # 调用现有的图片生成服务
            from app.services.image_service import image_service
            
            description = task_data.get("description", "")
            
            # 更新进度
            if task_info:
                task_info["progress"] = 70
            
            # 生成图片
            image_url = await image_service.generate_background(description)
            
            return {
                "image_url": image_url,
                "description": description
            }
            
        except Exception as e:
            logger.error(f"Image generation failed for task {task_id}: {e}")
            raise
    
    async def _handle_tts_generation(self, task_id: str, task_data: Dict[str, Any]):
        """处理TTS生成任务"""
        try:
            # 模拟进度更新
            task_info = self.tasks.get(task_id)
            if task_info:
                task_info["progress"] = 30
            
            # 调用现有的TTS服务
            from app.services.audio_service import audio_service
            
            text = task_data.get("text", "")
            voice = task_data.get("voice", "default")
            
            # 更新进度
            if task_info:
                task_info["progress"] = 60
            
            # 生成TTS
            tts_url = await audio_service.tts_to_audio(text, voice)
            
            return {
                "tts_url": tts_url,
                "text": text,
                "voice": voice
            }
            
        except Exception as e:
            logger.error(f"TTS generation failed for task {task_id}: {e}")
            raise
    
    def _start_cleanup_timer(self):
        """启动清理定时器"""
        def cleanup_old_tasks():
            while True:
                try:
                    # 清理24小时前的已完成任务
                    cutoff_time = datetime.now() - timedelta(hours=24)
                    
                    tasks_to_remove = []
                    for task_id, task_info in self.tasks.items():
                        if task_info.get("done", False):
                            completed_at = task_info.get("completed_at")
                            if completed_at:
                                try:
                                    completed_time = datetime.fromisoformat(completed_at)
                                    if completed_time < cutoff_time:
                                        tasks_to_remove.append(task_id)
                                except:
                                    pass
                    
                    # 移除旧任务
                    for task_id in tasks_to_remove:
                        del self.tasks[task_id]
                        logger.info(f"Cleaned up old task: {task_id}")
                    
                    # 每小时清理一次
                    time.sleep(3600)
                    
                except Exception as e:
                    logger.error(f"Error in cleanup timer: {e}")
                    time.sleep(3600)
        
        threading.Thread(target=cleanup_old_tasks, daemon=True).start()
        logger.info("Cleanup timer started")

# 创建全局实例
async_task_service = AsyncTaskService() 