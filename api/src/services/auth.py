from datetime import datetime, timedelta
from typing import Optional
import os
import base64
import secrets
from pathlib import Path

import strawberry
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

"""
Security configuration

AUTH_SECRET_KEY is the HMAC secret used to sign and verify JWTs (HS256).
It is NOT a user password. In production, set it via environment variables.

Example (generate a strong key):
  openssl rand -base64 32

If AUTH_SECRET_KEY is not set, we attempt to load it from a persisted file
at AUTH_SECRET_FILE (default: /config/auth_secret_key). If the file does not
exist, we will generate a secure secret and persist it there, so that tokens
remain valid across restarts. If persistence fails (e.g., during tests), we
fall back to an in-memory random key for this process only.
"""

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

AUTH_SECRET_FILE = os.getenv("AUTH_SECRET_FILE", "/config/auth_secret_key")


def _generate_secret_key() -> str:
    # 256-bit random key, URL-safe base64
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("ascii")


def _load_or_create_persisted_secret(path_str: str) -> Optional[str]:
    try:
        path = Path(path_str)
        if path.exists():
            content = path.read_text(encoding="utf-8").strip()
            return content or None

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        secret = _generate_secret_key()
        path.write_text(secret + "\n", encoding="utf-8")
        try:
            # Best-effort secure permissions
            os.chmod(path, 0o600)
        except Exception:
            # Ignore chmod errors on non-POSIX filesystems
            pass
        return secret
    except Exception:
        # Any IO error -> fall back to in-memory secret
        return None


def _load_secret_key() -> str:
    # Highest precedence: explicit environment variable
    env_secret = os.getenv("AUTH_SECRET_KEY")
    if env_secret:
        return env_secret

    # Next: persisted secret file in mounted config volume
    persisted = _load_or_create_persisted_secret(AUTH_SECRET_FILE)
    if persisted:
        return persisted

    # Fallback: ephemeral secret for this process only
    return _generate_secret_key()


SECRET_KEY = _load_secret_key()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@strawberry.type
class AuthToken:
    access_token: str
    token_type: str = "bearer"


@strawberry.input
class LoginInput:
    username: str
    password: str


class User(BaseModel):
    username: str
    hashed_password: str
    disabled: bool = False


class AuthService:
    def __init__(self) -> None:
        # TODO: Replace with proper user storage
        self.users = {
            "admin": User(
                username="admin",
                hashed_password=pwd_context.hash("admin"),
            )
        }

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_user(self, username: str) -> Optional[User]:
        return self.users.get(username)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if not isinstance(username, str):
                return None
            return username
        except JWTError:
            return None


auth_service = AuthService()
