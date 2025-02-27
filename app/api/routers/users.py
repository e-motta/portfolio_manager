from fastapi import APIRouter, Depends, HTTPException, status

from app import crud
from app.api.dependencies import (
    CurrentUserDepAnnotated,
    IsAdminDep,
    SessionDepAnnotated,
    get_user_or_404,
    validate_unique_email,
    validate_unique_username,
)
from app.models.users import User, UserCreate, UserRead, UserRegister, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


# Open
@router.post(
    "/register",
    response_model=UserRead,
    dependencies=[
        Depends(validate_unique_email),
        Depends(validate_unique_username),
    ],
)
def register_user(session: SessionDepAnnotated, user_in: UserRegister):
    user = crud.users.register(session, user_in)
    return user


# Logged-in user
@router.get("/me", response_model=UserRead)
def read_user_me(current_user: CurrentUserDepAnnotated):
    return current_user


# Admin
@router.get("/", response_model=list[UserRead], dependencies=[IsAdminDep])
def read_user_list(session: SessionDepAnnotated, include_deleted: bool = False):
    if include_deleted:
        users = crud.users.fetch_all(session)
    else:
        users = crud.users.fetch_active(session)
    return users


@router.get(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[IsAdminDep],
)
def read_user_detail(user_db: User = Depends(get_user_or_404)):
    return user_db


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
    user = crud.users.create(session, user_in)
    return user


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[
        IsAdminDep,
        Depends(validate_unique_email),
        Depends(validate_unique_username),
    ],
)
def update_user(
    session: SessionDepAnnotated,
    user_in: UserUpdate,
    user_db: User = Depends(get_user_or_404),
):
    crud.users.update(session, user_db, user_in)
    return user_db


@router.delete("/{user_id}", dependencies=[IsAdminDep])
def delete_user(
    session: SessionDepAnnotated,
    user_db: User = Depends(get_user_or_404),
    hard_delete: bool = False,
):
    if hard_delete:
        crud.users.hard_delete(session, user_db)
    else:
        crud.users.soft_delete(session, user_db)

    return {"ok": True}


@router.post("/{user_id}/recover", dependencies=[IsAdminDep], response_model=UserRead)
def recover_soft_deletion(
    session: SessionDepAnnotated,
    user_db: User = Depends(get_user_or_404),
):
    if user_db.deleted_at is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is already active"
        )

    crud.users.recover(session, user_db)
    return user_db
