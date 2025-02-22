import logging
from typing import Callable

from fastapi import FastAPI
from redis.asyncio import Redis

from src.core.config import Settings
from src.core.database import DatabaseManager
from src.core.redis import RedisManager
from src.core.tasks import TaskManager

logger = logging.getLogger(__name__)

async def startup_handler(app: FastAPI, settings: Settings) -> None:
    """Initialize application services on startup."""
    try:
        # Initialize database
        await DatabaseManager.initialize(settings)
        logger.info("Database connection initialized")

        # Initialize Redis
        await RedisManager.initialize(settings)
        redis = await RedisManager.get_redis()
        logger.info("Redis connection initialized")

        # Store Redis instance and task manager in app state
        app.state.redis = redis
        app.state.task_manager = TaskManager(redis)
        logger.info("Task manager initialized")

    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise

async def shutdown_handler(app: FastAPI) -> None:
    """Cleanup application resources on shutdown."""
    try:
        # Close database connections
        await DatabaseManager.close()
        logger.info("Database connections closed")

        # Close Redis connections
        await RedisManager.close()
        logger.info("Redis connections closed")

    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
        raise

def create_start_app_handler(
    app: FastAPI,
    settings: Settings
) -> Callable:
    """Create startup event handler."""
    async def start_app() -> None:
        await startup_handler(app, settings)
    return start_app

def create_stop_app_handler(app: FastAPI) -> Callable:
    """Create shutdown event handler."""
    async def stop_app() -> None:
        await shutdown_handler(app)
    return stop_app