from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    CurrentUserDepAnnotated,
    IsAdminDep,
    SessionDepAnnotated,
    validate_unique_email,
    validate_unique_username,
)
from app.models.users import User, UserCreate, UserRead, UserUpdate
from app import services

router = APIRouter(prefix="/users", tags=["users"])


# Open
# todo: register_user


# Logged-in user
@router.get("/me", response_model=UserRead)
def read_user_me(current_user: CurrentUserDepAnnotated):
    return current_user


# Admin
@router.get("/", response_model=list[UserRead], dependencies=[IsAdminDep])
def read_users(session: SessionDepAnnotated, include_deleted: bool = False):
    users = services.users.fetch(session, include_deleted)
    return users


@router.get(
    "/{id}",
    response_model=UserRead,
    dependencies=[IsAdminDep],
)
def read_user(session: SessionDepAnnotated, id: int):
    user = session.get(User, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post(
    "/",
    response_model=UserRead,
    dependencies=[
        IsAdminDep,
        Depends(validate_unique_email),
        Depends(validate_unique_username),
    ],
)
def create_user(session: SessionDepAnnotated, user_in: UserCreate):
    user = services.users.create(session, user_in)
    return user


@router.patch(
    "/{id}",
    response_model=UserRead,
    dependencies=[
        IsAdminDep,
        Depends(validate_unique_email),
        Depends(validate_unique_username),
    ],
)
def update_user(session: SessionDepAnnotated, id: int, user_in: UserUpdate):
    user_db = session.get(User, id)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user = services.users.update(session, user_db, user_in)
    return user


@router.delete("/{id}", dependencies=[IsAdminDep])
def delete_user(session: SessionDepAnnotated, id: int, hard_delete: bool = False):
    user_db = session.get(User, id)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if hard_delete:
        services.users.hard_delete(session, user_db)
    else:
        services.users.soft_delete(session, user_db)

    return {"ok": True}


@router.post("/{id}/recover", dependencies=[IsAdminDep], response_model=UserRead)
def recover_soft_deletion(session: SessionDepAnnotated, id: int):
    user_db = session.get(User, id)

    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user_db.deleted_at is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is already active"
        )

    services.users.recover(session, user_db)

    return user_db
