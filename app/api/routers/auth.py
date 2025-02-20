from fastapi import APIRouter, HTTPException, status
from datetime import timedelta

from ..dependencies import AuthenticateUserDepAnnotated
from ..utils import create_access_token
from ...models import Token
from ...core.config import settings


router = APIRouter(prefix="/auth")


@router.post("/token", tags=["auth"])
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
