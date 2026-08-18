from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.variant import VariantResponse, VariantUpdate
from app.services.validator import validate_variant
from app.services.variant_service import get_variant


router = APIRouter(
    prefix="/variants",
    tags=["Variants"],
)


@router.get(
    "/{variant_id}",
    response_model=VariantResponse,
)
def get_variant_endpoint(
    variant_id: UUID,
    db: Session = Depends(get_db),
):
    variant = get_variant(
        db=db,
        variant_id=variant_id,
    )

    if variant is None:
        raise HTTPException(
            status_code=404,
            detail="Variant not found.",
        )

    return variant


@router.put(
    "/{variant_id}",
    response_model=VariantResponse,
)
def update_variant_endpoint(
    variant_id: UUID,
    payload: VariantUpdate,
    db: Session = Depends(get_db),
):
    variant = get_variant(
        db=db,
        variant_id=variant_id,
    )

    if variant is None:
        raise HTTPException(
            status_code=404,
            detail="Variant not found.",
        )

    errors = validate_variant(
        content=payload.content,
        platform=variant.platform,
    )

    variant.content = payload.content
    variant.validation_errors = (
        "\n".join(errors)
        if errors
        else None
    )

    db.commit()
    db.refresh(variant)

    return variant