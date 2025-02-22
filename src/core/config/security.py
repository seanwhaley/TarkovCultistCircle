import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import secrets

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecretsManager:
    """Secure secrets management with encryption."""

    def __init__(self, key_path: Optional[Path] = None):
        self.key_path = key_path or Path(".secret_key")
        self._key = self._load_or_generate_key()
        self._fernet = Fernet(self._key)

    def _load_or_generate_key(self) -> bytes:
        """Load existing key or generate a new one."""
        if self.key_path.exists():
            return self.key_path.read_bytes()
        
        # Generate a new key
        salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secrets.token_bytes(32)))
        
        # Save the key
        self.key_path.write_bytes(key)
        return key

    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self._fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        return self._fernet.decrypt(encrypted_data.encode()).decode()

class SecureSettings:
    """Secure application settings management."""

    def __init__(
        self,
        env_file: str = ".env",
        secrets_file: str = ".secrets.json",
        environment: Optional[str] = None
    ):
        self.env_file = Path(env_file)
        self.secrets_file = Path(secrets_file)
        self.environment = environment or os.getenv("APP_ENV", "development")
        self.secrets_manager = SecretsManager()
        self._settings: Dict[str, Any] = {}
        self._load_settings()

    def _load_settings(self) -> None:
        """Load settings from environment and secrets files."""
        # Load .env file
        self._load_env_file()
        
        # Load encrypted secrets
        self._load_secrets()
        
        # Override with environment variables
        self._load_environment_variables()

    def _load_env_file(self) -> None:
        """Load settings from .env file."""
        if not self.env_file.exists():
            return
            
        with open(self.env_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                key, value = line.split('=', 1)
                self._settings[key.strip()] = value.strip()

    def _load_secrets(self) -> None:
        """Load encrypted secrets from file."""
        if not self.secrets_file.exists():
            return
            
        try:
            with open(self.secrets_file) as f:
                encrypted_data = json.load(f)
                
            # Decrypt environment-specific secrets
            if self.environment in encrypted_data:
                env_secrets = encrypted_data[self.environment]
                for key, value in env_secrets.items():
                    try:
                        decrypted = self.secrets_manager.decrypt(value)
                        self._settings[key] = decrypted
                    except Exception as e:
                        print(f"Failed to decrypt secret {key}: {str(e)}")
                        
        except Exception as e:
            print(f"Failed to load secrets: {str(e)}")

    def _load_environment_variables(self) -> None:
        """Override settings with environment variables."""
        for key, value in os.environ.items():
            self._settings[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self._settings.get(key, default)

    def set(self, key: str, value: str, encrypt: bool = False) -> None:
        """Set a setting value."""
        if encrypt:
            value = self.secrets_manager.encrypt(value)
            
        self._settings[key] = value
        
        # Update secrets file if encrypted
        if encrypt:
            self._save_secrets()

    def _save_secrets(self) -> None:
        """Save encrypted secrets to file."""
        encrypted_data = {self.environment: {}}
        
        try:
            # Load existing secrets
            if self.secrets_file.exists():
                with open(self.secrets_file) as f:
                    encrypted_data.update(json.load(f))
                    
            # Update with new secrets
            for key, value in self._settings.items():
                if isinstance(value, str) and value.startswith('gAAAAA'):
                    encrypted_data[self.environment][key] = value
                    
            # Save updated secrets
            with open(self.secrets_file, 'w') as f:
                json.dump(encrypted_data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save secrets: {str(e)}")

    def validate_required_settings(self, required_keys: list[str]) -> None:
        """Validate that required settings are present."""
        missing = [key for key in required_keys if key not in self._settings]
        if missing:
            raise ValueError(f"Missing required settings: {', '.join(missing)}")

    def get_database_url(self) -> str:
        """Get database connection URL with credentials."""
        return (
            f"bolt://{self.get('NEO4J_USER')}:{self.get('NEO4J_PASSWORD')}"
            f"@{self.get('NEO4J_HOST', 'localhost')}:{self.get('NEO4J_PORT', '7687')}"
        )

    def get_redis_url(self) -> str:
        """Get Redis connection URL with credentials."""
        return (
            f"redis://:{self.get('REDIS_PASSWORD', '')}@"
            f"{self.get('REDIS_HOST', 'localhost')}:{self.get('REDIS_PORT', '6379')}"
            f"/{self.get('REDIS_DB', '0')}"
        )