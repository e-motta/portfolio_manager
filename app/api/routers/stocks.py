from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select

from app.api.dependencies import (
    CurrentUserDepAnnotated,
    SessionDepAnnotated,
    get_account_or_404,
    get_stock_or_404,
)
from app.models import Account, Stock, StockCreate, StockRead, StockUpdate
from app import crud

router = APIRouter(prefix="/accounts/{account_id}/stocks", tags=["stocks"])


@router.get("/", response_model=list[StockRead])
def read_stocks(
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
):
    if current_user.id != account_db.user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return account_db.stocks


@router.post("/", response_model=StockRead)
def create_stock(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    stock_in: StockCreate,
    account_db: Account = Depends(get_account_or_404),
):
    if current_user.id != account_db.user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    stock_db = crud.stocks.create(session, stock_in, account_db)
    return stock_db


@router.patch("/{stock_id}", response_model=StockRead)
def update_stock(
    session: SessionDepAnnotated,
    stock_in: StockUpdate,
    stock_db: Stock = Depends(get_stock_or_404),
):
    crud.stocks.update(session, stock_db, stock_in)
    return stock_db


@router.delete("/{stock_id}")
def delete_stock(
    session: SessionDepAnnotated,
    stock_db: Stock = Depends(get_stock_or_404),
):
    crud.stocks.delete(session, stock_db)
    return {"ok": True}
