"""Authentication routes for TruthLens AI."""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import csv
import os
import logging

from database.postgres import get_db
from database.models import User
from utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    get_token_from_header
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ---------------------------------------------------------------------------
# CSV Fast-Pass — credentials stored server-side only (never exposed publicly)
# ---------------------------------------------------------------------------

_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "users.csv")


def _load_csv_users() -> list:
    """Load hashed-password user records from backend/data/users.csv."""
    path = os.path.normpath(_CSV_PATH)
    if not os.path.exists(path):
        logger.warning(f"[CSV-AUTH] users.csv not found at {path}")
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class CSVLoginRequest(BaseModel):
    email: str
    password: str


class CSVLoginResponse(BaseModel):
    success: bool
    user_id: str = ""
    email: str = ""
    username: str = ""
    created_at: str = ""
    message: str = ""


@router.post("/csv-login", response_model=CSVLoginResponse)
async def csv_login(request: CSVLoginRequest):
    """
    Fast-pass login using the server-side hashed-password CSV.
    Credentials are never exposed publicly — the CSV lives in backend/data/.
    """
    import bcrypt

    if not request.email or not request.password:
        raise HTTPException(status_code=400, detail="Email and password required")

    users = _load_csv_users()
    if not users:
        raise HTTPException(status_code=503, detail="User store unavailable")

    for row in users:
        if row.get("email", "").strip().lower() == request.email.strip().lower():
            stored_hash = row.get("password_hash", "")
            try:
                match = bcrypt.checkpw(
                    request.password.encode("utf-8"),
                    stored_hash.encode("utf-8"),
                )
            except Exception:
                match = False

            if match:
                logger.info(f"[CSV-AUTH] Successful login for {request.email}")
                return CSVLoginResponse(
                    success=True,
                    user_id=f"csv-{request.email}",
                    email=row["email"],
                    username=row.get("username", ""),
                    created_at=row.get("created_at", ""),
                    message="Login successful",
                )
            else:
                logger.warning(f"[CSV-AUTH] Wrong password for {request.email}")
                raise HTTPException(status_code=401, detail="Invalid credentials")

    logger.warning(f"[CSV-AUTH] User not found: {request.email}")
    raise HTTPException(status_code=401, detail="Invalid credentials")


# Request/Response Models
class SignupRequest(BaseModel):
    """Signup request model."""
    email: str
    password: str
    username: str


class LoginRequest(BaseModel):
    """Login request model."""
    email: str
    password: str


class UserResponse(BaseModel):
    """User response model."""
    user_id: str
    email: str
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    user: UserResponse


def get_current_user(
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from Bearer token.
    
    Args:
        token: Bearer token extracted from Authorization header
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    payload = verify_token(token)
    user_id = payload.get("user_id")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


# Routes
@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Register a new user.
    
    Args:
        request: Signup request with email, password, and username
        db: Database session
        
    Returns:
        TokenResponse with access_token and user info
        
    Raises:
        HTTPException: If email already exists or validation fails
    """
    # Validate input
    if not request.email or not request.password or not request.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email, password, and username are required"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with hashed password
    hashed_password = hash_password(request.password)
    new_user = User(
        email=request.email,
        password_hash=hashed_password,
        username=request.username
    )
    
    # Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate JWT token
    access_token = create_access_token(new_user.user_id)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(new_user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT token.
    
    Args:
        request: Login request with email and password
        db: Database session
        
    Returns:
        TokenResponse with access_token and user info
        
    Raises:
        HTTPException: If credentials are invalid
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Validate input
        if not request.email or not request.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        # Find user by email
        logger.debug(f"Attempting login for email: {request.email}")
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            logger.warning(f"Login failed: user not found for email {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not verify_password(request.password, user.password_hash):
            logger.warning(f"Login failed: invalid password for {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Generate JWT token
        access_token = create_access_token(user.user_id)
        logger.info(f"Successful login for {request.email}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information.
    
    Requires valid Bearer token in Authorization header.
    
    Args:
        current_user: Current user from Bearer token
        
    Returns:
        UserResponse with user information
    """
    return UserResponse.from_orm(current_user)


@router.post("/logout")
async def logout():
    """Logout user.
    
    Note: Token invalidation is handled on the client side.
    This endpoint just confirms logout on server side.
    
    Returns:
        Success message
    """
    return {"message": "Logged out successfully"}

