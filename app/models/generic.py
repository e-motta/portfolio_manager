from sqlmodel import SQLModel, Field, Column
from datetime import datetime
from sqlalchemy import TIMESTAMP, func


class BaseTableModel(SQLModel):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(sa_column=Column(TIMESTAMP, server_default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    )
    deleted_at: datetime | None = None
