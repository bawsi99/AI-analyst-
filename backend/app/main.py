from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.api.v1.api import api_router

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
    allow_origins=["*"],  # Allow all origins for development
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
    return {"status": "healthy", "service": "ai-analyst-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 