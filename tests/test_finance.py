import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_finance_flows():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register User
        res = await ac.post("/api/v1/auth/register", json={
            "name": "Finance User", "email": "finance@example.com", "password": "password"
        })
        # Login
        login_resp = await ac.post("/api/v1/auth/login", json={
            "email": "finance@example.com", "password": "password"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test Category Suggestion
        sugg = await ac.post("/api/v1/categories/suggest?description=mcdonalds", headers=headers)
        assert sugg.status_code == 200
        assert sugg.json()["suggested_category"] == "Food"
        
        # Create Transaction
        tx = await ac.post("/api/v1/transactions/", json={
            "amount": 50.0,
            "transaction_type": "EXPENSE",
            "category": "Food",
            "description": "McDonalds"
        }, headers=headers)
        assert tx.status_code == 200
        tx_data = tx.json()
        assert tx_data["amount"] == 50.0
        
        # Create Budget
        bg = await ac.post("/api/v1/budgets/", json={
            "name": "Food Budget",
            "amount": 200.0,
            "category": "Food",
            "month": 10,
            "year": 2026
        }, headers=headers)
        assert bg.status_code == 200
        
        # Test duplicate budget
        bg2 = await ac.post("/api/v1/budgets/", json={
            "name": "Food Budget 2",
            "amount": 300.0,
            "category": "Food",
            "month": 10,
            "year": 2026
        }, headers=headers)
        assert bg2.status_code == 400
        
        # Create Goal
        goal = await ac.post("/api/v1/goals/", json={
            "name": "Vacation",
            "target_amount": 1000.0,
            "target_date": "2026-12-31T00:00:00Z"
        }, headers=headers)
        assert goal.status_code == 200
        goal_id = goal.json()["id"]
        
        # Contribute to Goal
        contrib = await ac.post(f"/api/v1/goals/{goal_id}/contribute", json={
            "amount": 250.0
        }, headers=headers)
        assert contrib.status_code == 200
        assert contrib.json()["current_amount"] == 250.0
        assert contrib.json()["progress_percentage"] == 25.0
        assert contrib.json()["status"] == "ACTIVE"
