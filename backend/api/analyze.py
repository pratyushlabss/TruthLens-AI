"""Analyze endpoint for claims and articles."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from database.postgres import get_db
from database.models import Query
from services.scoring_engine import ScoringEngine

router = APIRouter()

# Initialize scoring engine
scoring_engine = ScoringEngine()


class AnalyzeRequest(BaseModel):
    """Analyze request model."""
    text: str
    session_id: Optional[str] = None


class AnalyzeResponse(BaseModel):
    """Analyze response model."""
    verdict: str
    confidence: float
    scores: dict
    propagation_risk: str
    propagation_score: float
    evidence_score: float
    summary: str
    claims: list
    evidence_sources: list
    key_signals: list
    model_breakdown: dict


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_claim(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    Analyze a claim using fusion of 3 models:
    - 60% RoBERTa NLP Classification
    - 25% Sentence-BERT Evidence Credibility
    - 15% Propagation Risk Analysis
    """
    try:
        # Validate input
        if not request.text or len(request.text.strip()) < 5:
            raise HTTPException(status_code=400, detail="Text must be at least 5 characters")
        
        # Run analysis
        result = scoring_engine.analyze(request.text)
        
        # Save to database if session_id provided
        if request.session_id:
            query = Query(
                session_id=request.session_id,
                input_text=request.text,
                verdict=result["verdict"],
                confidence=result["confidence"],
                score_real=result["scores"]["real"],
                score_rumor=result["scores"]["rumor"],
                score_fake=result["scores"]["fake"],
                propagation_risk=result["propagation_risk"],
                propagation_score=result["propagation_score"],
                evidence_score=result["evidence_score"],
                summary=result["summary"],
                key_signals=result["key_signals"],
                claims=result["claims"],
                evidence_sources=result["evidence_sources"],
                model_breakdown=result["model_breakdown"]
            )
            db.add(query)
            db.commit()
        
        return AnalyzeResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


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
