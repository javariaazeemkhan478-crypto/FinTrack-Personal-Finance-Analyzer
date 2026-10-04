from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import UserCreate, UserLogin, Token, UserResponse, Role
from app.core.security import get_password_hash, verify_password, create_access_token
from app.database.connection import get_db
from app.api.dependencies import get_current_user
from bson import ObjectId
from datetime import datetime, UTC
import secrets

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db=Depends(get_db)):
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    new_user = {
        "name": user.name,
        "email": user.email,
        "hashed_password": get_password_hash(user.password),
        "role": Role.FREE_USER.value,
        "is_active": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }
    
    result = await db.users.insert_one(new_user)
    new_user["id"] = str(result.inserted_id)
    return new_user

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db=Depends(get_db)):
    user = await db.users.find_one({"email": user_credentials.email})
    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account is inactive")
        
    access_token = create_access_token(subject=str(user["_id"]))
    refresh_token = secrets.token_hex(32)
    
    # Store refresh token in db
    await db.refresh_tokens.insert_one({
        "user_id": str(user["_id"]),
        "token": refresh_token,
        "expires_at": datetime.now(UTC) # In real app, add 7 days
    })
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh(refresh_token: str, db=Depends(get_db)):
    token_doc = await db.refresh_tokens.find_one({"token": refresh_token})
    if not token_doc:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    # Rotate token
    await db.refresh_tokens.delete_one({"_id": token_doc["_id"]})
    
    user_id = token_doc["user_id"]
    new_access_token = create_access_token(subject=user_id)
    new_refresh_token = secrets.token_hex(32)
    
    await db.refresh_tokens.insert_one({
        "user_id": user_id,
        "token": new_refresh_token,
        "expires_at": datetime.now(UTC)
    })
    
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(refresh_token: str, db=Depends(get_db)):
    result = await db.refresh_tokens.delete_one({"token": refresh_token})
    if result.deleted_count == 0:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    current_user["id"] = str(current_user["_id"])
    return current_user
