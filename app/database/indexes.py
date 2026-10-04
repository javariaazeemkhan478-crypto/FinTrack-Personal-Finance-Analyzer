from app.database.connection import get_db

async def create_indexes():
    db = get_db()
    
    # users
    await db.users.create_index("email", unique=True)
    
    # transactions
    await db.transactions.create_index("user_id")
    await db.transactions.create_index("transaction_date")
    await db.transactions.create_index("category_id")
    await db.transactions.create_index("transaction_type")
    
    # budgets
    await db.budgets.create_index("user_id")
    await db.budgets.create_index([("user_id", 1), ("category_id", 1), ("month", 1), ("year", 1)], unique=True)
    
    # goals
    await db.goals.create_index("user_id")
    
    # notifications
    await db.notifications.create_index("user_id")
    
    # audit_logs
    await db.audit_logs.create_index("user_id")\n