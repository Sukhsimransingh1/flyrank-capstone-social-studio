from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.variant import VariantResponse, VariantUpdate
from app.services.review_service import (
    ReviewError,
    approve_variant,
    reject_variant,
)
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

    if variant.status == "published":
        raise HTTPException(
            status_code=409,
            detail="Published variants cannot be edited.",
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

    # Editing an approved variant sends it back
    # into review.
    if variant.status == "approved":
        variant.status = "draft"

    db.commit()
    db.refresh(variant)

    return variant


@router.post(
    "/{variant_id}/approve",
    response_model=VariantResponse,
)
def approve_variant_endpoint(
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

    try:
        return approve_variant(
            db=db,
            variant=variant,
        )

    except ReviewError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


@router.post(
    "/{variant_id}/reject",
    response_model=VariantResponse,
)
def reject_variant_endpoint(
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

    try:
        return reject_variant(
            db=db,
            variant=variant,
        )

    except ReviewError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc