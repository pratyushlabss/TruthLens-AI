"""Caching for analysis results."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)


class AnalysisCache:
    """
    Simple in-memory cache for analysis results.
    
    Caches results for 1 hour and uses SHA256 hash of text as key.
    """
    
    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        """
        Initialize cache.
        
        Args:
            ttl_seconds: Time to live for cache entries (default 1 hour)
            max_size: Maximum number of cached entries
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache = {}
        self.hits = 0
        self.misses = 0
        logger.info(f"AnalysisCache initialized: TTL={ttl_seconds}s, max_size={max_size}")
    
    def _get_key(self, text: str) -> str:
        """Generate cache key from text."""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def get(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis result.
        
        Args:
            text: Input text
            
        Returns:
            Cached result or None if not found/expired
        """
        key = self._get_key(text)
        
        if key not in self._cache:
            self.misses += 1
            return None
        
        cached_entry = self._cache[key]
        
        # Check if expired
        if datetime.utcnow() > cached_entry["expires_at"]:
            del self._cache[key]
            self.misses += 1
            logger.debug(f"Cache expired for key: {key[:8]}...")
            return None
        
        self.hits += 1
        logger.debug(f"Cache hit for key: {key[:8]}... (total hits: {self.hits})")
        return cached_entry["result"]
    
    def set(self, text: str, result: Dict[str, Any]):
        """
        Cache an analysis result.
        
        Args:
            text: Input text
            result: Analysis result to cache
        """
        # Clear space if cache is full
        if len(self._cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k]["expires_at"]
            )
            del self._cache[oldest_key]
            logger.debug(f"Evicted oldest cache entry to make space")
        
        key = self._get_key(text)
        self._cache[key] = {
            "result": result,
            "expires_at": datetime.utcnow() + timedelta(seconds=self.ttl_seconds),
            "cached_at": datetime.utcnow()
        }
        logger.debug(f"Cached analysis result for key: {key[:8]}... (cache size: {len(self._cache)})")
    
    def clear(self):
        """Clear all cached entries."""
        self._cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Analysis cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total_requests,
            "hit_rate": f"{hit_rate:.1f}%",
            "ttl_seconds": self.ttl_seconds
        }


# Global analysis cache
analysis_cache = AnalysisCache()
