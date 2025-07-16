from fastapi import APIRouter
from app.api.v1.endpoints import upload, profile, train, predict, summary, export, auth, dashboard, ai_analysis, background_tasks, monitoring

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(train.router, prefix="/train", tags=["train"])
api_router.include_router(predict.router, prefix="/predict", tags=["predict"])
api_router.include_router(summary.router, prefix="/summary", tags=["summary"])
api_router.include_router(ai_analysis.router, prefix="/ai-analysis", tags=["ai-analysis"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(background_tasks.router, prefix="/background-tasks", tags=["background-tasks"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"]) 