from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.publish import PublishRecord
from app.schemas.schedule import ScheduleCreate, ScheduleResponse


router = APIRouter(
    prefix="/schedule",
    tags=["Scheduling"],
)


@router.post(
    "",
    response_model=ScheduleResponse,
    status_code=201,
)
def create_schedule(
    payload: ScheduleCreate,
    db: Session = Depends(get_db),
):
    """
    Create a scheduled publishing record.

    Scheduling is idempotent:
    - The same idempotency key cannot create duplicate records.
    - The same variant cannot be scheduled twice for the same slot.
    """

    existing = db.scalar(
        select(PublishRecord).where(
            PublishRecord.idempotency_key == payload.idempotency_key
        )
    )

    if existing is not None:
        return existing

    duplicate_slot = db.scalar(
        select(PublishRecord).where(
            PublishRecord.variant_id == payload.variant_id,
            PublishRecord.slot == payload.slot,
        )
    )

    if duplicate_slot is not None:
        raise HTTPException(
            status_code=409,
            detail="Variant is already scheduled for this slot.",
        )

    record = PublishRecord(
        variant_id=payload.variant_id,
        slot=payload.slot,
        idempotency_key=payload.idempotency_key,
        platform=payload.platform,
        status="scheduled",
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@router.get(
    "/{variant_id}",
    response_model=list[ScheduleResponse],
)
def get_variant_schedule(
    variant_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Return all scheduled publishing records for a variant.
    """

    records = db.scalars(
        select(PublishRecord)
        .where(PublishRecord.variant_id == variant_id)
        .order_by(PublishRecord.slot.asc())
    ).all()

    return records