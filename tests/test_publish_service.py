from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models.post import Post
from app.models.publish import PublishRecord
from app.models.variant import Variant
from app.services.publish_service import PublishService


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


def test_successful_publish(db, variant):
    service = PublishService(db)

    record = service.publish(
        variant_id=variant.id,
        platform="mock",
        slot=datetime.now(timezone.utc),
        idempotency_key="test-success-001",
    )

    assert record.status == "published"
    assert record.external_id is not None
    assert record.error is None


def test_idempotent_publish(db, variant):
    service = PublishService(db)

    slot = datetime.now(timezone.utc)

    first = service.publish(
        variant_id=variant.id,
        platform="mock",
        slot=slot,
        idempotency_key="test-idempotency-001",
    )

    second = service.publish(
        variant_id=variant.id,
        platform="mock",
        slot=slot,
        idempotency_key="test-idempotency-001",
    )

    assert first.id == second.id

    count = (
        db.query(PublishRecord)
        .filter(
            PublishRecord.idempotency_key
            == "test-idempotency-001"
        )
        .count()
    )

    assert count == 1


def test_missing_variant(db):
    service = PublishService(db)

    with pytest.raises(ValueError, match="not found"):
        service.publish(
            variant_id=uuid4(),
            platform="mock",
            slot=datetime.now(timezone.utc),
            idempotency_key="test-missing-variant",
        )


def test_platform_mismatch(db, variant):
    service = PublishService(db)

    with pytest.raises(ValueError, match="Variant platform"):
        service.publish(
            variant_id=variant.id,
            platform="linkedin",
            slot=datetime.now(timezone.utc),
            idempotency_key="test-platform-mismatch",
        )


def test_unsupported_platform_creates_failed_record(db):
    post = Post(
        source_type="manual",
        title="Unsupported Platform Test",
        source_markdown="# Test",
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    variant = Variant(
        post_id=post.id,
        platform="unsupported-platform",
        content="Unsupported platform test.",
        status="approved",
    )

    db.add(variant)
    db.commit()
    db.refresh(variant)

    service = PublishService(db)

    record = service.publish(
        variant_id=variant.id,
        platform="unsupported-platform",
        slot=datetime.now(timezone.utc),
        idempotency_key="test-unsupported-platform",
    )

    assert record.status == "failed"
    assert record.error is not None