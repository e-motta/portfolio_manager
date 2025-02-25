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
