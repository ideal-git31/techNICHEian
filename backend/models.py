import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

# Product class + Identity Columns
class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.UUID,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    brand_website_url: Mapped[str] = mapped_column(Text, nullable=False)

    # Category, Pricing and Timestamps
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    launch_year: Mapped[int] = mapped_column(Integer, nullable=False)
    base_price_inr: Mapped[int] = mapped_column(Integer, nullable=False)
    base_price_source: Mapped[str] = mapped_column(String(100), nullable=False, default="Brand Website")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Availability, specs, pros and cons
    availability: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    specs: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    
    pros: Mapped[list] = mapped_column(ARRAY(Text), nullable=False, default=list)
    cons: Mapped[list] = mapped_column(ARRAY(Text), nullable=False, default=list)
    use_cases: Mapped[list] = mapped_column(ARRAY(Text), nullable=False, default=list)
    tags: Mapped[list] = mapped_column(ARRAY(Text), nullable=False, default=list)

    # Description and Image URL
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str] = mapped_column(Text, nullable=False, default="")

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name!r} category={self.category!r}>"
    
class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.UUID,
        nullable=False,
    )    
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self):
        return f"<Feedback id={self.id} product_id={self.product_id} rating={self.rating}>"