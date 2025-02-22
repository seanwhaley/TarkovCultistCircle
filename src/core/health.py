from datetime import datetime
import logging
from typing import Dict, List, Optional

from src.core.database import DatabaseManager
from src.core.redis import RedisManager
from src.core.config import Settings

logger = logging.getLogger(__name__)

class HealthCheck:
    """Health check service for monitoring system components."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._status_cache: Dict[str, dict] = {}
        self._cache_time: Optional[datetime] = None
        self._cache_duration = 60  # Cache health results for 60 seconds

    async def check_database(self) -> dict:
        """Check Neo4j database health."""
        try:
            is_healthy = await DatabaseManager.health_check()
            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "message": "Connected to Neo4j" if is_healthy else "Database connection failed"
            }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Database error: {str(e)}"
            }

    async def check_redis(self) -> dict:
        """Check Redis health."""
        try:
            redis = await RedisManager.get_redis()
            await redis.ping()
            return {
                "status": "healthy",
                "message": "Connected to Redis"
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Redis error: {str(e)}"
            }

    async def check_memory(self) -> dict:
        """Check system memory usage."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                "status": "healthy" if memory.percent < 90 else "warning",
                "message": f"Memory usage: {memory.percent}%",
                "details": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                }
            }
        except Exception as e:
            logger.error(f"Memory check failed: {str(e)}")
            return {
                "status": "unknown",
                "message": f"Memory check error: {str(e)}"
            }

    async def check_disk(self) -> dict:
        """Check disk usage."""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            return {
                "status": "healthy" if disk.percent < 90 else "warning",
                "message": f"Disk usage: {disk.percent}%",
                "details": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                }
            }
        except Exception as e:
            logger.error(f"Disk check failed: {str(e)}")
            return {
                "status": "unknown",
                "message": f"Disk check error: {str(e)}"
            }

    def _should_refresh_cache(self) -> bool:
        """Check if health cache should be refreshed."""
        if not self._cache_time:
            return True
        return (datetime.now() - self._cache_time).total_seconds() > self._cache_duration

    async def get_health_status(self, force_refresh: bool = False) -> dict:
        """
        Get complete health status of all components.
        
        Args:
            force_refresh: Force refresh of cached results
        """
        if not force_refresh and not self._should_refresh_cache():
            return self._status_cache

        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "components": {
                "database": await self.check_database(),
                "redis": await self.check_redis(),
                "system": {
                    "memory": await self.check_memory(),
                    "disk": await self.check_disk()
                }
            }
        }

        # Update overall status based on components
        components = [
            status["components"]["database"],
            status["components"]["redis"],
            status["components"]["system"]["memory"],
            status["components"]["system"]["disk"]
        ]

        if any(c["status"] == "unhealthy" for c in components):
            status["status"] = "unhealthy"
        elif any(c["status"] == "warning" for c in components):
            status["status"] = "warning"

        # Cache results
        self._status_cache = status
        self._cache_time = datetime.now()

        return status

    async def get_component_status(self, component: str) -> dict:
        """Get health status of a specific component."""
        status = await self.get_health_status()
        if component == "database":
            return status["components"]["database"]
        elif component == "redis":
            return status["components"]["redis"]
        elif component == "memory":
            return status["components"]["system"]["memory"]
        elif component == "disk":
            return status["components"]["system"]["disk"]
        else:
            raise ValueError(f"Unknown component: {component}")

    def get_unhealthy_components(self) -> List[str]:
        """Get list of unhealthy components."""
        unhealthy = []
        for component, status in self._status_cache.get("components", {}).items():
            if isinstance(status, dict) and status.get("status") == "unhealthy":
                unhealthy.append(component)
            elif isinstance(status, dict):
                for subcomp, substatus in status.items():
                    if isinstance(substatus, dict) and substatus.get("status") == "unhealthy":
                        unhealthy.append(f"{component}.{subcomp}")
        return unhealthy