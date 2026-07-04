from pydantic import BaseModel, Field
from typing import Optional

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    slug: str
    is_active: bool = True

class CategoryCreate(CategoryBase):
    pass

class CategoryInDB(CategoryBase):
    id: str = Field(alias="_id")

    model_config = {"populate_by_name": True}

class CategoryResponse(CategoryBase):
    id: str = Field(alias="_id")

    model_config = {"populate_by_name": True, "from_attributes": True}
