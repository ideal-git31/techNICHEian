from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from database import get_db
from models import Product
from schemas import ProductCreate, ProductResponse

router = APIRouter(
    prefix="/products",
    tags=["products"],
)

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    db_product = Product(
        id = product.id or uuid.uuid4(),
        name = product.name,
        brand = product.brand,
        brand_website_url = product.brand_website_url,
        category = product.category,
        launch_year = product.launch_year,
        base_price_inr = product.base_price_inr,
        base_price_source = product.base_price_source,
        availability = [a.model_dump() for a in product.availability],
        specs = product.specs,
        pros = product.pros,
        cons = product.cons,
        use_cases = product.use_cases,
        description = product.description,
        image_url = product.image_url,
        tags = product.tags,
    )

    db.add(db_product)
    await db.flush()
    await db.refresh(db_product)
    return ProductResponse.model_validate(db_product)

@router.get("/", response_model=list[ProductResponse])
async def get_products(
    category: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    brand: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Product)

    if category:
        query = query.where(Product.category == category)
    if brand:
        query = query.where(Product.brand == brand)
    if min_price:
        query = query.where(Product.base_price_inr >= min_price)
    if max_price: 
        query = query.where(Product.base_price_inr <= max_price)

    result = await db.execute(query)
    products = result.scalars().all()
    return [ProductResponse.model_validate(p) for p in products]

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalars().first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    
    return ProductResponse.model_validate(product)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: uuid.UUID,
    product: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    db_product = result.scalars().first()

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )
    
    db_product.name = product.name
    db_product.brand = product.brand
    db_product.brand_website_url = product.brand_website_url
    db_product.category = product.category
    db_product.launch_year = product.launch_year
    db_product.base_price_inr = product.base_price_inr
    db_product.base_price_source = product.base_price_source
    db_product.availability = [a.model_dump() for a in product.availability]
    db_product.specs = product.specs
    db_product.pros = product.pros
    db_product.cons = product.cons
    db_product.use_cases = product.use_cases
    db_product.description = product.description
    db_product.image_url = product.image_url
    db_product.tags = product.tags

    await db.flush()
    await db.refresh(db_product)
    return ProductResponse.model_validate(db_product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    db_product = result.scalars().first()

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )
    
    await db.delete(db_product)
    await db.flush()