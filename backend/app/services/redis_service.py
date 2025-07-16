import redis
import json
import pickle
from typing import Any, Optional, Dict, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.default_ttl = 3600  # 1 hour default
    
    def _serialize(self, data: Any) -> str:
        """Serialize data for Redis storage"""
        try:
            return json.dumps(data)
        except (TypeError, ValueError):
            return pickle.dumps(data)
    
    def _deserialize(self, data: str) -> Any:
        """Deserialize data from Redis storage"""
        try:
            return json.loads(data)
        except (TypeError, ValueError):
            return pickle.loads(data)
    
    # Caching Methods
    def set_cache(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set a cache value with optional TTL"""
        try:
            serialized_value = self._serialize(value)
            ttl = ttl or self.default_ttl
            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Error setting cache for key {key}: {e}")
            return False
    
    def get_cache(self, key: str) -> Optional[Any]:
        """Get a cached value"""
        try:
            data = self.redis_client.get(key)
            if data:
                return self._deserialize(data)
            return None
        except Exception as e:
            logger.error(f"Error getting cache for key {key}: {e}")
            return None
    
    def delete_cache(self, key: str) -> bool:
        """Delete a cached value"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting cache for key {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing pattern {pattern}: {e}")
            return 0
    
    # Session Management
    def set_user_session(self, user_id: str, session_data: Dict[str, Any], ttl: int = 1800) -> bool:
        """Cache user session data (30 min default)"""
        key = f"session:{user_id}"
        return self.set_cache(key, session_data, ttl)
    
    def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user session data"""
        key = f"session:{user_id}"
        return self.get_cache(key)
    
    def delete_user_session(self, user_id: str) -> bool:
        """Delete user session data"""
        key = f"session:{user_id}"
        return self.delete_cache(key)
    
    # Model Caching
    def cache_model_metadata(self, model_id: str, metadata: Dict[str, Any], ttl: int = 86400) -> bool:
        """Cache model metadata (24 hour default)"""
        key = f"model:{model_id}"
        return self.set_cache(key, metadata, ttl)
    
    def get_model_metadata(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get cached model metadata"""
        key = f"model:{model_id}"
        return self.get_cache(key)
    
    def delete_model_metadata(self, model_id: str) -> bool:
        """Delete cached model metadata"""
        key = f"model:{model_id}"
        return self.delete_cache(key)
    
    # User Profile Caching
    def cache_user_profile(self, user_id: str, profile: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache user profile (1 hour default)"""
        key = f"user_profile:{user_id}"
        return self.set_cache(key, profile, ttl)
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user profile"""
        key = f"user_profile:{user_id}"
        return self.get_cache(key)
    
    def delete_user_profile(self, user_id: str) -> bool:
        """Delete cached user profile"""
        key = f"user_profile:{user_id}"
        return self.delete_cache(key)
    
    # Rate Limiting
    def check_rate_limit(self, identifier: str, limit: int = 100, window: int = 60) -> bool:
        """Check if request is within rate limit"""
        key = f"rate_limit:{identifier}"
        try:
            current = self.redis_client.incr(key)
            if current == 1:
                self.redis_client.expire(key, window)
            return current <= limit
        except Exception as e:
            logger.error(f"Error checking rate limit for {identifier}: {e}")
            return True  # Allow request if Redis fails
    
    def get_rate_limit_info(self, identifier: str) -> Dict[str, Any]:
        """Get current rate limit information"""
        key = f"rate_limit:{identifier}"
        try:
            current = int(self.redis_client.get(key) or 0)
            ttl = self.redis_client.ttl(key)
            return {
                "current": current,
                "remaining": max(0, 100 - current),
                "reset_in": ttl if ttl > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting rate limit info for {identifier}: {e}")
            return {"current": 0, "remaining": 100, "reset_in": 0}
    
    # Task Status Caching
    def cache_task_status(self, task_id: str, status: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache task status (1 hour default)"""
        key = f"task_status:{task_id}"
        return self.set_cache(key, status, ttl)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get cached task status"""
        key = f"task_status:{task_id}"
        return self.get_cache(key)
    
    # Data Analysis Caching
    def cache_data_profile(self, session_id: str, profile_data: Dict[str, Any], ttl: int = 7200) -> bool:
        """Cache data profile results (2 hour default)"""
        key = f"data_profile:{session_id}"
        return self.set_cache(key, profile_data, ttl)
    
    def get_data_profile(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get cached data profile"""
        key = f"data_profile:{session_id}"
        return self.get_cache(key)
    
    # Health Check
    def health_check(self) -> bool:
        """Check if Redis is healthy"""
        try:
            return self.redis_client.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
    
    # Statistics
    def get_stats(self) -> Dict[str, Any]:
        """Get Redis statistics"""
        try:
            info = self.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except Exception as e:
            logger.error(f"Error getting Redis stats: {e}")
            return {}
    
    def _calculate_hit_rate(self, info: Dict[str, Any]) -> float:
        """Calculate cache hit rate"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0

# Global instance
redis_service = RedisService() 