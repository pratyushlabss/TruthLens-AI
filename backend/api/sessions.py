"""Refactored Sessions endpoint with user authentication."""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from database.postgres import get_db
from database.models import Session as SessionModel, Query, User
from api.auth import get_current_user, verify_token

router = APIRouter()


class QueryResponse(BaseModel):
    """Single query response."""
    query_id: str
    input_text: str
    verdict: str
    confidence: float
    created_at: datetime


class SessionResponse(BaseModel):
    """Session response model."""
    session_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    query_count: int


class SessionDetailResponse(BaseModel):
    """Session with queries."""
    session_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    queries: List[QueryResponse]


class QueryDetailResponse(BaseModel):
    """Query response with all details."""
    query_id: str
    input_text: str
    verdict: str
    confidence: float
    source_count: int
    created_at: datetime


@router.get("/sessions", response_model=List[SessionResponse])
async def list_user_sessions(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get all sessions for the authenticated user.
    
    Returns list of sessions with query counts.
    """
    try:
        # Authenticate user
        if not authorization:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user(token, db)
        
        # Get all sessions for this user
        sessions = db.query(SessionModel).filter(
            SessionModel.user_id == user.user_id
        ).order_by(SessionModel.created_at.desc()).all()
        
        # Count queries for each session
        result = []
        for session in sessions:
            query_count = db.query(Query).filter(
                Query.session_id == session.session_id
            ).count()
            
            result.append(SessionResponse(
                session_id=session.session_id,
                title=session.title,
                created_at=session.created_at,
                updated_at=session.updated_at,
                query_count=query_count
            ))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/latest", response_model=List[QueryDetailResponse])
async def get_latest_queries(
    limit: int = 10,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get the latest queries across all sessions for the user.
    
    Returns the most recent queries in descending order.
    
    Args:
        limit: Maximum number of queries to return (default 10)
        authorization: Bearer token
        
    Returns:
        List of latest queries with all details
    """
    try:
        # Authenticate user
        if not authorization:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user(token, db)
        
        # Get all sessions for this user
        user_sessions = db.query(SessionModel).filter(
            SessionModel.user_id == user.user_id
        ).all()
        
        session_ids = [s.session_id for s in user_sessions]
        
        # Get latest queries across all sessions
        queries = db.query(Query).filter(
            Query.session_id.in_(session_ids) if session_ids else False
        ).order_by(Query.created_at.desc()).limit(limit).all()
        
        # Format response
        result = []
        for q in queries:
            source_count = 0
            if q.evidence_sources:
                if isinstance(q.evidence_sources, list):
                    source_count = len(q.evidence_sources)
                elif isinstance(q.evidence_sources, dict):
                    source_count = 1
            
            result.append(QueryDetailResponse(
                query_id=q.query_id,
                input_text=q.input_text,
                verdict=q.verdict,
                confidence=q.confidence,
                source_count=source_count,
                created_at=q.created_at
            ))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
async def get_session_detail(
    session_id: str,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get session details with all queries.
    
    Includes:
    - Session metadata
    - All queries in session with verdicts
    """
    try:
        # Authenticate user
        if not authorization:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user(token, db)
        
        # Get session
        session = db.query(SessionModel).filter(
            SessionModel.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Verify user ownership
        if session.user_id != user.user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Get queries
        queries = db.query(Query).filter(
            Query.session_id == session_id
        ).order_by(Query.created_at.desc()).all()
        
        return SessionDetailResponse(
            session_id=session.session_id,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            queries=[
                QueryResponse(
                    query_id=q.query_id,
                    input_text=q.input_text,
                    verdict=q.verdict,
                    confidence=q.confidence,
                    created_at=q.created_at
                )
                for q in queries
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}")
async def create_session(
    title: str,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Create new analysis session for authenticated user.
    
    Args:
        title: Name of the session
        authorization: Bearer token
        
    Returns:
        Created session with ID
    """
    try:
        # Authenticate user
        if not authorization:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user(token, db)
        
        # Create session
        session = SessionModel(
            user_id=user.user_id,
            title=title
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return {
            "session_id": session.session_id,
            "title": session.title,
            "created_at": session.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
