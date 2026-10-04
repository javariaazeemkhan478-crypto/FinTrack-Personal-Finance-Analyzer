from fastapi import APIRouter, Depends, status
from typing import List
from datetime import datetime
from bson import ObjectId
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse
from app.core.exceptions import NotFoundException, ValidationException
from app.database.connection import get_db
from app.api.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(budget: BudgetCreate, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    existing = await db.budgets.find_one({
        "user_id": current_user["id"],
        "category_id": budget.category_id,
        "month": budget.month,
        "year": budget.year
    })
    
    if existing:
        raise ValidationException("Budget already exists for this category and month")
        
    b_dict = budget.model_dump()
    b_dict["user_id"] = current_user["id"]
    b_dict["spent_amount"] = 0.0
    b_dict["remaining_amount"] = budget.monthly_limit
    b_dict["usage_percentage"] = 0.0
    b_dict["is_exceeded"] = False
    b_dict["created_at"] = datetime.utcnow()
    b_dict["updated_at"] = datetime.utcnow()
    
    result = await db.budgets.insert_one(b_dict)
    b_dict["id"] = str(result.inserted_id)
    return b_dict

@router.get("/", response_model=List[BudgetResponse])
async def get_budgets(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    cursor = db.budgets.find({"user_id": current_user["id"]})
    budgets = []
    async for b in cursor:
        b["id"] = str(b["_id"])
        budgets.append(b)
    return budgets

@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(budget_id: str, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    result = await db.budgets.delete_one({"_id": ObjectId(budget_id), "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise NotFoundException("Budget")
    return None
