import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.publish import PublishRecord
from app.publishers.registry import publisher_registry


logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Processes scheduled publishing records that are due.

    Lifecycle:

        scheduled -> publishing -> published
                              -> failed

    The existing PublishRecord is updated in place so the scheduler
    never creates duplicate records for an already scheduled job.
    """

    def __init__(self, db: Session):
        self.db = db

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

        logger.info(
            "Scheduler found %s due record(s).",
            len(records),
        )

        processed = 0

        for record in records:
            logger.info(
                "Processing publish record id=%s platform=%s slot=%s.",
                record.id,
                record.platform,
                record.slot,
            )

            self._process_record(record)
            processed += 1

        logger.info(
            "Scheduler iteration completed. processed=%s.",
            processed,
        )

        return processed

    def _process_record(self, record: PublishRecord) -> None:
        record.status = "publishing"
        record.error = None

        self.db.commit()
        self.db.refresh(record)

        logger.info(
            "Publish record id=%s transitioned to publishing.",
            record.id,
        )

        try:
            publisher = publisher_registry.get(record.platform)

            result = publisher.publish(
                self._get_variant_content(record.variant_id)
            )

            if result.success:
                record.status = "published"
                record.external_id = result.external_id
                record.published_at = datetime.now(timezone.utc)
                record.error = None

                logger.info(
                    "Publish record id=%s published successfully "
                    "external_id=%s.",
                    record.id,
                    record.external_id,
                )

            else:
                record.status = "failed"
                record.error = result.error

                logger.error(
                    "Publish record id=%s failed: %s",
                    record.id,
                    record.error,
                )

        except Exception as exc:
            record.status = "failed"
            record.error = str(exc)

            logger.exception(
                "Publish record id=%s raised an exception.",
                record.id,
            )

        self.db.commit()
        self.db.refresh(record)

        logger.info(
            "Publish record id=%s final status=%s.",
            record.id,
            record.status,
        )

    def _get_variant_content(self, variant_id):
        from app.models.variant import Variant

        variant = self.db.get(Variant, variant_id)

        if variant is None:
            raise ValueError(
                f"Variant {variant_id} not found."
            )

        return variant.content