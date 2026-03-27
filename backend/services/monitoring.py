"""Production monitoring and metrics tracking."""

import time
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)


class StructuredLogger:
    """Structured JSON logging for production."""
    
    def __init__(self, name: str):
        """Initialize structured logger."""
        self.logger = logging.getLogger(name)
        self.name = name
    
    def _format_log(self, level: str, message: str, **kwargs) -> str:
        """Format log entry as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "logger": self.name,
            "message": message,
            **kwargs
        }
        return json.dumps(log_entry)
    
    def info(self, message: str, **kwargs):
        """Log info with metadata."""
        self.logger.info(self._format_log("INFO", message, **kwargs))
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log error with metadata."""
        self.logger.error(self._format_log("ERROR", message, **kwargs), exc_info=exc_info)
    
    def warning(self, message: str, **kwargs):
        """Log warning with metadata."""
        self.logger.warning(self._format_log("WARNING", message, **kwargs))
    
    def debug(self, message: str, **kwargs):
        """Log debug with metadata."""
        self.logger.debug(self._format_log("DEBUG", message, **kwargs))


class MetricsCollector:
    """Collect and track application metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self._lock = threading.Lock()
        self.reset()
        self._logger = StructuredLogger("metrics")
    
    def reset(self):
        """Reset all metrics."""
        with self._lock:
            self.total_requests = 0
            self.total_errors = 0
            self.response_times = []  # Store all response times for average
            self.ml_inference_times = []  # Store ML inference times
            self.endpoint_hits = defaultdict(int)  # Track hits per endpoint
            self.error_details = []  # Store recent errors
    
    def record_request(self, endpoint: str, method: str, status_code: int, 
                      response_time: float, ml_time: Optional[float] = None,
                      error: Optional[str] = None):
        """Record a request metric.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method (GET, POST, etc)
            status_code: Response status code
            response_time: Total request time in seconds
            ml_time: ML inference time in seconds (optional)
            error: Error message if request failed (optional)
        """
        with self._lock:
            self.total_requests += 1
            self.endpoint_hits[endpoint] += 1
            self.response_times.append(response_time)
            
            if ml_time is not None:
                self.ml_inference_times.append(ml_time)
            
            if status_code >= 400:
                self.total_errors += 1
            
            if error:
                self.error_details.append({
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": status_code,
                    "error": error,
                    "response_time": response_time
                })
                # Keep only last 100 errors
                if len(self.error_details) > 100:
                    self.error_details = self.error_details[-100:]
            
            # Log the metric
            self._logger.info(
                "request_completed",
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time_ms=round(response_time * 1000, 2),
                ml_time_ms=round(ml_time * 1000, 2) if ml_time else None,
                error=error
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        with self._lock:
            avg_response_time = (
                sum(self.response_times) / len(self.response_times)
                if self.response_times else 0
            )
            avg_ml_time = (
                sum(self.ml_inference_times) / len(self.ml_inference_times)
                if self.ml_inference_times else 0
            )
            
            return {
                "total_requests": self.total_requests,
                "total_errors": self.total_errors,
                "error_rate": (
                    self.total_errors / self.total_requests * 100
                    if self.total_requests > 0 else 0
                ),
                "avg_response_time": round(avg_response_time, 4),
                "avg_response_time_ms": round(avg_response_time * 1000, 2),
                "avg_ml_inference_time": round(avg_ml_time, 4),
                "avg_ml_inference_time_ms": round(avg_ml_time * 1000, 2),
                "total_ml_inference_time": round(sum(self.ml_inference_times), 4),
                "endpoint_hits": dict(self.endpoint_hits),
                "recent_errors": self.error_details[-10:],  # Last 10 errors
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
    
    def get_simple_metrics(self) -> Dict[str, Any]:
        """Get simplified metrics for basic /metrics endpoint."""
        metrics = self.get_metrics()
        return {
            "total_requests": metrics["total_requests"],
            "avg_response_time": metrics["avg_response_time"],
            "errors": metrics["total_errors"]
        }


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create the global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


class MLInferenceTimer:
    """Context manager for timing ML inference operations."""
    
    def __init__(self):
        """Initialize timer."""
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing."""
        self.end_time = time.time()
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.end_time is None:
            return 0
        return self.end_time - self.start_time
