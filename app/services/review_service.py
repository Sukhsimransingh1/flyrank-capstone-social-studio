from sqlalchemy.orm import Session

from app.models.variant import Variant
from app.services.validator import validate_variant


class ReviewError(Exception):
    pass


def approve_variant(
    db: Session,
    variant: Variant,
) -> Variant:
    if variant.status not in {"draft", "rejected"}:
        raise ReviewError(
            f"Cannot approve variant in '{variant.status}' state."
        )

    validation_errors = validate_variant(
        content=variant.content,
        platform=variant.platform,
    )

    if validation_errors:
        variant.validation_errors = "\n".join(validation_errors)

        db.commit()
        db.refresh(variant)

        raise ReviewError(
            "Variant cannot be approved because it violates "
            "platform constraints."
        )

    variant.validation_errors = None
    variant.status = "approved"

    db.commit()
    db.refresh(variant)

    return variant


def reject_variant(
    db: Session,
    variant: Variant,
) -> Variant:
    if variant.status != "draft":
        raise ReviewError(
            f"Cannot reject variant in '{variant.status}' state."
        )

    variant.status = "rejected"

    db.commit()
    db.refresh(variant)

    return variant