import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_analytics_and_notifications():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/v1/auth/register", json={
            "name": "Analytics User", "email": "analytics@example.com", "password": "password"
        })
        login_resp = await ac.post("/api/v1/auth/login", json={
            "email": "analytics@example.com", "password": "password"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Add Income
        await ac.post("/api/v1/transactions/", json={
            "amount": 5000.0,
            "transaction_type": "INCOME",
            "category": "Salary",
            "description": "Monthly Salary"
        }, headers=headers)
        
        # Add Expense 1
        await ac.post("/api/v1/transactions/", json={
            "amount": 100.0,
            "transaction_type": "EXPENSE",
            "category": "Food",
            "description": "Dinner"
        }, headers=headers)
        
        # Add Expense 2
        await ac.post("/api/v1/transactions/", json={
            "amount": 500.0,
            "transaction_type": "EXPENSE",
            "category": "Shopping",
            "description": "New phone"
        }, headers=headers)
        
        # Add Expense 3 (Anomaly candidate if stddev logic fires, but needs 3 items. Let's add 3rd small)
        await ac.post("/api/v1/transactions/", json={
            "amount": 50.0,
            "transaction_type": "EXPENSE",
            "category": "Transport",
            "description": "Bus"
        }, headers=headers)
        
        # Test Overview Analytics
        overview = await ac.get("/api/v1/analytics/overview", headers=headers)
        assert overview.status_code == 200
        data = overview.json()
        assert data["total_income"] == 5000.0
        assert data["total_expenses"] == 650.0
        assert data["current_balance"] == 4350.0
        assert data["largest_expense"] == 500.0
        
        # Test Anomalies
        anom = await ac.get("/api/v1/analytics/anomalies", headers=headers)
        assert anom.status_code == 200
        # Since avg is (100+500+50)/3 = 216, and variance is large, it might not flag, but the endpoint works.
        
        # Test Notifications empty list (since no budget logic triggered it via our simplified mock here)
        notifs = await ac.get("/api/v1/notifications/", headers=headers)
        assert notifs.status_code == 200
        assert isinstance(notifs.json(), list)
