from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import select

from ...models.users import User, UserCreate, UserRead, UserUpdate
from ..dependencies import (
    CurrentUserDepAnnotated,
    IsAdminDep,
    SessionDepAnnotated,
    TokenDep,
    validate_unique_email,
    validate_unique_username,
)
from ..utils import get_password_hash

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserRead], dependencies=[IsAdminDep])
def read_users(
    session: SessionDepAnnotated,
    username: str | None = None,
    include_deleted: bool = False,
):
    statement = select(User)

    if username:
        statement = statement.where(User.username == username)
    if not include_deleted:
        statement = statement.where(User.deleted_at == None)

    users = session.exec(statement)

    return users


@router.get("/me", response_model=UserRead)
def read_user_me(current_user: CurrentUserDepAnnotated):
    return current_user


@router.get(
    "/{id}",
    response_model=UserRead,
    dependencies=[TokenDep],
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
    dependencies=[Depends(validate_unique_email), Depends(validate_unique_username)],
)
def create_user(session: SessionDepAnnotated, user_in: UserCreate):
    db_obj = User.model_validate(
        user_in, update={"password_hash": get_password_hash(user_in.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.patch("/{id}", response_model=UserRead)
def udpate_user(session: SessionDepAnnotated, id: int, user_in: UserUpdate):
    user_db = session.get(User, id)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user_data = user_in.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


@router.delete("/{id}")
def delete_user(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    id: int,
    hard_delete: bool = False,
):
    user_db = session.get(User, id)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not hard_delete:
        user_db.sqlmodel_update({"deleted_at": func.now()})
        session.add(user_db)
        session.commit()
        session.refresh(user_db)
    elif not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough permissions"
        )
    else:
        session.delete(user_db)
        session.commit()

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

    user_db.deleted_at = None
    session.add(user_db)
    session.commit()

    return user_db
