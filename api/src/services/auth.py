from datetime import datetime, timedelta
from typing import Optional

import strawberry
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Security configuration
SECRET_KEY = "your-secret-key"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
