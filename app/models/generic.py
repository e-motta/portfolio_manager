from datetime import datetime, timezone

from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlmodel import Field, SQLModel


class BaseTableModel(SQLModel):
    id: int = Field(default=None, primary_key=True)
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
