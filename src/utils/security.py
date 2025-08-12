import base64
from datetime import datetime, timedelta, timezone
from jwt import decode, encode
from bcrypt import hashpw, gensalt, checkpw

from config.settings import JWT_EXPIRE_MINUTES, PASSWORD_SALT_ROUNDS


class JWTHandler:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def encode(self, data: dict) -> str:
        """Encode data into a JWT token."""
        payload = {
            **data,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES),
            "iat": datetime.now(timezone.utc)
        }
        return encode(
            payload, 
            base64.b64decode(self.secret_key), 
            algorithm=self.algorithm, 
            headers={"typ": "JWT", "alg": self.algorithm}
        )

    def decode(self, token: str) -> dict:
        """Decode a JWT token back into data."""
        try:
            return decode(
                token, 
                base64.b64decode(self.secret_key), 
                algorithms=[self.algorithm]
            )
        except Exception as e:
            raise ValueError(f"Failed to decode JWT: {e}")


class PasswordManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using a secure hashing algorithm."""
        return hashpw(password.encode('utf-8'), gensalt(rounds=PASSWORD_SALT_ROUNDS)).decode('utf-8')

    @staticmethod
    def verify_password(stored_password: str, provided_password: str) -> bool:
        """Verify a provided password against a stored hashed password."""
        return checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))
