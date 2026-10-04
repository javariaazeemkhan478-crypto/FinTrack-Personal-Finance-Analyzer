import os
import re

files_to_update = [
    'app/api/v1/auth.py',
    'app/api/v1/transactions.py',
    'app/api/v1/budgets.py',
    'app/api/v1/goals.py',
    'app/core/security.py',
    'tests/test_finance.py'
]

for filepath in files_to_update:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace datetime.utcnow()
        if 'datetime.utcnow()' in content:
            if 'from datetime import datetime' in content and 'UTC' not in content:
                content = content.replace('from datetime import datetime', 'from datetime import datetime, UTC')
            content = content.replace('datetime.utcnow()', 'datetime.now(UTC)')
            
        # Replace .dict() for pydantic models
        content = re.sub(r'\.dict\(\)', '.model_dump()', content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
# UPDATE MAIN
content = """from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.connection import connect_to_mongo, close_mongo_connection
from app.api.v1 import auth, users, transactions, categories, budgets, goals, analytics, notifications

app = FastAPI(
    title=settings.APP_NAME,
    description="API for managing personal finances",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])
app.include_router(budgets.router, prefix="/api/v1/budgets", tags=["Budgets"])
app.include_router(goals.router, prefix="/api/v1/goals", tags=["Goals"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "database": "connected"}
"""

with open("app/main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Deprecations and main router updated.")
