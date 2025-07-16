from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.redis_service import redis_service

router = APIRouter()

@router.get("/redis/stats")
async def get_redis_stats():
    """
    Get Redis statistics and performance metrics.
    
    Returns:
    - Redis statistics including memory usage, hit rate, and performance metrics
    """
    try:
        stats = redis_service.get_stats()
        
        return {
            "message": "Redis statistics retrieved successfully",
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Redis stats: {str(e)}")

@router.get("/redis/health")
async def check_redis_health():
    """
    Check Redis health and connectivity.
    
    Returns:
    - Redis health status
    """
    try:
        is_healthy = redis_service.health_check()
        
        return {
            "message": "Redis health check completed",
            "success": True,
            "healthy": is_healthy,
            "status": "healthy" if is_healthy else "unhealthy"
        }
        
    except Exception as e:
        return {
            "message": "Redis health check failed",
            "success": False,
            "healthy": False,
            "status": "error",
            "error": str(e)
        }

@router.get("/system/health")
async def get_system_health():
    """
    Get overall system health status.
    
    Returns:
    - System health information including all services
    """
    try:
        # Check Redis health
        redis_healthy = redis_service.health_check()
        
        # Get Redis stats
        redis_stats = redis_service.get_stats()
        
        # Check if model storage directory exists
        import os
        from app.core.config import settings
        model_storage_exists = os.path.exists(settings.MODEL_STORAGE_PATH)
        upload_storage_exists = os.path.exists(settings.UPLOAD_STORAGE_PATH)
        
        # Overall system health
        system_healthy = redis_healthy and model_storage_exists and upload_storage_exists
        
        return {
            "message": "System health check completed",
            "success": True,
            "healthy": system_healthy,
            "services": {
                "redis": {
                    "healthy": redis_healthy,
                    "stats": redis_stats
                },
                "storage": {
                    "model_storage": model_storage_exists,
                    "upload_storage": upload_storage_exists
                }
            },
            "status": "healthy" if system_healthy else "degraded"
        }
        
    except Exception as e:
        return {
            "message": "System health check failed",
            "success": False,
            "healthy": False,
            "status": "error",
            "error": str(e)
        }
