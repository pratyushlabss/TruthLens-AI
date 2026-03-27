"""
Source Ranker - Dynamically assigns credibility scores to sources.
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class SourceRanker:
    """
    Dynamically ranks source credibility.
    """
    
    def __init__(self):
        """Initialize source ranker."""
        self.trusted_domains = {
            "bbc.com": 0.95, "reuters.com": 0.95, "apnews.com": 0.95,
            "theguardian.com": 0.90, "nporg": 0.90, "nytimes.com": 0.90,
            "washingtonpost.com": 0.90, "nature.com": 0.95, "who.int": 0.95
        }
        logger.info("SourceRanker initialized")
    
    def rank_sources(self, evidence_items: List[Dict], claim: str = "") -> List[Dict]:
        """
        Rank and score all evidence items.
        
        Args:
            evidence_items: List of evidence items
            claim: Original claim
            
        Returns:
            Ranked evidence items with credibility scores
        """
        logger.info(f"Ranking {len(evidence_items)} sources...")
        
        ranked = []
        
        for item in evidence_items:
            credibility = self._calculate_credibility(item)
            item["credibility"] = credibility
            ranked.append(item)
        
        ranked = sorted(ranked, key=lambda x: x["credibility"], reverse=True)
        
        logger.info(f"Ranking complete. Top credibility: {ranked[0]['credibility'] if ranked else 'N/A'}")
        
        return ranked
    
    def _calculate_credibility(self, item: Dict) -> float:
        """Calculate composite credibility score."""
        base_credibility = item.get("credibility", 0.5)
        domain_score = self._score_domain(item.get("source", ""))
        content_score = self._score_content(item)
        
        composite = (
            base_credibility * 0.3 +
            domain_score * 0.4 +
            content_score * 0.3
        )
        
        return round(min(1.0, max(0.0, composite)), 3)
    
    def _score_domain(self, source_name: str) -> float:
        """Score domain reputation."""
        source_lower = source_name.lower()
        
        for domain, score in self.trusted_domains.items():
            if domain in source_lower:
                return score
        
        score = 0.5
        if any(x in source_lower for x in [".edu", ".gov", ".org", ".ac.uk"]):
            score += 0.15
        if any(x in source_lower for x in ["reddit", "twitter", "tiktok"]):
            score = min(score, 0.3)
        
        return round(min(1.0, max(0.0, score)), 3)
    
    def _score_content(self, item: Dict) -> float:
        """Score content quality."""
        text = item.get("text", "")
        score = 0.5
        
        text_length = len(text)
        if text_length > 1000:
            score += 0.2
        elif text_length > 500:
            score += 0.15
        elif text_length > 200:
            score += 0.1
        
        if item.get("title") and len(item.get("title", "")) > 10:
            score += 0.1
        
        if item.get("snippet") and len(item.get("snippet", "")) > 100:
            score += 0.1
        
        return round(min(1.0, max(0.0, score)), 3)
    
    def score_agreement(self, evidence_items: List[Dict]) -> float:
        """Calculate agreement between sources."""
        if len(evidence_items) < 2:
            return 0.5
        
        supports = sum(1 for e in evidence_items if e["stance"] == "SUPPORTS")
        refutes = sum(1 for e in evidence_items if e["stance"] == "REFUTES")
        neutral = sum(1 for e in evidence_items if e["stance"] == "NEUTRAL")
        
        total = len(evidence_items)
        max_category = max(supports, refutes, neutral)
        consensus = max_category / total if total > 0 else 0.5
        
        return round(consensus, 3)


def rank_and_aggregate_evidence(evidence_items: List[Dict], claim: str = "") -> Dict:
    """
    Utility function to rank sources and aggregate statistics.
    
    Args:
        evidence_items: Raw evidence items
        claim: Original claim
        
    Returns:
        Aggregated evidence report
    """
    ranker = SourceRanker()
    ranked = ranker.rank_sources(evidence_items, claim)
    
    avg_credibility = sum(e["credibility"] for e in ranked) / len(ranked) if ranked else 0.5
    
    supports_items = [e for e in ranked if e["stance"] == "SUPPORTS"]
    refutes_items = [e for e in ranked if e["stance"] == "REFUTES"]
    neutral_items = [e for e in ranked if e["stance"] == "NEUTRAL"]
    
    support_score = sum(e["credibility"] for e in supports_items) if supports_items else 0
    refute_score = sum(e["credibility"] for e in refutes_items) if refutes_items else 0
    
    agreement = ranker.score_agreement(ranked)
    
    return {
        "ranked_evidence": ranked,
        "statistics": {
            "total_sources": len(ranked),
            "avg_credibility": round(avg_credibility, 3),
            "support_count": len(supports_items),
            "refute_count": len(refutes_items),
            "neutral_count": len(neutral_items),
            "support_score": round(support_score, 3),
            "refute_score": round(refute_score, 3),
            "agreement": agreement
        }
    }
