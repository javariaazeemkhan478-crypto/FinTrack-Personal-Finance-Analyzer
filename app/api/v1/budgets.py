from fastapi import APIRouter, Depends, HTTPException
from app.schemas.finance import BudgetCreate, BudgetResponse
from app.api.dependencies import get_current_user
from app.database.connection import get_db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=BudgetResponse)
async def create_budget(budget: BudgetCreate, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    # Duplicate check
    existing = await db.budgets.find_one({
        "user_id": str(current_user["_id"]),
        "category": budget.category,
        "month": budget.month,
        "year": budget.year
    })
    if existing:
        raise HTTPException(status_code=400, detail="Budget already exists for this category and month")

    doc = budget.model_dump()
    doc["user_id"] = str(current_user["_id"])
    doc["spent"] = 0.0
    doc["remaining"] = budget.amount
    doc["percentage_used"] = 0.0
    doc["exceeded"] = False
    
    result = await db.budgets.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc
