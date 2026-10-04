import pytest
import asyncio
from mongomock_motor import AsyncMongoMockClient
from httpx import AsyncClient, ASGITransport
from app.database.connection import get_db
from app.main import app

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def override_get_db():
    client = AsyncMongoMockClient()
    db = client.fintrack_test_db
    
    async def get_test_db():
        return db
        
    app.dependency_overrides[get_db] = get_test_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def setup_db():
    # Setup db is implicitly handled by override_get_db, but we provide it for compatibility
    yield
