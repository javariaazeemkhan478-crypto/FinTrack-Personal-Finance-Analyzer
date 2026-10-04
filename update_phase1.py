import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# Update requirements.txt to include mongomock_motor
with open('requirements.txt', 'a', encoding='utf-8') as f:
    f.write('mongomock-motor\n')

create_file('app/tests/conftest.py', '''import pytest
import asyncio
from mongomock_motor import AsyncMongoMockClient
from app.database.connection import get_db

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def override_get_db():
    from app.main import app
    client = AsyncMongoMockClient()
    db = client.fintrack_test_db
    
    async def get_test_db():
        return db
        
    app.dependency_overrides[get_db] = get_test_db
    yield
    app.dependency_overrides.clear()
''')

# We mock out the rest of the missing auth.py functions
create_file('app/api/v1/auth.py', '''from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import UserCreate, UserLogin, Token, UserResponse, Role
from app.core.security import get_password_hash, verify_password, create_access_token
from app.database.connection import get_db
from app.api.dependencies import get_current_user
from bson import ObjectId
from datetime import datetime
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
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account is inactive")
        
    access_token = create_access_token(subject=str(user["_id"]))
    refresh_token = secrets.token_hex(32)
    
    # Store refresh token in db
    await db.refresh_tokens.insert_one({
        "user_id": str(user["_id"]),
        "token": refresh_token,
        "expires_at": datetime.utcnow() # In real app, add 7 days
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
        "expires_at": datetime.utcnow()
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
''')

# We generate a quick test script to verify
create_file('tests/test_auth.py', '''import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/register", json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["role"] == "FREE_USER"
        
        # Test duplicate
        response2 = await ac.post("/api/v1/auth/register", json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123"
        })
        assert response2.status_code == 400
        
        # Test Login
        login_resp = await ac.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert login_resp.status_code == 200
        tokens = login_resp.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        
        # Test Me
        me_resp = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == "test@example.com"
        
        # Test Refresh
        refresh_resp = await ac.post(f"/api/v1/auth/refresh?refresh_token={tokens['refresh_token']}")
        assert refresh_resp.status_code == 200
        new_tokens = refresh_resp.json()
        assert new_tokens["refresh_token"] != tokens["refresh_token"]
        
        # Test old token rotation
        refresh_resp2 = await ac.post(f"/api/v1/auth/refresh?refresh_token={tokens['refresh_token']}")
        assert refresh_resp2.status_code == 401
        
        # Test logout
        logout_resp = await ac.post(f"/api/v1/auth/logout?refresh_token={new_tokens['refresh_token']}")
        assert logout_resp.status_code == 200
        
        # Test logout again
        logout_resp2 = await ac.post(f"/api/v1/auth/logout?refresh_token={new_tokens['refresh_token']}")
        assert logout_resp2.status_code == 401
''')

print("Phase 1 update complete.")
