from sqlmodel import SQLModel, Session


def get_by_id[
    T: SQLModel
](model: type[T], session: Session, account_id: int) -> T | None:
    return session.get(model, account_id)
