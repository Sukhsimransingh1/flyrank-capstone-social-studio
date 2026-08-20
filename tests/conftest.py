
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models.post import Post
from app.models.variant import Variant


TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def variant(db):
    post = Post(
        source_type="manual",
        title="Test Post",
        source_markdown="# Test",
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    variant = Variant(
        post_id=post.id,
        platform="mock",
        content="Hello from FlyRank.",
        status="approved",
    )

    db.add(variant)
    db.commit()
    db.refresh(variant)

    return variant
