from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.schemas.analytics import AnalyticsOverview, MonthlyAnalytics, CategoryAnalytics
from app.api.dependencies import get_current_user
from app.database.connection import get_db

router = APIRouter()

@router.get("/overview", response_model=AnalyticsOverview)
async def get_overview(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    user_id = str(current_user["_id"])
    
    # Due to mock constraints, we fallback to python logic if complex aggregates fail, but we'll try a basic group
    txs = await db.transactions.find({"user_id": user_id}).to_list(1000)
    
    inc = sum(t["amount"] for t in txs if t["transaction_type"] == "INCOME")
    exp = sum(t["amount"] for t in txs if t["transaction_type"] == "EXPENSE")
    bal = inc - exp
    sav = bal
    rate = (sav / inc * 100) if inc > 0 else 0.0
    
    expenses = [t["amount"] for t in txs if t["transaction_type"] == "EXPENSE"]
    largest = max(expenses) if expenses else 0.0
    avg = (sum(expenses) / len(expenses)) if expenses else 0.0
    
    return AnalyticsOverview(
        total_income=inc, total_expenses=exp, current_balance=bal,
        total_savings=sav, savings_rate=rate, transaction_count=len(txs),
        largest_expense=largest, average_expense=avg
    )

@router.get("/anomalies")
async def get_anomalies(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    user_id = str(current_user["_id"])
    txs = await db.transactions.find({"user_id": user_id, "transaction_type": "EXPENSE"}).to_list(1000)
    if len(txs) < 3:
        return [] # insufficient data
        
    amounts = [t["amount"] for t in txs]
    avg = sum(amounts) / len(amounts)
    # simple standard dev
    variance = sum((x - avg) ** 2 for x in amounts) / len(amounts)
    stddev = variance ** 0.5
    
    anomalies = []
    for t in txs:
        if stddev > 0 and (t["amount"] - avg) > (2 * stddev):
            t["id"] = str(t.pop("_id"))
            anomalies.append({
                "transaction": t,
                "amount": t["amount"],
                "category": t["category"],
                "anomaly_score": round((t["amount"] - avg) / stddev, 2),
                "reason": "This expense is significantly higher than your historical average.",
                "severity": "HIGH"
            })
    return anomalies
