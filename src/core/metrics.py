"""Basic application metrics collection."""
from datetime import datetime, timedelta
import threading
from typing import Dict
from collections import defaultdict

class MetricsCollector:
    """Collect basic application metrics in memory."""
    
    def __init__(self):
        self.lock = threading.Lock()
        self.request_counts = defaultdict(int)
        self.errors = defaultdict(int)
        self.last_reset = datetime.utcnow()
    
    def record_request(self, method: str, endpoint: str, status: int) -> None:
        """Record basic request metrics."""
        with self.lock:
            self.request_counts[f"{method}:{endpoint}"] += 1
            if status >= 400:
                self.errors[f"{method}:{endpoint}"] += 1
            
            # Reset counts every hour
            now = datetime.utcnow()
            if now - self.last_reset > timedelta(hours=1):
                self.request_counts.clear()
                self.errors.clear()
                self.last_reset = now
    
    def get_stats(self) -> Dict:
        """Get current metrics."""
        with self.lock:
            return {
                "total_requests": sum(self.request_counts.values()),
                "total_errors": sum(self.errors.values()),
                "routes": dict(self.request_counts),
                "error_routes": dict(self.errors)
            }

# Global collector instance
metrics_collector = MetricsCollector()