"""
[7] NLI MODEL - Natural Language Inference (BART MNLI) for stance detection
"""

import logging
from typing import Dict
import re

logger = logging.getLogger(__name__)


class NLIModel:
    """
    Detect stance (SUPPORT/REFUTE/NEUTRAL) of fact vs claim using NLI.
    Falls back to pattern matching if model unavailable.
    """
    
    def __init__(self):
        """Initialize NLI model."""
        self.model = None
        self._init_model()
    
    def _init_model(self):
        """Try to load BART MNLI model."""
        try:
            from transformers import pipeline
            logger.info("[NLI] Loading BART MNLI model...")
            self.model = pipeline(
                "zero-shot-classification",
                model="bart-large-mnli",
                device=-1  # CPU
            )
            logger.info("[NLI] ✅ BART MNLI model loaded")
        except Exception as e:
            logger.warning(f"[NLI] ⚠️ Could not load BART MNLI: {e}")
            logger.info("[NLI] Using pattern-based fallback")
            self.model = None
    
    def detect_stance(self, fact: str, claim: str) -> Dict:
        """
        Detect if fact SUPPORTS or REFUTES claim.
        
        Args:
            fact: Factual statement from article
            claim: Original claim to verify
            
        Returns:
            {'stance': 'SUPPORTS'|'REFUTES'|'NEUTRAL', 'confidence': float}
        """
        
        if not fact or not claim:
            return {'stance': 'NEUTRAL', 'confidence': 0.3}
        
        # Try NLI model first
        if self.model:
            return self._detect_nli(fact, claim)
        else:
            # Fallback to pattern matching
            return self._detect_pattern_based(fact, claim)
    
    def _detect_nli(self, fact: str, claim: str) -> Dict:
        """Use BART MNLI for stance detection."""
        try:
            # Truncate if too long
            fact = fact[:512]
            claim = claim[:512]
            
            result = self.model(
                fact,
                [claim],
                multi_class=False,
            )
            
            # Extract stance
            label = result['labels'][0]  # Most confident
            score = result['scores'][0]
            
            # Map to our stance labels
            if label == 'ENTAILMENT':
                stance = 'SUPPORTS'
            elif label == 'CONTRADICTION':
                stance = 'REFUTES'
            else:
                stance = 'NEUTRAL'
            
            logger.debug(f"[NLI] Detected: {stance} (confidence: {score:.2f})")
            
            return {
                'stance': stance,
                'confidence': score
            }
        
        except Exception as e:
            logger.warning(f"[NLI] Error in NLI detection: {e}")
            return {'stance': 'NEUTRAL', 'confidence': 0.3}
    
    def _detect_pattern_based(self, fact: str, claim: str) -> Dict:
        """
        Fallback pattern-based stance detection.
        Looks for contradictions, confirmations, negations.
        """
        fact_lower = fact.lower()
        claim_lower = claim.lower()
        
        # Extract key words from claim
        claim_words = set(claim_lower.split()) - self._stopwords()
        fact_words = set(fact_lower.split())
        
        # Semantic overlap
        overlap = len(claim_words & fact_words) / max(len(claim_words), 1)
        
        # No topical relation
        if overlap < 0.3:
            return {'stance': 'NEUTRAL', 'confidence': 0.3}
        
        # Check for explicit negation/refutation
        refuting_patterns = [
            r'not\s+(.+)',
            r"doesn't",
            r"isn't",
            r"aren't",
            r"wasn't",
            r"weren't",
            r'deny',
            r'denied',
            r'false',
            r'incorrect',
            r'wrong',
            r'refute',
            r'debunk',
            r'contrary to',
            r'opposite of',
        ]
        
        for pattern in refuting_patterns:
            if re.search(pattern, fact_lower):
                return {'stance': 'REFUTES', 'confidence': 0.75}
        
        # Check for confirmatory language
        support_patterns = [
            r'confirm',
            r'verified',
            r'proven',
            r'true',
            r'accurate',
            r'correct',
            r'research shows',
            r'study found',
            r'evidence',
        ]
        
        for pattern in support_patterns:
            if re.search(pattern, fact_lower):
                return {'stance': 'SUPPORTS', 'confidence': 0.75}
        
        # Check for implicit support (high overlap without negation)
        if overlap > 0.6:
            return {'stance': 'SUPPORTS', 'confidence': 0.6}
        
        return {'stance': 'NEUTRAL', 'confidence': 0.5}
    
    def _stopwords(self) -> set:
        """Common English stopwords."""
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
