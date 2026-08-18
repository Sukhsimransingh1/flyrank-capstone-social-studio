from uuid import UUID

from pydantic import BaseModel, ConfigDict


class VariantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    post_id: UUID
    platform: str
    content: str
    status: str
    validation_errors: str | None


class VariantUpdate(BaseModel):
    content: str