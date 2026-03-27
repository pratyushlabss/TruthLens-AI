"""Model caching and optimization utilities."""

import logging
from typing import Optional, Any
import threading

logger = logging.getLogger(__name__)


class ModelCache:
    """
    Thread-safe singleton model cache.
    
    Ensures models are loaded only once and reused across all requests.
    """
    
    _instance = None
    _lock = threading.Lock()
    _models = {}
    _loading = {}
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_model(self, model_name: str, loader_func) -> Any:
        """
        Get a cached model or load it.
        
        Args:
            model_name: Name of the model
            loader_func: Function to call if model not cached
            
        Returns:
            The model instance
        """
        # Return cached model if available
        if model_name in self._models:
            logger.debug(f"Returning cached model: {model_name}")
            return self._models[model_name]
        
        # Wait if model is currently being loaded by another thread
        if model_name in self._loading:
            logger.info(f"Waiting for {model_name} to be loaded by another thread...")
            while model_name in self._loading:
                pass
            return self._models.get(model_name)
        
        # Load the model
        with self._lock:
            # Double-check that no one else loaded it while we waited
            if model_name in self._models:
                return self._models[model_name]
            
            try:
                self._loading[model_name] = True
                logger.info(f"Loading model: {model_name}")
                model = loader_func()
                self._models[model_name] = model
                logger.info(f"Successfully loaded and cached: {model_name}")
                return model
            finally:
                self._loading.pop(model_name, None)
    
    def clear_cache(self, model_name: Optional[str] = None):
        """
        Clear cached models.
        
        Args:
            model_name: Specific model to clear, or None to clear all
        """
        with self._lock:
            if model_name:
                if model_name in self._models:
                    del self._models[model_name]
                    logger.info(f"Cleared cache for: {model_name}")
            else:
                self._models.clear()
                logger.info("Cleared all model caches")
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "cached_models": list(self._models.keys()),
            "loading_models": list(self._loading.keys()),
            "total_cached": len(self._models)
        }


# Global cache instance
model_cache = ModelCache()
