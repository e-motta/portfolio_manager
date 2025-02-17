from pydantic import computed_field
from sqlmodel import SQLModel
from datetime import datetime

from .generic import BaseTableModel


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
    username: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_admin: bool = False
