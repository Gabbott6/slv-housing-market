"""
AI response caching service to reduce API calls and improve performance.
Uses in-memory cache with TTL (Time To Live) expiration.
"""
import time
import json
import hashlib
from typing import Optional, Dict, Any


class AIResponseCache:
    """
    In-memory cache for AI API responses with TTL.

    Reduces redundant API calls by caching responses based on request parameters.
    Implements LRU eviction when cache size exceeds limits.
    """

    def __init__(self, max_size: int = 500, default_ttl: int = 3600):
        """
        Initialize cache.

        Args:
            max_size: Maximum number of cached entries
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}

    def _generate_cache_key(self, analysis_type: str, params: Dict[str, Any]) -> str:
        """
        Generate a unique cache key from analysis type and parameters.

        Args:
            analysis_type: Type of analysis (e.g., "summary", "recommend")
            params: Request parameters

        Returns:
            Cache key string
        """
        # Sort params to ensure consistent key generation
        param_str = json.dumps(params, sort_keys=True, default=str)
        hash_obj = hashlib.md5(param_str.encode())
        return f"ai:{analysis_type}:{hash_obj.hexdigest()}"

    async def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached response if it exists and hasn't expired.

        Args:
            cache_key: Cache key

        Returns:
            Cached data or None if not found/expired
        """
        if cache_key not in self.cache:
            return None

        entry = self.cache[cache_key]
        now = time.time()

        # Check if expired
        if now > entry["expires_at"]:
            del self.cache[cache_key]
            return None

        # Update access time for LRU
        entry["last_accessed"] = now

        return entry["data"]

    async def set(
        self,
        cache_key: str,
        data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> None:
        """
        Cache a response with TTL.

        Args:
            cache_key: Cache key
            data: Data to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        ttl = ttl or self.default_ttl
        now = time.time()

        # Evict old entries if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_lru()

        self.cache[cache_key] = {
            "data": data,
            "created_at": now,
            "last_accessed": now,
            "expires_at": now + ttl
        }

    def _evict_lru(self) -> None:
        """Evict least recently used cache entry."""
        if not self.cache:
            return

        # Find entry with oldest access time
        lru_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k]["last_accessed"]
        )

        del self.cache[lru_key]

    async def invalidate(self, cache_key: str) -> bool:
        """
        Invalidate a specific cache entry.

        Args:
            cache_key: Cache key to invalidate

        Returns:
            True if entry was found and removed, False otherwise
        """
        if cache_key in self.cache:
            del self.cache[cache_key]
            return True
        return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all cache entries matching a pattern.

        Args:
            pattern: Pattern to match (e.g., "ai:summary:*")

        Returns:
            Number of entries invalidated
        """
        # Simple pattern matching (supports * wildcard)
        pattern_parts = pattern.split("*")

        keys_to_delete = []
        for key in self.cache.keys():
            if all(part in key for part in pattern_parts):
                keys_to_delete.append(key)

        for key in keys_to_delete:
            del self.cache[key]

        return len(keys_to_delete)

    async def clear(self) -> None:
        """Clear entire cache."""
        self.cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = time.time()
        expired_count = sum(
            1 for entry in self.cache.values()
            if now > entry["expires_at"]
        )

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "expired_entries": expired_count,
            "utilization": len(self.cache) / self.max_size
        }

    def generate_key(self, analysis_type: str, **kwargs) -> str:
        """
        Public method to generate cache key.

        Args:
            analysis_type: Type of analysis
            **kwargs: Parameters to include in cache key

        Returns:
            Cache key string
        """
        return self._generate_cache_key(analysis_type, kwargs)
