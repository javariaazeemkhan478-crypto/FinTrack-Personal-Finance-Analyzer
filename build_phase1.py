import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# 1. Models / Schemas
create_file('app/models/user.py', '''from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class Role(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    FINANCIAL_ADVISOR = "FINANCIAL_ADVISOR"
    PREMIUM_USER = "PREMIUM_USER"
    FREE_USER = "FREE_USER"
    AUDITOR = "AUDITOR"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: Role
    is_active: bool
    created_at: datetime
    updated_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
''')

# 2. Dependencies
create_file('app/api/dependencies.py', '''from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.database.connection import get_db
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    db = await get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception
    return user

def require_roles(allowed_roles: list):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return current_user
    return role_checker
''')

# 3. Auth Routes
create_file('app/api/v1/auth.py', '''from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import UserCreate, UserLogin, Token, UserResponse, Role
from app.core.security import get_password_hash, verify_password, create_access_token
from app.database.connection import get_db
from app.api.dependencies import get_current_user
from bson import ObjectId
from datetime import datetime

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
        "role": Role.FREE_USER,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(new_user)
    new_user["id"] = str(result.inserted_id)
    return new_user

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db=Depends(get_db)):
    user = await db.users.find_one({"email": user_credentials.email})
    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    access_token = create_access_token(subject=str(user["_id"]))
    refresh_token = create_access_token(subject=str(user["_id"])) # Simplified for now
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    current_user["id"] = str(current_user["_id"])
    return current_user
''')

# 4. User Routes (Admin endpoints)
create_file('app/api/v1/users.py', '''from fastapi import APIRouter, Depends, HTTPException
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
''')

# 5. Database Connection Helper
create_file('app/database/connection.py', '''from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = None

async def connect_to_mongo():
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URL)

async def close_mongo_connection():
    client.close()

async def get_db():
    return client[settings.DATABASE_NAME]
''')

print("Files generated successfully.")
