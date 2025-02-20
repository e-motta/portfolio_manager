from fastapi import FastAPI
from contextlib import asynccontextmanager

from ..core.db import run_migrations
from ..core.config import settings
from .routers import users, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    yield


app = FastAPI(lifespan=lifespan, debug=True)

app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(auth.router, prefix=settings.API_V1_STR)
