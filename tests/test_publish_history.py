from datetime import datetime, timedelta, timezone

from app.models.publish import PublishRecord
from app.models.publish_history import PublishHistory
from app.services.scheduler_service import SchedulerService


def create_scheduled_record(db, variant, slot, key):
    record = PublishRecord(
        variant_id=variant.id,
        slot=slot,
        idempotency_key=key,
        platform=variant.platform,
        status="scheduled",
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def test_successful_publish_creates_history(db, variant):
    record = create_scheduled_record(
        db,
        variant,
        datetime.now(timezone.utc) - timedelta(minutes=1),
        "history-success-001",
    )

    scheduler = SchedulerService(db)

    processed = scheduler.process_due_records()

    history = (
        db.query(PublishHistory)
        .filter(
            PublishHistory.publish_record_id == record.id
        )
        .all()
    )

    assert processed == 1
    assert len(history) == 1

    assert history[0].status == "published"
    assert history[0].platform == variant.platform
    assert history[0].variant_id == variant.id
    assert history[0].external_id is not None
    assert history[0].error is None
    assert history[0].attempted_at is not None


def test_failed_publish_creates_history(db, variant):
    record = create_scheduled_record(
        db,
        variant,
        datetime.now(timezone.utc) - timedelta(minutes=1),
        "history-failure-001",
    )

    original_get = __import__(
        "app.services.scheduler_service",
        fromlist=["publisher_registry"],
    ).publisher_registry.get

    class FailingPublisher:
        def publish(self, content):
            raise RuntimeError("publisher unavailable")

    module = __import__(
        "app.services.scheduler_service",
        fromlist=["publisher_registry"],
    )

    module.publisher_registry.get = lambda platform: FailingPublisher()

    try:
        scheduler = SchedulerService(db)

        processed = scheduler.process_due_records()

        history = (
            db.query(PublishHistory)
            .filter(
                PublishHistory.publish_record_id == record.id
            )
            .all()
        )

        assert processed == 1
        assert len(history) == 1
        assert history[0].status == "failed"
        assert history[0].external_id is None
        assert "publisher unavailable" in history[0].error

    finally:
        module.publisher_registry.get = original_get