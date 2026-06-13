from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from database import get_db
from models import Product, Feedback
from schemas import FeedbackCreate, FeedbackResponse


router = APIRouter(
    prefix="/feedback",
    tags=["feedback"]
)

@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback: FeedbackCreate,
    db: AsyncSession = Depends(get_db)
):
    product = await db.get(Product, feedback.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {feedback.product_id} not found",
        )
    
    db_feedback = Feedback(
        id = uuid.uuid4(),
        product_id = feedback.product_id,
        username = feedback.username,
        rating = feedback.rating,
        comment = feedback.comment,
    )

    db.add(db_feedback)
    await db.flush()
    await db.refresh(db_feedback)
    return FeedbackResponse.model_validate(db_feedback)

@router.get("/{product_id}", response_model=list[FeedbackResponse])
async def get_product_feedback(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )
    
    result = await db.execute(
        select(Feedback)
        .where(Feedback.product_id == product_id)
        .order_by(Feedback.created_at.desc())
    )
    feedbacks = result.scalars().all()

    return [FeedbackResponse.model_validate(f) for f in feedbacks]