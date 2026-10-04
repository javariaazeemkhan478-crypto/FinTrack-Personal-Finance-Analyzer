from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.exceptions import FinTrackException
from app.database.connection import connect_to_mongo, close_mongo_connection
from app.database.indexes import create_indexes
from app.api.v1 import auth, transactions, categories, budgets, goals, analytics

app = FastAPI(
    title=settings.APP_NAME,
    description="API for managing personal finances",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    await create_indexes()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.exception_handler(FinTrackException)
async def fintrack_exception_handler(request: Request, exc: FinTrackException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])
app.include_router(budgets.router, prefix="/api/v1/budgets", tags=["Budgets"])
app.include_router(goals.router, prefix="/api/v1/goals", tags=["Goals"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "database": "connected"}
