"""
[3] QUERY EXPANSION ENGINE - Generate search variations
"""

import logging
from typing import List
import re

logger = logging.getLogger(__name__)


class QueryExpander:
    """Generate multiple search queries from a claim."""
    
    def expand(self, claim: str, inquiries: List[str]) -> List[str]:
        """Expand into 8-10 search queries."""
        queries = []
        
        # Base query
        queries.append(claim)
        
        # Fact-check variants
        queries.append(f"{claim} fact check")
        queries.append(f"{claim} true or false")
        queries.append(f"{claim} verify")
        
        # News variants
        main_entity = self._extract_main_entity(claim)
        if main_entity:
            queries.append(f"{main_entity} latest news")
            queries.append(f"{main_entity} recent news")
            queries.append(f"{main_entity} today")
            queries.append(f"{main_entity} updates")
        
        # Research/Scientific variants
        queries.append(f"{claim} research")
        queries.append(f"{claim} scientific study")
        
        # Inquiry-based
        for inquiry in inquiries[:3]:
            queries.append(inquiry)
        
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for q in queries:
            q_lower = q.lower()
            if q_lower not in seen and len(q) > 0:
                unique.append(q)
                seen.add(q_lower)
        
        logger.info(f"[QUERY-EXPANSION] Generated {len(unique)} unique queries")
        return unique[:10]  # Return top 10
    
    def _extract_main_entity(self, claim: str) -> str:
        """Extract primary entity (name, topic) from claim."""
        # Capital letters usually indicate proper nouns
        words = claim.split()
        
        for word in words:
            if word[0].isupper() and len(word) > 2:
                return word
        
        # Otherwise, first meaningful noun
        stop_words = {'is', 'are', 'was', 'were', 'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'that', 'this', 'which'}
        
        for word in words:
            if word.lower() not in stop_words:
                return word
        
        return claim[:20]  # Fallback
