from datetime import datetime, timedelta, timezone

from app.models.post import Post
from app.models.publish import PublishRecord
from app.models.publish_history import PublishHistory
from app.models.variant import Variant
from app.services.publish_service import PublishService
from app.services.scheduler_service import SchedulerService


def test_complete_publish_pipeline(db):
    # ---------------------------------------------------------
    # 1. Create source post
    # ---------------------------------------------------------
    post = Post(
        source_type="manual",
        title="End-to-End Test Post",
        source_markdown="# FlyRank Test",
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    # ---------------------------------------------------------
    # 2. Create approved variant
    # ---------------------------------------------------------
    variant = Variant(
        post_id=post.id,
        platform="mock",
        content="FlyRank end-to-end test content.",
        status="approved",
    )

    db.add(variant)
    db.commit()
    db.refresh(variant)

    # ---------------------------------------------------------
    # 3. Schedule the variant
    # ---------------------------------------------------------
    record = PublishRecord(
        variant_id=variant.id,
        slot=datetime.now(timezone.utc) - timedelta(minutes=1),
        idempotency_key="e2e-pipeline-001",
        platform="mock",
        status="scheduled",
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    assert record.status == "scheduled"

    # ---------------------------------------------------------
    # 4. Scheduler processes the due record
    # ---------------------------------------------------------
    scheduler = SchedulerService(db)

    processed = scheduler.process_due_records()

    db.refresh(record)

    assert processed == 1
    assert record.status == "published"
    assert record.external_id is not None
    assert record.error is None
    assert record.published_at is not None

    # ---------------------------------------------------------
    # 5. Verify publish history
    # ---------------------------------------------------------
    history = (
        db.query(PublishHistory)
        .filter(
            PublishHistory.publish_record_id == record.id
        )
        .all()
    )

    assert len(history) >= 1

    latest = history[-1]

    assert latest.publish_record_id == record.id
    assert latest.variant_id == variant.id
    assert latest.platform == "mock"
    assert latest.status == "published"
    assert latest.external_id == record.external_id
    assert latest.error is None