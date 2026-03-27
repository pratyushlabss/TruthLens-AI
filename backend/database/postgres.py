"""PostgreSQL database connection and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import os
from typing import Generator
import sys
from pathlib import Path
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get the project root directory using absolute path calculation
# This file is at: {project_root}/backend/database/postgres.py
postgres_file = Path(__file__).resolve()  # Use resolve() to get absolute path
backend_dir = postgres_file.parent.parent  # database -> backend
project_root = backend_dir.parent  # backend -> project root

logger.debug(f"postgres.py: __file__ = {__file__}")
logger.debug(f"postgres.py: postgres_file (resolved) = {postgres_file}")
logger.debug(f"postgres.py: backend_dir = {backend_dir}")
logger.debug(f"postgres.py: project_root = {project_root}")

# Database URL from environment. If missing, fallback to local SQLite for development.
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Alternative: Build from individual environment variables
if not DATABASE_URL:
    # SQLite database file - use absolute path to avoid working directory issues
    db_dir = project_root / "data"
    db_dir.mkdir(exist_ok=True, parents=True)
    db_file = db_dir / "truthlens.db"
    # Ensure we have an absolute path
    db_file_absolute = db_file.resolve()
    db_path_str = db_file_absolute.as_posix()
    # Create proper SQLite URL: sqlite:/// + absolute path
    DATABASE_URL = f"sqlite:///{db_path_str}"
    print(f"DEBUG: sqlite database path = {db_path_str}")
    print(f"DEBUG: DATABASE_URL = {DATABASE_URL}")
    logger.debug(f"postgres.py: Using LOCAL SQLite DATABASE_URL = {DATABASE_URL}")
elif "://" not in DATABASE_URL:
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "truthlens_db")
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Create engine with connection pooling
print(f"Creating SQLAlchemy engine with DATABASE_URL: {DATABASE_URL}")
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False, "timeout": 10},
        echo=False,
    )
    print(f"SQLite engine created successfully for: {DATABASE_URL}")
else:
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
        echo=False,  # Set to True for SQL logging
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session in FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from database.models import Base
    Base.metadata.create_all(bind=engine)
