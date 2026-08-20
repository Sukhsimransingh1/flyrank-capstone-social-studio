from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.publish import PublishRecord
from app.services.publish_service import PublishService


class SchedulerService:
    """
    Finds scheduled records that are due and sends them
    through the existing PublishService.
    """

    def __init__(self, db: Session):
        self.db = db
        self.publisher = PublishService(db)

    def process_due_records(self) -> int:
        now = datetime.now(timezone.utc)

        records = self.db.scalars(
            select(PublishRecord)
            .where(
                PublishRecord.status == "scheduled",
                PublishRecord.slot <= now,
            )
            .order_by(PublishRecord.slot.asc())
        ).all()

        processed = 0

        for record in records:
            try:
                self.publisher.publish(
                    variant_id=record.variant_id,
                    platform=record.platform,
                    slot=record.slot,
                    idempotency_key=record.idempotency_key,
                )

                processed += 1

            except Exception as exc:
                record.status = "failed"
                record.error = str(exc)
                self.db.commit()

        return processed