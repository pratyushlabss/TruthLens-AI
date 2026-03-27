"""Analytics endpoint for user statistics."""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from database.postgres import get_db
from database.models import Query, Session as SessionModel, User
from api.auth import get_current_user

router = APIRouter()


class AnalyticsResponse(BaseModel):
    """Analytics response model."""
    total_queries: int
    total_sessions: int
    queries_this_week: int
    avg_confidence: float
    true_count: int
    false_count: int
    uncertain_count: int
    recent_analyses: list


class AnalyticsDetailResponse(BaseModel):
    """Detailed analytics for charts and visualizations."""
    total_claims: int
    true_count: int
    false_count: int
    uncertain_count: int
    avg_confidence: float
    confidence_distribution: Dict[str, int]  # {high, medium, low}
    source_usage: List[Dict[str, Any]]  # [{name, count, avg_credibility}]
    verdict_distribution: Dict[str, int]  # {TRUE, FALSE, UNCERTAIN}
    recent_analyses: List[Dict[str, Any]]
    heatmap_data: List[Dict[str, Any]]  # For visualization


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_user_analytics(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get analytics for the authenticated user.
    
    Returns:
    - Total queries and sessions
    - Verdicts breakdown (TRUE vs FALSE vs UNCERTAIN)
    - Average confidence
    - Recent analyses
    """
    try:
        # Authenticate user
        if not authorization:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user(token, db)
        
        # Get user's sessions
        user_sessions = db.query(SessionModel).filter(
            SessionModel.user_id == user.user_id
        ).all()
        
        session_ids = [s.session_id for s in user_sessions]
        
        # Query stats
        queries = db.query(Query).filter(
            Query.session_id.in_(session_ids) if session_ids else False
        ).all()
        
        # Calculate metrics
        total_queries = len(queries)
        
        # This week queries
        week_ago = datetime.utcnow() - timedelta(days=7)
        week_queries = db.query(Query).filter(
            Query.session_id.in_(session_ids) if session_ids else False,
            Query.created_at >= week_ago
        ).all()
        queries_this_week = len(week_queries)
        
        # Verdict breakdown
        true_count = sum(1 for q in queries if q.verdict == "TRUE")
        false_count = sum(1 for q in queries if q.verdict == "FALSE")
        uncertain_count = sum(1 for q in queries if q.verdict == "UNCERTAIN")
        
        # Average confidence
        avg_confidence = sum(q.confidence for q in queries) / max(len(queries), 1) if queries else 0.0
        
        # Recent analyses
        recent_analyses = []
        for q in sorted(queries, key=lambda x: x.created_at, reverse=True)[:10]:
            recent_analyses.append({
                "query_id": q.query_id,
                "input_text": q.input_text[:100] + "..." if len(q.input_text) > 100 else q.input_text,
                "verdict": q.verdict,
                "confidence": q.confidence,
                "created_at": q.created_at.isoformat()
            })
        
        return AnalyticsResponse(
            total_queries=total_queries,
            total_sessions=len(user_sessions),
            queries_this_week=queries_this_week,
            avg_confidence=round(avg_confidence, 2),
            true_count=true_count,
            false_count=false_count,
            uncertain_count=uncertain_count,
            recent_analyses=recent_analyses
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/detailed", response_model=AnalyticsDetailResponse)
async def get_detailed_analytics(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for dashboards and visualizations.
    
    Returns:
    - Confidence distribution (high/medium/low)
    - Source usage frequency and credibility
    - Verdict distribution
    - Heatmap data for evidence visualization
    """
    try:
        # Authenticate user
        if not authorization:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        token = authorization.replace("Bearer ", "")
        user = get_current_user(token, db)
        
        # Get user's sessions
        user_sessions = db.query(SessionModel).filter(
            SessionModel.user_id == user.user_id
        ).all()
        
        session_ids = [s.session_id for s in user_sessions]
        
        # Query stats
        queries = db.query(Query).filter(
            Query.session_id.in_(session_ids) if session_ids else False
        ).all()
        
        if not queries:
            # Return empty structure if no queries
            return AnalyticsDetailResponse(
                total_claims=0,
                true_count=0,
                false_count=0,
                uncertain_count=0,
                avg_confidence=0.0,
                confidence_distribution={"high": 0, "medium": 0, "low": 0},
                source_usage=[],
                verdict_distribution={"TRUE": 0, "FALSE": 0, "UNCERTAIN": 0},
                recent_analyses=[],
                heatmap_data=[]
            )
        
        # Confidence distribution
        confidence_dist = {"high": 0, "medium": 0, "low": 0}
        for q in queries:
            confidence = q.confidence / 100.0 if q.confidence > 1 else q.confidence
            if confidence > 0.8:
                confidence_dist["high"] += 1
            elif confidence > 0.5:
                confidence_dist["medium"] += 1
            else:
                confidence_dist["low"] += 1
        
        # Verdict distribution
        verdict_dist = {
            "TRUE": sum(1 for q in queries if q.verdict == "TRUE"),
            "FALSE": sum(1 for q in queries if q.verdict == "FALSE"),
            "UNCERTAIN": sum(1 for q in queries if q.verdict == "UNCERTAIN")
        }
        
        # Source usage
        source_usage = {}
        for q in queries:
            if q.evidence_sources:
                sources = q.evidence_sources if isinstance(q.evidence_sources, list) else [q.evidence_sources]
                for src in sources:
                    if isinstance(src, dict):
                        src_name = src.get("title", "Unknown")
                        if src_name not in source_usage:
                            source_usage[src_name] = {"count": 0, "credibility_sum": 0, "credibility_count": 0}
                        
                        source_usage[src_name]["count"] += 1
                        
                        # Parse credibility
                        cred = src.get("credibility", "0.5")
                        try:
                            cred_val = float(cred) if isinstance(cred, str) else cred
                            if cred_val > 1:
                                cred_val = cred_val / 100.0
                            source_usage[src_name]["credibility_sum"] += cred_val
                            source_usage[src_name]["credibility_count"] += 1
                        except:
                            pass
        
        # Format source usage
        formatted_sources = []
        for name, data in sorted(source_usage.items(), key=lambda x: x[1]["count"], reverse=True)[:10]:
            avg_cred = (data["credibility_sum"] / data["credibility_count"] * 100) if data["credibility_count"] > 0 else 50
            formatted_sources.append({
                "name": name,
                "count": data["count"],
                "avg_credibility": round(avg_cred, 1)
            })
        
        # Recent analyses
        recent_analyses = []
        for q in sorted(queries, key=lambda x: x.created_at, reverse=True)[:5]:
            recent_analyses.append({
                "query_id": q.query_id,
                "input_text": q.input_text[:80] + "..." if len(q.input_text) > 80 else q.input_text,
                "verdict": q.verdict,
                "confidence": q.confidence / 100.0 if q.confidence > 1 else q.confidence,
                "source_count": len(q.evidence_sources) if q.evidence_sources else 0,
                "created_at": q.created_at.isoformat()
            })
        
        # Heatmap data (sources x claims)
        heatmap_data = []
        source_names = [src["name"] for src in formatted_sources]
        for source_name in source_names[:8]:  # Top 8 sources
            row = {"source": source_name, "bars": []}
            for q in sorted(queries, key=lambda x: x.created_at)[-10:]:  # Last 10 claims
                if q.evidence_sources:
                    sources = q.evidence_sources if isinstance(q.evidence_sources, list) else [q.evidence_sources]
                    for src in sources:
                        if isinstance(src, dict) and src.get("title") == source_name:
                            try:
                                cred = float(src.get("credibility", "0.5"))
                                if cred <= 1:
                                    cred = cred * 100
                                row["bars"].append(int(cred))
                                break
                            except:
                                row["bars"].append(50)
                    if len(row["bars"]) < len([q for q in sorted(queries, key=lambda x: x.created_at)[-10:]]):
                        row["bars"].append(0)
                        
            if row["bars"]:  # Only add if has data
                heatmap_data.append(row)
        
        # Calculate average confidence
        avg_confidence = sum(q.confidence for q in queries) / len(queries) if queries else 0.0
        if avg_confidence > 1:
            avg_confidence = avg_confidence / 100.0
        
        return AnalyticsDetailResponse(
            total_claims=len(queries),
            true_count=verdict_dist["TRUE"],
            false_count=verdict_dist["FALSE"],
            uncertain_count=verdict_dist["UNCERTAIN"],
            avg_confidence=round(avg_confidence, 2),
            confidence_distribution=confidence_dist,
            source_usage=formatted_sources,
            verdict_distribution=verdict_dist,
            recent_analyses=recent_analyses,
            heatmap_data=heatmap_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
