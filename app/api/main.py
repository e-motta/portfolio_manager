from fastapi import FastAPI
from contextlib import asynccontextmanager
from ..core.db import run_migrations
from .routers import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
