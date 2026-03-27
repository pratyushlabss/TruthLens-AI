"""Sessions management endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from database.postgres import get_db
from database.models import Session as SessionModel, Query

router = APIRouter()


class SessionCreateRequest(BaseModel):
    """Create session request."""
    user_id: str
    title: Optional[str] = None


class SessionResponse(BaseModel):
    """Session response model."""
    session_id: str
    user_id: str
    title: str
    created_at: datetime
    query_count: int = 0


@router.post("/sessions")
async def create_session(
    request: SessionCreateRequest,
    db: Session = Depends(get_db)
):
    """Create new analysis session."""
    try:
        session = SessionModel(
            user_id=request.user_id,
            title=request.title or "New Analysis"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "title": session.title,
            "created_at": session.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get session details."""
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get queries in session
    queries = db.query(Query).filter(
        Query.session_id == session_id
    ).all()
    
    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "title": session.title,
        "created_at": session.created_at,
        "query_count": len(queries),
        "queries": [
            {
                "query_id": q.query_id,
                "verdict": q.verdict,
                "confidence": q.confidence,
                "created_at": q.created_at
            }
            for q in queries
        ]
    }


@router.get("/sessions")
async def list_sessions(
    user_id: str,
    db: Session = Depends(get_db)
):
    """List all sessions for a user."""
    sessions = db.query(SessionModel).filter(
        SessionModel.user_id == user_id
    ).order_by(SessionModel.created_at.desc()).all()
    
    return {
        "user_id": user_id,
        "sessions": [
            {
                "session_id": s.session_id,
                "title": s.title,
                "created_at": s.created_at,
                "updated_at": s.updated_at
            }
            for s in sessions
        ]
    }
