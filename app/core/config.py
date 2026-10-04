from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FinTrack API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "fintrack_db"
    JWT_SECRET_KEY: str = "super-secret-key-for-jwt-do-not-use-in-prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"

settings = Settings()\n