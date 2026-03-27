"""Analyze endpoint using RAG pipeline with user authentication."""

from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile, Header
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import json

from database.postgres import get_db
from database.models import Query, Session as DBSession, User
from api.auth import get_current_user, verify_token
from utils.security import get_token_from_header
from services.scoring_engine import ScoringEngine
from services.monitoring import StructuredLogger

logger = logging.getLogger(__name__)
structured_logger = StructuredLogger(__name__)

router = APIRouter()

# Global RAG pipeline instance
_scoring_engine: Optional[ScoringEngine] = None


def get_scoring_engine() -> ScoringEngine:
    """Get or create the scoring engine (singleton)."""
    global _scoring_engine
    if _scoring_engine is None:
        _scoring_engine = ScoringEngine()
    return _scoring_engine


class AnalyzeRequest(BaseModel):
    """Analyze request model."""
    text: str
    use_cache: bool = True


class SourceInfo(BaseModel):
    """Information about a source."""
    title: str
    url: str
    credibility: str
    summary: str
    supports: Optional[str] = None


class AnalyzeResponse(BaseModel):
    """Clean response model."""
    verdict: str  # Only TRUE or FALSE
    confidence: float  # 0-100
    explanation: str
    sources: List[SourceInfo]
    signals: List[str]
    reasoning: str


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_claim(
    text: str = Form(...),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Analyze a claim using the scoring engine.
    
    This endpoint:
    1. Authenticates the user via JWT token
    2. Runs claim through scoring engine
    3. Generates verdict with confidence
    4. Returns evidence sources and reasoning
    5. Stores analysis in database per user
    
    Args:
        text: The claim to analyze
        authorization: Bearer token for authentication
        
    Returns:
        Verdict (TRUE/FALSE), confidence, explanation, sources, and reasoning
    """
    try:
        # 1. Validate input
        if not text or len(text.strip()) < 5:
            raise HTTPException(
                status_code=400,
                detail="Text must be at least 5 characters"
            )
        
        # 2. Authenticate user
        if not authorization:
            # For now, allow anonymous access (in production, require auth)
            # This makes testing easier during development
            user_id = "anonymous"
            user = None
        else:
            try:
                token = authorization.replace("Bearer ", "")
                user = get_current_user(token, db)
                user_id = user.user_id
            except Exception as auth_error:
                logger.warning(f"Auth error: {auth_error}")
                # Allow fallback to anonymous
                user_id = "anonymous"
                user = None
        
        # 3. Run scoring engine analysis
        engine = get_scoring_engine()
        rag_result = engine.analyze(text, include_explanations=False)
        
        # 4. Format response
        sources_list = []
        for src in rag_result.get("sources", []):
            try:
                sources_list.append(SourceInfo(
                    title=src.get("title", "Unknown"),
                    url=src.get("url", ""),
                    credibility=src.get("credibility", "Unknown"),
                    summary=src.get("summary", src.get("snippet", ""))[:300],
                    supports="TRUE" if rag_result["verdict"] == "TRUE" else "FALSE"
                ))
            except Exception as e:
                logger.warning(f"Failed to format source: {e}")
        
        response = AnalyzeResponse(
            verdict=rag_result["verdict"],  # Guaranteed TRUE or FALSE
            confidence=rag_result["confidence"],
            explanation=rag_result.get("summary", "Analysis complete"),
            sources=sources_list,
            signals=rag_result.get("key_signals", []),
            reasoning=rag_result.get("reasoning", "")
        )
        
        # 5. Store in database if user is authenticated
        if user:
            try:
                # Create or get user's default session for storing queries
                default_session = db.query(DBSession).filter(
                    DBSession.user_id == user_id,
                    DBSession.title == "Default Session"
                ).first()
                
                if not default_session:
                    default_session = DBSession(
                        user_id=user_id,
                        title="Default Session"
                    )
                    db.add(default_session)
                    db.commit()
                
                # Store the query
                query = Query(
                    session_id=default_session.session_id,
                    input_text=text,
                    verdict=response.verdict,
                    confidence=response.confidence,
                    score_real=100.0 if response.verdict == "TRUE" else 10.0,
                    score_rumor=50.0 if response.verdict == "FALSE" else 30.0,
                    score_fake=100.0 if response.verdict == "FALSE" else 10.0,
                    propagation_risk=rag_result.get("propagation_risk", "MEDIUM"),
                    propagation_score=rag_result.get("propagation_score", 50.0),
                    evidence_score=rag_result.get("evidence_score", response.confidence),
                    model_breakdown=rag_result.get("model_breakdown", {
                        "verdict": response.verdict,
                        "confidence": response.confidence,
                        "sources_count": len(sources_list)
                    }),
                    summary=response.explanation,
                    key_signals=response.signals,
                    claims=rag_result.get("claims", [text]),
                    evidence_sources=[src.dict() for src in sources_list]
                )
                
                db.add(query)
                db.commit()
                
                structured_logger.info(
                    "Query stored",
                    user_id=user_id,
                    verdict=response.verdict,
                    confidence=response.confidence
                )
            except Exception as db_error:
                logger.error(f"Database error: {db_error}")
                db.rollback()
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analyze endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred during analysis"
        )
