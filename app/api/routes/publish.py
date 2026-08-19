from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.publish import PublishRequest, PublishResponse
from app.services.publish_service import PublishService


router = APIRouter(
    prefix="/publish",
    tags=["publishing"],
)


@router.post(
    "",
    response_model=PublishResponse,
    status_code=status.HTTP_200_OK,
)
def publish_variant(
    request: PublishRequest,
    db: Session = Depends(get_db),
):
    service = PublishService(db)

    try:
        record = service.publish(
            variant_id=request.variant_id,
            platform=request.platform,
            slot=request.slot,
            idempotency_key=request.idempotency_key,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return PublishResponse(
        id=record.id,
        variant_id=record.variant_id,
        platform=record.platform,
        status=record.status,
        idempotency_key=record.idempotency_key,
        external_id=record.external_id,
        error=record.error,
        slot=record.slot,
        published_at=record.published_at,
    )