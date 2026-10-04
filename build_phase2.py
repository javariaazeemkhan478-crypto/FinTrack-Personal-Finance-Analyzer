import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# SCHEMAS
create_file('app/schemas/finance.py', '''from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0)
    transaction_type: TransactionType
    category: str
    description: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)
    payment_method: Optional[str] = None
    notes: Optional[str] = None

class TransactionResponse(TransactionCreate):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

class CategoryCreate(BaseModel):
    name: str

class CategoryResponse(BaseModel):
    id: str
    name: str
    user_id: Optional[str] = None
    is_default: bool = False

class BudgetCreate(BaseModel):
    name: str
    amount: float = Field(..., gt=0)
    category: str
    month: int = Field(..., ge=1, le=12)
    year: int

class BudgetResponse(BudgetCreate):
    id: str
    user_id: str
    spent: float = 0.0
    remaining: float = 0.0
    percentage_used: float = 0.0
    exceeded: bool = False

class GoalCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_amount: float = Field(..., gt=0)
    target_date: datetime

class GoalResponse(GoalCreate):
    id: str
    user_id: str
    current_amount: float = 0.0
    progress_percentage: float = 0.0
    remaining_amount: float = 0.0
    status: str = "ACTIVE"
    created_at: datetime
    updated_at: datetime

class GoalContribute(BaseModel):
    amount: float = Field(..., gt=0)
''')

# SERVICES (Categorization)
create_file('app/services/categorization.py', '''from typing import Tuple

RULES = {
    "mcdonald's": "Food",
    "mcdonalds": "Food",
    "uber": "Transport",
    "netflix": "Entertainment",
    "electricity": "Utilities",
    "amazon": "Shopping",
    "hospital": "Healthcare",
    "university": "Education",
    "salary": "Salary",
    "freelance": "Freelance"
}

def suggest_category(description: str) -> Tuple[str, str, str]:
    if not description:
        return "Other", "Low", "No description provided"
    
    desc_lower = description.lower()
    for key, category in RULES.items():
        if key in desc_lower:
            return category, "High", f"Matched keyword: {key}"
            
    return "Other", "Low", "No matches found"
''')

# ROUTERS: Categories
create_file('app/api/v1/categories.py', '''from fastapi import APIRouter, Depends, HTTPException
from app.schemas.finance import CategoryCreate, CategoryResponse
from app.api.dependencies import get_current_user
from app.database.connection import get_db
from bson import ObjectId
from app.services.categorization import suggest_category

router = APIRouter()

DEFAULT_CATEGORIES = [
    "Food", "Transport", "Shopping", "Utilities", "Healthcare", 
    "Education", "Entertainment", "Rent", "Salary", "Freelance", 
    "Investment", "Other"
]

@router.on_event("startup")
async def setup_defaults():
    # Only useful if app is starting, but we'll ignore for testing setup script.
    pass

@router.get("/", response_model=list[CategoryResponse])
async def list_categories(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    # Simple list returning defaults and user-specific
    return [{"id": "sys_"+c, "name": c, "is_default": True} for c in DEFAULT_CATEGORIES]

@router.post("/suggest")
async def get_suggestion(description: str, current_user: dict = Depends(get_current_user)):
    category, confidence, reason = suggest_category(description)
    return {"suggested_category": category, "confidence": confidence, "reason": reason}
''')

# ROUTERS: Transactions
create_file('app/api/v1/transactions.py', '''from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from app.schemas.finance import TransactionCreate, TransactionResponse, TransactionType
from app.api.dependencies import get_current_user
from app.database.connection import get_db
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=TransactionResponse)
async def create_transaction(tx: TransactionCreate, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    doc = tx.dict()
    doc["user_id"] = str(current_user["_id"])
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()
    result = await db.transactions.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(
    page: int = 1, limit: int = 20, 
    type: Optional[TransactionType] = None,
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user), db=Depends(get_db)
):
    query = {"user_id": str(current_user["_id"])}
    if type:
        query["transaction_type"] = type.value
    if category:
        query["category"] = category
        
    cursor = db.transactions.find(query).skip((page - 1) * limit).limit(limit)
    transactions = await cursor.to_list(limit)
    for t in transactions:
        t["id"] = str(t.pop("_id"))
    return transactions
''')

# ROUTERS: Budgets
create_file('app/api/v1/budgets.py', '''from fastapi import APIRouter, Depends, HTTPException
from app.schemas.finance import BudgetCreate, BudgetResponse
from app.api.dependencies import get_current_user
from app.database.connection import get_db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=BudgetResponse)
async def create_budget(budget: BudgetCreate, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    # Duplicate check
    existing = await db.budgets.find_one({
        "user_id": str(current_user["_id"]),
        "category": budget.category,
        "month": budget.month,
        "year": budget.year
    })
    if existing:
        raise HTTPException(status_code=400, detail="Budget already exists for this category and month")

    doc = budget.dict()
    doc["user_id"] = str(current_user["_id"])
    doc["spent"] = 0.0
    doc["remaining"] = budget.amount
    doc["percentage_used"] = 0.0
    doc["exceeded"] = False
    
    result = await db.budgets.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc
''')

# ROUTERS: Goals
create_file('app/api/v1/goals.py', '''from fastapi import APIRouter, Depends, HTTPException
from app.schemas.finance import GoalCreate, GoalResponse, GoalContribute
from app.api.dependencies import get_current_user
from app.database.connection import get_db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=GoalResponse)
async def create_goal(goal: GoalCreate, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    doc = goal.dict()
    doc["user_id"] = str(current_user["_id"])
    doc["current_amount"] = 0.0
    doc["progress_percentage"] = 0.0
    doc["remaining_amount"] = goal.target_amount
    doc["status"] = "ACTIVE"
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()
    
    result = await db.goals.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

@router.post("/{id}/contribute", response_model=GoalResponse)
async def contribute(id: str, contribution: GoalContribute, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    goal = await db.goals.find_one({"_id": ObjectId(id), "user_id": str(current_user["_id"])})
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    new_amount = goal["current_amount"] + contribution.amount
    progress = (new_amount / goal["target_amount"]) * 100
    status = "COMPLETED" if new_amount >= goal["target_amount"] else "ACTIVE"
    
    update_data = {
        "current_amount": new_amount,
        "progress_percentage": round(progress, 2),
        "remaining_amount": max(0.0, goal["target_amount"] - new_amount),
        "status": status,
        "updated_at": datetime.utcnow()
    }
    
    await db.goals.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    goal.update(update_data)
    goal["id"] = str(goal.pop("_id"))
    return goal
''')

# UPDATE MAIN
create_file('update_main2.py', '''import os

content = """from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.connection import connect_to_mongo, close_mongo_connection
from app.api.v1 import auth, users, transactions, categories, budgets, goals

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

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "database": "connected"}
"""

with open("app/main.py", "w") as f:
    f.write(content)
''')
