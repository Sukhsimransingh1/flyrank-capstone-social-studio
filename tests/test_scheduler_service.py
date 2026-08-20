from datetime import datetime, timedelta, timezone

from app.models.publish import PublishRecord
from app.models.variant import Variant
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


def test_due_record_is_published(db, variant):
    record = create_scheduled_record(
        db,
        variant,
        datetime.now(timezone.utc) - timedelta(minutes=1),
        "scheduler-success-001",
    )

    scheduler = SchedulerService(db)

    processed = scheduler.process_due_records()

    db.refresh(record)

    assert processed == 1
    assert record.status == "published"
    assert record.external_id is not None
    assert record.published_at is not None
    assert record.error is None


def test_future_record_is_not_processed(db, variant):
    record = create_scheduled_record(
        db,
        variant,
        datetime.now(timezone.utc) + timedelta(hours=1),
        "scheduler-future-001",
    )

    scheduler = SchedulerService(db)

    processed = scheduler.process_due_records()

    db.refresh(record)

    assert processed == 0
    assert record.status == "scheduled"


def test_scheduler_does_not_create_duplicate_record(db, variant):
    record = create_scheduled_record(
        db,
        variant,
        datetime.now(timezone.utc) - timedelta(minutes=1),
        "scheduler-idempotency-001",
    )

    scheduler = SchedulerService(db)

    scheduler.process_due_records()

    db.refresh(record)

    count = (
        db.query(PublishRecord)
        .filter(
            PublishRecord.variant_id == variant.id,
            PublishRecord.slot == record.slot,
        )
        .count()
    )

    assert count == 1
    assert record.status == "published"


def test_scheduler_processes_records_in_slot_order(db, variant):
    first = create_scheduled_record(
        db,
        variant,
        datetime.now(timezone.utc) - timedelta(minutes=2),
        "scheduler-order-001",
    )

    second = create_scheduled_record(
        db,
        variant,
        datetime.now(timezone.utc) - timedelta(minutes=1),
        "scheduler-order-002",
    )

    scheduler = SchedulerService(db)

    processed = scheduler.process_due_records()

    db.refresh(first)
    db.refresh(second)

    assert processed == 2
    assert first.status == "published"
    assert second.status == "published"