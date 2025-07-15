from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Mini AI Analyst"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "*"  # Allow all origins for development
    ]
    
    # File Upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_STORAGE_PATH: str = "./uploads"
    MODEL_STORAGE_PATH: str = "./models"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/ai_analyst"
    
    # Redis (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # S3 Storage (optional)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""
    
    # Supabase Configuration
    SUPABASE_URL: str = "https://edajrfiicoffqgzdkelh.supabase.co"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVkYWpyZmlpY29mZnFnemRrZWxoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI1NjA4MzcsImV4cCI6MjA2ODEzNjgzN30.mNJT48TejS6qVrg42qs2FrT5mDUeATPNbsfXZUteJBs"
    SUPABASE_SERVICE_ROLE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVkYWpyZmlpY29mZnFnemRrZWxoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjU2MDgzNywiZXhwIjoyMDY4MTM2ODM3fQ.e3k7HKT7tYnsbmMSm6z-SIYYSKEcE7AAZHQqoaS2Fb4"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ML Configuration
    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2
    MAX_FEATURES: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Create directories if they don't exist
os.makedirs(settings.UPLOAD_STORAGE_PATH, exist_ok=True)
os.makedirs(settings.MODEL_STORAGE_PATH, exist_ok=True) 