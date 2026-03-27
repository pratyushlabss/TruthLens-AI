"""
Verdict Engine - Computes final verdict based on evidence scores.
Rule-based decision logic, not ML-driven.
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class VerdictEngine:
    """
    Computes final verdict using rule-based logic.
    """
    
    def __init__(self):
        """Initialize verdict engine."""
        self.decision_threshold = 1.5
        self.min_confidence_threshold = 0.3
        logger.info("VerdictEngine initialized")
    
    def compute(
        self,
        evidence_items: List[Dict],
        nlp_score: float = 50.0,
        propagation_risk: str = "LOW"
    ) -> Dict:
        """
        Compute final verdict from evidence.
        
        Args:
            evidence_items: Ranked evidence items with credibility scores
            nlp_score: NLP classification score (0-100)
            propagation_risk: "LOW", "MEDIUM", "HIGH"
            
        Returns:
            Verdict result
        """
        
        logger.info(f"Computing verdict from {len(evidence_items)} evidence items")
        
        if not evidence_items:
            logger.warning("No evidence provided - returning UNCERTAIN")
            return self._uncertain_verdict(reason="No evidence found", nlp_score=nlp_score)
        
        # Calculate support and refute scores
        support_score = self._calculate_support_score(evidence_items)
        refute_score = self._calculate_refute_score(evidence_items)
        neutral_score = self._calculate_neutral_score(evidence_items)
        
        logger.info(
            f"Evidence scores - Support: {support_score:.2f}, "
            f"Refute: {refute_score:.2f}, Neutral: {neutral_score:.2f}"
        )
        
        # Apply decision logic
        verdict, confidence = self._apply_decision_logic(
            support_score,
            refute_score,
            neutral_score,
            len(evidence_items)
        )
        
        # Build reasoning
        reasoning = self._build_reasoning(
            verdict,
            support_score,
            refute_score,
            neutral_score,
            len(evidence_items)
        )
        
        # Calculate metrics
        metrics = self._calculate_metrics(evidence_items, support_score, refute_score)
        
        result = {
            "verdict": verdict,
            "confidence": confidence,
            "support_score": round(support_score, 3),
            "refute_score": round(refute_score, 3),
            "neutral_score": round(neutral_score, 3),
            "reasoning": reasoning,
            "metrics": metrics
        }
        
        logger.info(f"Verdict computed: {verdict} (confidence: {confidence:.1%})")
        
        return result
    
    def _calculate_support_score(self, evidence_items: List[Dict]) -> float:
        """Calculate weighted support score."""
        score = 0.0
        
        for item in evidence_items:
            if item.get("stance") == "SUPPORTS":
                credibility = item.get("credibility", 0.5)
                relevance = item.get("relevance", 0.5)
                weight = credibility * (1.0 + relevance * 0.5)
                score += weight
        
        return score
    
    def _calculate_refute_score(self, evidence_items: List[Dict]) -> float:
        """Calculate weighted refute score."""
        score = 0.0
        
        for item in evidence_items:
            if item.get("stance") == "REFUTES":
                credibility = item.get("credibility", 0.5)
                relevance = item.get("relevance", 0.5)
                weight = credibility * (1.0 + relevance * 0.5)
                score += weight
        
        return score
    
    def _calculate_neutral_score(self, evidence_items: List[Dict]) -> float:
        """Calculate neutral score."""
        score = 0.0
        
        for item in evidence_items:
            if item.get("stance") == "NEUTRAL":
                credibility = item.get("credibility", 0.5)
                score += credibility
        
        return score
    
    def _apply_decision_logic(
        self,
        support_score: float,
        refute_score: float,
        neutral_score: float,
        evidence_count: int
    ) -> tuple:
        """
        Apply decision logic.
        
        Args:
            support_score: Support evidence weight
            refute_score: Refute evidence weight
            neutral_score: Neutral evidence weight
            evidence_count: Total number of evidence items
            
        Returns:
            Tuple of (verdict, confidence)
        """
        
        total_score = support_score + refute_score + neutral_score
        
        if total_score < 0.5:
            return ("UNCERTAIN", 0.3)
        
        if refute_score > support_score * self.decision_threshold:
            confidence = min(
                1.0,
                (refute_score - support_score) / max(total_score, 1.0)
            )
            
            if confidence >= self.min_confidence_threshold or evidence_count >= 3:
                return ("FALSE", confidence)
            else:
                return ("UNCERTAIN", (confidence + 0.3) / 2)
        
        if support_score > refute_score * self.decision_threshold:
            confidence = min(
                1.0,
                (support_score - refute_score) / max(total_score, 1.0)
            )
            
            if confidence >= self.min_confidence_threshold or evidence_count >= 3:
                return ("TRUE", confidence)
            else:
                return ("UNCERTAIN", (confidence + 0.3) / 2)
        
        return ("UNCERTAIN", 0.5)
    
    def _build_reasoning(
        self,
        verdict: str,
        support_score: float,
        refute_score: float,
        neutral_score: float,
        evidence_count: int
    ) -> str:
        """Build human-readable reasoning."""
        
        if evidence_count == 0:
            return "No evidence found to verify or refute this claim."
        
        if verdict == "TRUE":
            return (
                f"This claim is classified as TRUE based on {evidence_count} sources. "
                f"Supporting sources (credibility score: {support_score:.1f}) outweigh "
                f"contradictory sources (credibility score: {refute_score:.1f})."
            )
        
        if verdict == "FALSE":
            return (
                f"This claim is classified as FALSE based on {evidence_count} sources. "
                f"Contradictory sources (credibility score: {refute_score:.1f}) outweigh "
                f"supporting sources (credibility score: {support_score:.1f})."
            )
        
        if support_score > 0 and refute_score > 0:
            return (
                f"This claim cannot be definitively verified. Evidence is mixed with "
                f"{evidence_count} sources providing conflicting information."
            )
        
        return "Insufficient evidence to reach a verdict on this claim."
    
    def _calculate_metrics(
        self,
        evidence_items: List[Dict],
        support_score: float,
        refute_score: float
    ) -> Dict:
        """Calculate auxiliary metrics."""
        
        if not evidence_items:
            return {
                "evidence_quality": 0.3,
                "agreement": 0.5,
                "source_count": 0
            }
        
        avg_credibility = sum(e.get("credibility", 0.5) for e in evidence_items) / len(evidence_items)
        
        support_count = sum(1 for e in evidence_items if e.get("stance") == "SUPPORTS")
        refute_count = sum(1 for e in evidence_items if e.get("stance") == "REFUTES")
        neutral_count = sum(1 for e in evidence_items if e.get("stance") == "NEUTRAL")
        
        total = len(evidence_items)
        max_category = max(support_count, refute_count, neutral_count)
        agreement = max_category / total if total > 0 else 0.5
        
        return {
            "evidence_quality": round(avg_credibility, 3),
            "agreement": round(agreement, 3),
            "source_count": total,
            "support_count": support_count,
            "refute_count": refute_count,
            "neutral_count": neutral_count
        }
    
    def _uncertain_verdict(self, reason: str, nlp_score: float = 50.0) -> Dict:
        """Return an UNCERTAIN verdict."""
        return {
            "verdict": "UNCERTAIN",
            "confidence": 0.3,
            "support_score": 0.0,
            "refute_score": 0.0,
            "neutral_score": 0.0,
            "reasoning": reason,
            "metrics": {
                "evidence_quality": 0.3,
                "agreement": 0.5,
                "source_count": 0
            }
        }
