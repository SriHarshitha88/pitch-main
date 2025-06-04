import redis
import json
from typing import Any, Optional
import os

# Get Redis URL from environment variable
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create Redis client
redis_client = redis.from_url(REDIS_URL)

class Cache:
    def __init__(self, client: redis.Redis = redis_client):
        self.client = client

    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set a value in cache with expiration"""
        try:
            serialized = json.dumps(value)
            return self.client.setex(key, expire, serialized)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a value from cache"""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache"""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False

# Create cache instance
cache = Cache() 