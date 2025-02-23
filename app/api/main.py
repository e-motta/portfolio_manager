from contextlib import asynccontextmanager

from fastapi import FastAPI

from ..core.config import settings
from ..core.db import run_migrations
from .routers import accounts, auth, stocks, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    yield


app = FastAPI(lifespan=lifespan, debug=True)

app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(accounts.router, prefix=settings.API_V1_STR)
app.include_router(stocks.router, prefix=settings.API_V1_STR)
