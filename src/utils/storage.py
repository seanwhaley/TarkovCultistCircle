import json
import os
from datetime import datetime
from pathlib import Path

class ResponseStorage:
    def __init__(self):
        self.storage_dir = Path("storage/responses")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.latest_file = self.storage_dir / "latest_response.json"
    
    def save_response(self, response_data):
        """Save API response to storage"""
        try:
            # Save as latest response
            with open(self.latest_file, 'w') as f:
                json.dump(response_data, f, indent=2)
                
            # Also save timestamped version
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            archive_file = self.storage_dir / f"response_{timestamp}.json"
            with open(archive_file, 'w') as f:
                json.dump(response_data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving response: {e}")
            return False
    
    def load_latest_response(self):
        """Load the most recent API response"""
        try:
            if self.latest_file.exists():
                with open(self.latest_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading response: {e}")
        return None

response_storage = ResponseStorage()
