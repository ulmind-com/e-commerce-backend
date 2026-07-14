from pydantic import BaseModel, Field
from typing import Optional

class BrandBase(BaseModel):
    name: str
    description: Optional[str] = None
    slug: str
    is_active: bool = True
    logo_url: Optional[str] = None

class BrandCreate(BrandBase):
    pass

class BrandInDB(BrandBase):
    id: str = Field(alias="_id")

    model_config = {"populate_by_name": True}

class BrandResponse(BrandBase):
    id: str = Field(alias="_id")

    model_config = {"populate_by_name": True, "from_attributes": True}
