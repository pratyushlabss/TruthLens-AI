"""Analyze endpoint for claims and articles with multimodal support."""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import time

from database.postgres import get_db
from database.models import Query, ClaimHistory
from services.scoring_engine import ScoringEngine
from services.analysis_cache import analysis_cache
from services.monitoring import get_metrics_collector, StructuredLogger, MLInferenceTimer
from services.multimodal_vision import MultimodalVisionService

logger = logging.getLogger(__name__)
structured_logger = StructuredLogger(__name__)

router = APIRouter()

# Lazy-loaded global instances
_scoring_engine: Optional[ScoringEngine] = None
_vision_service: Optional[MultimodalVisionService] = None

def get_scoring_engine() -> ScoringEngine:
    """Get or create the global scoring engine (singleton with lazy loading)."""
    global _scoring_engine
    if _scoring_engine is None:
        _scoring_engine = ScoringEngine()
    return _scoring_engine

def get_vision_service() -> MultimodalVisionService:
    """Get or create the global vision service (singleton with lazy loading)."""
    global _vision_service
    if _vision_service is None:
        _vision_service = MultimodalVisionService()
    return _vision_service


class AnalyzeRequest(BaseModel):
    """Analyze request model with optional multimodal inputs."""
    text: str
    session_id: Optional[str] = None
    use_cache: bool = True  # Allow disabling cache if needed


class AnalyzeResponse(BaseModel):
    """
    Enhanced analyze response model with explainability and multimodal support.
    
    Three-model fusion logic (60% NLP + 25% SBERT Evidence + 15% Propagation):
    - truth_score: Final normalized confidence (0-1)
    - explanation_map: Word-level impact scores from SHAP
    - top_evidence_sources: Top 3 credible sources supporting/refuting claim
    """
    verdict: str
    confidence: float
    truth_score: float  # NEW: Normalized final score (0-1)
    explanation_map: Dict[str, float]  # NEW: SHAP word impact map
    top_evidence_sources: List[Dict[str, Any]]  # NEW: Top 3 sources
    scores: dict
    confidence_label: str
    reasoning: str
    highlighted_text: list
    propagation_risk: str
    propagation_score: float
    evidence_score: float
    summary: str
    claims: list
    evidence_sources: list
    sources: list
    key_signals: list
    model_breakdown: dict
    image_analysis: Optional[Dict] = None  # NEW: Image caption + mismatch score


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_claim(
    text: str = Form(...),
    session_id: Optional[str] = Form(None),
    use_cache: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Analyze a claim using three-model fusion pipeline:
    
    1. RoBERTa (60% weight): NLP-based misinformation detection
    2. Sentence-BERT (25% weight): Semantic evidence retrieval and credibility
    3. Propagation Model (15% weight): Spread risk analysis using NetworkX
    
    Multimodal support:
    - Text claims
    - Image sources (converted to captions via BLIP)
    - Combined analysis for claim + image context
    
    Response includes:
    - truth_score: Normalized 0-1 confidence
    - explanation_map: SHAP word-level importance
    - top_evidence_sources: Top 3 supporting/refuting sources
    """
    metrics_collector = get_metrics_collector()
    request_start_time = time.time()
    ml_time = None
    
    try:
        # Validate input
        if not text or len(text.strip()) < 5:
            raise HTTPException(status_code=400, detail="Text must be at least 5 characters")
        
        # Process image if provided
        image_analysis = None
        if image:
            try:
                vision_service = get_vision_service()
                image_bytes = await image.read()
                image_analysis = vision_service.analyze_image_for_claim(
                    image_bytes,
                    text
                )
                logger.info(f"Image analyzed: {image_analysis.get('caption', 'No caption')}")
            except Exception as e:
                logger.warning(f"Image analysis failed: {e}")
                image_analysis = {"error": str(e)}
        
        # Check cache first (if enabled)
        result = None
        cache_hit = False
        if use_cache:
            result = analysis_cache.get(text)
            if result:
                cache_hit = True
                structured_logger.info("Cache hit", text_length=len(text))
        
        # Run analysis if not cached
        if result is None:
            scoring_engine = get_scoring_engine()
            
            # Track ML inference time
            with MLInferenceTimer() as timer:
                result = scoring_engine.analyze(text, include_explanations=True)
            
            ml_time = timer.elapsed
            structured_logger.info(
                "ML inference completed",
                text_length=len(text),
                ml_time_ms=round(ml_time * 1000, 2),
                verdict=result.get("verdict", "UNKNOWN")
            )
        
        # Calculate truth_score (normalized 0-1)
        truth_score = float(result.get("confidence", 0)) / 100.0
        
        # Get explanation map (SHAP word impact) from result
        explanation_map = result.get("explanation_map", {})
        
        # Get top 3 evidence sources
        evidence_sources = result.get("evidence_sources", [])
        top_evidence_sources = [
            {
                "name": src.get("name", "Unknown"),
                "url": src.get("url", ""),
                "relevance": src.get("relevance", 0),
                "supports": src.get("supports", "NEUTRAL")
            }
            for src in evidence_sources[:3]
        ]
        
        # Ensure all response fields are the correct type
        scores_dict = result.get("scores", {})
        if isinstance(scores_dict, dict):
            scores = {
                "real": float(scores_dict.get("real", 50)),
                "rumor": float(scores_dict.get("rumor", 25)),
                "fake": float(scores_dict.get("fake", 25))
            }
        else:
            scores = {"real": 50, "rumor": 25, "fake": 25}

        score_total = max(scores["real"] + scores["rumor"] + scores["fake"], 1.0)
        scores = {
            "real": round(scores["real"] / score_total * 100, 2),
            "rumor": round(scores["rumor"] / score_total * 100, 2),
            "fake": round(scores["fake"] / score_total * 100, 2),
        }
        
        # Build clean response matching AnalyzeResponse model
        clean_response = {
            "verdict": str(result.get("verdict", "UNKNOWN")),
            "confidence": float(result.get("confidence", 0)),
            "truth_score": truth_score,  # NEW field
            "explanation_map": explanation_map,  # NEW field
            "top_evidence_sources": top_evidence_sources,  # NEW field
            "scores": scores,
            "confidence_label": str(result.get("confidence_label", "LOW")),
            "reasoning": str(result.get("reasoning", "")),
            "highlighted_text": list(result.get("highlighted_text", [])),
            "propagation_risk": str(result.get("propagation_risk", "UNKNOWN")),
            "propagation_score": float(result.get("propagation_score", 0)),
            "evidence_score": float(result.get("evidence_score", 50)),
            "summary": str(result.get("summary", "")),
            "claims": list(result.get("claims", [])),
            "evidence_sources": list(result.get("evidence_sources", [])),
            "sources": list(result.get("sources", [])),
            "key_signals": list(result.get("key_signals", [])),
            "model_breakdown": {
                k: float(v) if isinstance(v, (int, float, str)) else v
                for k, v in result.get("model_breakdown", {}).items()
            },
            "image_analysis": image_analysis,  # NEW field
        }
        
        # Cache result for future requests
        analysis_cache.set(text, clean_response)
        
        # Persist history record for dashboard regardless of session mode
        try:
            history = ClaimHistory(
                text=text,
                verdict=clean_response["verdict"],
                confidence=clean_response["confidence"],
                confidence_label=clean_response["confidence_label"],
                scores=clean_response["scores"],
                reasoning=clean_response["reasoning"],
                key_signals=clean_response["key_signals"],
                highlighted_text=clean_response["highlighted_text"],
                sources=clean_response["sources"],
            )
            db.add(history)
            db.commit()
        except Exception as history_error:
            db.rollback()
            logger.warning(f"History save failed: {history_error}")

        # Keep legacy session-query behavior for backward compatibility
        if session_id:
            try:
                query = Query(
                    session_id=session_id,
                    input_text=text,
                    verdict=clean_response["verdict"],
                    confidence=clean_response["confidence"],
                    score_real=scores["real"],
                    score_rumor=scores["rumor"],
                    score_fake=scores["fake"],
                    propagation_risk=clean_response["propagation_risk"],
                    propagation_score=clean_response["propagation_score"],
                    evidence_score=clean_response["evidence_score"],
                    summary=clean_response["summary"],
                    key_signals=clean_response["key_signals"],
                    claims=clean_response["claims"],
                    evidence_sources=clean_response["evidence_sources"],
                    model_breakdown=clean_response["model_breakdown"],
                )
                db.add(query)
                db.commit()
            except Exception as query_error:
                db.rollback()
                logger.warning(f"Session query save failed: {query_error}")
        
        return AnalyzeResponse(**clean_response)
    
    except HTTPException:
        raise
    except Exception as e:
        response_time = time.time() - request_start_time
        structured_logger.error(
            "Analysis failed",
            error=str(e),
            text_length=len(request.text),
            response_time_ms=round(response_time * 1000, 2),
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/history")
async def get_history(limit: int = 50, db: Session = Depends(get_db)):
    """Return latest analyzed claims for dashboard history."""
    try:
        rows = (
            db.query(ClaimHistory)
            .order_by(ClaimHistory.timestamp.desc())
            .limit(min(max(limit, 1), 200))
            .all()
        )

        history = [
            {
                "id": row.id,
                "text": row.text,
                "verdict": row.verdict,
                "confidence": row.confidence,
                "confidence_label": row.confidence_label,
                "timestamp": row.timestamp.isoformat() if isinstance(row.timestamp, datetime) else str(row.timestamp),
            }
            for row in rows
        ]

        return {"history": history, "count": len(history)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")


@router.post("/analyze/batch")
async def analyze_batch(texts: list[str], db: Session = Depends(get_db)):
    """
    Analyze multiple claims in batch.
    """
    results = []
    for text in texts:
        try:
            result = scoring_engine.analyze(text)
            results.append(result)
        except Exception as e:
            results.append({"error": str(e), "text": text})
    
    return {"results": results, "count": len(results)}
