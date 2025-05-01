from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from fastapi import HTTPException, status
from sqlmodel import Session

from app import crud
from app.constants.messages import Messages
from app.core.logging_config import logger
from app.integrations import get_tickers_data
from app.models.accounts import Account
from app.models.generic import DetailItem
from app.models.securities import Security, SecurityCreate


@dataclass
class TickerInfo:
    symbol: str
    name: str
    latest_price: Decimal
    category: str
    type: str


def _get_price_from_ticker(ticker_info: dict):
    for key in ("bid", "previousClose"):
        if key in ticker_info:
            return Decimal(str(ticker_info[key]))
    return Decimal(0)


def fetch_tickers_info(symbols: str | list[str]) -> dict[str, TickerInfo]:
    logger.info(Messages.Security.FETCHING)

    if isinstance(symbols, str):
        symbols = [symbols]

    try:
        tickers = get_tickers_data(symbols)
        out: dict[str, TickerInfo] = {}

        for symbol in symbols:
            ticker_info = tickers.get(symbol)

            if not ticker_info:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=DetailItem(
                        type="external_service_error",
                        loc=[],
                        msg=Messages.External.could_not_fetch_symbols(symbol),
                    ).model_dump(),
                )

            ticker_info = TickerInfo(
                symbol=symbol,
                name=ticker_info.get("longName", ""),
                latest_price=_get_price_from_ticker(ticker_info),
                category=ticker_info.get("category", ""),
                type=ticker_info.get("typeDisp", ""),
            )
            out[symbol] = ticker_info

        return out
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=DetailItem(
                type="external_service_error",
                loc=[],
                msg=Messages.External.could_not_fetch_symbols(symbols),
            ).model_dump(),
        )


def create_security_with_info(
    session: Session, security_in: SecurityCreate, account: Account
):
    tickers_info = fetch_tickers_info(security_in.symbol)
    info = tickers_info.get(security_in.symbol)
    if info is not None and info.name:
        security = crud.securities.create(session, security_in, account)
        update_securities_info(session, security, tickers_info)
        return security
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=DetailItem(
            type="external_service_error",
            loc=[],
            msg=Messages.External.could_not_fetch_symbols(security_in.symbol),
        ).model_dump(),
    )


def update_securities_info(
    session: Session,
    securities: Security | Iterable[Security],
    new_tickers_info: dict[str, TickerInfo],
    fields: list[Literal["name", "latest_price"]] = ["name", "latest_price"],
) -> None:
    if isinstance(securities, Security):
        securities = [securities]
    for sec in securities:
        for field in fields:
            new_value = getattr(new_tickers_info[sec.symbol], field)
            setattr(sec, field, new_value)
        crud.securities.update(session, sec)
