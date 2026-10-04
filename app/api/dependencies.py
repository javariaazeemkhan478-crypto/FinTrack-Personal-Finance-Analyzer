from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.database.connection import get_db
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException(message="Invalid credentials")
    except JWTError:
        raise UnauthorizedException(message="Invalid credentials")
        
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise UnauthorizedException(message="User not found")
    if not user.get("is_active", True):
        raise UnauthorizedException(message="Inactive user")
        
    user["id"] = str(user["_id"])
    return user