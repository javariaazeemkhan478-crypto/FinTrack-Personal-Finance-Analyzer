from pydantic import BaseModel, Field
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
