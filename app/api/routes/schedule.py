from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.publish import PublishRecord
from app.models.variant import Variant, VariantStatus
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

    Rules:
    - The same idempotency key cannot create duplicate records.
    - The same variant cannot be scheduled twice for the same slot.
    - Only approved variants can be scheduled.
    - The platform must match the variant platform.
    """

    # ---------------------------------------------------------
    # 1. Idempotency check
    # ---------------------------------------------------------
    existing = db.scalar(
        select(PublishRecord).where(
            PublishRecord.idempotency_key == payload.idempotency_key
        )
    )

    if existing is not None:
        return existing

    # ---------------------------------------------------------
    # 2. Load variant
    # ---------------------------------------------------------
    variant = db.get(Variant, payload.variant_id)

    if variant is None:
        raise HTTPException(
            status_code=404,
            detail="Variant not found.",
        )

    # ---------------------------------------------------------
    # 3. Only approved variants can be scheduled
    # ---------------------------------------------------------
    if variant.status != VariantStatus.APPROVED.value:
        raise HTTPException(
            status_code=409,
            detail="Only approved variants can be scheduled.",
        )

    # ---------------------------------------------------------
    # 4. Validate platform
    # ---------------------------------------------------------
    if variant.platform != payload.platform:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Variant platform is '{variant.platform}', "
                f"but schedule request specified '{payload.platform}'."
            ),
        )

    # ---------------------------------------------------------
    # 5. Prevent duplicate scheduling for same variant + slot
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 6. Create scheduled record
    # ---------------------------------------------------------
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