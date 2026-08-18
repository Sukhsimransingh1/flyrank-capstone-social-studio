from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.post import PostCreate, PostResponse
from app.schemas.variant import VariantResponse
from app.services.post_service import create_post, get_post
from app.services.variant_service import (
    generate_variants,
    get_variants_for_post,
)


router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post_endpoint(
    payload: PostCreate,
    db: Session = Depends(get_db),
):
    return create_post(
        db=db,
        payload=payload,
    )


@router.get(
    "/{post_id}/variants",
    response_model=list[VariantResponse],
)
def get_post_variants(
    post_id: UUID,
    db: Session = Depends(get_db),
):
    post = get_post(
        db=db,
        post_id=post_id,
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    return get_variants_for_post(
        db=db,
        post_id=post_id,
    )


@router.post(
    "/{post_id}/generate",
    response_model=list[VariantResponse],
    status_code=status.HTTP_201_CREATED,
)
def generate_post_variants(
    post_id: UUID,
    db: Session = Depends(get_db),
):
    post = get_post(
        db=db,
        post_id=post_id,
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    return generate_variants(
        db=db,
        post=post,
    )


@router.get(
    "/{post_id}",
    response_model=PostResponse,
)
def get_post_endpoint(
    post_id: UUID,
    db: Session = Depends(get_db),
):
    post = get_post(
        db=db,
        post_id=post_id,
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )

    return post