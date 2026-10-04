from fastapi import APIRouter, Depends, status
from typing import List
from datetime import datetime
from bson import ObjectId
from app.schemas.category import CategoryCreate, CategoryResponse
from app.core.exceptions import NotFoundException, ValidationException
from app.database.connection import get_db
from app.api.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    c_dict = category.model_dump()
    c_dict["user_id"] = current_user["id"]
    c_dict["created_at"] = datetime.utcnow()
    
    result = await db.categories.insert_one(c_dict)
    c_dict["id"] = str(result.inserted_id)
    return c_dict

@router.get("/", response_model=List[CategoryResponse])
async def get_categories(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    # Get user categories AND system categories (where user_id is None)
    query = {"$or": [{"user_id": current_user["id"]}, {"type": "SYSTEM"}]}
    cursor = db.categories.find(query)
    categories = []
    async for c in cursor:
        c["id"] = str(c["_id"])
        categories.append(c)
    return categories

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: str, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    # Cannot delete if transactions are using it
    count = await db.transactions.count_documents({"category_id": category_id})
    if count > 0:
        raise ValidationException("Cannot delete category in use by transactions")
        
    result = await db.categories.delete_one({"_id": ObjectId(category_id), "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise NotFoundException("Category")
    return None
