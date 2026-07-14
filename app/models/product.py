from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ProductBase(BaseModel):
    title: str
    description: str = ""
    price: float
    original_price: float = 0.0
    rating: float = 0.0
    returns_policy: str = "7 days"
    warranty: str = "No Warranty"
    stock_quantity: int
    category_id: Optional[str] = None
    brand_id: Optional[str] = None
    image_urls: List[str] = []
    is_published: bool = True
    express_delivery_distance_km: float = 0.0

class ProductCreate(ProductBase):
    pass

class ProductInDB(ProductBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}

class ProductResponse(ProductBase):
    id: str = Field(alias="_id")
    created_at: datetime = datetime.utcnow()

    model_config = {"populate_by_name": True, "from_attributes": True}
