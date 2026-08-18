from fastapi import FastAPI

from app.core.config import settings
from app.db.session import check_database_connection


app = FastAPI(
    title="FlyRank Social Media Studio",
    version="0.1.0",
    description="Reliable multi-platform social publishing backend.",
)


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
        "version": "0.1.0",
        "docs": "/docs",
    }
