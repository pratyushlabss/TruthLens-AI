"""
TruthLens Backend - Package initialization
"""

from app.services.nlp_analyzer import analyze_with_nlp, generate_embeddings
from app.services.image_processor import process_image
from app.services.web_scraper import scrape_url
from app.services.evidence_retriever import query_pinecone

__all__ = [
    'analyze_with_nlp',
    'generate_embeddings',
    'process_image',
    'scrape_url',
    'query_pinecone'
]
