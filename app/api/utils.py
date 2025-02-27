from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    if not expires_delta:
        expires_delta = timedelta(minutes=15)

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.AUTH_ALGORITHM
    )
    return encoded_jwt


def verify_ownership_or_403(
    child_owner_id: int | str, owner_id: int | str, current_user_is_admin: bool = False
):
    if current_user_is_admin:
        return

    has_access = child_owner_id == owner_id
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
