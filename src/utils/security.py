import secrets
import string
from typing import Optional
from jose import jwt, JWTError
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SecurityManager:
    """Security utilities for the application"""

    def __init__(self, secret_key: Optional[str] = None):
        """Initialize with optional secret key"""
        self.secret_key = secret_key or self._generate_secret_key()

    def _generate_secret_key(self, length: int = 32) -> str:
        """Generate a secure secret key"""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def create_jwt_token(
            self,
            team_id: str,
            expires_delta: timedelta = timedelta(hours=1)
    ) -> str:
        """Create JWT token for team authentication"""
        try:
            expire = datetime.utcnow() + expires_delta
            to_encode = {
                "team_id": team_id,
                "exp": expire
            }
            return jwt.encode(
                to_encode,
                self.secret_key,
                algorithm="HS256"
            )
        except Exception as e:
            logger.error(f"Error creating JWT token: {str(e)}")
            raise

    def validate_jwt_token(self, token: str) -> Optional[str]:
        """Validate JWT token and return team_id"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=["HS256"]
            )
            return payload.get("team_id")
        except JWTError as e:
            logger.error(f"Error validating JWT token: {str(e)}")
            return None

    def sanitize_input(self, input_str: str) -> str:
        """Sanitize user input"""
        # Add your sanitization rules here
        return input_str.strip()


# Initialize global security manager
security_manager = SecurityManager()