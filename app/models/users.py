from pydantic import computed_field, Field, EmailStr
from sqlmodel import SQLModel
from datetime import datetime

from .generic import BaseTableModel
from ..core.config import settings


class UserBase(SQLModel):
    username: str
    email: str
    first_name: str
    last_name: str
    is_admin: bool = False

    @computed_field
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class User(BaseTableModel, UserBase, table=True):
    password_hash: str


class UserCreate(UserBase):
    username: str = Field(max_length=settings.USERNAME_MAX_LENGTH)
    email: EmailStr
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    @computed_field
    def is_active(self) -> bool:
        return self.deleted_at is None


class UserUpdate(SQLModel):
    username: str | None = Field(max_length=settings.USERNAME_MAX_LENGTH, default=None)
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_admin: bool = False
