from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import chromadb
from chromadb.utils import embedding_functions

from database import get_db
from models import Product
from schemas import(
    ProductResponse,
    ProductSearchRequest,
    ProductSearchResult,
    ProductSearchResponse,
)



router = APIRouter(
    prefix="/search",
    tags=["search"]
)

CHROMA_PATH = "./chroma_store"
COLLECTION_NAME = "products"

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn,
)

@router.post("/", response_model=ProductSearchResponse)
async def search_products(
    request: ProductSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    # Layer 1: SQL pre-filter 
    query = select(Product)

    if request.category:
        query = query.where(Product.category == request.category)
    if request.min_price_inr:
        query = query.where(Product.base_price_inr >= request.min_price_inr)
    if request.max_price_inr:
        query = query.where(Product.base_price_inr <= request.max_price_inr)
    
    result = await db.execute(query)
    filtered_products = result.scalars().all()

    if not filtered_products:
        return ProductSearchResponse(
            query=request.query,
            result=[],
            total=0,
        )
    
    # Layer 2: ChromaDB semantic search
    filtered_ids = [str(p.id) for p in filtered_products]

    chroma_reaults = collection.query(
        query_texts=[request.query],
        n_results=min(request.top_k, len(filtered_ids)),
        ids=filtered_ids,
    )

    matched_ids = chroma_reaults["ids"][0]
    matched_distances = chroma_reaults["distances"][0]

    # Layer 3: Build Response
    product_map = {str(p.id): p for p in filtered_products}

    results = []
    for product_id, distance in zip(matched_ids, matched_distances):
        product = product_map.get(product_id)
        if not product:
            continue
        score = round(1 - distance, 4)
        results.append(
            ProductSearchResult(
                product = ProductResponse.model_validate(product),
                score = score,
            )
        )

    return ProductSearchResponse(
        query = request.query,
        results = results,
        total = len(results),
    )