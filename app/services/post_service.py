from uuid import UUID

from sqlalchemy.orm import Session

from app.models.post import Post
from app.schemas.post import PostCreate


def create_post(db: Session, payload: PostCreate) -> Post:
    if payload.url:
        post = Post(
            source_type="url",
            source_url=payload.url.strip(),
            source_markdown=None,
        )
    else:
        post = Post(
            source_type="markdown",
            source_url=None,
            source_markdown=payload.markdown.strip(),
        )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


def get_post(db: Session, post_id: UUID) -> Post | None:
    return db.get(Post, post_id)