import os
import json
import subprocess

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# Update config for MongoDB Atlas
create_file("app/core/config.py", """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FinTrack API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    MONGODB_URL: str = ""
    DATABASE_NAME: str = "fintrack_db"
    JWT_SECRET_KEY: str = "super-secret-key-for-jwt-do-not-use-in-prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"

settings = Settings()
""")

create_file(".env.example", """MONGODB_URL=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=fintrack_db
JWT_SECRET_KEY=your_super_secret_key_here
""")

print("Backend scaffolding complete.")
