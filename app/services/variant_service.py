from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.variant import Variant
from app.models.post import Post
from app.services.validator import validate_variant
from app.services.variant_generator import generate_variant_content


SUPPORTED_PLATFORMS = (
    "telegram",
    "x",
    "linkedin",
)


def generate_variants(
    db: Session,
    post: Post,
) -> list[Variant]:
    variants: list[Variant] = []

    for platform in SUPPORTED_PLATFORMS:
        content = generate_variant_content(
            post=post,
            platform=platform,
        )

        validation_errors = validate_variant(
            content=content,
            platform=platform,
        )

        variant = Variant(
            post_id=post.id,
            platform=platform,
            content=content,
            status="draft",
            validation_errors=(
                "\n".join(validation_errors)
                if validation_errors
                else None
            ),
        )

        db.add(variant)
        variants.append(variant)

    db.commit()

    for variant in variants:
        db.refresh(variant)

    return variants


def get_variants_for_post(
    db: Session,
    post_id: UUID,
) -> list[Variant]:
    statement = (
        select(Variant)
        .where(Variant.post_id == post_id)
        .order_by(Variant.created_at)
    )

    return list(db.scalars(statement).all())


def get_variant(
    db: Session,
    variant_id: UUID,
) -> Variant | None:
    return db.get(Variant, variant_id)