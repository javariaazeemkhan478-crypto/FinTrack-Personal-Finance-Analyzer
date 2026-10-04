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