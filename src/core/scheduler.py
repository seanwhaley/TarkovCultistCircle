"""Task scheduling using APScheduler with in-memory storage."""
from datetime import datetime
import logging
from typing import Any, Callable, Dict, List, Optional
import uuid
import asyncio

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.core.config import Settings
from src.core.cache import cache
from src.core.exceptions import AppException
from src.core.database import DatabaseManager

logger = logging.getLogger(__name__)

class SchedulerManager:
    """Manager for scheduled tasks."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.scheduler = BackgroundScheduler()
        self._setup_jobs()

    def _setup_jobs(self) -> None:
        """Setup scheduled jobs."""
        # Database maintenance - daily at 3 AM
        self.scheduler.add_job(
            self._database_maintenance,
            CronTrigger(hour=3),
            id='database_maintenance',
            replace_existing=True
        )
        
        # Market data update - every 5 minutes
        self.scheduler.add_job(
            self._update_market_data,
            IntervalTrigger(minutes=5),
            id='market_data_update',
            replace_existing=True
        )
        
        # Cache cleanup - every hour
        self.scheduler.add_job(
            self._cleanup_cache,
            IntervalTrigger(hours=1),
            id='cache_cleanup',
            replace_existing=True
        )

    def _database_maintenance(self) -> None:
        """Run database maintenance tasks."""
        try:
            with DatabaseManager.get_session() as session:
                # Run Neo4j maintenance queries
                session.run("CALL db.stats()")
                session.run("CALL db.indexes()")
                session.run("CALL db.constraints()")
                session.run("CALL db.clearQueryCaches()")
            logger.info("Database maintenance completed")
        except Exception as e:
            logger.error(f"Database maintenance failed: {str(e)}")

    def _update_market_data(self) -> None:
        """Update market data from external sources."""
        try:
            from src.services.market_service import MarketService
            service = MarketService()
            service.update_market_data()
            logger.info("Market data updated successfully")
        except Exception as e:
            logger.error(f"Market data update failed: {str(e)}")

    def _cleanup_cache(self) -> None:
        """Clean up expired cache entries."""
        try:
            cache._cleanup()
            logger.info("Cache cleanup completed")
        except Exception as e:
            logger.error(f"Cache cleanup failed: {str(e)}")

    def add_job(
        self,
        func: Callable,
        trigger: str,
        **trigger_args: Any
    ) -> str:
        """Add a new scheduled job."""
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

    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job."""
        try:
            self.scheduler.remove_job(job_id)
            return True
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {str(e)}")
            return False

    def get_jobs(self) -> List[Dict[str, Any]]:
        """Get list of all scheduled jobs."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time,
                'trigger': str(job.trigger)
            })
        return jobs

    def start(self) -> None:
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def stop(self) -> None:
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")