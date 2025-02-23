from typing import Dict, Any, Optional
import requests
from urllib.parse import urlencode
import logging
from datetime import datetime, timedelta
from src.database.exceptions import AuthenticationError

logger = logging.getLogger(__name__)

class OAuthHandler:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None

    def get_token(self) -> str:
        if self.is_token_valid():
            return self.token or ""
        return self.refresh_token()

    def is_token_valid(self) -> bool:
        if not self.token or not self.token_expiry:
            return False
        return datetime.utcnow() < self.token_expiry

    def refresh_token(self) -> str:
        try:
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.config['client_id'],
                'client_secret': self.config['client_secret'],
                'scope': self.config.get('scope', 'read write')
            }
            
            response = requests.post(
                self.config['token_endpoint'],
                data=urlencode(data),
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code != 200:
                raise AuthenticationError(f"OAuth token request failed: {response.text}")
                
            token_data = response.json()
            self.token = token_data['access_token']
            expires_in = int(token_data.get('expires_in', 3600))
            self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
            
            return self.token
            
        except Exception as e:
            logger.error(f"Failed to refresh OAuth token: {str(e)}")
            raise AuthenticationError("Failed to authenticate with OAuth provider")

    def revoke_token(self) -> None:
        if not self.token:
            return

        try:
            response = requests.post(
                self.config['revoke_endpoint'],
                data={'token': self.token},
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code not in (200, 204):
                raise AuthenticationError(f"Failed to revoke token: {response.text}")
                
            self.token = None
            self.token_expiry = None
            
        except Exception as e:
            logger.error(f"Failed to revoke token: {str(e)}")
            raise AuthenticationError("Failed to revoke token")
