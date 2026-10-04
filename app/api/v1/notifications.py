from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.analytics import NotificationResponse
from app.api.dependencies import get_current_user
from app.database.connection import get_db
from bson import ObjectId

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
async def list_notifications(page: int = 1, limit: int = 20, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    cursor = db.notifications.find({"user_id": str(current_user["_id"])}).sort("created_at", -1).skip((page-1)*limit).limit(limit)
    notifs = await cursor.to_list(limit)
    for n in notifs:
        n["id"] = str(n.pop("_id"))
    return notifs

@router.patch("/{id}/read")
async def mark_read(id: str, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    res = await db.notifications.update_one({"_id": ObjectId(id), "user_id": str(current_user["_id"])}, {"$set": {"is_read": True}})
    if res.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"success": True}

@router.patch("/read-all")
async def mark_all_read(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    await db.notifications.update_many({"user_id": str(current_user["_id"]), "is_read": False}, {"$set": {"is_read": True}})
    return {"success": True}
