"""
Analyze V2 API Endpoint - NEW PRODUCTION RAG PIPELINE
Uses Wikipedia+query expansion, semantic ranking, and hybrid confidence scoring.
"""

import logging
import time
import asyncio
from typing import Optional, Dict, List
from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from pydantic import BaseModel
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
    """Initialize RAG pipeline on first request."""
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
        logger.error(f"[V2-INIT] ❌ CRITICAL: Pipeline initialization failed", exc_info=True)
        raise RAGPipelineError(f"Failed to initialize RAG pipeline: {str(e)}")


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AnalyzeV2Request(BaseModel):
    """Request model for new pipeline."""
    claim: str
    session_id: Optional[str] = None


class EvidenceItem(BaseModel):
    """Individual evidence piece."""
    sentence: str
    source: str
    url: str
    similarity_score: float
    nli_entailment: float = 0.0
    nli_contradiction: float = 0.0
    nli_neutral: float = 0.0


class AnalyzeV2Metadata(BaseModel):
    """Metadata about analysis."""
    queries_used: List[str]
    total_articles_fetched: int
    total_sentences_extracted: int
    total_unique_sentences: int
    final_evidence_count: int
    processing_time_ms: float
    nli_enabled: bool
    timestamp: str


class AnalyzeV2Response(BaseModel):
    """Response model for new pipeline."""
    success: bool
    claim: str
    answer: str
    verdict: str  # 'TRUE', 'FALSE', 'UNCERTAIN'
    confidence: float  # 0.0 - 1.0
    evidence: List[EvidenceItem]
    metadata: AnalyzeV2Metadata


def _error_response_v2(claim: str, error_msg: str) -> AnalyzeV2Response:
    """Create error response."""
    return AnalyzeV2Response(
        success=False,
        claim=claim,
        answer=f"ERROR: {error_msg}",
        verdict="ERROR",
        confidence=0.0,
        evidence=[],
        metadata=AnalyzeV2Metadata(
            queries_used=[],
            total_articles_fetched=0,
            total_sentences_extracted=0,
            total_unique_sentences=0,
            final_evidence_count=0,
            processing_time_ms=0.0,
            nli_enabled=False,
            timestamp=datetime.now().isoformat()
        )
    )


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/analyze/v2", response_model=AnalyzeV2Response)
async def analyze_v2_endpoint(
    claim: str = Form(...),
    session_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
) -> AnalyzeV2Response:
    """
    New fact-checking endpoint using production RAG pipeline.
    
    Features:
    ✅ Query expansion (3-5 search variants)
    ✅ Wikipedia API retrieval (reliable, curated sources)
    ✅ Sentence-level evidence extraction
    ✅ Semantic ranking (embedding-based)
    ✅ NLI inference (optional, BART-large-MNLI)
    ✅ Hybrid confidence (60% similarity + 40% NLI)
    ✅ Deterministic outputs
    
    FormData Parameters:
        - claim: claim text to fact-check (required)
        - session_id: optional session identifier
        - image: optional image file (reserved for future)
    
    Returns: AnalyzeV2Response with structured evidence and metadata
    
    Example:
        POST /analyze/v2
        claim=Is the Earth flat?
        session_id=user123
    
    Response:
        {
            "success": true,
            "claim": "Is the Earth flat?",
            "answer": "FALSE: The Earth is an oblate spheroid...",
            "verdict": "FALSE",
            "confidence": 0.92,
            "evidence": [
                {
                    "sentence": "The Earth is approximately an oblate spheroid.",
                    "source": "Wikipedia",
                    "url": "https://en.wikipedia.org/wiki/Earth",
                    "similarity_score": 0.89,
                    "nli_entailment": 0.95,
                    ...
                }
            ],
            "metadata": {...}
        }
    """
    logger.info("=" * 80)
    logger.info(f"[V2] 🎯 NEW ANALYSIS REQUEST (v2 pipeline)")
    logger.info(f"[V2] Claim: {claim[:100]}")
    if session_id:
        logger.info(f"[V2] Session: {session_id}")
    logger.info("=" * 80)
    
    request_start = time.time()
    
    try:
        # Validate input
        if not claim or not claim.strip():
            logger.warning("[V2] ❌ Empty claim provided")
            return _error_response_v2("", "No claim text provided")
        
        claim = claim.strip()
        
        # Initialize pipeline
        logger.debug("[V2] Initializing pipeline...")
        pipeline = _initialize_pipeline()
        
        if not pipeline:
            logger.error("[V2] ❌ Pipeline not initialized")
            return _error_response_v2(claim, "Pipeline initialization failed")
        
        # Execute analysis
        logger.info("[V2] ✅ EXECUTING NEW RAG PIPELINE")
        
        # BUG FIX 7: Wrap with asyncio timeout of 60 seconds
        try:
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, pipeline.analyze,
                    claim, Config.NEW_RAG_TOP_K_EVIDENCE,
                    Config.NEW_RAG_QUERY_EXPANSION),
                timeout=60.0
            )
        except asyncio.TimeoutError:
            logger.error("[V2] ❌ Pipeline analysis timeout (60s)")
            return _error_response_v2(claim, "Analysis timeout - took longer than 60 seconds")
        except Exception as analyze_err:
            logger.error(f"[V2] ❌ Pipeline analysis error: {analyze_err}")
            result = pipeline.analyze(
                claim=claim,
                top_k_evidence=Config.NEW_RAG_TOP_K_EVIDENCE,
                query_expansion_enabled=Config.NEW_RAG_QUERY_EXPANSION
            )
        
        # Convert result to response model
        evidence_items = [EvidenceItem(**item) for item in result.get("evidence", [])]
        
        metadata_dict = result.get("metadata", {})
        metadata = AnalyzeV2Metadata(
            queries_used=metadata_dict.get("queries_used", []),
            total_articles_fetched=metadata_dict.get("total_articles_fetched", 0),
            total_sentences_extracted=metadata_dict.get("total_sentences_extracted", 0),
            total_unique_sentences=metadata_dict.get("total_unique_sentences", 0),
            final_evidence_count=metadata_dict.get("final_evidence_count", 0),
            processing_time_ms=metadata_dict.get("processing_time_ms", 0.0),
            nli_enabled=metadata_dict.get("nli_enabled", False),
            timestamp=metadata_dict.get("timestamp", datetime.now().isoformat())
        )
        
        response = AnalyzeV2Response(
            success=result.get("success", True),
            claim=claim,
            answer=result.get("answer", ""),
            verdict=result.get("verdict", "UNCERTAIN"),
            confidence=result.get("confidence", 0.0),
            evidence=evidence_items,
            metadata=metadata
        )
        
        total_duration = time.time() - request_start
        
        logger.info("[V2] ✅ Analysis complete")
        logger.info(f"[V2] Verdict: {response.verdict} (confidence: {response.confidence:.2%})")
        logger.info(f"[V2] Evidence: {len(response.evidence)} pieces")
        logger.info(f"[V2] Total time: {total_duration:.2f}s")
        logger.info("=" * 80)
        
        return response
        
    except RAGPipelineError as e:
        logger.error(f"[V2] ❌ Pipeline error: {str(e)}", exc_info=True)
        return _error_response_v2(claim, f"Analysis failed: {str(e)[:100]}")
        
    except Exception as e:
        logger.error(f"[V2] ❌ Unexpected error: {str(e)}", exc_info=True)
        return _error_response_v2(claim, f"Unexpected error: {str(e)[:100]}")


@router.post("/analyze/v2/streamlined", response_model=AnalyzeV2Response)
async def analyze_v2_streamlined(
    claim: str = Form(...),
    session_id: Optional[str] = Form(None)
) -> AnalyzeV2Response:
    """
    Fast, deterministic endpoint without NLI (streamlined version).
    
    Uses only semantic similarity for confidence scoring.
    Fastest option, good for high-volume deployments.
    """
    logger.info("[V2-LITE] Starting streamlined analysis...")
    
    try:
        if not claim or not claim.strip():
            return _error_response_v2("", "No claim text provided")
        
        claim = claim.strip()
        
        # Use streamlined pipeline (no NLI)
        pipeline = StreamlineRAGPipeline(
            embedder_model=Config.NEW_RAG_EMBEDDER_MODEL,
            device=Config.NEW_RAG_DEVICE
        )
        
        result = pipeline.analyze(
            claim=claim,
            top_k_evidence=Config.NEW_RAG_TOP_K_EVIDENCE
        )
        
        evidence_items = [EvidenceItem(**item) for item in result.get("evidence", [])]
        
        metadata_dict = result.get("metadata", {})
        metadata = AnalyzeV2Metadata(
            queries_used=metadata_dict.get("queries_used", []),
            total_articles_fetched=metadata_dict.get("total_articles_fetched", 0),
            total_sentences_extracted=metadata_dict.get("total_sentences_extracted", 0),
            total_unique_sentences=metadata_dict.get("total_unique_sentences", 0),
            final_evidence_count=metadata_dict.get("final_evidence_count", 0),
            processing_time_ms=metadata_dict.get("processing_time_ms", 0.0),
            nli_enabled=False,
            timestamp=datetime.now().isoformat()
        )
        
        return AnalyzeV2Response(
            success=True,
            claim=claim,
            answer=result.get("answer", ""),
            verdict=result.get("verdict", "UNCERTAIN"),
            confidence=result.get("confidence", 0.0),
            evidence=evidence_items,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"[V2-LITE] Error: {str(e)}", exc_info=True)
        return _error_response_v2(claim, str(e)[:100])


@router.get("/analyze/v2/health")
async def health_check_v2() -> Dict:
    """
    Health check endpoint for v2 pipeline.
    
    Returns status and configuration info.
    """
    try:
        pipeline = _initialize_pipeline()
        status = "healthy" if pipeline else "degraded"
    except Exception as e:
        status = "unhealthy"
        logger.error(f"[V2-HEALTH] Error: {str(e)}")
    
    return {
        "status": status,
        "version": "v2",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "use_nli": Config.NEW_RAG_USE_NLI,
            "embedder": Config.NEW_RAG_EMBEDDER_MODEL,
            "device": Config.NEW_RAG_DEVICE,
            "top_k": Config.NEW_RAG_TOP_K_EVIDENCE,
            "query_expansion": Config.NEW_RAG_QUERY_EXPANSION
        }
    }


@router.post("/analyze/v2/batch")
async def batch_analyze_v2(
    claims: List[str],
    session_id: Optional[str] = None
) -> Dict:
    """
    Batch analysis endpoint for multiple claims.
    
    Parameters:
        - claims: List of claim strings
        - session_id: Optional session ID
    
    Returns:
        List of AnalyzeV2Response objects
    """
    logger.info(f"[V2-BATCH] Analyzing {len(claims)} claims...")
    
    try:
        pipeline = _initialize_pipeline()
        results = []
        
        for i, claim in enumerate(claims):
            logger.debug(f"[V2-BATCH] Processing {i+1}/{len(claims)}: {claim[:50]}...")
            
            try:
                result = pipeline.analyze(
                    claim=claim,
                    top_k_evidence=Config.NEW_RAG_TOP_K_EVIDENCE
                )
                
                evidence_items = [EvidenceItem(**item) for item in result.get("evidence", [])]
                metadata_dict = result.get("metadata", {})
                
                response = AnalyzeV2Response(
                    success=True,
                    claim=claim,
                    answer=result.get("answer", ""),
                    verdict=result.get("verdict", "UNCERTAIN"),
                    confidence=result.get("confidence", 0.0),
                    evidence=evidence_items,
                    metadata=AnalyzeV2Metadata(
                        queries_used=metadata_dict.get("queries_used", []),
                        total_articles_fetched=metadata_dict.get("total_articles_fetched", 0),
                        total_sentences_extracted=metadata_dict.get("total_sentences_extracted", 0),
                        total_unique_sentences=metadata_dict.get("total_unique_sentences", 0),
                        final_evidence_count=metadata_dict.get("final_evidence_count", 0),
                        processing_time_ms=metadata_dict.get("processing_time_ms", 0.0),
                        nli_enabled=Config.NEW_RAG_USE_NLI,
                        timestamp=datetime.now().isoformat()
                    )
                )
                results.append(response)
                
            except Exception as e:
                logger.warning(f"[V2-BATCH] Error analyzing claim {i}: {str(e)}")
                results.append(_error_response_v2(claim, str(e)[:100]))
        
        logger.info(f"[V2-BATCH] Completed batch analysis: {len(results)} results")
        
        return {
            "count": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[V2-BATCH] Batch error: {str(e)}", exc_info=True)
        return {
            "error": str(e),
            "count": 0,
            "results": []
        }
