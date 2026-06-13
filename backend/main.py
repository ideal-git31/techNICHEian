from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import products, search, feedback

app = FastAPI(
    title="TechNICHEian API",
    description="Backend API fo TechNICHEian product discovery platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://techNICHEian.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(search.router)
app.include_router(feedback.router)