"""
Evidence Builder - Converts raw articles into structured evidence format.
Performs stance detection and snippet extraction.
"""

import logging
from typing import List, Dict, Optional
import re
from datetime import datetime

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)


class EvidenceBuilder:
    """
    Converts raw scraped articles into structured evidence format.
    Performs NLI-based stance detection and relevance scoring.
    """
    
    def __init__(self):
        """Initialize evidence builder with NLI model."""
        self.nli_model = None
        self.transformers_available = TRANSFORMERS_AVAILABLE
        
        logger.info(f"EvidenceBuilder initialized - Transformers: {TRANSFORMERS_AVAILABLE}")
    
    def _load_nli_model(self):
        """Lazy load NLI model on first use."""
        if self.nli_model is None and self.transformers_available:
            try:
                logger.info("Loading NLI model...")
                self.nli_model = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli"
                )
                logger.info("NLI model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load NLI model: {e}")
                self.nli_model = None
    
    def build(
        self,
        claim: str,
        raw_articles: List[Dict],
        max_evidence: int = 10
    ) -> Dict:
        """
        Convert raw articles into structured evidence.
        
        Args:
            claim: Original claim to verify
            raw_articles: List of raw scraped articles
            max_evidence: Maximum evidence items to return
            
        Returns:
            Structured evidence dictionary
        """
        logger.info(f"Building evidence from {len(raw_articles)} articles for claim: {claim[:80]}")
        
        evidence_list = []
        
        for article in raw_articles:
            try:
                evidence_item = self._process_article(claim, article)
                if evidence_item:
                    evidence_list.append(evidence_item)
            except Exception as e:
                logger.error(f"Failed to process article: {e}")
        
        # Sort by relevance
        evidence_list = sorted(
            evidence_list,
            key=lambda x: x["relevance"],
            reverse=True
        )[:max_evidence]
        
        # Generate summary
        summary = self._generate_evidence_summary(evidence_list)
        
        result = {
            "claim": claim,
            "evidence": evidence_list,
            "summary": summary
        }
        
        logger.info(f"Evidence built: {len(evidence_list)} items")
        
        return result
    
    def _process_article(self, claim: str, article: Dict) -> Optional[Dict]:
        """
        Process single article into evidence item.
        
        Args:
            claim: Original claim
            article: Raw article from retrieval engine
            
        Returns:
            Evidence item or None
        """
        # Validate article
        if not article.get("text") or len(article.get("text", "")) < 100:
            logger.debug(f"Article too short for {article.get('title', 'unknown')}")
            return None
        
        # Detect stance
        stance, stance_score = self._detect_stance(claim, article["text"])
        
        # Calculate relevance
        relevance = self._calculate_relevance(claim, article["text"])
        
        # Extract best matching sentence
        matched_sentence = self._find_matched_sentence(claim, article["text"])
        
        # Extract snippet
        snippet = self._extract_snippet(article["text"], matched_sentence)
        
        evidence_item = {
            "source": article.get("source", "Unknown"),
            "url": article.get("url", ""),
            "title": article.get("title", "Unknown"),
            "text": article.get("text", "")[:2000],
            "snippet": snippet,
            "stance": stance,
            "credibility": self._estimate_credibility(article),
            "relevance": relevance,
            "matched_sentence": matched_sentence,
            "retrieved_at": article.get("retrieved_at", datetime.now().isoformat())
        }
        
        return evidence_item
    
    def _detect_stance(self, claim: str, text: str) -> tuple:
        """
        Detect stance of article toward claim.
        
        Args:
            claim: Original claim
            text: Article text
            
        Returns:
            Tuple of (stance, score)
        """
        # Simple keyword-based fallback
        return self._detect_stance_keyword(claim, text)
    
    def _detect_stance_keyword(self, claim: str, text: str) -> tuple:
        """
        Fallback stance detection using keyword matching.
        
        Args:
            claim: Original claim
            text: Article text
            
        Returns:
            Tuple of (stance, score)
        """
        text_lower = text.lower()
        claim_lower = claim.lower()
        
        # Extract key entities/keywords from claim
        keywords = self._extract_keywords(claim)
        
        # Count keyword matches
        keyword_matches = sum(1 for kw in keywords if kw in text_lower)
        
        if keyword_matches < 2:
            return ("NEUTRAL", 0.3)
        
        return ("SUPPORTS", 0.6)
    
    def _extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        """
        Extract important keywords from text.
        
        Args:
            text: Input text
            top_k: Number of keywords to extract
            
        Returns:
            List of keywords
        """
        stop_words = {
            "the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
            "be", "been", "being", "have", "has", "had", "do", "does", "did"
        }
        
        words = text.lower().split()
        words = [
            w.strip(".,!?;:\"'()") for w in words
            if len(w) > 3 and w.lower() not in stop_words
        ]
        
        seen = set()
        unique_words = []
        for w in words:
            if w not in seen:
                seen.add(w)
                unique_words.append(w)
        
        return unique_words[:top_k]
    
    def _calculate_relevance(self, claim: str, text: str) -> float:
        """
        Calculate relevance of article to claim (0-1).
        
        Args:
            claim: Original claim
            text: Article text
            
        Returns:
            Relevance score
        """
        claim_keywords = set(self._extract_keywords(claim, top_k=10))
        text_keywords = set(self._extract_keywords(text, top_k=20))
        
        if not claim_keywords:
            return 0.3
        
        overlap = len(claim_keywords & text_keywords)
        relevance = min(1.0, overlap / len(claim_keywords))
        
        if len(text) > 500:
            relevance = min(1.0, relevance + 0.1)
        
        return round(relevance, 2)
    
    def _find_matched_sentence(self, claim: str, text: str) -> str:
        """
        Find the best matching sentence in text to claim.
        
        Args:
            claim: Original claim
            text: Article text
            
        Returns:
            Best matching sentence or empty string
        """
        sentences = text.split(".")
        best_sentence = ""
        best_score = 0
        
        claim_words = set(claim.lower().split())
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            sentence_words = set(sentence.lower().split())
            overlap = len(claim_words & sentence_words)
            
            if overlap > best_score:
                best_score = overlap
                best_sentence = sentence
        
        return best_sentence[:200] if best_sentence else ""
    
    def _extract_snippet(self, text: str, matched_sentence: str = "") -> str:
        """
        Extract a representative snippet from text.
        
        Args:
            text: Full article text
            matched_sentence: Pre-identified matching sentence
            
        Returns:
            Snippet (max 300 characters)
        """
        if matched_sentence:
            return matched_sentence[:300]
        
        paragraphs = text.split("\n\n")
        for para in paragraphs:
            para = para.strip()
            if len(para) > 100:
                return para[:300]
        
        return text[:300]
    
    def _estimate_credibility(self, article: Dict) -> float:
        """
        Estimate source credibility.
        
        Args:
            article: Article data
            
        Returns:
            Credibility score (0-1)
        """
        source = (article.get("source") or "").lower()
        
        trusted_domains = {
            "bbc": 0.95, "reuters": 0.95, "ap news": 0.95,
            "the guardian": 0.9, "npr": 0.9
        }
        
        for trusted, score in trusted_domains.items():
            if trusted in source:
                return score
        
        text_length = len(article.get("text", ""))
        base_score = min(1.0, text_length / 1000)
        
        return max(0.3, base_score * 0.8)
    
    def _generate_evidence_summary(self, evidence_list: List[Dict]) -> str:
        """
        Generate summary of evidence.
        
        Args:
            evidence_list: List of evidence items
            
        Returns:
            Summary string
        """
        if not evidence_list:
            return "No supporting or contradicting evidence found."
        
        supports = sum(1 for e in evidence_list if e["stance"] == "SUPPORTS")
        refutes = sum(1 for e in evidence_list if e["stance"] == "REFUTES")
        neutral = sum(1 for e in evidence_list if e["stance"] == "NEUTRAL")
        
        summary_parts = []
        
        if supports > 0:
            summary_parts.append(f"{supports} source(s) support the claim")
        if refutes > 0:
            summary_parts.append(f"{refutes} source(s) refute the claim")
        if neutral > 0:
            summary_parts.append(f"{neutral} source(s) are neutral")
        
        if summary_parts:
            return "; ".join(summary_parts) + "."
        
        return "Mixed evidence found."
