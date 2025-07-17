from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.api.v1.api import api_router

# Ensure required directories exist at startup
def ensure_directories():
    """Ensure all required directories exist and are writable"""
    directories = [
        settings.UPLOAD_STORAGE_PATH,
        settings.MODEL_STORAGE_PATH,
        "/tmp/matplotlib"  # For matplotlib cache
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            # Test if directory is writable
            test_file = os.path.join(directory, ".test_write")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print(f"✅ Directory {directory} is ready")
        except Exception as e:
            print(f"⚠️ Warning: Directory {directory} is not writable: {e}")

# Run directory checks at startup
ensure_directories()

app = FastAPI(
    title="Mini AI Analyst API",
    description="A comprehensive AI-powered data analysis and machine learning service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://orthoaiassgnment.vercel.app",
        "https://orthoaiassgnment-git-main-aaryan-manawats-projects.vercel.app",
        "https://orthoaiassgnment-ezjyoxl4s-aaryan-manawats-projects.vercel.app",
        "https://orthoaiassgnment-3osm.vercel.app",
        "https://orthoaiassgnment-3osm-git-main-aaryan-manawats-projects.vercel.app",
        "https://orthoaiassgnment-3osm-hb729wy34-aaryan-manawats-projects.vercel.app",
        "http://localhost:3000",  # For local development
        "http://localhost:3001",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Mount static files for model storage
if os.path.exists(settings.MODEL_STORAGE_PATH):
    app.mount("/models", StaticFiles(directory=settings.MODEL_STORAGE_PATH), name="models")

@app.get("/")
async def root():
    return {
        "message": "Mini AI Analyst API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    from app.services.redis_service import redis_service
    
    # Check Redis health
    redis_healthy = redis_service.health_check()
    
    return {
        "status": "healthy" if redis_healthy else "degraded",
        "service": "ai-analyst-api",
        "redis": "healthy" if redis_healthy else "unhealthy"
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 