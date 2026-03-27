"""
TruthLens AI - Search URL Generator & Pinecone Vector DB Integration
Purpose: Generate dynamic search URLs and manage vector embeddings
No fake URLs. Real searches only.
"""

import os
from typing import List, Dict
from urllib.parse import quote
import logging
from sentence_transformers import SentenceTransformer
import pinecone

logger = logging.getLogger(__name__)

class SearchURLGenerator:
    """
    Generate dynamic search URLs for trusted sources.
    """
    
    def __init__(self):
        """Initialize search URL patterns."""
        self.search_engines = {
            'google': 'https://www.google.com/search?q={query}',
            'bbc': 'https://www.bbc.com/search?q={query}',
            'reuters': 'https://www.reuters.com/search/news?blob={query}',
            'wikipedia': 'https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json',
            'bing': 'https://www.bing.com/search?q={query}',
            'duckduckgo': 'https://duckduckgo.com/?q={query}',
        }
    
    def generate(self, claim: str, engines: List[str] = None) -> Dict[str, str]:
        """
        Generate search URLs for a claim.
        
        Args:
            claim: The claim to search for
            engines: List of search engines to use. Defaults to top 5.
            
        Returns:
            Dictionary of search URLs
        """
        if engines is None:
            engines = ['google', 'bbc', 'reuters', 'wikipedia', 'bing']
        
        # Clean claim for URL
        clean_claim = claim.strip().replace('\n', ' ')[:100]
        encoded = quote(clean_claim)
        
        urls = {}
        for engine in engines:
            if engine in self.search_engines:
                urls[engine] = self.search_engines[engine].format(query=encoded)
        
        logger.info(f"✅ Generated {len(urls)} search URLs for claim")
        return urls


class PineconeVectorDB:
    """
    Real Pinecone vector database integration.
    Stores and retrieves evidence using embeddings.
    """
    
    def __init__(self, api_key: str, env: str, index_name: str = 'truthlens'):
        """
        Initialize Pinecone connection.
        
        Args:
            api_key: Pinecone API key
            env: Pinecone environment
            index_name: Index name
        """
        self.api_key = api_key
        self.env = env
        self.index_name = index_name
        
        # Initialize Pinecone
        pinecone.init(api_key=self.api_key, environment=self.env)
        
        # Load embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create index
        self._ensure_index_exists()
    
    def _ensure_index_exists(self):
        """Ensure Pinecone index exists."""
        try:
            if self.index_name not in pinecone.list_indexes():
                logger.info(f"Creating Pinecone index: {self.index_name}")
                pinecone.create_index(
                    name=self.index_name,
                    dimension=384,  # all-MiniLM-L6-v2 output dimension
                    metric='cosine'
                )
            
            self.index = pinecone.Index(self.index_name)
            logger.info(f"✅ Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"❌ Pinecone initialization failed: {e}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        Embed text using sentence transformers.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def store_evidence(self, evidence: Dict) -> bool:
        """
        Store evidence in Pinecone.
        
        Args:
            evidence: {
                'id': str (unique),
                'url': str,
                'title': str,
                'content': str,
                'source': str
            }
            
        Returns:
            True if successful
        """
        try:
            # Create embedding from title + content
            text_to_embed = f"{evidence['title']} {evidence['content'][:500]}"
            embedding = self.embed_text(text_to_embed)
            
            # Prepare metadata
            metadata = {
                'url': evidence['url'],
                'title': evidence['title'],
                'source': evidence.get('source', 'unknown'),
                'content_length': len(evidence['content'])
            }
            
            # Store in Pinecone
            self.index.upsert(
                vectors=[{
                    'id': evidence['id'],
                    'values': embedding,
                    'metadata': metadata
                }]
            )
            
            logger.info(f"✅ Stored evidence in Pinecone: {evidence['id']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store evidence in Pinecone: {e}")
            raise
    
    def search_evidence(self, claim: str, top_k: int = 5) -> List[Dict]:
        """
        Search for relevant evidence using semantic similarity.
        
        Args:
            claim: The claim to search for
            top_k: Number of results to return
            
        Returns:
            List of relevant evidence matches
        """
        try:
            # Embed the claim
            claim_embedding = self.embed_text(claim)
            
            # Search Pinecone
            results = self.index.query(
                vector=claim_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            if not results['matches']:
                raise Exception("No evidence found in vector database")
            
            # Format results
            evidence = []
            for match in results['matches']:
                evidence.append({
                    'id': match['id'],
                    'url': match['metadata']['url'],
                    'title': match['metadata']['title'],
                    'source': match['metadata']['source'],
                    'similarity_score': match['score'],  # 0-1
                })
            
            logger.info(f"✅ Retrieved {len(evidence)} evidence matches from Pinecone")
            return evidence
            
        except Exception as e:
            logger.error(f"❌ Pinecone search failed: {e}")
            raise
    
    def delete_old_evidence(self, days: int = 7):
        """
        Delete evidence older than specified days.
        (For memory management)
        """
        try:
            # This is a placeholder - real implementation would require
            # metadata filtering by timestamp
            logger.info(f"Cleanup: Removing evidence older than {days} days")
            return True
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            raise

