from pydantic import BaseModel
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
