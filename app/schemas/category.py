from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    type: str = Field(..., description="E.g., SYSTEM or CUSTOM")

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: str
    user_id: Optional[str]
    created_at: datetime\n