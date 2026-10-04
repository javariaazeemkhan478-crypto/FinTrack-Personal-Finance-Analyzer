from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse, TransactionType
from app.core.exceptions import NotFoundException
from app.database.connection import get_db
from app.api.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction: TransactionCreate, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    t_dict = transaction.model_dump()
    t_dict["user_id"] = current_user["id"]
    t_dict["created_at"] = datetime.utcnow()
    t_dict["updated_at"] = datetime.utcnow()
    
    if not t_dict.get("category_id"):
        title_lower = t_dict["title"].lower()
        if "mcdonald" in title_lower or "kfc" in title_lower or "food" in title_lower:
            pass
            
    result = await db.transactions.insert_one(t_dict)
    t_dict["id"] = str(result.inserted_id)
    return t_dict

@router.get("/", response_model=dict)
async def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    type: Optional[TransactionType] = None,
    category_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    query = {"user_id": current_user["id"]}
    if type:
        query["transaction_type"] = type.value
    if category_id:
        query["category_id"] = category_id
        
    skip = (page - 1) * limit
    cursor = db.transactions.find(query).sort("transaction_date", -1).skip(skip).limit(limit)
    transactions = []
    async for t in cursor:
        t["id"] = str(t["_id"])
        transactions.append(t)
        
    total = await db.transactions.count_documents(query)
    
    return {
        "items": transactions,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total + limit - 1) // limit
    }

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    t = await db.transactions.find_one({"_id": ObjectId(transaction_id), "user_id": current_user["id"]})
    if not t:
        raise NotFoundException("Transaction")
    t["id"] = str(t["_id"])
    return t

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(transaction_id: str, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    result = await db.transactions.delete_one({"_id": ObjectId(transaction_id), "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise NotFoundException("Transaction")
    return None
