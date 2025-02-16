from fastapi import APIRouter, HTTPException, status

from ...models.users import UserRead

router = APIRouter()

fake_users = [
    {
        "id": 1,
        "username": "rick",
        "first_name": "Rick",
        "last_name": "Sanchez",
        "email": "rick.sanchez@example.com",
        "created_at": "2025-02-16T12:00:00Z",
        "updated_at": "2025-02-16T12:00:00Z",
        "deleted_at": None,
        "is_admin": True,
    },
    {
        "id": 2,
        "username": "morty",
        "first_name": "Morty",
        "last_name": "Smith",
        "email": "morty.smith@example.com",
        "created_at": "2025-02-16T12:05:00Z",
        "updated_at": "2025-02-16T12:05:00Z",
        "deleted_at": None,
        "is_admin": False,
    },
    {
        "id": 3,
        "username": "summer",
        "first_name": "Summer",
        "last_name": "Smith",
        "email": "summer.smith@example.com",
        "created_at": "2025-02-16T12:10:00Z",
        "updated_at": "2025-02-16T12:10:00Z",
        "deleted_at": None,
        "is_admin": False,
    },
]


@router.get("/users/", tags=["users"])
def read_users() -> list[UserRead]:
    users = [UserRead(**user) for user in fake_users]
    return users


@router.get("/users/me", tags=["users"])
def read_user_me() -> UserRead:
    return UserRead(**fake_users[0])


@router.get("/users/{username}", tags=["users"])
def read_user(id: int) -> UserRead:
    users_filtered = [user for user in fake_users if user["id"] == id]
    if not users_filtered:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return UserRead(**users_filtered[0])
