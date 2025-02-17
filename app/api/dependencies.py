from collections.abc import Generator
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select, SQLModel
from typing import Annotated

from ..core.db import engine
from ..models.users import User, UserCreate


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


def validate_unique_username(session: SessionDep, user_in: UserCreate):
    statement = select(User).where(User.username == user_in.username)
    users = session.exec(statement).first()
    if users:
        raise (
            HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Username already in use"
            )
        )


def validate_unique_email(session: SessionDep, user_in: UserCreate):
    statement = select(User).where(User.email == user_in.email)
    users = session.exec(statement).first()
    if users:
        raise (
            HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already in use"
            )
        )
