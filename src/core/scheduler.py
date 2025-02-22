from datetime import datetime, timedelta
import logging
from typing import Any, Callable, Dict, List, Optional
import asyncio
import uuid

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from redis.asyncio import Redis

from src.core.config import Settings
from src.core.tasks import TaskManager
from src.core.exceptions import AppException

logger = structlog.get_logger(__name__)

class SchedulerManager:
    """Manager for scheduled tasks using APScheduler."""
    
    def __init__(
        self,
        settings: Settings,
        redis: Redis,
        task_manager: TaskManager
    ):
        self.settings = settings
        self.redis = redis
        self.task_manager = task_manager
        self.scheduler = AsyncIOScheduler()
        
        # Configure job stores
        self.scheduler.add_jobstore(
            'redis',
            jobs_key='scheduled_jobs',
            run_times_key='job_runs',
            client=redis
        )

    async def start(self) -> None:
        """Start the scheduler."""
        try:
            # Register default jobs
            await self._register_default_jobs()
            
            # Start scheduler
            self.scheduler.start()
            logger.info("Task scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            raise AppException(f"Scheduler initialization failed: {str(e)}")

    async def stop(self) -> None:
        """Stop the scheduler."""
        try:
            self.scheduler.shutdown()
            logger.info("Task scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")

    async def _register_default_jobs(self) -> None:
        """Register default scheduled jobs."""
        # Market data update job
        self.scheduler.add_job(
            self._update_market_data,
            CronTrigger(minute='*/5'),  # Every 5 minutes
            id='market_data_update',
            replace_existing=True
        )
        
        # Cache cleanup job
        self.scheduler.add_job(
            self._cleanup_cache,
            CronTrigger(hour=3),  # Daily at 3 AM
            id='cache_cleanup',
            replace_existing=True
        )
        
        # Price alert check job
        self.scheduler.add_job(
            self._check_price_alerts,
            IntervalTrigger(minutes=15),  # Every 15 minutes
            id='price_alert_check',
            replace_existing=True
        )
        
        # Metrics rollup job
        self.scheduler.add_job(
            self._rollup_metrics,
            CronTrigger(minute=0),  # Every hour
            id='metrics_rollup',
            replace_existing=True
        )

    async def _update_market_data(self) -> None:
        """Update market data from external sources."""
        try:
            task_id = await self.task_manager.create_task(
                name="market_data_update",
                coro=self._fetch_and_process_market_data
            )
            logger.info(f"Started market data update task: {task_id}")
        except Exception as e:
            logger.error(f"Market data update failed: {str(e)}")

    async def _cleanup_cache(self) -> None:
        """Clean up expired cache entries."""
        try:
            # Find expired cache keys
            pattern = "cache:*"
            keys = await self.redis.keys(pattern)
            
            # Group deletion in batches
            batch_size = 1000
            for i in range(0, len(keys), batch_size):
                batch = keys[i:i + batch_size]
                # Check TTL for each key
                for key in batch:
                    ttl = await self.redis.ttl(key)
                    if ttl < 0:
                        await self.redis.delete(key)
                        
            logger.info("Cache cleanup completed")
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {str(e)}")

    async def _check_price_alerts(self) -> None:
        """Check and trigger price alerts."""
        try:
            # Get all active price alerts
            alerts_key = "price_alerts"
            alerts = await self.redis.hgetall(alerts_key)
            
            for user_id, alerts_data in alerts.items():
                await self._process_user_alerts(
                    user_id.decode(),
                    alerts_data.decode()
                )
                
            logger.info("Price alert check completed")
            
        except Exception as e:
            logger.error(f"Price alert check failed: {str(e)}")

    async def _rollup_metrics(self) -> None:
        """Roll up metrics data for long-term storage."""
        try:
            current_hour = datetime.now().replace(
                minute=0, second=0, microsecond=0
            )
            
            # Get metrics from the last hour
            start_time = int((current_hour - timedelta(hours=1)).timestamp())
            end_time = int(current_hour.timestamp())
            
            # Aggregate metrics
            metrics_key = f"metrics:hourly:{end_time}"
            await self._aggregate_metrics(
                start_time,
                end_time,
                metrics_key
            )
            
            logger.info("Metrics rollup completed")
            
        except Exception as e:
            logger.error(f"Metrics rollup failed: {str(e)}")

    async def add_job(
        self,
        func: Callable,
        trigger: str,
        **trigger_args: Any
    ) -> str:
        """
        Add a new scheduled job.
        
        Args:
            func: Function to execute
            trigger: Trigger type ('date', 'interval', or 'cron')
            trigger_args: Arguments for the trigger
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        try:
            if trigger == 'interval':
                self.scheduler.add_job(
                    func,
                    IntervalTrigger(**trigger_args),
                    id=job_id,
                    replace_existing=True
                )
            elif trigger == 'cron':
                self.scheduler.add_job(
                    func,
                    CronTrigger(**trigger_args),
                    id=job_id,
                    replace_existing=True
                )
            else:
                raise ValueError(f"Unsupported trigger type: {trigger}")
                
            logger.info(f"Added new scheduled job: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to add job: {str(e)}")
            raise AppException(f"Failed to schedule job: {str(e)}")

    async def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job."""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed scheduled job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove job: {str(e)}")
            return False

    async def get_jobs(self) -> List[Dict[str, Any]]:
        """Get list of all scheduled jobs."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "trigger": str(job.trigger),
                "next_run": job.next_run_time.isoformat() 
                    if job.next_run_time else None
            })
        return jobs

    async def pause_job(self, job_id: str) -> bool:
        """Pause a scheduled job."""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Paused job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to pause job: {str(e)}")
            return False

    async def resume_job(self, job_id: str) -> bool:
        """Resume a paused job."""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Resumed job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to resume job: {str(e)}")
            return False