"""
[5-6] FACT EXTRACTOR - Split articles into meaningful sentences
"""

import logging
from typing import List
import re

logger = logging.getLogger(__name__)


class FactExtractor:
    """Extract factual sentences from article text."""
    
    def extract(self, text: str, max_facts: int = 20) -> List[str]:
        """
        Extract meaningful sentences from text.
        
        Args:
            text: Article/content text
            max_facts: Maximum facts to extract
            
        Returns:
            List of factual sentences
        """
        
        if not text or len(text) < 20:
            return []
        
        # Split into sentences
        sentences = self._split_sentences(text)
        
        # Filter meaningful sentences
        facts = []
        for sentence in sentences:
            sentence = sentence.strip()
            
            # Skip if too short
            if len(sentence) < 30:
                continue
            
            # Skip common fluff
            if self._is_fluff(sentence):
                continue
            
            # Skip ads/navigation
            if self._is_ad_or_nav(sentence):
                continue
            
            facts.append(sentence)
        
        logger.info(f"[FACT-EXTRACTION] Extracted {len(facts)} facts from {len(text)} chars")
        return facts[:max_facts]
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Remove line breaks and extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Split on periods/exclamation/question marks
        # But handle cases like "Dr.", "U.S.", etc.
        sentence_pattern = r'(?<![.A-Z])[.!?]+(?=\s+[A-Z]|\Z)'
        
        sentences = re.split(sentence_pattern, text)
        
        return [s.strip() for s in sentences if s.strip()]
    
    def _is_fluff(self, sentence: str) -> bool:
        """Check if sentence is just fluff."""
        fluff_patterns = [
            r'(click here|read more|subscribe|sign up|follow us)',
            r'(advertisement|ad|sponsored)',
            r'(recommended|popular|trending|top)',
            r'(share this|like this|comment below)',
        ]
        
        sentence_lower = sentence.lower()
        for pattern in fluff_patterns:
            if re.search(pattern, sentence_lower):
                return True
        
        # Length check
        if len(sentence) < 30 or len(sentence) > 1000:
            return True
        
        return False
    
    def _is_ad_or_nav(self, sentence: str) -> bool:
        """Check if sentence is navigation/ads."""
        patterns = [
            r'(home|about|contact|privacy|terms)',
            r'(menu|navigation|sidebar)',
            r'(advertisement|sponsored content)',
            r'(©|trademark|©)',
        ]
        
        sentence_lower = sentence.lower()
        for pattern in patterns:
            if re.search(pattern, sentence_lower):
                return True
        
        return False
