from pydantic_settings import BaseSettings
from typing import List
import os
from pydantic import Field

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
        "https://orthoaiassgnment-phi.vercel.app",  # Vercel frontend
        "https://orthoaiassgnment.vercel.app",      # Alternative Vercel domain
        "https://orthoaiassgnment-git-main-aaryan-manawats-projects.vercel.app",  # Vercel preview domain
        "https://orthoaiassgnment-8qwz7a87u-aaryan-manawats-projects.vercel.app",  # Vercel preview domain
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
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    # JWT
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ML Configuration
    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2
    MAX_FEATURES: int = 100
    
    # Gemini LLM Configuration
    GEMINI_LLM_API_KEY: str = ""
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }

settings = Settings()

# Create directories if they don't exist
os.makedirs(settings.UPLOAD_STORAGE_PATH, exist_ok=True)
os.makedirs(settings.MODEL_STORAGE_PATH, exist_ok=True) 