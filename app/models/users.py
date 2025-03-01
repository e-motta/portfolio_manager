from datetime import datetime

from pydantic import EmailStr, Field, computed_field
from sqlmodel import Relationship, SQLModel

from app.core.config import settings
from app.models.accounts import Account
from app.models.generic import BaseTableModel


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
    __tablename__: str = "users"

    password_hash: str
    accounts: list[Account] | None = Relationship(back_populates="user")


class UserCreate(UserBase):
    username: str = Field(max_length=settings.USERNAME_MAX_LENGTH)
    email: EmailStr
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    accounts: list[Account]

    @computed_field
    def is_active(self) -> bool:
        return self.deleted_at is None


class UserRegister(SQLModel):
    username: str = Field(max_length=settings.USERNAME_MAX_LENGTH)
    email: EmailStr
    first_name: str
    last_name: str
    password: str


class UserUpdate(SQLModel):
    username: str | None = Field(max_length=settings.USERNAME_MAX_LENGTH, default=None)
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = None
    is_admin: bool = False
