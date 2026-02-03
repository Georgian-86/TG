"""
Response caching utilities for lesson generation
Reduces duplicate API calls by caching generated lessons
"""
import hashlib
import json
from typing import Optional, Dict, Any
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


import os
import pickle
import tempfile
from pathlib import Path

class LessonCache:
    """Cache for generated lessons to avoid duplicate OpenAI API calls"""
    
    def __init__(self, redis_client=None):
        """
        Initialize cache with optional Redis client
        Falls back to file-based cache for multi-worker support
        """
        self.redis = redis_client
        self.cache_ttl = 86400  # 24 hours
        
        # Setup file cache
        self.cache_dir = Path(tempfile.gettempdir()) / "teachgenie_cache"
        self.cache_dir.mkdir(exist_ok=True)
        logger.info(f"File cache directory: {self.cache_dir}")
        
    def _generate_key(self, topic: str, level: str, duration: int, include_quiz: bool) -> str:
        """Generate cache key from lesson parameters"""
        params = f"{topic}|{level}|{duration}|{include_quiz}"
        return f"lesson_{hashlib.md5(params.lower().encode()).hexdigest()}"
    
    async def get(self, topic: str, level: str, duration: int, include_quiz: bool) -> Optional[Dict[str, Any]]:
        """Retrieve cached lesson if exists"""
        key = self._generate_key(topic, level, duration, include_quiz)
        
        try:
            if self.redis:
                cached = await self.redis.get(key)
                if cached:
                    logger.info(f"Redis cache HIT for topic: {topic}")
                    return json.loads(cached)
            else:
                # File cache
                cache_file = self.cache_dir / f"{key}.json"
                if cache_file.exists():
                    # Check TTL (modification time)
                    mtime = cache_file.stat().st_mtime
                    if time.time() - mtime < self.cache_ttl:
                        async with aiofiles.open(cache_file, 'r') as f:
                            content = await f.read()
                            logger.info(f"File cache HIT for topic: {topic}")
                            return json.loads(content)
                    else:
                        # Expired
                        cache_file.unlink()
                        logger.info(f"File cache expired for topic: {topic}")
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
        
        logger.info(f"Cache MISS for topic: {topic}")
        return None
    
    async def set(self, topic: str, level: str, duration: int, include_quiz: bool, data: Dict[str, Any]):
        """Store lesson in cache"""
        key = self._generate_key(topic, level, duration, include_quiz)
        
        try:
            if self.redis:
                await self.redis.setex(key, self.cache_ttl, json.dumps(data))
                logger.info(f"Cached lesson to Redis: {topic}")
            else:
                # File cache
                cache_file = self.cache_dir / f"{key}.json"
                async with aiofiles.open(cache_file, 'w') as f:
                    await f.write(json.dumps(data))
                logger.info(f"Cached lesson to file: {topic}")
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
    
    async def clear(self):
        """Clear all cached lessons"""
        try:
            if self.redis:
                keys = await self.redis.keys("lesson_*")
                if keys:
                    await self.redis.delete(*keys)
                logger.info(f"Cleared {len(keys)} cached lessons from Redis")
            else:
                count = 0
                for f in self.cache_dir.glob("lesson_*.json"):
                    f.unlink()
                    count += 1
                logger.info(f"Cleared {count} cached lessons from file system")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")


# Global cache instance
lesson_cache: Optional[LessonCache] = None

def init_cache(redis_client=None):
    """Initialize global cache instance"""
    global lesson_cache
    lesson_cache = LessonCache(redis_client)
    logger.info("Lesson cache initialized")

def get_cache() -> LessonCache:
    """Get global cache instance"""
    global lesson_cache
    if lesson_cache is None:
        # Fallback to memory cache
        lesson_cache = LessonCache()
    return lesson_cache
