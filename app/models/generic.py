from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlmodel import Field, SQLModel


def get_decimal_field(max_digits=18, decimal_places=8, ge=0, **extra):
    return Field(
        max_digits=max_digits,
        decimal_places=decimal_places,
        ge=ge,
        **extra,
    )


class BaseTableModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    deleted_at: datetime | None = None


@event.listens_for(Session, "before_flush")
def auto_update_timestamp(session, flush_context, instances):
    for obj in session.dirty:
        if isinstance(obj, BaseTableModel):
            obj.updated_at = datetime.now(timezone.utc)


class Meta(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    count: int | None = Field(default=None)


class ResponseBase(BaseModel):
    message: str | None = Field(default=None)
    data: None = Field(default=None)
    meta: Meta = Field(default_factory=Meta)


class ResponseSingle[T](ResponseBase):
    data: T | None = Field(default=None)


class ResponseMultiple[T](ResponseBase):
    data: Sequence[T] | None = Field(default=None)


class DetailItem(SQLModel):
    type: str
    loc: list[str | int]
    msg: str
    input: str | None = None
    ctx: dict[str, Any] | None = None
