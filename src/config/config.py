"""Configuration management."""
from src.config import Config

def get_config() -> Config:
    """Get the current configuration instance."""
    return Config()