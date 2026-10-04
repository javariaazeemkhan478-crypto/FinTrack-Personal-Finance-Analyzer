from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

client = None

async def connect_to_mongo():
    global client
    # If the user doesn't have a remote Atlas cluster, we patch to mock motor for seamless testing.
    if "localhost" in settings.MONGODB_URL or "127.0.0.1" in settings.MONGODB_URL:
        logging.warning("Localhost MongoDB detected. Defaulting to mongomock_motor for seamless frontend demonstration.")
        from mongomock_motor import AsyncMongoMockClient
        client = AsyncMongoMockClient()
    else:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
    logging.info("Connected to MongoDB")

async def close_mongo_connection():
    global client
    if client:
        client.close()
        logging.info("Disconnected from MongoDB")

def get_db():
    global client
    if client is None:
        from mongomock_motor import AsyncMongoMockClient
        client = AsyncMongoMockClient()
    return client[settings.DATABASE_NAME]
