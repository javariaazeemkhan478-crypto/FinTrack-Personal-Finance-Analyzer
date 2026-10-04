from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class GoalStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class GoalBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    target_amount: float = Field(..., gt=0)
    deadline: datetime
    description: Optional[str] = None

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    target_amount: Optional[float] = None
    deadline: Optional[datetime] = None
    description: Optional[str] = None
    status: Optional[GoalStatus] = None

class GoalResponse(GoalBase):
    id: str
    user_id: str
    saved_amount: float
    status: GoalStatus
    progress_percentage: float
    created_at: datetime
    updated_at: datetime

class GoalContribute(BaseModel):
    amount: float = Field(..., gt=0)\n