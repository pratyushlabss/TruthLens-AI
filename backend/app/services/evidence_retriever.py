"""
Evidence Retrieval Service - Query Pinecone for similar evidence
Retrieves fact-checking and corroborating evidence sources
"""

import os
import requests
from typing import List, Dict, Any, Optional

PINECONE_KEY = os.getenv('PINECONE_KEY', 'pcsk_4GpH3o_LT2E8HvMKk1n2eR3ZAbFqiFD3xS5TxxMcDYujatBNZvcMYpvzrZP3dGj9qeHj9p')
PINECONE_API_URL = 'https://api.pinecone.io/indexes/truthlens-evidence/vectors/query'

def query_pinecone(
    embedding: List[float],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Query Pinecone for similar evidence documents
    Returns: list of evidence sources with relevance scores
    """
    if not PINECONE_KEY:
        print('Warning: PINECONE_KEY not configured, skipping evidence retrieval')
        return []
    
    try:
        response = requests.post(
            PINECONE_API_URL,
            headers={
                'Api-Key': PINECONE_KEY,
                'Content-Type': 'application/json'
            },
            json={
                'vector': embedding,
                'topK': top_k,
                'includeMetadata': True
            },
            timeout=30
        )
        
        if not response.ok:
            print(f'Pinecone query failed: {response.status_code}')
            return []
        
        data = response.json()
        
        # Parse matches
        evidence_sources = []
        if 'matches' in data:
            for match in data['matches']:
                metadata = match.get('metadata', {})
                evidence_sources.append({
                    'name': metadata.get('source_name', 'Unknown Source'),
                    'url': metadata.get('url'),
                    'relevance': round((match.get('score', 0) or 0) * 100),
                    'supports': metadata.get('supports', 'NEUTRAL')
                })
        
        return evidence_sources
        
    except Exception as e:
        print(f'Pinecone evidence retrieval error: {str(e)}')
        return []

def mock_evidence_sources() -> List[Dict[str, Any]]:
    """
    Return mock evidence sources for testing
    """
    return [
        {
            'name': 'Reuters Fact Check',
            'url': 'https://reuters.com',
            'relevance': 85,
            'supports': 'CONFIRMS'
        },
        {
            'name': 'Snopes',
            'url': 'https://snopes.com',
            'relevance': 72,
            'supports': 'CONTRADICTS'
        }
    ]
