import os

files = {}

files["app/core/permissions.py"] = """
from enum import Enum
from fastapi import Depends
from app.core.exceptions import ForbiddenException

class Role(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    FINANCIAL_ADVISOR = "FINANCIAL_ADVISOR"
    PREMIUM_USER = "PREMIUM_USER"
    FREE_USER = "FREE_USER"
    AUDITOR = "AUDITOR"

def require_roles(allowed_roles: list[Role]):
    def role_checker(current_user: dict):
        if current_user.get("role") not in [role.value for role in allowed_roles]:
            raise ForbiddenException(message="You do not have enough permissions to perform this action.")
        return current_user
    return role_checker
"""

files["app/schemas/category.py"] = """
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    type: str = Field(..., description="E.g., SYSTEM or CUSTOM")

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: str
    user_id: Optional[str]
    created_at: datetime
"""

files["app/schemas/transaction.py"] = """
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
    updated_at: datetime
"""

files["app/schemas/budget.py"] = """
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
"""

files["app/schemas/goal.py"] = """
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
    amount: float = Field(..., gt=0)
"""

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.strip() + "\\n")
print("Files generated.")
