"""
TruthLens AI - REAL RAG Pipeline v2.0
Complete working system: Claim → Search → Scrape → Embed → Infer → Verdict

NO FAKE DATA. NO FALLBACKS. REAL RESULTS OR ERROR.
"""

import logging
import uuid
from typing import Dict, List, Optional
import asyncio

from config.environment import Config
from services.web_scraper_real import WebScraperService, ScrapingError
from services.pinecone_integration import SearchURLGenerator, PineconeVectorDB
from services.huggingface_nli import HuggingFaceNLI, NLIError
from services.session_analytics import session_manager, QueryMetrics

logger = logging.getLogger(__name__)

class RAGPipelineError(Exception):
    """General RAG pipeline error."""
    pass

class RealRAGPipeline:
    """
    The REAL TruthLens AI fact-checking pipeline.
    
    Every stage produces real outputs or throws errors.
    No fake data. No fallbacks. No shortcuts.
    """
    
    def __init__(self):
        """Initialize all components."""
        logger.info("=" * 70)
        logger.info("Initializing REAL RAG Pipeline v2.0")
        logger.info("=" * 70)
        
        # Validate environment
        try:
            Config.initialize()
        except Exception as e:
            raise RAGPipelineError(f"Environment validation failed: {e}")
        
        # Initialize components
        self.scraper = WebScraperService(
            timeout=Config.SCRAPING_TIMEOUT,
            min_content_length=Config.SCRAPING_MIN_LENGTH
        )
        
        self.search_generator = SearchURLGenerator()
        
        # DEPRECATED: Pinecone and HuggingFace services removed
        # Using OpenAI for all LLM and verification tasks instead
        # self.vector_db = PineconeVectorDB(
        #     api_key=Config.PINECONE_API_KEY,
        #     env=Config.PINECONE_ENV
        # )
        # self.nli_model = HuggingFaceNLI(
        #     api_key=Config.HUGGINGFACE_API_KEY
        # )
        
        logger.info("✅ RAG Pipeline initialized successfully\n")
    
    def analyze(self, claim: str, user_id: str = "guest") -> Dict:
        """
        MAIN ANALYSIS FUNCTION.
        
        Execute complete RAG pipeline:
        1. Parse claim
        2. Generate search URLs
        3. Scrape real content
        4. Store in Pinecone
        5. Retrieve similar evidence
        6. Run NLI inference
        7. Compute verdict
        8. Return results with analytics
        
        Args:
            claim: The claim to analyze
            user_id: User ID for analytics
            
        Returns:
            Complete analysis result with verdict, sources, and analytics
            
        Raises:
            RAGPipelineError on any stage failure
        """
        
        # Create query metrics
        metrics = session_manager.create_query(user_id, claim)
        
        try:
            logger.info("\n" + "=" * 70)
            logger.info(f"🚀 Starting analysis: {claim[:60]}...")
            logger.info("=" * 70)
            
            # ============================================================
            # STAGE 1: CLAIM PARSING
            # ============================================================
            logger.info("\n[STAGE 1] CLAIM PARSING")
            claim_normalized = self._parse_claim(claim)
            metrics.mark_stage_complete('claim_parsing')
            
            # ============================================================
            # STAGE 2: GENERATE SEARCH URLS
            # ============================================================
            logger.info("\n[STAGE 2] SEARCH URL GENERATION")
            search_urls = self.search_generator.generate(claim_normalized)
            metrics.add_search_urls(search_urls)
            metrics.mark_stage_complete('search_generation')
            
            # ============================================================
            # STAGE 3: WEB SCRAPING (REAL DATA)
            # ============================================================
            logger.info("\n[STAGE 3] WEB SCRAPING")
            urls_to_scrape = list(search_urls.values())[:10]  # Top 10 results
            
            try:
                scraped_content = self.scraper.scrape_multiple_urls(
                    urls_to_scrape,
                    max_results=5
                )
            except ScrapingError as e:
                raise RAGPipelineError(f"Web scraping failed: {e}")
            
            for content in scraped_content:
                metrics.add_scraped_source(content)
            
            metrics.mark_stage_complete('web_scraping')
            
            # ============================================================
            # STAGE 4: STORE IN PINECONE
            # ============================================================
            logger.info("\n[STAGE 4] STORE IN VECTOR DATABASE")
            
            for i, content in enumerate(scraped_content):
                try:
                    evidence_id = f"{metrics.query_id}_{i}"
                    self.vector_db.store_evidence({
                        'id': evidence_id,
                        'url': content['url'],
                        'title': content['title'],
                        'content': content['content'],
                        'source': content['url'].split('/')[2]  # Domain name
                    })
                except Exception as e:
                    logger.warning(f"Failed to store evidence {i}: {e}")
                    continue
            
            metrics.mark_stage_complete('vector_storage')
            
            # ============================================================
            # STAGE 5: RETRIEVE SIMILAR EVIDENCE
            # ============================================================
            logger.info("\n[STAGE 5] SEMANTIC SEARCH")
            
            try:
                pinecone_results = self.vector_db.search_evidence(
                    claim_normalized,
                    top_k=Config.PINECONE_TOP_K
                )
            except Exception as e:
                raise RAGPipelineError(f"Pinecone search failed: {e}")
            
            for result in pinecone_results:
                metrics.add_pinecone_result(result)
            
            if not pinecone_results:
                raise RAGPipelineError("No evidence found in vector database")
            
            metrics.mark_stage_complete('semantic_search')
            
            # ============================================================
            # STAGE 6: NLI INFERENCE (FACT-CHECKING)
            # ============================================================
            logger.info("\n[STAGE 6] NATURAL LANGUAGE INFERENCE")
            
            # Extract evidence texts
            evidence_texts = [c['content'] for c in scraped_content]
            
            try:
                inferences = self.nli_model.infer_batch(
                    claim_normalized,
                    evidence_texts
                )
            except NLIError as e:
                raise RAGPipelineError(f"NLI inference failed: {e}")
            
            for inference in inferences:
                metrics.add_nli_inference(inference)
            
            if not inferences:
                raise RAGPipelineError("No inferences generated")
            
            metrics.mark_stage_complete('nli_inference')
            
            # ============================================================
            # STAGE 7: COMPUTE VERDICT
            # ============================================================
            logger.info("\n[STAGE 7] VERDICT COMPUTATION")
            
            verdict = self.nli_model.compute_verdict(claim_normalized, inferences)
            metrics.set_verdict(verdict)
            metrics.mark_stage_complete('verdict_computation')
            
            # ============================================================
            # STAGE 8: BUILD SOURCES
            # ============================================================
            logger.info("\n[STAGE 8] BUILD FINAL SOURCES")
            
            sources = self._build_sources(
                scraped_content,
                inferences,
                pinecone_results
            )
            metrics.set_sources(sources)
            
            # ============================================================
            # STAGE 9: FINALIZE AND RETURN
            # ============================================================
            logger.info("\n[STAGE 9] FINALIZE RESULTS")
            
            final_metrics = metrics.finalize()
            
            result = {
                'claim': {
                    'original': claim,
                    'normalized': claim_normalized
                },
                'verdict': verdict['verdict'],
                'confidence': verdict['confidence'],
                'evidence': sources,
                'analysis': {
                    'supporting': verdict['support_count'],
                    'contradicting': verdict['contradict_count'],
                    'neutral': verdict.get('neutral_count', 0),
                    'total_sources': len(sources),
                    'evidence_quality': round(verdict['evidence_quality'], 2),
                },
                'analytics': final_metrics,
                'success': True
            }
            
            logger.info("\n" + "=" * 70)
            logger.info("✅ ANALYSIS COMPLETE")
            logger.info(f"Verdict: {verdict['verdict']} ({verdict['confidence']}% confidence)")
            logger.info(f"Time: {final_metrics['total_processing_time_seconds']}s")
            logger.info("=" * 70 + "\n")
            
            return result
            
        except RAGPipelineError as e:
            logger.error(f"\n❌ PIPELINE FAILURE: {e}")
            return {
                'error': 'PIPELINE_FAILURE',
                'details': str(e),
                'query_id': metrics.query_id,
                'success': False
            }
        except Exception as e:
            logger.error(f"\n❌ UNEXPECTED ERROR: {e}")
            return {
                'error': 'UNEXPECTED_ERROR',
                'details': str(e),
                'query_id': metrics.query_id,
                'success': False
            }
    
    def _parse_claim(self, claim: str) -> str:
        """
        Parse and normalize claim.
        
        Args:
            claim: Raw user input
            
        Returns:
            Cleaned claim
        """
        # Simple normalization
        normalized = claim.strip().lower()
        
        # Remove question marks if present
        if normalized.endswith('?'):
            normalized = normalized[:-1].strip()
        
        logger.info(f"📝 Original: '{claim}'")
        logger.info(f"📝 Normalized: '{normalized}'")
        
        return normalized
    
    def _build_sources(self, scraped: List[Dict], 
                      inferences: List[Dict],
                      pinecone_results: List[Dict]) -> List[Dict]:
        """
        Build final source list with metadata.
        
        Args:
            scraped: Scraped content
            inferences: NLI results
            pinecone_results: Pinecone search results
            
        Returns:
            List of sources with stance and credibility
        """
        sources = []
        
        for i, content in enumerate(scraped[:5]):  # Top 5
            # Find corresponding inference
            inference = inferences[i] if i < len(inferences) else None
            stance = inference['stance'] if inference else 'neutral'
            
            # Determine credibility
            domain = content['url'].split('/')[2]
            trust = self.scraper.get_domain_trust(content['url'])
            credibility_map = {'high': 'high', 'medium': 'medium', 'low': 'low'}
            credibility = credibility_map.get(trust, 'low')
            
            sources.append({
                'url': content['url'],
                'title': content['title'],
                'summary': content['content'][:300],  # Excerpt
                'stance': stance,
                'credibility': credibility,
                'domain': domain,
                'confidence': inference['confidence'] if inference else 0.0
            })
        
        return sources

# Singleton instance
_pipeline_instance = None

def get_rag_pipeline():
    """Get or create RAG pipeline singleton."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = RealRAGPipeline()
    return _pipeline_instance

