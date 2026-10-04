import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# SCHEMAS for Analytics and Notifications
create_file('app/schemas/analytics.py', '''from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AnalyticsOverview(BaseModel):
    total_income: float
    total_expenses: float
    current_balance: float
    total_savings: float
    savings_rate: float
    transaction_count: int
    largest_expense: float
    average_expense: float

class MonthlyAnalytics(BaseModel):
    month: int
    year: int
    total_income: float
    total_expenses: float
    savings: float
    transaction_count: int

class CategoryAnalytics(BaseModel):
    category: str
    total_spending: float
    percentage: float
    transaction_count: int

class NotificationCreate(BaseModel):
    type: str
    title: str
    message: str
    related_resource_id: Optional[str] = None

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
    related_resource_id: Optional[str] = None
''')

# SERVICES for Alerts and Notifications
create_file('app/services/notifications.py', '''from datetime import datetime, UTC
from bson import ObjectId

async def create_notification(db, user_id: str, type: str, title: str, message: str, related_resource_id: str = None):
    doc = {
        "user_id": user_id,
        "type": type,
        "title": title,
        "message": message,
        "is_read": False,
        "created_at": datetime.now(UTC),
        "related_resource_id": related_resource_id
    }
    await db.notifications.insert_one(doc)

async def check_budget_alerts(db, user_id: str, budget_id: str, spent: float, limit: float):
    if limit <= 0: return
    percentage = (spent / limit) * 100
    
    thresholds = [
        (100, "BUDGET_EXCEEDED", "Budget Exceeded"),
        (80, "BUDGET_LIMIT_REACHED", "Budget at 80%"),
        (50, "BUDGET_WARNING", "Budget at 50%")
    ]
    
    for t_val, t_type, t_title in thresholds:
        if percentage >= t_val:
            # Check if this alert was already sent
            existing = await db.notifications.find_one({
                "user_id": user_id,
                "type": t_type,
                "related_resource_id": budget_id
            })
            if not existing:
                await create_notification(
                    db, user_id, t_type, t_title, 
                    f"Your budget has reached {round(percentage, 1)}%", budget_id
                )
            break # only trigger highest applicable threshold
''')

# ROUTERS: Notifications
create_file('app/api/v1/notifications.py', '''from fastapi import APIRouter, Depends, HTTPException
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
''')

# ROUTERS: Analytics
create_file('app/api/v1/analytics.py', '''from fastapi import APIRouter, Depends, HTTPException
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
''')
