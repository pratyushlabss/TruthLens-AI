"""Production utilities for RAG pipeline."""
import re
import logging
from typing import List, Dict
import numpy as np

try:
    from nltk.tokenize import sent_tokenize
except ImportError:
    import nltk
    nltk.download("punkt", quiet=True)
    from nltk.tokenize import sent_tokenize

logger = logging.getLogger(__name__)


def extract_sentences(text: str, min_length: int = 15) -> List[str]:
    """Extract sentences from text using NLTK tokenizer."""
    if not text:
        return []
    try:
        sents = sent_tokenize(text)
        return [s.strip() for s in sents if len(s.strip()) >= min_length]
    except Exception as e:
        logger.warning(f"Error extracting sentences: {e}")
        return []


def clean_text(text: str) -> str:
    """Clean text by removing HTML, normalizing whitespace."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def format_evidence_dict(
    sentence: str,
    source_url: str,
    source_title: str,
    similarity_score: float = 0.0,
    nli_scores: Dict = None
) -> Dict:
    """Format evidence into standardized dictionary."""
    if nli_scores is None:
        nli_scores = {"entailment": 0.0, "contradiction": 0.0, "neutral": 1.0}
    
    return {
        "sentence": sentence,
        "source": source_title,
        "url": source_url,
        "similarity_score": float(similarity_score),
        "nli_entailment": float(nli_scores.get("entailment", 0.0)),
        "nli_contradiction": float(nli_scores.get("contradiction", 0.0)),
        "nli_neutral": float(nli_scores.get("neutral", 0.0))
    }
