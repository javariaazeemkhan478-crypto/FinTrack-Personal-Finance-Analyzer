from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class PaymentMethod(str, Enum):
    CASH = "CASH"
    CARD = "CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    MOBILE_WALLET = "MOBILE_WALLET"
    OTHER = "OTHER"

class TransactionBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    amount: float = Field(..., gt=0)
    transaction_type: TransactionType
    category_id: Optional[str] = None
    description: Optional[str] = None
    transaction_date: datetime
    payment_method: PaymentMethod = PaymentMethod.OTHER
    tags: List[str] = []

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    transaction_type: Optional[TransactionType] = None
    category_id: Optional[str] = None
    description: Optional[str] = None
    transaction_date: Optional[datetime] = None
    payment_method: Optional[PaymentMethod] = None
    tags: Optional[List[str]] = None

class TransactionResponse(TransactionBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime\n