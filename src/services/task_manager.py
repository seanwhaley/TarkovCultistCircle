"""Task management for background processing."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import asyncio
import structlog
from collections import deque

from src.core.logging import get_logger
from src.models.item import Item

logger = get_logger(__name__)

class TaskResult(BaseModel):
    """Task result model."""
    task_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
    completed_at: Optional[datetime] = None

class TaskQueue:
    """Async task queue manager."""
    
    def __init__(self, max_concurrent: int = 3):
        self.queue = deque()
        self.results = {}
        self.max_concurrent = max_concurrent
        self.running = set()
        self._workers = []

    async def start(self):
        """Start task queue workers."""
        self._workers = [
            asyncio.create_task(self._worker())
            for _ in range(self.max_concurrent)
        ]

    async def stop(self):
        """Stop all workers."""
        for worker in self._workers:
            worker.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()

    async def _worker(self):
        """Worker process to handle queued tasks."""
        while True:
            try:
                if not self.queue:
                    await asyncio.sleep(0.1)
                    continue

                task_id, coro = self.queue.popleft()
                self.running.add(task_id)

                try:
                    result = await coro
                    self.results[task_id] = TaskResult(
                        task_id=task_id,
                        status="completed",
                        result=result,
                        completed_at=datetime.utcnow()
                    )
                except Exception as e:
                    logger.exception("Task failed", task_id=task_id)
                    self.results[task_id] = TaskResult(
                        task_id=task_id,
                        status="failed",
                        error=str(e),
                        completed_at=datetime.utcnow()
                    )
                finally:
                    self.running.remove(task_id)

            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Worker error")
                await asyncio.sleep(1)

    async def enqueue(self, task_id: str, coro) -> None:
        """Add a task to the queue."""
        self.queue.append((task_id, coro))
        logger.info("Task enqueued", task_id=task_id)

    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """Get the result of a task."""
        return self.results.get(task_id)

# Global task queue instance
task_queue = TaskQueue()