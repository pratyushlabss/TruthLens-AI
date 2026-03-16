"""
NLP Analysis Service - Text-based misinformation detection
Uses Hugging Face API for text analysis and embeddings
"""

import os
import requests
import json
from typing import Dict, List, Any

HF_TOKEN = os.getenv('HF_TOKEN', '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')
HF_API_URL = 'https://api-inference.huggingface.co/models'

def analyze_with_nlp(text: str) -> Dict[str, Any]:
    """
    Analyze text using RoBERTa-based fake news detector
    Returns: {score: float (0-100), label: str, confidence: float}
    """
    if not HF_TOKEN:
        raise ValueError('HF_TOKEN not configured')
    
    try:
        # Truncate text to avoid token limits
        truncated_text = text[:512]
        
        response = requests.post(
            f'{HF_API_URL}/roberta-base-openai-detector',
            headers={'Authorization': f'Bearer {HF_TOKEN}'},
            json={'inputs': truncated_text},
            timeout=30
        )
        
        if not response.ok:
            raise ValueError(f'HF API error: {response.status_code} - {response.text}')
        
        result = response.json()
        
        # Handle response format
        if isinstance(result, list) and len(result) > 0:
            scores = result[0]
            if isinstance(scores, list) and len(scores) > 0:
                top_result = scores[0]
                is_fake = top_result.get('label', '').lower() == 'fake'
                score = top_result.get('score', 0.5)
                
                # Map to 0-100 scale
                final_score = (score * 100) if is_fake else ((1 - score) * 100)
                final_score = max(0, min(100, final_score))  # Clamp 0-100
                
                return {
                    'score': final_score,
                    'label': top_result.get('label', 'neutral').lower(),
                    'confidence': score
                }
        
        # Fallback if response format unexpected
        return {'score': 50, 'label': 'neutral', 'confidence': 0.5}
        
    except Exception as e:
        print(f'NLP analysis error: {str(e)}')
        raise ValueError(f'NLP analysis failed: {str(e)}')

def generate_embeddings(text: str) -> List[float]:
    """
    Generate embeddings using all-MiniLM-L6-v2
    Returns: list of floats (384-dimensional vector)
    """
    if not HF_TOKEN:
        raise ValueError('HF_TOKEN not configured')
    
    try:
        # Truncate text
        truncated_text = text[:512]
        
        response = requests.post(
            f'{HF_API_URL}/sentence-transformers/all-MiniLM-L6-v2',
            headers={'Authorization': f'Bearer {HF_TOKEN}'},
            json={'inputs': truncated_text},
            timeout=30
        )
        
        if not response.ok:
            raise ValueError(f'Embedding API error: {response.status_code} - {response.text}')
        
        result = response.json()
        
        # Response should be a list of floats
        if isinstance(result, list):
            return result
        
        raise ValueError(f'Unexpected embedding response format: {type(result)}')
        
    except Exception as e:
        print(f'Embedding generation error: {str(e)}')
        raise ValueError(f'Embedding generation failed: {str(e)}')
