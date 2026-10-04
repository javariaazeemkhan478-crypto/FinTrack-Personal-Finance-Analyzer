from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.database.connection import get_db
from app.api.dependencies import get_current_user
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.get("/overview")
async def get_overview(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    pipeline = [
        {"$match": {"user_id": current_user["id"]}},
        {"$group": {
            "_id": "$transaction_type",
            "total": {"$sum": "$amount"},
            "count": {"$sum": 1}
        }}
    ]
    
    cursor = db.transactions.aggregate(pipeline)
    
    total_income = 0
    total_expenses = 0
    total_count = 0
    
    async for doc in cursor:
        if doc["_id"] == "INCOME":
            total_income = doc["total"]
        elif doc["_id"] == "EXPENSE":
            total_expenses = doc["total"]
        total_count += doc["count"]
            
    balance = total_income - total_expenses
    savings_rate = 0
    if total_income > 0:
        savings_rate = ((total_income - total_expenses) / total_income) * 100
        
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
        "savings_rate": savings_rate,
        "total_transactions": total_count
    }
