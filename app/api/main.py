from fastapi import FastAPI
from contextlib import asynccontextmanager
from ..core.db import init_db
from .routers import users


# todo: remove when migrations are implemented
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # Create tables on startup
    yield  # Keep the app running


app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
