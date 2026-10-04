from fastapi import APIRouter, Depends, status
from typing import List
from datetime import datetime
from bson import ObjectId
from app.schemas.goal import GoalCreate, GoalContribute, GoalResponse, GoalStatus
from app.core.exceptions import NotFoundException
from app.database.connection import get_db
from app.api.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(goal: GoalCreate, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    g_dict = goal.model_dump()
    g_dict["user_id"] = current_user["id"]
    g_dict["saved_amount"] = 0.0
    g_dict["status"] = GoalStatus.ACTIVE.value
    g_dict["progress_percentage"] = 0.0
    g_dict["created_at"] = datetime.utcnow()
    g_dict["updated_at"] = datetime.utcnow()
    
    result = await db.goals.insert_one(g_dict)
    g_dict["id"] = str(result.inserted_id)
    return g_dict

@router.get("/", response_model=List[GoalResponse])
async def get_goals(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    cursor = db.goals.find({"user_id": current_user["id"]})
    goals = []
    async for g in cursor:
        g["id"] = str(g["_id"])
        goals.append(g)
    return goals

@router.post("/{goal_id}/contribute", response_model=GoalResponse)
async def contribute_goal(goal_id: str, contribution: GoalContribute, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    g = await db.goals.find_one({"_id": ObjectId(goal_id), "user_id": current_user["id"]})
    if not g:
        raise NotFoundException("Goal")
        
    new_amount = g["saved_amount"] + contribution.amount
    progress = (new_amount / g["target_amount"]) * 100
    status_val = GoalStatus.COMPLETED.value if progress >= 100 else g["status"]
    
    await db.goals.update_one(
        {"_id": ObjectId(goal_id)},
        {"$set": {
            "saved_amount": new_amount,
            "progress_percentage": min(progress, 100.0),
            "status": status_val,
            "updated_at": datetime.utcnow()
        }}
    )
    
    g["saved_amount"] = new_amount
    g["progress_percentage"] = min(progress, 100.0)
    g["status"] = status_val
    g["id"] = str(g["_id"])
    return g
