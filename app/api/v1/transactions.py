from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, UTC
from app.schemas.finance import TransactionCreate, TransactionResponse, TransactionType
from app.api.dependencies import get_current_user
from app.database.connection import get_db
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=TransactionResponse)
async def create_transaction(tx: TransactionCreate, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    doc = tx.model_dump()
    doc["user_id"] = str(current_user["_id"])
    doc["created_at"] = datetime.now(UTC)
    doc["updated_at"] = datetime.now(UTC)
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
