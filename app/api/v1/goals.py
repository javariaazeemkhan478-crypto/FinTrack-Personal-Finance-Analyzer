from fastapi import APIRouter, Depends, HTTPException
from app.schemas.finance import GoalCreate, GoalResponse, GoalContribute
from app.api.dependencies import get_current_user
from app.database.connection import get_db
from bson import ObjectId
from datetime import datetime, UTC

router = APIRouter()

@router.post("/", response_model=GoalResponse)
async def create_goal(goal: GoalCreate, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    doc = goal.model_dump()
    doc["user_id"] = str(current_user["_id"])
    doc["current_amount"] = 0.0
    doc["progress_percentage"] = 0.0
    doc["remaining_amount"] = goal.target_amount
    doc["status"] = "ACTIVE"
    doc["created_at"] = datetime.now(UTC)
    doc["updated_at"] = datetime.now(UTC)
    
    result = await db.goals.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

@router.post("/{id}/contribute", response_model=GoalResponse)
async def contribute(id: str, contribution: GoalContribute, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    goal = await db.goals.find_one({"_id": ObjectId(id), "user_id": str(current_user["_id"])})
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    new_amount = goal["current_amount"] + contribution.amount
    progress = (new_amount / goal["target_amount"]) * 100
    status = "COMPLETED" if new_amount >= goal["target_amount"] else "ACTIVE"
    
    update_data = {
        "current_amount": new_amount,
        "progress_percentage": round(progress, 2),
        "remaining_amount": max(0.0, goal["target_amount"] - new_amount),
        "status": status,
        "updated_at": datetime.now(UTC)
    }
    
    await db.goals.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    goal.update(update_data)
    goal["id"] = str(goal.pop("_id"))
    return goal
