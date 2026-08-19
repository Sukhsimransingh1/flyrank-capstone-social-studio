from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.publish import PublishRecord
from app.models.variant import Variant
from app.publishers.registry import publisher_registry


class PublishService:
    """
    Handles the lifecycle of publishing a social-media variant.

    Responsibilities:
    - Validate that the variant exists.
    - Prevent duplicate publishing through idempotency keys.
    - Create a publish record.
    - Resolve the appropriate publisher adapter.
    - Execute publishing.
    - Persist success/failure state.
    """

    def __init__(self, db: Session):
        self.db = db

    def publish(
        self,
        variant_id: UUID,
        platform: str,
        slot: datetime,
        idempotency_key: str,
    ) -> PublishRecord:
        # ---------------------------------------------------------
        # 1. Idempotency check
        # ---------------------------------------------------------
        existing = self.db.scalar(
            select(PublishRecord).where(
                PublishRecord.idempotency_key == idempotency_key
            )
        )

        if existing is not None:
            return existing

        # ---------------------------------------------------------
        # 2. Load variant
        # ---------------------------------------------------------
        variant = self.db.get(Variant, variant_id)

        if variant is None:
            raise ValueError(
                f"Variant {variant_id} not found."
            )

        # ---------------------------------------------------------
        # 3. Validate platform
        # ---------------------------------------------------------
        if variant.platform != platform:
            raise ValueError(
                f"Variant platform is '{variant.platform}', "
                f"but publish request specified '{platform}'."
            )

        # ---------------------------------------------------------
        # 4. Create pending publish record
        # ---------------------------------------------------------
        record = PublishRecord(
            variant_id=variant.id,
            slot=slot,
            idempotency_key=idempotency_key,
            platform=platform,
            status="pending",
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        # ---------------------------------------------------------
        # 5. Resolve publisher adapter
        # ---------------------------------------------------------
        try:
            publisher = publisher_registry.get(platform)
        except ValueError as exc:
            record.status = "failed"
            record.error = str(exc)

            self.db.commit()
            self.db.refresh(record)

            return record

        # ---------------------------------------------------------
        # 6. Publish
        # ---------------------------------------------------------
        try:
            result = publisher.publish(
                variant.content
            )
        except Exception as exc:
            record.status = "failed"
            record.error = str(exc)

            self.db.commit()
            self.db.refresh(record)

            return record

        # ---------------------------------------------------------
        # 7. Persist result
        # ---------------------------------------------------------
        if result.success:
            record.status = "published"
            record.external_id = result.external_id
            record.published_at = datetime.now(timezone.utc)
            record.error = None
        else:
            record.status = "failed"
            record.error = result.error

        self.db.commit()
        self.db.refresh(record)

        return record