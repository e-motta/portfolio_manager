from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
import jwt
from fastapi import HTTPException, status

from app.constants.messages import Messages
from app.core.config import settings
from app.models.generic import DetailItem


def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


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
    child_owner_id: int | UUID,
    owner_id: int | UUID,
    current_user_is_admin: bool = False,
):
    if current_user_is_admin:
        return

    has_access = child_owner_id == owner_id
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=DetailItem(
                type="forbidden", loc=[], msg=Messages.Auth.FORBIDDEN
            ).model_dump(),
        )
