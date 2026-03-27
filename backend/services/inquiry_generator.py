"""
[2] INQUIRY GENERATOR - Convert claim → verification questions
"""

import logging
from typing import Dict, List
import re

logger = logging.getLogger(__name__)


class InquiryGenerator:
    """Generate meaningful verification questions from claims."""
    
    def __init__(self):
        """Initialize inquiry patterns."""
        self.patterns = {
            'person_alive': r'(is|are|was|were)\s+(.*?)\s+(dead|died|alive)',
            'person_claim': r'(.*?)\s+(is|are|was|were|claim|said|believe)',
            'event': r'(.*?)\s+(happen|occurred|took place|event)',
            'scientific': r'(.*?)\s+(prove|research|study|fact)',
            'location': r'(.*?)\s+(in|at|located)',
        }
    
    def understand(self, claim: str) -> Dict:
        """Extract entities and patterns from claim."""
        entities = self._extract_entities(claim)
        patterns = self._detect_patterns(claim)
        domain = self._classify_domain(claim)
        
        return {
            'entities': entities,
            'patterns': patterns,
            'domain': domain
        }
    
    def generate_inquiries(self, claim: str, analysis: Dict) -> List[str]:
        """Generate 3-5 verification questions."""
        inquiries = []
        entities = analysis.get('entities', [])
        domain = analysis.get('domain', 'general')
        
        # Pattern 1: Direct verification
        inquiries.append(f"Is it true that {claim}?")
        
        # Pattern 2: Entity-focused
        if entities:
            main_entity = entities[0]
            if domain == 'person':
                inquiries.append(f"What is {main_entity}'s current status?")
                inquiries.append(f"Is {main_entity} alive or dead?")
            elif domain == 'health':
                inquiries.append(f"What is the scientific evidence about {claim.lower()}?")
            elif domain == 'political':
                inquiries.append(f"What are the facts about {main_entity}?")
        
        # Pattern 3: Recent activity
        if domain == 'person':
            inquiries.append(f"Recent news about {entities[0] if entities else 'this'}")
        
        # Pattern 4: Scientific verification
        if domain in ['health', 'science']:
            inquiries.append(f"Research about {claim.lower()}")
        
        # Pattern 5: Fact-check
        inquiries.append(f"{claim} - fact check")
        
        return inquiries[:5]
    
    def _extract_entities(self, claim: str) -> List[str]:
        """Extract potential entities (names, organizations, etc.)."""
        entities = []
        
        # Capitalized words (likely proper nouns)
        capitalized = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', claim)
        entities.extend(capitalized)
        
        # Words in quotes
        quoted = re.findall(r'"([^"]+)"', claim)
        entities.extend(quoted)
        
        return list(set(entities))[:5]
    
    def _detect_patterns(self, claim: str) -> List[str]:
        """Detect claim patterns."""
        patterns = []
        claim_lower = claim.lower()
        
        if any(word in claim_lower for word in ['dead', 'died', 'alive', 'death', 'suicide']):
            patterns.append('mortality_claim')
        
        if any(word in claim_lower for word in ['cure', 'treat', 'vaccine', 'disease', 'medicine']):
            patterns.append('health_claim')
        
        if any(word in claim_lower for word in ['election', 'vote', 'president', 'parliament', 'law']):
            patterns.append('political_claim')
        
        if any(word in claim_lower for word in ['earth', 'moon', 'sun', 'orbit', 'flat', 'round']):
            patterns.append('scientific_claim')
        
        if any(word in claim_lower for word in ['born', 'nationality', 'country', 'citizen']):
            patterns.append('biographical_claim')
        
        return patterns
    
    def _classify_domain(self, claim: str) -> str:
        """Classify claim into domain."""
        claim_lower = claim.lower()
        
        if any(word in claim_lower for word in ['dead', 'died', 'alive', 'person', 'actor', 'president', 'politician']):
            return 'person'
        elif any(word in claim_lower for word in ['vaccine', 'cure', 'disease', 'medicine', 'therapy']):
            return 'health'
        elif any(word in claim_lower for word in ['election', 'vote', 'government', 'law', 'parliament']):
            return 'political'
        elif any(word in claim_lower for word in ['earth', 'moon', 'sun', 'universe', 'physics']):
            return 'science'
        elif any(word in claim_lower for word in ['economy', 'stock', 'business', 'market']):
            return 'economy'
        else:
            return 'general'
