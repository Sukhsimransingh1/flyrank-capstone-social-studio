from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.posts import router as posts_router
from app.api.routes.variants import router as variants_router
from app.core.config import settings
from app.db.session import Base, check_database_connection, engine
from app.models.post import Post  # noqa: F401
from app.models.publish import PublishRecord  # noqa: F401
from app.models.variant import Variant  # noqa: F401
from app.api.routes.publish import router as publish_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="FlyRank Social Media Studio",
    version="0.2.0",
    description="Reliable multi-platform social publishing backend.",
    lifespan=lifespan,
)

app.include_router(posts_router)
app.include_router(publish_router)
app.include_router(variants_router)


@app.get("/health")
def health() -> dict:
    database_ok = check_database_connection()

    return {
        "status": "ok" if database_ok else "degraded",
        "service": settings.app_name,
        "database": "ok" if database_ok else "unavailable",
    }


@app.get("/")
def root() -> dict:
    return {
        "service": settings.app_name,
        "version": "0.2.0",
        "docs": "/docs",
    }