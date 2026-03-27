"""
[11] REASONING ENGINE - Logical inference rules for verdict determination
"""

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class ReasoningEngine:
    """
    Apply logical inference rules to facts, stances, and evidence.
    Handles multi-step reasoning, contradiction detection, temporal inference.
    """
    
    def __init__(self):
        """Initialize reasoning engine."""
        logger.info("[REASONING] Engine initialized")
    
    def reason(self, facts: List[Dict], claim: str, stances: Dict) -> Dict:
        """
        Apply inference rules to determine verdict.
        
        Args:
            facts: List of extracted facts with metadata
            claim: Original claim to verify
            stances: Dict mapping fact_id → stance {'stance': 'SUPPORTS'|'REFUTES'|'NEUTRAL', 'confidence': float}
            
        Returns:
            {
                'inference': str (reasoning path),
                'logic_chain': List[str] (step-by-step reasoning),
                'confidence_adjustment': float (-0.3 to +0.3),
                'verdict_override': str or None ('TRUE'|'FALSE'|None)
            }
        """
        
        if not facts:
            return {
                'inference': 'No facts available for reasoning',
                'logic_chain': ['No facts to analyze'],
                'confidence_adjustment': 0.0,
                'verdict_override': None
            }
        
        logic_chain = []
        
        # Step 1: Count stances
        support_count, refute_count, neutral_count = self._count_stances(stances)
        total = support_count + refute_count  # Ignore neutral for count
        
        logic_chain.append(f"Stance distribution: {support_count} SUPPORT, {refute_count} REFUTE, {neutral_count} NEUTRAL")
        
        # Step 2: Detect strong primary signal
        if refute_count >= total * 0.7 and total > 0:
            logic_chain.append("🚨 Strong refutation signal detected (70%+ articles contradict claim)")
            return {
                'inference': 'Multiple sources directly contradict the claim',
                'logic_chain': logic_chain,
                'confidence_adjustment': +0.25,
                'verdict_override': 'FALSE'
            }
        
        if support_count >= total * 0.7 and total > 0:
            logic_chain.append("✅ Strong support signal detected (70%+ articles confirm claim)")
            return {
                'inference': 'Multiple sources directly confirm the claim',
                'logic_chain': logic_chain,
                'confidence_adjustment': +0.25,
                'verdict_override': 'TRUE'
            }
        
        # Step 3: Detect indirect contradictions (e.g., "person is dead" vs recent activity)
        indirect_inference = self._check_indirect_contradiction(facts, claim)
        if indirect_inference:
            logic_chain.append(indirect_inference['reasoning'])
            return {
                'inference': indirect_inference['reasoning'],
                'logic_chain': logic_chain,
                'confidence_adjustment': indirect_inference['adjustment'],
                'verdict_override': indirect_inference['override']
            }
        
        # Step 4: Check for temporal shifts (outdated claim)
        temporal_inference = self._check_temporal_logic(facts, claim)
        if temporal_inference:
            logic_chain.append(temporal_inference['reasoning'])
            return {
                'inference': temporal_inference['reasoning'],
                'logic_chain': logic_chain,
                'confidence_adjustment': temporal_inference['adjustment'],
                'verdict_override': temporal_inference['override']
            }
        
        # Step 5: Consistency check (conflicting verses)
        if self._has_internal_conflict(facts):
            logic_chain.append("⚠️ Conflicting evidence detected - data sources disagree")
            return {
                'inference': 'Sources provide conflicting information - requires further investigation',
                'logic_chain': logic_chain,
                'confidence_adjustment': -0.15,
                'verdict_override': None
            }
        
        # Step 6: No strong signal
        logic_chain.append("No decisive inference pattern found")
        return {
            'inference': 'Insufficient evidence for definitive reasoning',
            'logic_chain': logic_chain,
            'confidence_adjustment': 0.0,
            'verdict_override': None
        }
    
    def _count_stances(self, stances: Dict) -> Tuple[int, int, int]:
        """Count support/refute/neutral stances."""
        support = sum(1 for s in stances.values() if s.get('stance') == 'SUPPORTS')
        refute = sum(1 for s in stances.values() if s.get('stance') == 'REFUTES')
        neutral = sum(1 for s in stances.values() if s.get('stance') == 'NEUTRAL')
        return support, refute, neutral
    
    def _check_indirect_contradiction(self, facts: List[Dict], claim: str) -> Dict or None:
        """
        Detect indirect contradictions (e.g., "person X is dead" vs "person X spoke yesterday").
        """
        claim_lower = claim.lower()
        
        # Pattern: "X is dead" or "X died"
        if any(pattern in claim_lower for pattern in [' is dead', ' died', ' has died', ' was killed']):
            # Look for recent activity
            activity_keywords = ['spoke', 'said', 'announced', 'posted', 'tweeted', 'appeared', 
                                'held', 'attended', 'visited', 'met', 'released', 'published',
                                'today', 'yesterday', 'recent', 'latest', '2024', '2025']
            
            for fact in facts:
                fact_text = fact.get('text', '').lower() if isinstance(fact, dict) else str(fact).lower()
                # If recent activity found, this contradicts death claim
                if any(kw in fact_text for kw in activity_keywords):
                    return {
                        'reasoning': 'Claims person is dead, but recent activity evidence suggests person is alive',
                        'adjustment': +0.2,
                        'override': 'FALSE'
                    }
        
        # Pattern: "X has Y disease" vs "X is healthy/recovered"
        if any(kw in claim_lower for kw in ['has cancer', 'has aids', 'has covid', 'is sick']):
            recovery_keywords = ['recovered', 'cured', 'healthy', 'virus-free', 'clear of']
            for fact in facts:
                fact_text = fact.get('text', '').lower() if isinstance(fact, dict) else str(fact).lower()
                if any(kw in fact_text for kw in recovery_keywords):
                    return {
                        'reasoning': 'Claim about disease contradicted by recovery evidence',
                        'adjustment': +0.15,
                        'override': 'FALSE'
                    }
        
        return None
    
    def _check_temporal_logic(self, facts: List[Dict], claim: str) -> Dict or None:
        """
        Check temporal consistency (e.g., old claims should be reassessed with recent data).
        """
        claim_lower = claim.lower()
        
        # Pattern: "X will happen" or "X might happen"
        if any(pattern in claim_lower for pattern in [' will ', ' might ', ' could ', ' may ']):
            # Check if future event already happened
            past_tense_keywords = ['actually', 'happened', 'already', 'occurred', 'took place', 'happened on', 
                                   'on date', 'this week', 'last week', 'ago']
            
            for fact in facts:
                fact_text = fact.get('text', '').lower() if isinstance(fact, dict) else str(fact).lower()
                if any(kw in fact_text for kw in past_tense_keywords):
                    return {
                        'reasoning': 'Future prediction claim contradicted by past-tense evidence',
                        'adjustment': +0.15,
                        'override': 'FALSE'
                    }
        
        return None
    
    def _has_internal_conflict(self, facts: List[Dict]) -> bool:
        """
        Check if facts contain contradictory statements.
        """
        if len(facts) < 2:
            return False
        
        # Simple heuristic: check for negation in one fact vs assertion in another
        for i, fact1 in enumerate(facts):
            text1 = fact1.get('text', '').lower() if isinstance(fact1, dict) else str(fact1).lower()
            
            # Words that appear in fact1
            words1 = set(text1.split())
            
            # Look for contradictory patterns
            if 'not' in words1 or 'never' in words1 or 'false' in words1:
                for fact2 in facts[i+1:]:
                    text2 = fact2.get('text', '').lower() if isinstance(fact2, dict) else str(fact2).lower()
                    words2 = set(text2.split())
                    
                    # If fact2 makes positive statement with similar keywords
                    overlap = len(words1 & words2)
                    if overlap > 3:  # Sufficient semantic overlap
                        if 'not' not in text2 and 'false' not in text2:
                            return True  # Conflict found
        
        return False
