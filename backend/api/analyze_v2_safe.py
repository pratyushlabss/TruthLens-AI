"""
FIXED: Analyze V2 API Endpoint - PRODUCTION SAFE VERSION
Features safe error handling, fallbacks, and comprehensive logging.
"""

import asyncio
import logging
import time
from typing import Optional, Dict, List
from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from pydantic import BaseModel, validator
from datetime import datetime

from services.pipeline_new import ProductionRAGPipeline, StreamlineRAGPipeline, RAGPipelineError
from config.environment import Config

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================================================
# GLOBAL PIPELINE INSTANCE (Initialized once on first request)
# ============================================================================

_pipeline_initialized = False
_rag_pipeline = None


def _initialize_pipeline():
    """Initialize RAG pipeline on first request - WITH SAFE ERROR HANDLING."""
    global _pipeline_initialized, _rag_pipeline
    
    if _pipeline_initialized and _rag_pipeline is not None:
        return _rag_pipeline
    
    logger.info("=" * 80)
    logger.info("[V2-INIT] 🚀 INITIALIZING NEW RAG PIPELINE")
    logger.info("=" * 80)
    
    try:
        logger.info(f"[V2-INIT] Config: NLI={Config.NEW_RAG_USE_NLI}, "
                   f"Embedder={Config.NEW_RAG_EMBEDDER_MODEL}, "
                   f"Device={Config.NEW_RAG_DEVICE}")
        
        # Initialize pipeline based on config
        _rag_pipeline = ProductionRAGPipeline(
            use_nli=Config.NEW_RAG_USE_NLI,
            embedder_model=Config.NEW_RAG_EMBEDDER_MODEL,
            device=Config.NEW_RAG_DEVICE
        )
        
        _pipeline_initialized = True
        
        logger.info("=" * 80)
        logger.info("[V2-INIT] ✅ NEW RAG PIPELINE INITIALIZED")
        logger.info("[V2-INIT] Pipeline features:")
        logger.info(f"  - Wikipedia API retrieval: ENABLED")
        logger.info(f"  - Query expansion: {Config.NEW_RAG_QUERY_EXPANSION}")
        logger.info(f"  - NLI inference: {Config.NEW_RAG_USE_NLI}")
        logger.info(f"  - Top-K evidence: {Config.NEW_RAG_TOP_K_EVIDENCE}")
        logger.info(f"  - Embedder: {Config.NEW_RAG_EMBEDDER_MODEL}")
        logger.info("=" * 80)
        
        return _rag_pipeline
        
    except Exception as e:
        logger.error(f"[V2-INIT] ❌ CRITICAL: Pipeline initialization failed: {e}", exc_info=True)
        _pipeline_initialized = False
        _rag_pipeline = None
        # Return None - caller must handle gracefully
        return None


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AnalyzeV2Request(BaseModel):
    """Request model for new pipeline."""
    claim: str
    session_id: Optional[str] = None
    
    @validator('claim')
    def validate_claim(cls, v):
        """Validate claim length and content - SAFE."""
        try:
            if not v or not v.strip():
                raise ValueError("Claim cannot be empty")
            if len(v.strip()) < 5:
                raise ValueError("Claim must be at least 5 characters")
            if len(v.strip()) > 1000:
                raise ValueError("Claim must be less than 1000 characters")
            return v.strip()
        except ValueError as e:
            logger.warning(f"[V2] Claim validation failed: {e}")
            raise


class EvidenceItem(BaseModel):
    """Individual evidence piece - SAFE DEFAULTS."""
    sentence: str = ""
    source: str = "Unknown"
    url: str = ""
    similarity_score: float = 0.0
    credibility_score: float = 0.0
    evidence_score: float = 0.0
    evidence_type: str = "unknown"
    nli_entailment: float = 0.0
    nli_contradiction: float = 0.0
    nli_neutral: float = 0.0


class KeySignalItem(BaseModel):
    """Key signal surfaced for UI explanations - SAFE DEFAULTS."""
    text: str = ""
    similarity: float = 0.0
    credibility: float = 0.0
    score: float = 0.0
    source: str = "Unknown"


class AnalysisDetails(BaseModel):
    """Explainability details for UI - SAFE DEFAULTS."""
    why_selected: str = ""
    why_removed: str = ""
    consistency: str = ""
    reasoning: str = ""
    why_confidence: str = ""
    top_influence: str = ""
    rejected_evidence: str = ""


class ConfidenceBreakdown(BaseModel):
    """Confidence contribution breakdown - SAFE DEFAULTS."""
    evidence: float = 0.0
    consistency: float = 0.0
    reasoning: float = 0.0


class AnalyzeV2Metadata(BaseModel):
    """Metadata about analysis - SAFE DEFAULTS."""
    queries_used: List[str] = []
    total_articles_fetched: int = 0
    total_sentences_extracted: int = 0
    total_unique_sentences: int = 0
    final_evidence_count: int = 0
    processing_time_ms: float = 0.1
    nli_enabled: bool = False
    timestamp: str = ""


class AnalyzeV2Response(BaseModel):
    """Response model for new pipeline - SAFE DEFAULTS."""
    success: bool = False
    claim: str = ""
    label: str = "UNCERTAIN"
    confidence_percentage: float = 0.0
    summary: str = ""
    key_signals: List[KeySignalItem] = []
    analysis_details: AnalysisDetails = AnalysisDetails()
    confidence_breakdown: ConfidenceBreakdown = ConfidenceBreakdown()
    evidence: List[EvidenceItem] = []
    metadata: AnalyzeV2Metadata = AnalyzeV2Metadata()
    verdict: Optional[str] = None
    confidence: Optional[float] = None
    answer: Optional[str] = None


def _safe_evidence_item_from_dict(item: Dict) -> EvidenceItem:
    """Safely convert dict to EvidenceItem with defaults."""
    try:
        return EvidenceItem(
            sentence=str(item.get("sentence", "")).strip()[:1000],
            source=str(item.get("source", "Unknown")).strip()[:200],
            url=str(item.get("url", "")).strip()[:2000],
            similarity_score=float(item.get("similarity_score", item.get("similarity", 0.0))),
            credibility_score=float(item.get("credibility_score", 0.0)),
            evidence_score=float(item.get("evidence_score", 0.0)),
            evidence_type=str(item.get("evidence_type", "unknown")).strip()[:50],
            nli_entailment=float(item.get("nli_entailment", 0.0)),
            nli_contradiction=float(item.get("nli_contradiction", 0.0)),
            nli_neutral=float(item.get("nli_neutral", 0.0)),
        )
    except Exception as e:
        logger.warning(f"[V2] Failed to parse evidence item: {e}")
        return EvidenceItem(source="Error: unparseable evidence")


def _error_response_v2(claim: str, error_msg: str, processing_time_ms: float = 0.1) -> AnalyzeV2Response:
    """Create safe error response with minimum required fields."""
    try:
        return AnalyzeV2Response(
            success=False,
            claim=claim[:1000] if claim else "",
            label="UNCERTAIN",
            confidence_percentage=0.0,
            summary=f"Analysis error: {error_msg[:200]}",
            key_signals=[],
            analysis_details=AnalysisDetails(),
            confidence_breakdown=ConfidenceBreakdown(),
            evidence=[],
            metadata=AnalyzeV2Metadata(
                queries_used=[],
                total_articles_fetched=0,
                total_sentences_extracted=0,
                total_unique_sentences=0,
                final_evidence_count=0,
                processing_time_ms=max(0.1, processing_time_ms),
                nli_enabled=False,
                timestamp=datetime.now().isoformat(),
            ),
            verdict="ERROR",
            confidence=0.0,
            answer=f"Error: {error_msg[:200]}",
        )
    except Exception as fallback_e:
        logger.error(f"[V2] CRITICAL: Even error response failed: {fallback_e}")
        # Return minimal valid response
        return AnalyzeV2Response(
            success=False,
            claim=claim[:50] if claim else "",
            label="UNCERTAIN",
            verdict="ERROR",
            confidence=0.0,
            processing_time_ms=0.1
        )


async def _run_analysis_with_timeout(pipeline, claim: str, timeout_seconds: int = 60):
    """Run analysis with timeout protection - SAFE."""
    if not pipeline:
        raise RAGPipelineError("Pipeline not initialized")
    
    try:
        loop = asyncio.get_event_loop()
        # Run the blocking pipeline.analyze() in a thread executor
        result = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: pipeline.analyze(
                    claim=claim,
                    top_k_evidence=Config.NEW_RAG_TOP_K_EVIDENCE,
                    query_expansion_enabled=Config.NEW_RAG_QUERY_EXPANSION
                )
            ),
            timeout=timeout_seconds
        )
        return result
    except asyncio.TimeoutError:
        logger.error(f"[V2] ❌ Analysis timeout after {timeout_seconds}s for claim: {claim[:80]}")
        raise RAGPipelineError(f"Analysis timeout: request exceeded {timeout_seconds}s limit")
    except Exception as e:
        logger.error(f"[V2] ❌ Analysis execution error: {e}", exc_info=True)
        raise RAGPipelineError(f"Analysis execution failed: {str(e)[:100]}")


# ============================================================================
# API ENDPOINTS - COMPREHENSIVE SAFE ERROR HANDLING
# ============================================================================

@router.post("/analyze/v2", response_model=AnalyzeV2Response)
async def analyze_v2_endpoint(
    claim: str = Form(...),
    session_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
) -> AnalyzeV2Response:
    """
    ✅ PRODUCTION-SAFE Analysis endpoint.
    
    ALL ERRORS ARE CAUGHT AND SAFE JSON RETURNED.
    NEVER CRASHES - always returns valid AnalyzeV2Response.
    """
    logger.info("=" * 80)
    logger.info(f"[V2] 🎯 NEW ANALYSIS REQUEST")
    logger.info(f"[V2] Claim: {claim[:100] if claim else '(empty)'}")
    if session_id:
        logger.info(f"[V2] Session: {session_id[:50]}")
    logger.info("=" * 80)
    
    request_start = time.time()
    
    # STEP 1: Input validation - SAFE
    try:
        if not claim or not claim.strip():
            logger.warning("[V2] ❌ Empty claim provided")
            return _error_response_v2("", "No claim text provided", 0.01)
        
        claim = claim.strip()[:1000]
        
        if len(claim) < 5:
            logger.warning("[V2] ❌ Claim too short")
            return _error_response_v2(claim, "Claim must be at least 5 characters")
        
        if len(claim) > 1000:
            logger.warning("[V2] ❌ Claim too long")
            return _error_response_v2(claim, "Claim must be less than 1000 characters")
        
        logger.debug(f"[V2] ✅ Input validation passed")
        
    except Exception as e:
        logger.error(f"[V2] ❌ Input validation error: {e}")
        return _error_response_v2(claim[:50], f"Invalid input: {str(e)[:50]}")
    
    # STEP 2: Initialize pipeline - SAFE
    try:
        logger.debug("[V2] Initializing pipeline...")
        pipeline = _initialize_pipeline()
        
        if not pipeline:
            logger.error("[V2] ❌ Pipeline initialization failed (returned None)")
            return _error_response_v2(claim, "Pipeline initialization failed", time.time() - request_start)
        
        logger.debug("[V2] ✅ Pipeline initialized")
        
    except Exception as e:
        logger.error(f"[V2] ❌ Pipeline initialization error: {e}", exc_info=True)
        return _error_response_v2(claim, f"Pipeline init failed: {str(e)[:50]}", time.time() - request_start)
    
    # STEP 3: Execute analysis - SAFE WITH FALLBACK
    try:
        logger.info("[V2] ✅ EXECUTING RAG PIPELINE (with 60s timeout)")
        result = await _run_analysis_with_timeout(pipeline, claim, timeout_seconds=60)
        
        if not result or not isinstance(result, dict):
            logger.error(f"[V2] ❌ Pipeline returned invalid result: {type(result)}")
            return _error_response_v2(claim, "Pipeline returned invalid result", time.time() - request_start)
        
        logger.debug(f"[V2] ✅ Pipeline analysis complete")
        
    except RAGPipelineError as e:
        logger.error(f"[V2] ❌ RAG Pipeline error: {str(e)}")
        return _error_response_v2(claim, f"Analysis failed: {str(e)[:50]}", time.time() - request_start)
        
    except asyncio.TimeoutError:
        logger.error(f"[V2] ❌ Analysis timeout")
        return _error_response_v2(claim, "Analysis exceeded 60 second timeout", time.time() - request_start)
        
    except Exception as e:
        logger.error(f"[V2] ❌ Analysis execution error: {e}", exc_info=True)
        return _error_response_v2(claim, f"Unexpected error: {str(e)[:50]}", time.time() - request_start)
    
    # STEP 4: Convert result to response - SAFE WITH DEFAULTS
    try:
        logger.debug("[V2] Converting result to response model...")
        
        # Safely extract evidence items
        evidence_list = result.get("evidence", [])
        if not isinstance(evidence_list, list):
            logger.warning("[V2] ⚠️ Evidence list not a list, using empty")
            evidence_list = []
        
        evidence_items = []
        for idx, item in enumerate(evidence_list):
            try:
                evidence_items.append(_safe_evidence_item_from_dict(item))
            except Exception as e:
                logger.warning(f"[V2] ⚠️ Failed to parse evidence item {idx}: {e}")
                continue
        
        # Safely extract key signals
        key_signals_raw = result.get("key_signals", [])
        key_signals = []
        if isinstance(key_signals_raw, list):
            for ks in key_signals_raw:
                try:
                    key_signals.append(KeySignalItem(
                        text=str(ks.get("text", "")).strip()[:500],
                        similarity=float(ks.get("similarity", 0.0)),
                        credibility=float(ks.get("credibility", 0.0)),
                        score=float(ks.get("score", 0.0)),
                        source=str(ks.get("source", "Unknown")).strip()[:100],
                    ))
                except Exception as e:
                    logger.warning(f"[V2] ⚠️ Failed to parse key signal: {e}")
                    continue
        
        # Safely extract metadata
        metadata_dict = result.get("metadata", {})
        if not isinstance(metadata_dict, dict):
            metadata_dict = {}
        
        metadata = AnalyzeV2Metadata(
            queries_used=metadata_dict.get("queries_used", []) if isinstance(metadata_dict.get("queries_used"), list) else [],
            total_articles_fetched=int(metadata_dict.get("total_articles_fetched", 0)),
            total_sentences_extracted=int(metadata_dict.get("total_sentences_extracted", 0)),
            total_unique_sentences=int(metadata_dict.get("total_unique_sentences", 0)),
            final_evidence_count=int(metadata_dict.get("final_evidence_count", 0)),
            processing_time_ms=max(0.1, float(metadata_dict.get("processing_time_ms", 0.1))),
            nli_enabled=bool(metadata_dict.get("nli_enabled", False)),
            timestamp=str(metadata_dict.get("timestamp", datetime.now().isoformat())),
        )
        
        # Safely extract analysis details
        details_dict = result.get("analysis_details", {})
        analysis_details = AnalysisDetails(
            why_selected=str(details_dict.get("why_selected", "")).strip()[:500],
            why_removed=str(details_dict.get("why_removed", "")).strip()[:500],
            consistency=str(details_dict.get("consistency", "")).strip()[:500],
            reasoning=str(details_dict.get("reasoning", "")).strip()[:1000],
            why_confidence=str(details_dict.get("why_confidence", "")).strip()[:500],
            top_influence=str(details_dict.get("top_influence", "")).strip()[:500],
            rejected_evidence=str(details_dict.get("rejected_evidence", "")).strip()[:500],
        )
        
        # Safely extract confidence breakdown
        cb_dict = result.get("confidence_breakdown", {})
        confidence_breakdown = ConfidenceBreakdown(
            evidence=float(cb_dict.get("evidence", 0.0)),
            consistency=float(cb_dict.get("consistency", 0.0)),
            reasoning=float(cb_dict.get("reasoning", 0.0)),
        )
        
        # Create response
        response = AnalyzeV2Response(
            success=result.get("success", True),
            claim=claim,
            label=str(result.get("label", "UNCERTAIN")).strip().upper()[:20],
            confidence_percentage=float(result.get("confidence_percentage", 0.0)),
            summary=str(result.get("summary", "")).strip()[:1000],
            key_signals=key_signals,
            analysis_details=analysis_details,
            confidence_breakdown=confidence_breakdown,
            evidence=evidence_items,
            metadata=metadata,
            verdict=str(result.get("verdict", "UNCERTAIN")).strip()[:20],
            confidence=float(result.get("confidence", 0.0)),
            answer=str(result.get("answer", "")).strip()[:1000],
        )
        
        total_duration = time.time() - request_start
        
        logger.info("[V2] ✅ Analysis complete")
        logger.info(f"[V2] Label: {response.label} (confidence: {response.confidence_percentage:.1f}%)")
        logger.info(f"[V2] Evidence: {len(response.evidence)} pieces")
        logger.info(f"[V2] Total time: {total_duration:.2f}s")
        logger.info("=" * 80)
        
        return response
        
    except Exception as e:
        logger.error(f"[V2] ❌ Response conversion error: {e}", exc_info=True)
        return _error_response_v2(claim, f"Response conversion failed: {str(e)[:50]}", time.time() - request_start)


@router.post("/health/analyze", response_model=Dict)
async def health_check() -> Dict:
    """Health check endpoint - SAFE."""
    try:
        pipeline = _initialize_pipeline()
        return {
            "status": "healthy" if pipeline else "degraded",
            "pipeline": "ready" if pipeline else "not_initialized",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"[HEALTH] Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)[:100],
            "timestamp": datetime.now().isoformat(),
        }
