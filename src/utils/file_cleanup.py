"""File cleanup utilities."""
import os
import subprocess
import logging
from typing import Optional
from flask import current_app

logger = logging.getLogger(__name__)

def delete_file(filepath: str) -> bool:
    """
    Delete a file, preferring PowerShell's Remove-Item when available.
    
    Args:
        filepath: Path to the file to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    if not os.path.exists(filepath):
        logger.warning(f"File not found for deletion: {filepath}")
        return False
        
    try:
        # Try PowerShell Remove-Item first if enabled
        if current_app.config.get('FILE_CLEANUP_USE_POWERSHELL', True):
            try:
                # Use PowerShell's Remove-Item with -Force
                subprocess.run(
                    ['powershell', '-Command', f'Remove-Item -Path "{filepath}" -Force'],
                    check=True,
                    capture_output=True
                )
                logger.info(f"Successfully deleted file using PowerShell: {filepath}")
                return True
            except subprocess.CalledProcessError as e:
                logger.warning(f"PowerShell deletion failed, falling back to os.remove: {e}")
        
        # Fallback to standard os.remove
        os.remove(filepath)
        logger.info(f"Successfully deleted file using os.remove: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to delete file {filepath}: {str(e)}")
        return False