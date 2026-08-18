from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PostCreate(BaseModel):
    url: str | None = Field(default=None, max_length=2048)
    markdown: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_source(self):
        has_url = bool(self.url and self.url.strip())
        has_markdown = bool(self.markdown and self.markdown.strip())

        if has_url == has_markdown:
            raise ValueError("Provide exactly one of 'url' or 'markdown'.")

        return self


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_type: str
    source_url: str | None
    source_markdown: str | None
    title: str | None