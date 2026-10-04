from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = None

async def connect_to_mongo():
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URL)

async def close_mongo_connection():
    client.close()

async def get_db():
    return client[settings.DATABASE_NAME]
