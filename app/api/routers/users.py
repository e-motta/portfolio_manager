from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select
from sqlalchemy import func

from ...models.users import User, UserRead, UserCreate, UserUpdate
from ..dependencies import SessionDep, validate_unique_email, validate_unique_username


router = APIRouter()


@router.get("/users/", tags=["users"], response_model=list[UserRead])
def read_users(
    session: SessionDep, username: str | None = None, include_deleted: bool = False
):
    statement = select(User)

    if username:
        statement = statement.where(User.username == username)
    if not include_deleted:
        statement = statement.where(User.deleted_at == None)

    users = session.exec(statement)

    return users


# @router.get("/users/me", tags=["users"])
# def read_user_me() -> UserRead:
#     return UserRead(**fake_users[0])


@router.get("/users/{id}", tags=["users"], response_model=UserRead)
def read_user(session: SessionDep, id: int):
    user = session.get(User, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post(
    "/users/",
    tags=["users"],
    response_model=UserRead,
    dependencies=[Depends(validate_unique_email), Depends(validate_unique_username)],
)
def create_user(session: SessionDep, user_in: UserCreate):
    # todo: hash password
    db_obj = User.model_validate(user_in, update={"password_hash": user_in.password})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


@router.post("/users/{id}", tags=["users"], response_model=UserRead)
def udpate_user(session: SessionDep, id: int, user_in: UserUpdate):
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


@router.delete("/users/{id}", tags=["users"])
def delete_user(session: SessionDep, id: int, hard_delete: bool = False):
    print("hard_delete", hard_delete)
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
    else:
        session.delete(user_db)
        session.commit()

    return {"ok": True}
