from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import entities
from app.endpoint.v1 import (patients, documents,auth)


@asynccontextmanager

async def lifespan(app: FastAPI):
    # Development only.
    # Use Alembic migrations in production.
    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )
    yield
    await engine.dispose()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth.router,
    prefix=settings.API_V1_STR,
)

app.include_router(
    patients.router,
    prefix=settings.API_V1_STR,
)

app.include_router(
    documents.router,
    prefix=settings.API_V1_STR,
)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "cliniq-api",
    }