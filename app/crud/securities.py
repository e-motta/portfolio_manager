from decimal import Decimal

from sqlmodel import Session, col, func, select

from app.models.accounts import Account
from app.models.securities import (
    Security,
    SecurityCreate,
    SecurityServiceUpdate,
    SecurityUpdate,
)


def get_total_target_allocation(session: Session, account: Account):
    statement = select(
        func.sum(Security.target_allocation).label("total_allocation")
    ).where(Security.account_id == account.id)

    result = session.exec(statement).one()

    total_allocation = Decimal(result) if result is not None else Decimal(0)

    return total_allocation


def get_all_for_account(session: Session, account: Account):
    statement = (
        select(Security)
        .where(Security.account_id == account.id)
        .order_by(col(Security.created_at))
    )

    securities = session.exec(statement).all()
    return securities


def create(session: Session, security_in: SecurityCreate, account_db: Account):
    security_db = Security.model_validate(
        security_in, update={"account_id": account_db.id}
    )
    session.add(security_db)
    session.commit()
    session.refresh(security_db)
    return security_db


def update(
    session: Session,
    security_db: Security,
    security_in: SecurityUpdate | SecurityServiceUpdate | None = None,
):
    if security_in:
        security_data = security_in.model_dump(exclude_unset=True)
        security_db.sqlmodel_update(security_data)
    session.add(security_db)
    session.commit()
    session.refresh(security_db)


def delete(session: Session, security_db: Security):
    session.delete(security_db)
    session.commit()
