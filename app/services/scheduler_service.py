import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.publish import PublishRecord
from app.publishers.registry import publisher_registry
from app.services.telegram_service import TelegramService


logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Processes scheduled publishing records that are due.

    Lifecycle:

        scheduled -> publishing -> published
                              -> failed

    Telegram notifications are sent after processing.
    """

    def __init__(self, db: Session):
        self.db = db
        self.telegram = TelegramService()

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
            self._process_record(record)
            processed += 1

        logger.info(
            "Scheduler iteration completed. processed=%s",
            processed,
        )

        return processed

    def _process_record(self, record: PublishRecord) -> None:
        record.status = "publishing"
        record.error = None

        self.db.commit()
        self.db.refresh(record)

        try:
            publisher = publisher_registry.get(record.platform)

            content = self._get_variant_content(
                record.variant_id
            )

            result = publisher.publish(content)

            if result.success:
                record.status = "published"
                record.external_id = result.external_id
                record.published_at = datetime.now(timezone.utc)
                record.error = None

                self.db.commit()
                self.db.refresh(record)

                logger.info(
                    "Published record %s successfully.",
                    record.id,
                )

                self.telegram.send_message(
                    self._success_message(record)
                )

            else:
                record.status = "failed"
                record.error = result.error

                self.db.commit()
                self.db.refresh(record)

                logger.error(
                    "Publishing failed for record %s: %s",
                    record.id,
                    result.error,
                )

                self.telegram.send_message(
                    self._failure_message(record)
                )

        except Exception as exc:
            record.status = "failed"
            record.error = str(exc)

            self.db.commit()
            self.db.refresh(record)

            logger.exception(
                "Scheduler failed processing record %s.",
                record.id,
            )

            self.telegram.send_message(
                self._failure_message(record)
            )

    def _get_variant_content(self, variant_id):
        from app.models.variant import Variant

        variant = self.db.get(Variant, variant_id)

        if variant is None:
            raise ValueError(
                f"Variant {variant_id} not found."
            )

        return variant.content

    @staticmethod
    def _success_message(record: PublishRecord) -> str:
        return (
            "✅ FlyRank Social Studio\n\n"
            "Scheduled post published successfully.\n\n"
            f"Platform: {record.platform}\n"
            f"Record ID: {record.id}\n"
            f"External ID: {record.external_id}"
        )

    @staticmethod
    def _failure_message(record: PublishRecord) -> str:
        return (
            "❌ FlyRank Social Studio\n\n"
            "Scheduled post failed.\n\n"
            f"Platform: {record.platform}\n"
            f"Record ID: {record.id}\n"
            f"Error: {record.error}"
        )