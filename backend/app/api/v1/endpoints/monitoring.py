from fastapi import APIRouter, HTTPException, status, Depends
from services.redis_service import redis_service
from core.auth import get_current_user
from typing import Dict, Any

router = APIRouter()

@router.get("/redis/stats")
async def get_redis_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get Redis statistics and performance metrics.
    
    Returns Redis memory usage, hit rates, and performance statistics.
    """
    try:
        stats = redis_service.get_stats()
        return {
            "message": "Redis statistics retrieved successfully",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving Redis stats: {str(e)}"
        )

@router.get("/redis/health")
async def get_redis_health(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Check Redis health status.
    
    Returns Redis connection status and basic health information.
    """
    try:
        is_healthy = redis_service.health_check()
        return {
            "message": "Redis health check completed",
            "healthy": is_healthy,
            "status": "healthy" if is_healthy else "unhealthy"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking Redis health: {str(e)}"
        )

@router.post("/redis/clear-cache")
async def clear_cache(
    pattern: str = "cache:*",
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Clear Redis cache entries matching a pattern.
    
    - **pattern**: Redis key pattern to match (default: "cache:*")
    - Returns number of keys cleared
    """
    try:
        cleared_count = redis_service.clear_pattern(pattern)
        return {
            "message": f"Cache cleared successfully",
            "pattern": pattern,
            "keys_cleared": cleared_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cache: {str(e)}"
        )

@router.get("/redis/rate-limit/{identifier}")
async def get_rate_limit_info(
    identifier: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get rate limit information for a specific identifier.
    
    - **identifier**: User ID, IP, or other identifier
    - Returns current rate limit status
    """
    try:
        rate_info = redis_service.get_rate_limit_info(identifier)
        return {
            "message": "Rate limit information retrieved",
            "identifier": identifier,
            "rate_limit": rate_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting rate limit info: {str(e)}"
        ) 