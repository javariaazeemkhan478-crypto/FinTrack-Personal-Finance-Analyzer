import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# Update requirements.txt
create_file('requirements.txt', '''fastapi>=0.100.0
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

# Core Security
create_file('app/core/security.py', '''from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt
''')

print("Backend scaffolding step 1 complete.")
