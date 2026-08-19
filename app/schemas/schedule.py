from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ScheduleCreate(BaseModel):
    variant_id: UUID
    platform: str = Field(min_length=1, max_length=50)
    slot: datetime
    idempotency_key: str = Field(min_length=1, max_length=255)


class ScheduleResponse(BaseModel):
    id: UUID
    variant_id: UUID
    platform: str
    slot: datetime
    idempotency_key: str
    status: str
    external_id: str | None = None
    error: str | None = None
    published_at: datetime | None = None

    model_config = {
        "from_attributes": True,
    }