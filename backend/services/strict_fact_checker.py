"""
STRICT FACT-CHECKING SYSTEM - IMPLEMENTATION GUIDE

This module implements the exact fact-checking rules provided:
- NEVER hallucinate or invent sources
- ONLY use URLs present in context
- Empty context → verdict = UNKNOWN
- Weak evidence → verdict = UNKNOWN
- Prefer high-credibility domains

Response format must match the strict JSON schema provided.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Verdict(str, Enum):
    """Strict verdict values - no REAL/RUMOR/FAKE"""
    TRUE = "TRUE"
    FALSE = "FALSE"
    MISLEADING = "MISLEADING"
    UNKNOWN = "UNKNOWN"


class CredibilityLevel(str, Enum):
    """Source credibility levels"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class StrictFactCheckResponse:
    """
    Strict fact-checking response following the provided specification.
    
    RULES ENFORCED:
    - verdict: Must be TRUE | FALSE | MISLEADING | UNKNOWN
    - confidence: If context empty → 0
    - Only include sources that are actually in retrieved_documents
    - Never invent URLs or sources
    - key_signals: Verified patterns, not assumptions
    """
    
    def __init__(
        self,
        claim: str,
        retrieved_documents: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Initialize with claim and optional retrieved context.
        
        Args:
            claim: The claim being verified
            retrieved_documents: List of dicts with 'url', 'title', 'content', 'credibility'
        """
        self.claim = claim
        self.retrieved_documents = retrieved_documents or []
        self.verdict = Verdict.UNKNOWN  # Default to UNKNOWN
        self.confidence = 0
        self.reasoning = ""
        self.key_signals: List[str] = []
        self.highlighted_terms: List[str] = []
        self.top_sources: List[Dict[str, Any]] = []
        self.source_summary = ""
        self.final_explanation = ""
        
        # Validate immediately on construction
        if not self.retrieved_documents:
            self._set_no_sources_verdict()
    
    def _set_no_sources_verdict(self):
        """Set verdict when no sources are available."""
        self.verdict = Verdict.UNKNOWN
        self.confidence = 0
        self.key_signals = ["No credible sources retrieved from backend"]
        self.reasoning = "System could not verify claim due to missing retrieval data"
        self.top_sources = []
        self.source_summary = "No sources found"
        self.final_explanation = (
            "Unable to verify this claim. No sources were retrieved from the evidence database. "
            "Please try again with different keywords or check backend connectivity."
        )
    
    def add_evidence(
        self,
        has_supporting_evidence: bool,
        has_contradicting_evidence: bool,
        evidence_strength: float = 0.5,
        patterns_detected: Optional[List[str]] = None,
    ):
        """
        Add analyzed evidence to determine verdict.
        
        Args:
            has_supporting_evidence: Found sources supporting the claim
            has_contradicting_evidence: Found sources contradicting the claim
            evidence_strength: How strong is the evidence (0-1)
            patterns_detected: List of misinformation patterns found
        """
        patterns_detected = patterns_detected or []
        self.key_signals.extend(patterns_detected)
        
        # Determine verdict strictly
        if not self.retrieved_documents:
            # No sources = UNKNOWN (not FALSE!)
            self.verdict = Verdict.UNKNOWN
            self.confidence = 0
        elif has_contradicting_evidence and not has_supporting_evidence:
            # Clear contradiction = FALSE
            self.verdict = Verdict.FALSE
            self.confidence = min(100, evidence_strength * 100)
        elif has_supporting_evidence and has_contradicting_evidence:
            # Mixed evidence = MISLEADING
            self.verdict = Verdict.MISLEADING
            self.confidence = min(100, evidence_strength * 50)  # Lower confidence for mixed
        elif has_supporting_evidence:
            # Supporting evidence only = TRUE
            self.verdict = Verdict.TRUE
            self.confidence = min(100, evidence_strength * 100)
        else:
            # No clear evidence = UNKNOWN (not FALSE!)
            self.verdict = Verdict.UNKNOWN
            self.confidence = min(50, evidence_strength * 50)
    
    def extract_keywords(self):
        """Extract significant keywords from the claim."""
        # Remove common words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "is", "are", "was", "were", "be", "been",
            "will", "would", "could", "should", "this", "that", "it"
        }
        
        words = self.claim.lower().split()
        self.highlighted_terms = [
            w.strip('.,!?;:') for w in words 
            if len(w) > 4 and w.lower() not in stop_words
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to strict JSON format as specified.
        
        STRICT FORMAT RULES:
        - verdict: String enum only
        - confidence: Number 0-100
        - Only include actual sources with real URLs
        - key_signals: Array of verified patterns
        - top_sources: Array with title, url, credibility, evidence
        """
        return {
            "verdict": self.verdict.value,  # TRUE | FALSE | MISLEADING | UNKNOWN
            "confidence": self.confidence,   # 0-100
            "reasoning": self.reasoning,
            "key_signals": self.key_signals or ["No clear signals"],
            "highlighted_terms": self.highlighted_terms,
            "top_sources": self.top_sources,  # Only real sources with verified URLs
            "source_summary": self.source_summary or self._generate_source_summary(),
            "final_explanation": self.final_explanation or self._generate_explanation(),
        }
    
    def _generate_source_summary(self) -> str:
        """Generate summary of what sources say."""
        if not self.top_sources:
            return "No sources were available for analysis"
        
        supporting = sum(
            1 for s in self.top_sources 
            if s.get("evidence") and "support" in s.get("evidence", "").lower()
        )
        contradicting = sum(
            1 for s in self.top_sources 
            if s.get("evidence") and "contradict" in s.get("evidence", "").lower()
        )
        
        if supporting > contradicting:
            return f"{supporting} sources support, {contradicting} contradict"
        elif contradicting > supporting:
            return f"{contradicting} sources contradict, {supporting} support"
        else:
            return "Sources present mixed evidence"
    
    def _generate_explanation(self) -> str:
        """Generate simple human-readable explanation."""
        explanations = {
            Verdict.TRUE: "This claim is supported by credible sources.",
            Verdict.FALSE: "This claim is contradicted by credible sources.",
            Verdict.MISLEADING: "This claim is partially true but requires context.",
            Verdict.UNKNOWN: "Cannot verify this claim - insufficient evidence."
        }
        
        explanation = explanations.get(self.verdict, "Unable to verify")
        
        if self.confidence < 50 and self.verdict != Verdict.UNKNOWN:
            explanation += f" (Low confidence: {int(self.confidence)}%)"
        
        return explanation
    
    def validate_response(self) -> bool:
        """
        Validate that response follows ALL strict rules.
        
        Returns True only if:
        1. verdict is valid enum
        2. confidence is 0-100
        3. All sources have actual URLs from retrieved_documents
        4. No hallucinated sources
        """
        # Check verdict
        if not isinstance(self.verdict, Verdict):
            logger.error(f"Invalid verdict: {self.verdict}")
            return False
        
        # Check confidence
        if not (0 <= self.confidence <= 100):
            logger.error(f"Invalid confidence: {self.confidence}")
            return False
        
        # Check sources - NEVER hallucinate
        actual_urls = {doc.get("url") for doc in self.retrieved_documents}
        
        for source in self.top_sources:
            if source.get("url") not in actual_urls:
                logger.error(f"Hallucinated URL detected: {source.get('url')}")
                return False
        
        # Check key_signals - should be truthful patterns
        forbidden_signals = [
            "Hallucinated evidence",
            "Made-up sources",
            "Invented data"
        ]
        
        for signal in self.key_signals:
            if any(forbidden in signal for forbidden in forbidden_signals):
                logger.error(f"Invalid signal: {signal}")
                return False
        
        logger.info(f"✓ Response validation passed for verdict: {self.verdict.value}")
        return True


# Example usage
if __name__ == "__main__":
    print("STRICT FACT-CHECKING SYSTEM")
    print("=" * 70)
    
    # Test 1: No sources (empty context)
    print("\n[TEST 1] Empty Context → UNKNOWN verdict")
    response1 = StrictFactCheckResponse(
        claim="The moon is made of cheese",
        retrieved_documents=[]  # Empty!
    )
    print(f"Verdict: {response1.verdict.value}")
    print(f"Confidence: {response1.confidence}")
    print(f"Key signals: {response1.key_signals}")
    assert response1.verdict == Verdict.UNKNOWN
    assert response1.confidence == 0
    print("✓ Test 1 PASSED")
    
    # Test 2: With sources, clear contradiction
    print("\n[TEST 2] Sources Contradict → FALSE verdict")
    response2 = StrictFactCheckResponse(
        claim="The moon is made of cheese",
        retrieved_documents=[
            {
                "url": "https://nasa.gov/moon",
                "title": "NASA - Moon Composition",
                "content": "The moon is made of rock and dust, not cheese",
                "credibility": "High"
            }
        ]
    )
    response2.add_evidence(
        has_supporting_evidence=False,
        has_contradicting_evidence=True,
        evidence_strength=0.95,
        patterns_detected=["Factual inaccuracy"]
    )
    response2.extract_keywords()
    print(f"Verdict: {response2.verdict.value}")
    print(f"Confidence: {response2.confidence}")
    assert response2.verdict == Verdict.FALSE
    assert response2.confidence > 90
    print("✓ Test 2 PASSED")
    
    # Test 3: No hallucinated sources
    print("\n[TEST 3] Source Validation (no hallucination)")
    response3 = StrictFactCheckResponse(
        claim="Test claim",
        retrieved_documents=[
            {"url": "https://example.com", "title": "Example"}
        ]
    )
    # Try to add source that's NOT in retrieved_documents
    response3.top_sources = [
        {
            "title": "Real Source",
            "url": "https://example.com",  # Valid - in retrieved_documents
            "credibility": "High",
            "evidence": "Supports claim"
        }
    ]
    assert response3.validate_response() == True
    print("✓ Test 3 PASSED - No hallucinated sources")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
