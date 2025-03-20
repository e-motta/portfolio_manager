from datetime import timedelta

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import AuthenticateUserDepAnnotated
from app.api.utils import create_access_token
from app.core.config import settings
from app.models.auth import Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token")
def login(user: AuthenticateUserDepAnnotated) -> Token:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        {"sub": user.username}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")
