"""Embedding-based ranking system for RAG pipeline."""
import logging
from typing import List, Dict, Tuple
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError("sentence-transformers required: pip install sentence-transformers")

from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class SentenceTransformerEmbedder:
    """Handles text embeddings using SentenceTransformer."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        """Initialize embedder with transformer model."""
        self.model_name = model_name
        self.device = device
        try:
            self.model = SentenceTransformer(model_name, device=device)
            logger.info(f"Loaded embedder: {model_name} on {device}")
        except Exception as e:
            logger.error(f"Failed to load embedder: {e}")
            raise
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Embed multiple texts using the model."""
        if not texts:
            return np.array([])
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error embedding texts: {e}")
            raise
    
    def rank_by_similarity(self, query: str, sentences: List[str], top_k: int = 5) -> Dict:
        """Rank sentences by similarity to query."""
        if not sentences or not query:
            return {
                "ranked_evidence": [],
                "similarity_scores": [],
                "indices": [],
                "mean_similarity": 0.0
            }
        
        try:
            query_emb = self.model.encode([query], convert_to_numpy=True)
            text_emb = self.embed_texts(sentences)
            
            similarities = cosine_similarity(query_emb, text_emb)[0]
            top_indices = np.argsort(similarities)[::-1][:min(top_k, len(sentences))]
            
            return {
                "ranked_evidence": [sentences[i] for i in top_indices],
                "similarity_scores": similarities[top_indices].tolist(),
                "indices": top_indices.tolist(),
                "mean_similarity": float(np.mean(similarities[top_indices]))
            }
        except Exception as e:
            logger.error(f"Error ranking sentences: {e}")
            return {
                "ranked_evidence": [],
                "similarity_scores": [],
                "indices": [],
                "mean_similarity": 0.0
            }


class RankingPipeline:
    """Orchestrates evidence ranking."""
    
    def __init__(self, embedder_model: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        """Initialize ranking pipeline."""
        self.embedder = SentenceTransformerEmbedder(embedder_model, device)
    
    def rank_evidence(self, query: str, evidence_list: List[str], top_k: int = 5) -> Dict:
        """Rank evidence list and return results."""
        return self.embedder.rank_by_similarity(query, evidence_list, top_k)
