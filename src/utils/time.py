from datetime import datetime, timedelta, timezone
from typing import Union

def format_timestamp(dt: datetime, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    return dt.strftime(fmt)

def parse_duration(duration: Union[str, int]) -> timedelta:
    if isinstance(duration, int):
        return timedelta(seconds=duration)
    else:
        return timedelta(seconds=int(duration))

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def time_since(dt: datetime) -> str:
    delta = utc_now() - dt
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return f"{seconds} seconds ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minutes ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hours ago"
    days = hours // 24
    return f"{days} days ago"