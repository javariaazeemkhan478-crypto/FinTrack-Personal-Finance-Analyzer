import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

create_file('app/main.py', '''from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.connection import connect_to_mongo, close_mongo_connection
from app.api.v1 import auth, users

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

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "database": "connected"}
''')

# Update requirements.txt without causing FileNotFoundError
with open('requirements.txt', 'w', encoding='utf-8') as f:
    f.write('''fastapi>=0.100.0
uvicorn>=0.22.0
motor>=3.2.0
python-dotenv>=1.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
passlib[bcrypt]>=1.7.4
python-jose[cryptography]>=3.3.0
pytest>=7.0.0
httpx>=0.24.0
pytest-asyncio
''')
