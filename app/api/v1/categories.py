from fastapi import APIRouter, Depends, HTTPException
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
