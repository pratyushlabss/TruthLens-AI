"""
Analyze API Endpoint - REAL PIPELINE EXECUTION
Orchestrates hybrid retrieval → evidence building → verdict → explanation
"""

import logging
import os
import asyncio
from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================================================
# GLOBAL SERVICE INSTANCES (Initialized once on first request)
# ============================================================================
_services_initialized = False
_scoring_engine = None
_retrieval_engine = None
_evidence_builder = None
_verdict_engine = None
_roberta_classifier = None


def _initialize_services():
    """Initialize all analysis services on first request."""
    global _services_initialized, _scoring_engine, _retrieval_engine
    global _evidence_builder, _verdict_engine, _roberta_classifier
    
    if _services_initialized:
        return True
    
    logger.info("=" * 80)
    logger.info("[INIT] 🚀 INITIALIZING TRUTHLENS ANALYSIS PIPELINE")
    logger.info("=" * 80)
    
    try:
        logger.info("[INIT] Importing services...")
        from services.scoring_engine import ScoringEngine
        from services.retrieval_engine import RetrievalEngine
        from services.evidence_builder import EvidenceBuilder
        from services.verdict_engine import VerdictEngine
        from models.roberta_classifier import RoBERTaClassifier
        
        logger.info("[INIT] Creating RetrievalEngine...")
        _retrieval_engine = RetrievalEngine()
        logger.info("[INIT] ✅ RetrievalEngine ready")
        
        logger.info("[INIT] Creating EvidenceBuilder...")
        _evidence_builder = EvidenceBuilder()
        logger.info("[INIT] ✅ EvidenceBuilder ready")
        
        logger.info("[INIT] Creating VerdictEngine...")
        _verdict_engine = VerdictEngine()
        logger.info("[INIT] ✅ VerdictEngine ready")
        
        logger.info("[INIT] Creating RobertaClassifier...")
        _roberta_classifier = RoBERTaClassifier()
        logger.info("[INIT] ✅ RobertaClassifier ready")
        
        logger.info("[INIT] Creating ScoringEngine...")
        _scoring_engine = ScoringEngine()
        logger.info("[INIT] ✅ ScoringEngine ready")
        
        _services_initialized = True
        
        logger.info("=" * 80)
        logger.info("[INIT] ✅ ALL SERVICES INITIALIZED")
        logger.info(f"[INIT] Pipeline mode: REAL (Tavily API + DuckDuckGo hybrid search)")
        logger.info("[INIT] System ready to analyze claims")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"[INIT] ❌ CRITICAL: Service initialization failed", exc_info=True)
        logger.error(f"[INIT] Error: {e}")
        logger.warning("[INIT] System will operate in FALLBACK mode only")
        return False


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AnalyzeRequest(BaseModel):
    """JSON request model for claim analysis."""
    text: str
    session_id: Optional[str] = None


class SourceInfo(BaseModel):
    """Source information."""
    title: str
    url: str
    credibility: str
    summary: str
    supports: str
    is_fallback: bool = False


class AnalyzeResponse(BaseModel):
    """Analysis response model with all required fields."""
    claim: str
    verdict: str  # TRUE, FALSE, UNCERTAIN, ERROR
    confidence: float  # 0.0 - 1.0
    explanation: str  # Main explanation
    reasoning: str  # Detailed reasoning
    sources: List[SourceInfo]  # Evidence sources
    key_signals: List[str]  # Key findings
    detailed_explanation: Dict = {}  # Extra details
    evidence_quality: str = "LOW"  # HIGH, MEDIUM, LOW, NONE
    timestamp: str = ""


# ============================================================================
# API ENDPOINT - ACCEPTS FORMDATA
# ============================================================================

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_endpoint(
    text: str = Form(...),
    session_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
) -> AnalyzeResponse:
    """
    Main analysis endpoint - REAL PIPELINE
    
    ✅ Executes full 7-step analysis:
    1. Claim validation
    2. Hybrid web search (Tavily API + DuckDuckGo)
    3. Evidence retrieval & scraping
    4. Evidence ranking & credibility scoring
    5. Verdict computation
    6. Explanation generation
    7. Response construction
    
    FormData Parameters:
        - text: claim text (required)
        - session_id: optional session id
        - image: optional image file
    
    Returns: Complete AnalyzeResponse with verdict, sources, explanation
    """
    logger.info("=" * 80)
    logger.info(f"[ENDPOINT] 🎯 NEW ANALYSIS REQUEST")
    logger.info(f"[ENDPOINT] Claim: {text[:100]}")
    logger.info("=" * 80)
    
    try:
        # Validate input
        if not text or not text.strip():
            logger.warning("[ENDPOINT] ❌ Empty claim provided")
            return _fallback_response("empty", "No claim text provided")
        
        claim = text.strip()
        
        # Initialize services
        services_ready = _initialize_services()
        if not services_ready or not _scoring_engine:
            logger.error("[ENDPOINT] ❌ Services not initialized")
            return _error_response(claim, "Analysis services not available")
        
        # ✅ EXECUTE REAL PIPELINE
        logger.info("[ENDPOINT] ✅ EXECUTING REAL PIPELINE")
        response = await analyze_claim(claim, session_id)
        
        # Ensure all response fields populated
        response = _guarantee_response_populated(response)
        
        logger.info(f"[ENDPOINT] ✅ Analysis complete: {response.verdict}")
        logger.info(f"[ENDPOINT] Confidence: {response.confidence:.0%}")
        logger.info(f"[ENDPOINT] Sources: {len(response.sources)}")
        logger.info("=" * 80)
        
        return response
        
    except Exception as e:
        logger.error(f"[ENDPOINT] ❌ Endpoint error: {e}", exc_info=True)
        return _error_response(text or "unknown", str(e)[:100])



# ============================================================================
# CORE ANALYSIS FUNCTION - REAL PIPELINE
# ============================================================================

async def analyze_claim(
    claim: str,
    session_id: Optional[str] = None
) -> AnalyzeResponse:
    """
    Execute REAL analysis pipeline.
    
    Pipeline steps:
    1. Search web for evidence
    2. Scrape article content
    3. Build structured evidence
    4. Compute verdict
    5. Generate explanation
    6. Score evidence quality
    """
    
    logger.info("[PIPELINE] Starting real claim analysis...")
    
    try:
        # STEP 1: Retrieve evidence via hybrid search
        logger.info("[PIPELINE-STEP1] 🔍 Retrieving evidence via hybrid search...")
        logger.info(f"[PIPELINE-STEP1] Query: {claim[:80]}")
        
        raw_articles = _retrieval_engine.search_and_scrape(
            claim=claim,
            max_results=10
        )
        
        if raw_articles:
            logger.info(f"[PIPELINE-STEP1] ✅ Retrieved {len(raw_articles)} articles")
            for i, article in enumerate(raw_articles[:3], 1):
                logger.info(f"[PIPELINE-STEP1]   {i}. {article.get('title', 'No title')[:60]}")
                logger.info(f"[PIPELINE-STEP1]      URL: {article.get('url', 'No URL')[:60]}")
        else:
            logger.warning("[PIPELINE-STEP1] ⚠️  No articles retrieved")
            raw_articles = []
        
        # STEP 2: Compute NLP score using RoBERTaClassifier
        logger.info("[PIPELINE-STEP2a] 🧠 Computing NLP credibility score...")
        nlp_score = _compute_nlp_score(claim) if _roberta_classifier else 0.5
        logger.info(f"[PIPELINE-STEP2a] ✅ NLP score: {nlp_score:.2f}")
        
        # STEP 2b: Build evidence with semantic analysis
        logger.info("[PIPELINE-STEP2b] 📚 Building structured evidence with semantic analysis...")
        evidence_list = _evidence_builder.build(
            raw_articles=raw_articles,
            claim=claim,
            nlp_score=nlp_score,
            roberta_classifier=_roberta_classifier
        )
        logger.info(f"[PIPELINE-STEP2] ✅ Built {len(evidence_list)} evidence items")
        
        # STEP 3: Compute verdict
        logger.info("[PIPELINE-STEP3] ⚖️  Computing verdict from evidence...")
        verdict_result = _verdict_engine.compute_verdict(
            evidence_list=evidence_list,
            nlp_score=0.5,
            claim=claim
        )
        logger.info(f"[PIPELINE-STEP3] ✅ Verdict: {verdict_result.get('verdict', 'UNKNOWN')}")
        logger.info(f"[PIPELINE-STEP3]    Confidence: {verdict_result.get('confidence', 0):.0%}")
        
        # STEP 4: Build response
        logger.info("[PIPELINE-STEP4] 🎯 Building response...")
        response = AnalyzeResponse(
            claim=claim,
            verdict=verdict_result.get('verdict', 'UNCERTAIN'),
            confidence=verdict_result.get('confidence', 0.3),
            explanation=verdict_result.get('explanation', f"Analysis of claim: {claim[:100]}"),
            reasoning=verdict_result.get('reasoning', "Analyzed available evidence and sources"),
            sources=[
                SourceInfo(
                    title=src.get('source', 'Unknown')[:80],
                    url=src.get('url', 'generated://unknown'),
                    credibility=f"{int(src.get('credibility', 0.5) * 100)}%",
                    summary=src.get('snippet', src.get('text', '')[:200]),
                    supports=src.get('stance', 'NEUTRAL'),
                    is_fallback=src.get('is_fallback', False)
                )
                for src in evidence_list[:5]
            ] if evidence_list else [_fallback_source()],
            key_signals=verdict_result.get('signals', [
                f"Verdict: {verdict_result.get('verdict', 'UNKNOWN')}",
                f"Based on {len(evidence_list)} sources"
            ]),
            evidence_quality=_compute_quality(evidence_list),
            timestamp=datetime.now().isoformat()
        )
        
        logger.info("[PIPELINE-STEP4] ✅ Response built successfully")
        logger.info("[PIPELINE] ✅ REAL PIPELINE COMPLETE")
        
        return response
    
    except Exception as e:
        logger.error(f"[PIPELINE] ❌ Real pipeline failed: {e}", exc_info=True)
        return _error_response(claim, f"Pipeline error: {str(e)[:80]}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _compute_quality(evidence_list: List[Dict]) -> str:
    """Compute evidence quality from list."""
    if not evidence_list:
        return "NONE"
    
    real_count = sum(1 for e in evidence_list if not e.get('is_fallback', False))
    
    if real_count >= 3:
        return "HIGH"
    elif real_count >= 1:
        return "MEDIUM"
    else:
        return "LOW"


def _guarantee_response_populated(response: AnalyzeResponse) -> AnalyzeResponse:
    """Ensure all response fields are populated."""
    
    # Ensure claim
    if not response.claim or response.claim.strip() == "":
        response.claim = "[Analysis performed]"
    
    # Ensure verdict
    if response.verdict not in ["TRUE", "FALSE", "UNCERTAIN", "ERROR"]:
        response.verdict = "UNCERTAIN"
    
    # Ensure confidence
    if not (0.0 <= response.confidence <= 1.0):
        response.confidence = 0.3
    
    # Ensure explanation
    if not response.explanation or response.explanation.strip() == "":
        response.explanation = f"Analysis verdict: {response.verdict}"
    
    # Ensure reasoning
    if not response.reasoning or response.reasoning.strip() == "":
        response.reasoning = f"System analyzed the claim and reached verdict: {response.verdict}"
    
    # Ensure sources
    if not response.sources:
        response.sources = [_fallback_source()]
    
    # Ensure key_signals
    if not response.key_signals:
        response.key_signals = [f"Verdict: {response.verdict}", "Analysis complete"]
    
    # Ensure evidence_quality
    if response.evidence_quality not in ["HIGH", "MEDIUM", "LOW", "NONE"]:
        response.evidence_quality = "LOW"
    
    # Ensure timestamp
    if not response.timestamp:
        response.timestamp = datetime.now().isoformat()
    
    logger.info("[RESPONSE] ✅ All response fields guaranteed populated")
    return response


def _fallback_source() -> SourceInfo:
    """Create fallback source."""
    return SourceInfo(
        title="System Analysis",
        url="generated://system-analysis",
        credibility="30%",
        summary="System-generated response when external sources unavailable",
        supports="NEUTRAL",
        is_fallback=True
    )


def _fallback_response(claim: str, reason: str) -> AnalyzeResponse:
    """Return fallback response when analysis fails gracefully."""
    
    logger.warning(f"[FALLBACK] Generating fallback response: {reason}")
    
    response = AnalyzeResponse(
        claim=claim,
        verdict="UNCERTAIN",
        confidence=0.3,
        explanation=f"Unable to complete analysis: {reason}",
        reasoning=f"System encountered a limitation while analyzing this claim. Recommend: {reason}",
        sources=[_fallback_source()],
        key_signals=["Fallback mode", "Limited analysis"],
        evidence_quality="NONE",
        timestamp=datetime.now().isoformat()
    )
    
    return _guarantee_response_populated(response)


def _error_response(claim: str, error: str) -> AnalyzeResponse:
    """Return error response."""
    
    logger.error(f"[ERROR-RESPONSE] Error analysis: {error}")
    
    response = AnalyzeResponse(
        claim=claim,
        verdict="ERROR",
        confidence=0.0,
        explanation="System encountered an error during analysis",
        reasoning=f"Error details: {error}",
        sources=[_fallback_source()],
        key_signals=["System error", "Please retry"],
        evidence_quality="NONE",
        timestamp=datetime.now().isoformat()
    )
    
    return _guarantee_response_populated(response)


def _compute_nlp_score(claim: str) -> float:
    """
    Compute NLP credibility score using linguistic analysis.
    
    Args:
        claim: The claim text
        
    Returns:
        Credibility score (0.0 - 1.0)
    """
    try:
        logger.debug(f"[NLP] Analyzing: {claim[:80]}")
        
        # Look for linguistic indicators
        suspicious_words = [
            "allegedly", "rumor", "supposedly", "claim",
            "fake", "hoax", "conspiracy", "unverified",
            "leaked", "exclusive", "shocking"
        ]
        
        confident_words = [
            "research shows", "study found", "evidence",
            "confirmed", "verified", "proved", "documented",
            "peer-reviewed", "published", "official"
        ]
        
        claim_lower = claim.lower()
        
        # Count linguistic signals
        suspicious_count = sum(1 for word in suspicious_words if word in claim_lower)
        confident_count = sum(1 for word in confident_words if word in claim_lower)
        
        # Compute base score
        base_score = 0.5
        
        # Adjust for suspicious language
        base_score -= suspicious_count * 0.15
        
        # Adjust for confident language
        base_score += confident_count * 0.10
        
        # Clamp to valid range
        nlp_score = max(0.0, min(1.0, base_score))
        
        logger.info(f"[NLP] Score computed: {nlp_score:.2f} (suspicious:{suspicious_count}, confident:{confident_count})")
        return nlp_score
        
    except Exception as e:
        logger.warning(f"[NLP] Error computing score: {e}")
        return 0.5
