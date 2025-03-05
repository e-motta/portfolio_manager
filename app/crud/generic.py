from uuid import UUID

from sqlmodel import Session, SQLModel


def get_by_id[
    T: SQLModel
](model: type[T], session: Session, account_id: int | UUID) -> T | None:
    return session.get(model, account_id)
