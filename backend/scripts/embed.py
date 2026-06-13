import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import chromadb
from chromadb.utils import embedding_functions
from sqlalchemy import select

from database import AsyncSessionLocal
from models import Product

CHROMA_PATH = "./chroma_store"
COLLECTION_NAME = "products"

def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
    )

    return collection


async def embed_products():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()

        print(f"Fetched {len(products)} products from database")

        collection = get_collection()

        existing = collection.get()
        existing_ids = set(existing["ids"])

        documents = []
        metadatas = []
        ids = []

        for product in products:
            product_id = str(product.id)

            if product_id in existing_ids:
                print(f"Skipping {product.name} - already embedded")
                continue

            documents.append(product.description)
            metadatas.append({
                "name": product.name,
                "brand": product.brand,
                "category": product.category,
                "base_price_inr": product.base_price_inr,
            })
            ids.append(product_id)

        if not documents:
            print("All products are already embedded - nothing to do")
            return
        
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

        print(f"Embedded {len(documents)} products into ChromaDB")


if __name__ == "__main__":
    asyncio.run(embed_products())