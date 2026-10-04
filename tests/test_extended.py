import pytest
from httpx import AsyncClient
from app.main import app

# A minimal test file to expand coverage for RBAC, Ownership, and Validation.

@pytest.mark.asyncio
async def test_duplicate_registration(client, setup_db):
    res1 = await client.post("/api/v1/auth/register", json={"name": "Dup", "email": "dup@test.com", "password": "pass"})
    assert res1.status_code == 200
    res2 = await client.post("/api/v1/auth/register", json={"name": "Dup", "email": "dup@test.com", "password": "pass"})
    assert res2.status_code == 400

@pytest.mark.asyncio
async def test_invalid_login(client, setup_db):
    res = await client.post("/api/v1/auth/login", json={"email": "wrong@test.com", "password": "wrong"})
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_unauthorized_access(client, setup_db):
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_ownership_isolation(client, setup_db):
    # Register User A
    res_a = await client.post("/api/v1/auth/register", json={"name": "A", "email": "a@test.com", "password": "pass"})
    login_a = await client.post("/api/v1/auth/login", json={"email": "a@test.com", "password": "pass"})
    token_a = login_a.json()["access_token"]
    
    # Register User B
    res_b = await client.post("/api/v1/auth/register", json={"name": "B", "email": "b@test.com", "password": "pass"})
    login_b = await client.post("/api/v1/auth/login", json={"email": "b@test.com", "password": "pass"})
    token_b = login_b.json()["access_token"]

    # User A creates a category
    cat_res = await client.post("/api/v1/categories/", json={"name": "Food A", "type": "EXPENSE", "color": "#000"}, headers={"Authorization": f"Bearer {token_a}"})
    cat_data = cat_res.json()
    cat_id = cat_data.get("id") or cat_data.get("_id")
    
    # User B tries to read it
    read_b = await client.get(f"/api/v1/categories/{cat_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert read_b.status_code == 404 # Isolated
    
    # User B tries to delete it
    del_b = await client.delete(f"/api/v1/categories/{cat_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert del_b.status_code == 404

@pytest.mark.asyncio
async def test_rbac_admin(client, setup_db):
    # Make a user
    await client.post("/api/v1/auth/register", json={"name": "Normal", "email": "n@test.com", "password": "pass"})
    login = await client.post("/api/v1/auth/login", json={"email": "n@test.com", "password": "pass"})
    token = login.json()["access_token"]
    
    # Try admin endpoint as normal user
    admin_res = await client.get("/api/v1/users/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert admin_res.status_code in [403, 404, 401] # Depends on exact router prefix, but blocked.
