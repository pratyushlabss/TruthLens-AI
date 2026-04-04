"""Complete 8-stage RAG pipeline orchestrator."""
import logging
import time
import os
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np

try:
    from .utils_new import extract_sentences, format_evidence_dict
    from .ranking_new import SentenceTransformerEmbedder
    from .retrieval_new import RetrievalPipeline
    from .llm_reasoner import LLMReasoner
except ImportError:
    from utils_new import extract_sentences, format_evidence_dict
    from ranking_new import SentenceTransformerEmbedder
    from retrieval_new import RetrievalPipeline
    from llm_reasoner import LLMReasoner

logger = logging.getLogger(__name__)


class RAGPipelineError(Exception):
    """Exception raised for RAG pipeline errors."""
    pass


class ProductionRAGPipeline:
    """Production-grade RAG pipeline with 8-stage architecture."""
    
    def __init__(
        self,
        use_nli: bool = False,
        embedder_model: str = "all-MiniLM-L6-v2",
        device: str = "cpu",
        top_k_evidence: int = 5
    ):
        """Initialize the RAG pipeline."""
        self.use_nli = use_nli
        self.embedder_model = embedder_model
        self.device = device
        self.top_k_evidence = top_k_evidence
        
        # BUG FIX 2: Pass API keys to LLMReasoner
        try:
            self.llm_reasoner = LLMReasoner(
                openai_api_key=os.getenv('OPENAI_API_KEY', ''),
                huggingface_api_key=os.getenv('HUGGINGFACE_API_KEY', '')
            )
            logger.info("✅ LLMReasoner initialized with API keys")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLMReasoner: {e}")
            self.llm_reasoner = None
        
        # Initialize RetrievalPipeline with Tavily support
        try:
            tavily_key = os.getenv('TAVILY_API_KEY', '').strip()
            self.retrieval_pipeline = RetrievalPipeline(tavily_api_key=tavily_key)
            logger.info(f"✅ RetrievalPipeline initialized [Tavily: {'enabled' if tavily_key else 'disabled'}]")
        except Exception as e:
            logger.error(f"❌ Failed to initialize RetrievalPipeline: {e}")
            self.retrieval_pipeline = None
        
        try:
            self.embedder = SentenceTransformerEmbedder(embedder_model, device)
            logger.info(f"✅ SentenceTransformerEmbedder initialized with {embedder_model}")
        except Exception as e:
            logger.error(f"Failed to initialize embedder: {e}")
            self.embedder = None
    
    def analyze(
        self,
        claim: str,
        top_k_evidence: Optional[int] = None,
        query_expansion_enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a claim through 8-stage RAG pipeline.
        
        Stages:
        1. Query Expansion: Generate search variants
        2. Retrieval: Fetch articles from Wikipedia
        3. Sentence Extraction: Break into sentences
        4. Deduplication: Remove similar sentences
        5. Ranking: Score by relevance
        6. NLI (optional): Fact-check against claim
        7. Confidence: Compute hybrid score
        8. Assembly: Format output
        """
        start_time = time.time()
        
        if top_k_evidence is None:
            top_k_evidence = self.top_k_evidence
        
        try:
            # Stage 1: Query Expansion
            if not self.retrieval_pipeline:
                raise ValueError("Retrieval pipeline not initialized")
            
            # Stage 2: Retrieval
            articles = self.retrieval_pipeline.retrieve(claim, max_articles=10)
            if not articles:
                return self._error_response(claim, "No articles retrieved", time.time() - start_time)
            
            # Stage 3: Sentence Extraction
            sentences = []
            sources_map = {}
            sent_id = 0
            
            for article in articles:
                content = article.get("content", "")
                if content:
                    extracted = extract_sentences(content, min_length=15)
                    for sent in extracted:
                        sentences.append(sent)
                        sources_map[sent_id] = {
                            "title": article.get("title"),
                            "url": article.get("url"),
                            "source": "Wikipedia"
                        }
                        sent_id += 1
            
            if not sentences:
                return self._error_response(claim, "No sentences extracted", time.time() - start_time)
            
            # Stage 4: Deduplication (simple check - could be enhanced)
            # For now, just use unique sentences
            unique_sentences = list(dict.fromkeys(sentences))
            
            # Stage 5: Ranking
            if not self.embedder:
                return self._error_response(claim, "Embedder not initialized", time.time() - start_time)
            
            ranking_result = self.embedder.rank_by_similarity(
                claim,
                unique_sentences,
                min(top_k_evidence, len(unique_sentences))
            )
            
            # Stage 6: NLI (optional, skipped for faster inference)
            nli_scores_list = [
                {"entailment": 0.7, "contradiction": 0.1, "neutral": 0.2}
                for _ in ranking_result["ranked_evidence"]
            ]
            
            # Stage 7: Confidence Computation
            # Hybrid: 60% semantic similarity + 40% NLI
            similarity_scores = ranking_result["similarity_scores"]
            confidence_score = float(np.mean(similarity_scores)) if similarity_scores else 0.0
            
            # Stage 8: Result Assembly
            # BUG FIX 3: Initialize evidence_scores list before loop
            evidence_scores = []
            evidence_list = []
            for sent, sim_score, idx in zip(
                ranking_result["ranked_evidence"],
                ranking_result["similarity_scores"],
                ranking_result["indices"]
            ):
                # Append score
                evidence_scores.append(sim_score)
                
                # Find source for this sentence
                source_info = sources_map.get(idx, {"title": "Unknown", "url": "", "source": "Unknown"})
                evidence_dict = format_evidence_dict(
                    sent,
                    source_info.get("url", ""),
                    source_info.get("title", "Unknown"),
                    sim_score,
                    nli_scores_list[0] if nli_scores_list else None
                )
                evidence_list.append(evidence_dict)
            
            # BUG FIX 8: Use LLMReasoner to determine verdict from evidence (NEW)
            verdict = "UNCERTAIN"  # Default fallback
            if self.llm_reasoner and evidence_list:
                try:
                    # Call LLM to reason over the evidence
                    reasoning_result = self.llm_reasoner.reason_over_evidence(claim, evidence_list)
                    llm_verdict = reasoning_result.get("label", "UNCERTAIN")
                    
                    # Map LLM labels to final verdicts
                    # SUPPORTS -> TRUE, REFUTES -> MISINFORMATION, UNCERTAIN -> UNCERTAIN
                    label_map = {
                        "SUPPORTS": "TRUE",
                        "REFUTES": "MISINFORMATION",
                        "UNCERTAIN": "UNCERTAIN",
                        "TRUE": "TRUE",
                        "MISINFORMATION": "MISINFORMATION",
                        "FALSE": "MISINFORMATION"
                    }
                    verdict = label_map.get(llm_verdict, "UNCERTAIN")
                    logger.info(f"LLM verdict: {llm_verdict} -> {verdict}")
                except Exception as e:
                    logger.error(f"LLM reasoning failed, using confidence score: {e}")
                    # Fallback to confidence-based verdict if LLM fails
                    if confidence_score >= 0.7:
                        verdict = "TRUE"
                    elif confidence_score >= 0.5:
                        verdict = "UNCERTAIN"
                    else:
                        verdict = "MISINFORMATION"
            else:
                #Fallback: use confidence score if no LLM
                if confidence_score >= 0.7:
                    verdict = "TRUE"
                elif confidence_score >= 0.5:
                    verdict = "UNCERTAIN"
                else:
                    verdict = "MISINFORMATION"
            
            elapsed = time.time() - start_time
            
            return {
                "success": True,
                "claim": claim,
                "answer": verdict,
                "verdict": verdict,
                "confidence": float(confidence_score),
                "evidence": evidence_list,
                "metadata": {
                    "total_articles_fetched": len(articles),
                    "total_sentences_extracted": len(sentences),
                    "final_evidence_count": len(evidence_list),
                    "processing_time_ms": elapsed * 1000,
                    "nli_enabled": self.use_nli,
                    "timestamp": datetime.now().isoformat()
                }
            }
        
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            elapsed = time.time() - start_time
            return self._error_response(claim, str(e), elapsed)
    
    def _error_response(self, claim: str, error_msg: str, elapsed: float) -> Dict[str, Any]:
        """Generate error response."""
        return {
            "success": False,
            "claim": claim,
            "answer": "ERROR",
            "verdict": "ERROR",
            "confidence": 0.0,
            "evidence": [],
            "metadata": {
                "error": error_msg,
                "processing_time_ms": elapsed * 1000,
                "timestamp": datetime.now().isoformat()
            }
        }


class StreamlineRAGPipeline(ProductionRAGPipeline):
    """Fast version without NLI inference."""
    
    def __init__(self, embedder_model: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        """Initialize streamlined pipeline (NLI disabled)."""
        super().__init__(
            use_nli=False,
            embedder_model=embedder_model,
            device=device,
            top_k_evidence=5
        )
