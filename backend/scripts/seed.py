import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent)) # will look upto whole backend folder for the required packages

from dotenv import load_dotenv
load_dotenv() # loaded before as database.py reads from environment at import time if it runs after environment variable will be None

from database import AsyncSessionLocal
from models import Product
from schemas import ProductCreate


DATA_DIR = Path(__file__).parent.parent.parent / "data"

JSON_FILES = [
    "laptops.json",
    "smartphones.json",
    "tablets.json",
    "tws.json",
]

def load_products() -> list[ProductCreate]:
    all_products = []

    for filename in JSON_FILES:
        filepath = DATA_DIR / filename
        with open(filepath, "r") as f:
            data = json.load(f)

        for entry in data:
            try:
                product = ProductCreate.model_validate(entry)
                all_products.append(product)
            except Exception as e:
                print(f"Validation failed for {entry.get('name', 'unknown')}: {e}")

    print(f"Loaded and validated {len(all_products)} products")
    return all_products


async def seed():
    products = load_products()

    async with AsyncSessionLocal() as session: # opening database sesssion directly
        inserted = 0
        skipped = 0

        for product in products:
            existing = await session.get(Product, product.id) # checking if product is alredy existed

            if existing:
                print(f"Skippinf {product.name} - already exists")
                skipped += 1
                continue

            data = product.model_dump()
            data["availability"] = [a.model_dump() for a in product.availability]

            db_product = Product(**data)
            session.add(db_product)
            inserted += 1

        await session.commit() # commiting all the staged products at once instead of one by one
        print(f" Seed complete - {inserted} inserted, {skipped} skipped")


if __name__ == "__main__":
    asyncio.run(seed())