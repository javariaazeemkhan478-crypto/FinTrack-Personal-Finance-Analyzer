import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

create_file('tests/test_auth.py', '''import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_register_and_login():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
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

print("Test fixed.")
