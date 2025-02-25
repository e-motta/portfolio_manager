from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, Session

from app.api.dependencies import CurrentUserDepAnnotated, SessionDepAnnotated
from app.models import Account, Stock, StockCreate, StockRead, StockUpdate, User


def create(
    session: Session, stock_in: StockCreate, account_id: int, current_user: User
):
    stock_db = Stock.model_validate(stock_in, update={"account_id": account_id})
    session.add(stock_db)
    session.commit()
    session.refresh(stock_db)
    return stock_db


def get_by_id(session: Session, stock_id: int):
    stock_statement = select(Stock).where(Stock.id == stock_id)
    stock = session.exec(stock_statement).first()
    return stock


def update(session: Session, stock_db: Stock, stock_in: StockUpdate):
    stock_data = stock_in.model_dump(exclude_unset=True)
    stock_db.sqlmodel_update(stock_data)
    session.add(stock_db)
    session.commit()
    session.refresh(stock_db)


def delete(session: Session, stock_db: Stock):
    session.delete(stock_db)
    session.commit()
