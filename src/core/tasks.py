import asyncio
from datetime import datetime
import logging
from typing import Any, Callable, Dict, Optional
import uuid

from fastapi import BackgroundTasks
from redis.asyncio import Redis

from src.core.redis import RedisManager

logger = logging.getLogger(__name__)

class TaskManager:
    """Manager for background tasks with Redis-based state tracking."""
    
    def __init__(self, redis: Redis):
        self.redis = redis
        self.key_prefix = "task:"
        self.default_timeout = 3600  # 1 hour

    async def create_task(
        self,
        name: str,
        coro: Callable,
        *args: Any,
        **kwargs: Any
    ) -> str:
        """
        Create and start a new background task.
        
        Args:
            name: Task name for identification
            coro: Coroutine to execute
            args: Positional arguments for the coroutine
            kwargs: Keyword arguments for the coroutine
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        key = f"{self.key_prefix}{task_id}"
        
        # Store initial task state
        task_info = {
            "id": task_id,
            "name": name,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "progress": 0,
            "result": None,
            "error": None
        }
        
        await self.redis.hset(key, mapping=task_info)
        await self.redis.expire(key, self.default_timeout)
        
        # Create and start the task
        background_task = asyncio.create_task(
            self._run_task(task_id, coro, *args, **kwargs)
        )
        
        # Store task reference
        task_info["_task"] = background_task
        
        return task_id

    async def _run_task(
        self,
        task_id: str,
        coro: Callable,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """Execute the task and update its state."""
        key = f"{self.key_prefix}{task_id}"
        
        try:
            # Update task status to running
            await self._update_task_status(task_id, "running")
            
            # Execute the coroutine
            result = await coro(*args, **kwargs)
            
            # Store successful result
            await self.redis.hset(key, "result", str(result))
            await self._update_task_status(task_id, "completed")
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {str(e)}")
            # Store error information
            await self.redis.hset(key, "error", str(e))
            await self._update_task_status(task_id, "failed")
            
        finally:
            # Update completion time
            await self.redis.hset(
                key,
                "updated_at",
                datetime.utcnow().isoformat()
            )

    async def _update_task_status(
        self,
        task_id: str,
        status: str,
        progress: Optional[int] = None
    ) -> None:
        """Update task status and progress."""
        key = f"{self.key_prefix}{task_id}"
        
        updates = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
        if progress is not None:
            updates["progress"] = progress
            
        await self.redis.hset(key, mapping=updates)

    async def get_task_info(self, task_id: str) -> Dict[str, Any]:
        """Get current task information."""
        key = f"{self.key_prefix}{task_id}"
        info = await self.redis.hgetall(key)
        
        if not info:
            raise ValueError(f"Task {task_id} not found")
            
        return {
            "id": info[b"id"].decode(),
            "name": info[b"name"].decode(),
            "status": info[b"status"].decode(),
            "created_at": info[b"created_at"].decode(),
            "updated_at": info[b"updated_at"].decode(),
            "progress": int(info[b"progress"]) if b"progress" in info else 0,
            "result": info[b"result"].decode() if b"result" in info else None,
            "error": info[b"error"].decode() if b"error" in info else None
        }

    async def update_progress(
        self,
        task_id: str,
        progress: int
    ) -> None:
        """Update task progress percentage."""
        if not 0 <= progress <= 100:
            raise ValueError("Progress must be between 0 and 100")
            
        await self._update_task_status(task_id, "running", progress)

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        key = f"{self.key_prefix}{task_id}"
        info = await self.redis.hgetall(key)
        
        if not info:
            return False
            
        # Cancel the task if it's still running
        if info[b"status"] == b"running":
            await self._update_task_status(task_id, "cancelled")
            return True
            
        return False

    async def cleanup_old_tasks(self, max_age_seconds: int = 86400) -> int:
        """Clean up completed tasks older than specified age."""
        pattern = f"{self.key_prefix}*"
        count = 0
        
        try:
            keys = await self.redis.keys(pattern)
            now = datetime.utcnow()
            
            for key in keys:
                info = await self.redis.hgetall(key)
                if not info:
                    continue
                    
                created_at = datetime.fromisoformat(info[b"created_at"].decode())
                age = (now - created_at).total_seconds()
                
                if age > max_age_seconds:
                    status = info[b"status"].decode()
                    if status in ("completed", "failed", "cancelled"):
                        await self.redis.delete(key)
                        count += 1
                        
            return count
            
        except Exception as e:
            logger.error(f"Task cleanup error: {str(e)}")
            return 0