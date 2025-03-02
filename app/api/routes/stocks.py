from fastapi import APIRouter, Depends, status

from app import crud
from app.api.dependencies import (
    CurrentUserDepAnnotated,
    SessionDepAnnotated,
    get_account_or_404,
    get_stock_or_404,
)
from app.api.utils import verify_ownership_or_403
from app.core.config import settings
from app.models import Account, Stock, StockCreate, StockRead, StockUpdate

router = APIRouter(
    prefix=f"/{settings.ACCOUNTS_ROUTE_STR}/{{account_id}}/{settings.STOCKS_ROUTE_STR}",
    tags=[settings.STOCKS_ROUTE_STR],
)


@router.get("/", response_model=list[StockRead])
def read_stock_list(
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    return account_db.stocks


@router.get("/{stock_id}", response_model=StockRead)
def read_stock_detail(
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
    stock_db: Stock = Depends(get_stock_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    verify_ownership_or_403(stock_db.account_id, account_db.id)
    return stock_db


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=StockRead)
def create_stock(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    stock_in: StockCreate,
    account_db: Account = Depends(get_account_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    stock_db = crud.stocks.create(session, stock_in, account_db)
    return stock_db


@router.patch("/{stock_id}", response_model=StockRead)
def update_stock(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    stock_in: StockUpdate,
    account_db: Account = Depends(get_account_or_404),
    stock_db: Stock = Depends(get_stock_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    verify_ownership_or_403(stock_db.account_id, account_db.id)
    crud.stocks.update(session, stock_db, stock_in)
    return stock_db


@router.delete("/{stock_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stock(
    session: SessionDepAnnotated,
    current_user: CurrentUserDepAnnotated,
    account_db: Account = Depends(get_account_or_404),
    stock_db: Stock = Depends(get_stock_or_404),
):
    verify_ownership_or_403(account_db.user_id, current_user.id, current_user.is_admin)
    verify_ownership_or_403(stock_db.account_id, account_db.id)
    crud.stocks.delete(session, stock_db)
    return {"ok": True}
