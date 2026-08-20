from datetime import datetime, timedelta, timezone

from app.models.publish import PublishRecord
from app.models.variant import VariantStatus


def test_unapproved_variant_cannot_be_scheduled(
    client,
    db,
    variant,
):
    variant.status = VariantStatus.DRAFT.value
    db.commit()
    db.refresh(variant)

    response = client.post(
        "/schedule",
        json={
            "variant_id": str(variant.id),
            "platform": variant.platform,
            "slot": (
                datetime.now(timezone.utc) + timedelta(hours=1)
            ).isoformat(),
            "idempotency_key": "blocked-schedule-test-001",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Only approved variants can be scheduled."
    )

    record = db.query(PublishRecord).filter(
        PublishRecord.idempotency_key
        == "blocked-schedule-test-001"
    ).first()

    assert record is None