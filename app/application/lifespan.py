from contextlib import asynccontextmanager

from fastapi import FastAPI

from .models.core import SQLManager
from .settings import settings

sql_manager = SQLManager(settings.DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # With start app
    await sql_manager.initial_database()
    yield
    # With stop app
    await sql_manager.close()
