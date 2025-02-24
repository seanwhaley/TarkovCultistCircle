"""Rate limiting metrics collection."""
import logging
from dataclasses import dataclass
from typing import Dict
from datetime import datetime, timedelta
from src.core.middleware.ratelimit import _limiter

logger = logging.getLogger(__name__)

@dataclass
class RateLimitMetrics:
    """Rate limit metrics container."""
    total_requests: int
    limited_requests: int
    active_limits: int
    unique_ips: int

def get_rate_limit_metrics() -> RateLimitMetrics:
    """Get current rate limiting metrics."""
    now = datetime.utcnow()
    window = timedelta(minutes=5)  # Look at last 5 minutes
    
    with _limiter._lock:
        # Count requests in last 5 minutes
        recent_requests: Dict[str, int] = {}
        limited_ips = set()
        
        for ip, timestamps in _limiter._requests.items():
            # Filter to recent timestamps
            recent = [ts for ts in timestamps if now - ts < window]
            if recent:
                recent_requests[ip] = len(recent)
                # Check if IP is currently limited
                if len(recent) > _limiter.limit:
                    limited_ips.add(ip)
        
        return RateLimitMetrics(
            total_requests=sum(recent_requests.values()),
            limited_requests=len(limited_ips),
            active_limits=len(limited_ips),
            unique_ips=len(recent_requests)
        )

def log_rate_limit_metrics(interval: int = 300) -> None:
    """Log rate limiting metrics periodically."""
    try:
        metrics = get_rate_limit_metrics()
        logger.info(
            "Rate limit metrics - "
            f"Total requests: {metrics.total_requests}, "
            f"Limited requests: {metrics.limited_requests}, "
            f"Active limits: {metrics.active_limits}, "
            f"Unique IPs: {metrics.unique_ips}"
        )
    except Exception as e:
        logger.error(f"Failed to collect rate limit metrics: {str(e)}")