from datetime import datetime, UTC
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
