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
from app.constants.messages import Messages
from app.core.config import settings
from app.models.generic import DetailItem, Meta, ResponseMultiple, ResponseSingle
from app.models.users import User, UserCreate, UserRead, UserRegister, UserUpdate

router = APIRouter(
    prefix=f"/{settings.USERS_ROUTE_STR}", tags=[settings.USERS_ROUTE_STR]
)


# Open
@router.post(
    "/register",
    response_model=ResponseSingle[UserRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(validate_unique_email),
        Depends(validate_unique_username),
    ],
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Conflict - Username or Email already in use",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["string", 0],
                                "msg": "string",
                                "type": "string",
                            }
                        ]
                    }
                }
            },
        }
    },
)
def register_user(session: SessionDepAnnotated, user_in: UserRegister):
    user = crud.users.register(session, user_in)
    return ResponseSingle(data=user, message=Messages.User.REGISTRATION_SUCCESSFUL)


# Logged-in user
@router.get("/me", response_model=ResponseSingle[UserRead])
def read_user_me(current_user: CurrentUserDepAnnotated):
    return ResponseSingle(data=current_user)


@router.patch(
    "/me",
    response_model=ResponseSingle[UserRead],
    dependencies=[
        Depends(validate_unique_email),
        Depends(validate_unique_username),
    ],
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Conflict - Username or Email already in use",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["string", 0],
                                "msg": "string",
                                "type": "string",
                            }
                        ]
                    }
                }
            },
        }
    },
)
def update_user_me(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    user_in: UserUpdate,
):
    crud.users.update(session, current_user, user_in)
    return ResponseSingle(data=current_user, message=Messages.User.UPDATED)


# Admin
@router.get("/", response_model=ResponseMultiple[UserRead], dependencies=[IsAdminDep])
def read_user_list(session: SessionDepAnnotated, include_deleted: bool = False):
    if include_deleted:
        users, count = crud.users.fetch_all(session)
    else:
        users, count = crud.users.fetch_active(session)
    return ResponseMultiple(data=users, meta=Meta(count=count))


@router.get(
    "/{user_id}",
    response_model=ResponseSingle[UserRead],
    dependencies=[IsAdminDep],
)
def read_user_detail(user_db: User = Depends(get_user_or_404)):
    return ResponseSingle(data=user_db)


@router.post(
    "/",
    response_model=ResponseSingle[UserRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        IsAdminDep,
        Depends(validate_unique_email),
        Depends(validate_unique_username),
    ],
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Conflict - Username or Email already in use",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["string", 0],
                                "msg": "string",
                                "type": "string",
                            }
                        ]
                    }
                }
            },
        }
    },
)
def create_user(session: SessionDepAnnotated, user_in: UserCreate):
    user = crud.users.create(session, user_in)
    return ResponseSingle(data=user, message=Messages.User.CREATED)


@router.patch(
    "/{user_id}",
    response_model=ResponseSingle[UserRead],
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
    return ResponseSingle(data=user_db, message=Messages.User.UPDATED)


@router.delete(
    "/{user_id}",
    response_model=ResponseSingle[None],
    status_code=status.HTTP_200_OK,
    dependencies=[IsAdminDep],
)
def delete_user(
    session: SessionDepAnnotated,
    user_db: User = Depends(get_user_or_404),
    hard_delete: bool = False,
):
    if hard_delete:
        crud.users.hard_delete(session, user_db)
    else:
        crud.users.soft_delete(session, user_db)

    return ResponseSingle(message=Messages.User.DELETED)


@router.patch(
    "/{user_id}/recover",
    response_model=ResponseSingle[UserRead],
    dependencies=[IsAdminDep],
)
def recover_soft_deletion(
    session: SessionDepAnnotated,
    user_db: User = Depends(get_user_or_404),
):
    if user_db.deleted_at is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DetailItem(
                type="already_active", loc=[], msg=Messages.User.ALREADY_ACTIVE
            ).model_dump(),
        )

    crud.users.recover(session, user_db)
    return ResponseSingle(data=user_db, message=Messages.User.RECOVERED)
