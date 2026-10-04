from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BudgetBase(BaseModel):
    category_id: str
    monthly_limit: float = Field(..., gt=0)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000)

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    monthly_limit: Optional[float] = None

class BudgetResponse(BudgetBase):
    id: str
    user_id: str
    spent_amount: float = 0.0
    remaining_amount: float = 0.0
    usage_percentage: float = 0.0
    is_exceeded: bool = False
    created_at: datetime
    updated_at: datetime