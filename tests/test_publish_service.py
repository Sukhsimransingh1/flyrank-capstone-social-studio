from datetime import datetime, timezone

from app.services.publish_service import PublishService


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