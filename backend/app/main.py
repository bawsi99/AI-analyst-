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
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["*"],
    max_age=86400,  # Cache preflight requests for 24 hours
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

@app.get("/cors-test")
async def cors_test():
    """Test endpoint to verify CORS is working"""
    return {
        "message": "CORS test successful",
        "cors_origins": settings.CORS_ORIGINS,
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.options("/cors-test")
async def cors_test_options():
    """Handle preflight requests for CORS test"""
    return {"message": "Preflight request handled"}

@app.get("/debug/cors")
async def debug_cors():
    """Debug endpoint to check CORS configuration"""
    return {
        "cors_origins": settings.CORS_ORIGINS,
        "cors_origins_count": len(settings.CORS_ORIGINS),
        "has_wildcard": "*" in settings.CORS_ORIGINS,
        "vercel_domains": [origin for origin in settings.CORS_ORIGINS if "vercel.app" in origin],
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 