"""Sentence-BERT evidence retrieval engine."""

from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import List, Dict
import os

class EvidenceEngine:
    """
    Retrieves evidence from vector database using Sentence-BERT embeddings.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize evidence engine.
        
        Args:
            model_name: SentenceTransformer model identifier
        """
        self.model = SentenceTransformer(model_name)
        self.pinecone_index = None
        self._init_pinecone()
    
    def _init_pinecone(self):
        """Initialize Pinecone vector database."""
        try:
            import pinecone
            
            api_key = os.getenv("PINECONE_API_KEY", "")
            environment = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")
            
            if api_key:
                pinecone.init(api_key=api_key, environment=environment)
                self.pinecone_index = pinecone.Index("truthlens-evidence")
        except Exception as e:
            print(f"Pinecone initialization warning: {e}")
            self.pinecone_index = None
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        return self.model.encode(text, convert_to_numpy=True)
    
    def retrieve_evidence(self, claim: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve evidence for a claim.
        
        Args:
            claim: Claim text to verify
            top_k: Number of evidence articles to retrieve
            
        Returns:
            List of evidence sources
        """
        # Generate embedding
        embedding = self.get_embedding(claim).tolist()
        
        # Query Pinecone
        if self.pinecone_index:
            try:
                results = self.pinecone_index.query(
                    vector=embedding,
                    top_k=top_k,
                    include_metadata=True
                )
                
                evidence = []
                for match in results.get("matches", []):
                    metadata = match.get("metadata", {})
                    evidence.append({
                        "name": metadata.get("source_name", "Unknown"),
                        "url": metadata.get("url", ""),
                        "relevance": round(match.get("score", 0) * 100, 2),
                        "supports": self._determine_support(claim, metadata.get("text", "")),
                        "text": metadata.get("text", "")[:200]  # Preview
                    })
                
                return evidence
            except Exception as e:
                print(f"Pinecone query error: {e}")
        
        # Fallback: Return mock evidence
        return self._get_mock_evidence(claim)
    
    def _determine_support(self, claim: str, evidence_text: str) -> str:
        """Determine if evidence confirms, contradicts, or is neutral."""
        claim_emb = self.get_embedding(claim)
        evidence_emb = self.get_embedding(evidence_text)
        
        similarity = util.cos_sim(claim_emb, evidence_emb)[0][0].item()
        
        if similarity > 0.7:
            return "CONFIRMS"
        elif similarity < 0.3:
            return "CONTRADICTS"
        else:
            return "NEUTRAL"
    
    def _get_mock_evidence(self, claim: str) -> List[Dict]:
        """Get mock evidence for demonstration."""
        return [
            {
                "name": "Reuters",
                "url": "https://reuters.com/fact-check",
                "relevance": 85,
                "supports": "CONFIRMS",
                "text": "Verified: No evidence of microchips in vaccines..."
            },
            {
                "name": "WHO",
                "url": "https://who.int",
                "relevance": 92,
                "supports": "CONFIRMS",
                "text": "WHO statement confirming vaccine safety..."
            },
            {
                "name": "Snopes",
                "url": "https://snopes.com",
                "relevance": 78,
                "supports": "CONFIRMS",
                "text": "Debunked: Microchip conspiracy theories..."
            }
        ]
