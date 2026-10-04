from fastapi import APIRouter, Depends, HTTPException
from app.models.user import UserResponse, Role
from app.api.dependencies import get_current_user, require_roles
from app.database.connection import get_db
from bson import ObjectId

router = APIRouter()

@router.get("/admin/users")
async def get_all_users(db=Depends(get_db), current_user: dict = Depends(require_roles([Role.SUPER_ADMIN, Role.ADMIN]))):
    users = await db.users.find().to_list(100)
    for u in users:
        u["id"] = str(u["_id"])
    return users

@router.patch("/admin/users/{id}/role")
async def update_user_role(id: str, role: Role, db=Depends(get_db), current_user: dict = Depends(require_roles([Role.SUPER_ADMIN]))):
    result = await db.users.update_one({"_id": ObjectId(id)}, {"$set": {"role": role}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Role updated"}
