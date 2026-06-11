import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

class AvailabilityItem(BaseModel):
    platform: str = Field(..., examples=["Amazon Indian", "Flipkart"])
    url: str = Field(..., examples=["https://www.amazon.in/..."])
    price_inr: int = Field(..., gt=0)

class LaptopSpecs(BaseModel):
    processor: str
    ram_gb: int
    storage_gb: int
    display_inches: float
    display_type: str
    battery_whr: float
    weight_kg: float 
    os: str
    gpu: str

class SmartphoneSpecs(BaseModel):
    processor: str
    ram_gb: int
    storage_gb: int
    battery_mah: int
    display_inches: float
    display_type: str
    camera_mp: int
    os: str
    weight_grams: int
    charging_watts: int

class TabletSpecs(BaseModel):
    processor: str
    ram_gb: int
    storage_gb: int
    display_inches: float
    display_type: str
    battery_mah: int
    os: str
    weight_grams: int
    stylus_support: bool
    cellular: bool    

class TWSSpecs(BaseModel):
    driver_size_mm: int
    anc: bool
    battery_hrs_buds: float
    battery_hrs_case: float
    connectivity: str
    ipx_rating: str
    charging_type: str
    multipoint: bool    

CATEGORY_SPECS_MAP: dict[str, type[BaseModel]] = {
    "laptop": LaptopSpecs,
    "smartphone": SmartphoneSpecs,
    "tablet": TabletSpecs,
    "tws": TWSSpecs,
}    

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    brand: str = Field(..., min_length=1, max_length=100)
    brand_website_url: str
    category: str = Field(..., pattern="^(laptop|smartphone|tablet|tws)$")
    launch_year: int = Field(..., ge=2000, le=2100)
    base_price_inr: int = Field(..., gt=0),
    base_price_source: str = Field(default="Brand Website")
    availability: list[AvailabilityItem] = Field(..., min_length=1)
    specs: dict[str, Any]
    pros: list[str] = Field(..., min_length=1)
    cons: list[str] = Field(..., min_length=1)
    use_cases: list[str] = Field(..., min_length=1)
    description: str = Field(..., min_length=50)
    image_url: str = Field(default="") 
    tags: list[str] = Field(..., min_length=1)

    @field_validator("category")
    @classmethod
    def category_must_be_valid(cls, v: str) -> str:
        allowed = {"laptop", "smartphone", "tablet", "tws"}
        if v not in allowed:
            raise ValueError(f"category must be one of the {allowed}, got {v!r}")
        return v
    
class ProductCreate(ProductBase):
    id: uuid.UUID | None = Field(
        default=None,
        description="Optional - if provided, preserves the UUID from seed JSON",
    ) 

    @model_validator(mode="after")
    def validate_spec_for_category(self) -> "ProductCreate":
        specs_model = CATEGORY_SPECS_MAP.get(self.category)
        if specs_model is None:
            raise ValueError(f"No specs model is found for category {self.category!r}")   
        specs_model.model_validate(self.specs)
        return self
    
class ProductResponse(ProductBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}   

class ProductSearchRequest(BaseModel):
    query: str = Field(...,
         min_length=3,
         max_length=500,
         examples=["I need a lightweight laptop for college under 60000"],                           
    )
    category: str | None = Field(
        default=None,
        pattern="^(laptop|smartphone|tablet|tws)$",
    )  
    max_price_inr: int | None = Field(default=None, gt=0)
    min_price_inr: int | None = Field(default=None, gt=0)
    top_k: int = Field(default=5, ge=1, le=20)

class ProductSearchResult(BaseModel):
    product: ProductResponse
    score: float = Field(..., ge=0.0, le=1.0)

class ProductSearchResponse(BaseModel):
    query: str
    results: list[ProductSearchResult]
    total: int    


class FeedbackCreate(BaseModel):
    product_id: uuid.UUID
    username: str | None = Field(default=None, max_length=100)
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(default="", max_length=2000)

class FeedbackResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    username: str | None
    rating: int
    comment: str
    created_at: datetime

    model_config = {"from_attributes": True}    


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    product_ids: list[uuid.UUID] = Field(
        default_factory=list,
        description="IDs of products currently in the result feed"
    )    
    conversation_history: list[dict[str, str]] = Field(
        default_factory=list,
        description="[{role: user|assistant, content: str}, ...]"
    )

class ChatResponse(BaseModel):
    answer: str
    sources: list[uuid.UUID] = Field(
        default_factory=list,
        description="Product Ids referenced in the answer"
    )    