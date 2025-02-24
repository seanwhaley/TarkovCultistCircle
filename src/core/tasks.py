"""Background task management using thread pool."""
import logging
from typing import Any, Callable, Dict, Optional
import uuid
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from threading import Lock
from functools import wraps
from flask import current_app

logger = logging.getLogger(__name__)

@dataclass
class TaskResult:
    """Task result container."""
    task_id: str
    status: str
    result: Any = None
    error: Optional[str] = None
    started_at: datetime = None
    completed_at: Optional[datetime] = None

class TaskManager:
    """Manager for background tasks using thread pool."""
    
    def __init__(self, max_workers: int = 3):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._results: Dict[str, TaskResult] = {}
        self._lock = Lock()
        
    def create_task(
        self,
        name: str,
        func: Callable,
        *args: Any,
        **kwargs: Any
    ) -> str:
        """Create and start a new background task."""
        task_id = str(uuid.uuid4())
        
        def wrapped_func():
            with self._lock:
                self._results[task_id] = TaskResult(
                    task_id=task_id,
                    status="running",
                    started_at=datetime.utcnow()
                )
            
            try:
                result = func(*args, **kwargs)
                with self._lock:
                    self._results[task_id] = TaskResult(
                        task_id=task_id,
                        status="completed",
                        result=result,
                        started_at=self._results[task_id].started_at,
                        completed_at=datetime.utcnow()
                    )
                return result
            except Exception as e:
                logger.exception(f"Task {task_id} failed")
                with self._lock:
                    self._results[task_id] = TaskResult(
                        task_id=task_id,
                        status="failed",
                        error=str(e),
                        started_at=self._results[task_id].started_at,
                        completed_at=datetime.utcnow()
                    )
                raise
        
        self._executor.submit(wrapped_func)
        return task_id
        
    def get_task_info(self, task_id: str) -> Optional[TaskResult]:
        """Get current task information."""
        with self._lock:
            return self._results.get(task_id)
            
    def cleanup_old_tasks(self, max_age_hours: int = 24) -> None:
        """Remove old task results."""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        with self._lock:
            self._results = {
                task_id: result 
                for task_id, result in self._results.items()
                if not result.completed_at or result.completed_at > cutoff
            }

def background_task(name: Optional[str] = None):
    """Decorator to run a function as a background task."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            task_name = name or f.__name__
            task_manager = current_app.config.get('task_manager')
            if not task_manager:
                task_manager = TaskManager()
                current_app.config['task_manager'] = task_manager
            return task_manager.create_task(task_name, f, *args, **kwargs)
        return wrapped
    return decorator

# Default task manager instance
task_manager = TaskManager()