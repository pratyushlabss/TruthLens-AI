"""FastAPI main application file."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os

# Import routes
from api import analyze, upload, sessions

# Initialize database
from database.models import Base
from database.postgres import engine

# Create tables on startup
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 TruthLens AI Backend Starting...")
    yield
    # Shutdown
    print("🛑 TruthLens AI Backend Shutting Down...")


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

# Include routers
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(sessions.router, prefix="/api", tags=["Sessions"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "TruthLens AI"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "TruthLens AI - Misinformation Detection Engine",
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
        reload=reload
    )
