"""Background task management using in-memory queue."""
import logging
from typing import Any, Callable, Dict, Optional
import uuid
from datetime import datetime

from fastapi import BackgroundTasks

from src.services.task_manager import task_queue, TaskResult

logger = logging.getLogger(__name__)

class TaskManager:
    """Manager for background tasks using in-memory queue."""

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

        # Create wrapped coroutine with args
        async def wrapped_coro():
            return await coro(*args, **kwargs)

        # Enqueue the task
        await task_queue.enqueue(task_id, wrapped_coro())
        
        return task_id

    async def get_task_info(self, task_id: str) -> Dict[str, Any]:
        """Get current task information."""
        result = task_queue.get_result(task_id)
        
        if not result:
            if task_id in task_queue.running:
                return {
                    "id": task_id,
                    "status": "running",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "progress": 0,
                    "result": None,
                    "error": None
                }
            raise ValueError(f"Task {task_id} not found")

        return {
            "id": task_id,
            "status": result.status,
            "created_at": result.created_at.isoformat() if result.created_at else None,
            "completed_at": result.completed_at.isoformat() if result.completed_at else None,
            "result": result.result,
            "error": result.error
        }

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task if possible."""
        if task_id in task_queue.running:
            # Note: Current implementation doesn't support cancellation
            # Could be added by storing Task objects and calling cancel()
            return False
        return False

# Global task manager instance
task_manager = TaskManager()