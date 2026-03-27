"""
Evidence Builder - FIXED with guaranteed non-empty evidence.
Converts raw articles into structured evidence with stance detection.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EvidenceBuilder:
    """
    Builds structured evidence from raw articles.
    === FIX 2: GUARANTEED NON-EMPTY EVIDENCE ===
    Always returns evidence, never empty.
    """
    
    def __init__(self):
        """Initialize evidence builder."""
        self.stance_labels = ["SUPPORTS", "REFUTES", "NEUTRAL"]
    
    def build(
        self,
        raw_articles: List[Dict],
        claim: str,
        nlp_score: float = 0.5
    ) -> List[Dict]:
        """
        Build structured evidence from raw articles.
        === FIX 2: GUARANTEED NON-EMPTY EVIDENCE ===
        Always returns at least one evidence item.
        
        Args:
            raw_articles: Raw scraped articles
            claim: The claim being analyzed
            nlp_score: NLP classification score
            
        Returns:
            Structured evidence list (guaranteed non-empty)
        """
        evidence_list = []
        
        logger.info(f"[FIX2] Building evidence from {len(raw_articles)} articles")
        
        # Process each article
        if raw_articles:
            for article in raw_articles:
                try:
                    evidence_item = self._build_evidence_item(
                        article, claim, nlp_score
                    )
                    if evidence_item:
                        evidence_list.append(evidence_item)
                except Exception as e:
                    logger.warning(f"[FIX2] Error building evidence item: {e}")
                    continue
        
        # === FIX 2: FORCE FALLBACK EVIDENCE IF EMPTY ===
        if not evidence_list:
            logger.warning(
                "[FIX2] No evidence items built - adding fallback evidence"
            )
            fallback_evidence = {
                "source": "System Fallback",
                "stance": "NEUTRAL",
                "credibility": 0.3,
                "snippet": "Insufficient real sources available",
                "text": (
                    f"Claim: {claim}\n\n"
                    f"Status: No strong corroborating or refuting sources found.\n"
                    f"This may indicate:\n"
                    f"  - Limited external evidence availability\n"
                    f"  - Claim specificity or recency\n"
                    f"  - Search source limitations\n\n"
                    f"Analysis proceeding with system classification."
                ),
                "url": "generated://system-fallback",
                "is_fallback": True,
                "credibility_reason": "System-generated due to lack of real sources",
                "stance_confidence": 0.33,
                "retrieved_at": datetime.now().isoformat()
            }
            evidence_list = [fallback_evidence]
        
        logger.info(f"[FIX2] Returning {len(evidence_list)} evidence items")
        return evidence_list
    
    def _build_evidence_item(
        self,
        article: Dict,
        claim: str,
        nlp_score: float
    ) -> Optional[Dict]:
        """
        Build a single evidence item from an article.
        
        Args:
            article: Raw article data
            claim: The claim being analyzed
            nlp_score: NLP classification score
            
        Returns:
            Structured evidence item
        """
        try:
            # Determine stance based on NLP score
            if nlp_score > 0.6:
                stance = "SUPPORTS"
            elif nlp_score < 0.4:
                stance = "REFUTES"
            else:
                stance = "NEUTRAL"
            
            # Get credibility
            credibility = article.get("credibility", 0.5)
            is_fallback = article.get("is_fallback", False)
            
            evidence_item = {
                "source": article.get("source", "Unknown Source"),
                "stance": stance,
                "credibility": credibility,
                "credibility_reason": (
                    "From external source" if not is_fallback 
                    else "System-generated fallback"
                ),
                "snippet": article.get("snippet", article.get("title", "No text")),
                "text": article.get("text", ""),
                "url": article.get("url", "unknown"),
                "is_fallback": is_fallback,
                "stance_confidence": abs(nlp_score - 0.5) * 2,  # 0 to 1
                "retrieved_at": article.get(
                    "retrieved_at",
                    datetime.now().isoformat()
                )
            }
            
            return evidence_item
        
        except Exception as e:
            logger.warning(f"[FIX2] Error in _build_evidence_item: {e}")
            return None
    
    def deduplicate_evidence(self, evidence_list: List[Dict]) -> List[Dict]:
        """
        Remove duplicate evidence items.
        Preserves fallback evidence.
        
        Args:
            evidence_list: Raw evidence list
            
        Returns:
            Deduplicated evidence (guaranteed non-empty)
        """
        if not evidence_list:
            return self._fallback_single_evidence()
        
        seen_sources = set()
        deduplicated = []
        fallback_items = []
        
        for item in evidence_list:
            source_key = (
                item.get("source", ""),
                item.get("snippet", "")[:50]
            )
            
            if source_key not in seen_sources:
                if item.get("is_fallback", False):
                    fallback_items.append(item)
                else:
                    deduplicated.append(item)
                seen_sources.add(source_key)
        
        # Always include fallback items at end if dedup is empty
        result = deduplicated if deduplicated else fallback_items
        
        if not result:
            result = self._fallback_single_evidence()
        
        logger.info(f"[FIX2] Deduplicated to {len(result)} items")
        return result
    
    def _fallback_single_evidence(self) -> List[Dict]:
        """Return single fallback evidence item."""
        return [
            {
                "source": "System Fallback",
                "stance": "NEUTRAL",
                "credibility": 0.3,
                "credibility_reason": "System-generated due to lack of sources",
                "snippet": "No external sources available",
                "text": "Analysis proceeding with system classification only.",
                "url": "generated://system",
                "is_fallback": True,
                "stance_confidence": 0.33,
                "retrieved_at": datetime.now().isoformat()
            }
        ]
