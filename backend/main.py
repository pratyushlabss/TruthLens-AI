"""FastAPI main application file."""

# Load environment variables from .env file FIRST
from pathlib import Path
from dotenv import load_dotenv

# Load .env from root directory (parent of backend)
root_env = Path(__file__).parent.parent / ".env"
if root_env.exists():
    load_dotenv(root_env)
else:
    # Try to load from backend directory
    backend_env = Path(__file__).parent / ".env"
    if backend_env.exists():
        load_dotenv(backend_env)

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import uvicorn
import os
import logging
import json
from datetime import datetime
import time

# Import routes
from api import analyze, upload, sessions, auth, analytics
from services.monitoring import get_metrics_collector, StructuredLogger

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"  # Using json format from StructuredLogger
)
logger = logging.getLogger(__name__)
structured_logger = StructuredLogger(__name__)


# Error response model
class ErrorResponse:
    """Standardized error response."""
    
    @staticmethod
    def to_dict(error: str, status_code: int, detail: str = None):
        """Convert error to dict format."""
        return {
            "error": error,
            "status": status_code,
            "detail": detail,
            "timestamp": datetime.utcnow().isoformat()
        }


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    structured_logger.info("Backend starting", status="startup")
    try:
        # Initialize database with proper error handling
        from database.models import Base
        from database.postgres import engine, DATABASE_URL
        
        structured_logger.info(f"Initializing database", database_url=DATABASE_URL[:50] + "...")
        
        # Test connection first
        try:
            conn = engine.connect()
            conn.close()
            structured_logger.debug("Database connection test passed")
        except Exception as conn_err:
            structured_logger.warning(f"Database connection failed", error=str(conn_err))
            raise
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        structured_logger.info("Database initialized successfully", database="sqlite")
    except Exception as e:
        structured_logger.warning("Database initialization failed", error=str(e), exc_info=True)
    yield
    # Shutdown
    structured_logger.info("Backend shutting down", status="shutdown")
    metrics = get_metrics_collector().get_metrics()
    structured_logger.info("Final metrics", **metrics)


# Create FastAPI app
app = FastAPI(
    title="TruthLens AI",
    description="Production-grade misinformation detection system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.warning(f"Validation error for {request.url}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse.to_dict(
            "Validation Error",
            422,
            str(exc.errors()[0] if exc.errors() else str(exc))
        )
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse.to_dict(
            "Internal Server Error",
            500,
            "An unexpected error occurred. Please try again later."
        )
    )


@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """Monitor requests with timing and metrics collection."""
    start_time = time.time()
    endpoint = request.url.path
    method = request.method
    
    # Log incoming request
    structured_logger.debug(
        "request_received",
        method=method,
        endpoint=endpoint,
        client=request.client.host if request.client else "unknown"
    )
    
    # Process request
    error_msg = None
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception as e:
        error_msg = str(e)
        structured_logger.error(
            "request_failed",
            method=method,
            endpoint=endpoint,
            error=error_msg,
            exc_info=True
        )
        raise
    finally:
        # Record metrics even on error
        response_time = time.time() - start_time
        metrics_collector = get_metrics_collector()
        metrics_collector.record_request(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            error=error_msg
        )


# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(sessions.router, prefix="/api", tags=["Sessions"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "TruthLens AI",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/metrics")
async def get_metrics():
    """Get application metrics."""
    metrics_collector = get_metrics_collector()
    return metrics_collector.get_metrics()


@app.get("/metrics/simple")
async def get_simple_metrics():
    """Get simplified metrics endpoint."""
    metrics_collector = get_metrics_collector()
    return metrics_collector.get_simple_metrics()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "TruthLens AI - Misinformation Detection Engine",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("ENV", "development") == "development"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
