from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import time

from prometheus_client import Counter, Gauge, Histogram, Summary
import structlog
from redis.asyncio import Redis

from src.core.redis import RedisManager

logger = structlog.get_logger(__name__)

# Define metrics
REQUEST_COUNT = Counter(
    'app_request_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

ACTIVE_USERS = Gauge(
    'app_active_users',
    'Number of active users'
)

DB_QUERY_DURATION = Summary(
    'app_db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation']
)

CACHE_HIT_RATIO = Gauge(
    'app_cache_hit_ratio',
    'Cache hit ratio'
)

class MetricsCollector:
    """Collect and store application metrics."""
    
    def __init__(self, redis: Redis):
        self.redis = redis
        self.metrics_key_prefix = "metrics:"
        self.window_size = timedelta(minutes=5)

    async def record_request(
        self,
        method: str,
        endpoint: str,
        status: int,
        duration: float
    ) -> None:
        """Record API request metrics."""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
        
        # Store in Redis for real-time analytics
        timestamp = datetime.now().timestamp()
        key = f"{self.metrics_key_prefix}requests:{int(timestamp/300)}"
        
        await self.redis.hincrby(
            key,
            f"{method}:{endpoint}:{status}",
            1
        )
        await self.redis.expire(key, 86400)  # Expire after 24 hours

    async def record_db_operation(
        self,
        operation: str,
        duration: float
    ) -> None:
        """Record database operation metrics."""
        DB_QUERY_DURATION.labels(operation=operation).observe(duration)

    async def update_active_users(self, count: int) -> None:
        """Update active users gauge."""
        ACTIVE_USERS.set(count)

    async def update_cache_metrics(
        self,
        hits: int,
        misses: int
    ) -> None:
        """Update cache performance metrics."""
        total = hits + misses
        ratio = hits / total if total > 0 else 0
        CACHE_HIT_RATIO.set(ratio)

    async def get_request_stats(
        self,
        minutes: int = 5
    ) -> Dict[str, Dict[str, int]]:
        """Get recent request statistics."""
        now = datetime.now()
        start_time = int((now - timedelta(minutes=minutes)).timestamp() / 300)
        end_time = int(now.timestamp() / 300)
        
        stats: Dict[str, Dict[str, int]] = {}
        
        for time_bucket in range(start_time, end_time + 1):
            key = f"{self.metrics_key_prefix}requests:{time_bucket}"
            data = await self.redis.hgetall(key)
            
            for metric, count in data.items():
                method, endpoint, status = metric.decode().split(":")
                if endpoint not in stats:
                    stats[endpoint] = {}
                stats[endpoint][status] = (
                    stats[endpoint].get(status, 0) + int(count)
                )
                
        return stats

    async def get_performance_stats(
        self,
        minutes: int = 5
    ) -> Dict[str, float]:
        """Get recent performance statistics."""
        # Calculate percentiles from Prometheus metrics
        latency_stats = {
            "p50": REQUEST_LATENCY.collect()[0].samples[0].value,
            "p95": REQUEST_LATENCY.collect()[0].samples[1].value,
            "p99": REQUEST_LATENCY.collect()[0].samples[2].value,
        }
        
        # Add database metrics
        db_stats = DB_QUERY_DURATION.collect()[0].samples[0].value
        latency_stats["db_avg_duration"] = db_stats
        
        # Add cache performance
        cache_ratio = CACHE_HIT_RATIO.collect()[0].value
        latency_stats["cache_hit_ratio"] = cache_ratio
        
        return latency_stats

class MetricsMiddleware:
    """Middleware for collecting request metrics."""
    
    def __init__(self, app, metrics_collector: MetricsCollector):
        self.app = app
        self.metrics = metrics_collector

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
            
        start_time = time.time()
        
        # Create a response interceptor
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                duration = time.time() - start_time
                await self.metrics.record_request(
                    method=scope["method"],
                    endpoint=scope["path"],
                    status=message["status"],
                    duration=duration
                )
            await send(message)
            
        return await self.app(scope, receive, send_wrapper)

def setup_metrics(app, redis: Redis):
    """Setup metrics collection for the application."""
    metrics_collector = MetricsCollector(redis)
    app.add_middleware(MetricsMiddleware, metrics_collector=metrics_collector)
    return metrics_collector