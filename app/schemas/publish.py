from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PublishRequest(BaseModel):
    variant_id: UUID
    platform: str = Field(min_length=1, max_length=50)
    slot: datetime
    idempotency_key: str = Field(
        min_length=1,
        max_length=255,
    )


class PublishResponse(BaseModel):
    id: UUID
    variant_id: UUID
    platform: str
    status: str
    idempotency_key: str
    external_id: str | None = None
    error: str | None = None
    slot: datetime
    published_at: datetime | None = None