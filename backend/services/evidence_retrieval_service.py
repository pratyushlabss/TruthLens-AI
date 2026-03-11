"""Enhanced evidence retrieval service with vector database support."""

import logging
from typing import List, Dict, Optional, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import json
from pathlib import Path
import pickle
from datetime import datetime

logger = logging.getLogger(__name__)


class EvidenceRetrievalService:
    """Retrieves relevant evidence from vector database."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", use_faiss: bool = True):
        """
        Initialize evidence retrieval service.

        Args:
            model_name: Sentence transformer model name
            use_faiss: Use FAISS for local vector search
        """
        self.use_faiss = use_faiss
        self.embedding_model = SentenceTransformer(model_name)
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        self.faiss_index = None
        self.evidence_store = []
        self.pinecone_client = None

        logger.info(f"Initialized evidence retrieval with {model_name}")

        # Load or create FAISS index
        if self.use_faiss:
            self._init_faiss_index()

        # Try to initialize Pinecone as fallback
        try:
            from pinecone import Pinecone

            self.pinecone_client = Pinecone(api_key="sk-mock")
            logger.info("Initialized Pinecone as backup")
        except Exception as e:
            logger.warning(f"Pinecone initialization failed: {e}")

    def _init_faiss_index(self):
        """Initialize FAISS index for local vector search."""
        try:
            # Load existing index if available
            index_path = Path(__file__).parent.parent / "data" / "evidence_index.faiss"
            store_path = Path(__file__).parent.parent / "data" / "evidence_store.pkl"

            if index_path.exists():
                self.faiss_index = faiss.read_index(str(index_path))
                with open(store_path, "rb") as f:
                    self.evidence_store = pickle.load(f)
                logger.info(f"Loaded FAISS index with {len(self.evidence_store)} items")
            else:
                # Create new index
                self.faiss_index = faiss.IndexFlatL2(self.embedding_dim)
                logger.info("Created new FAISS index")

        except Exception as e:
            logger.error(f"FAISS initialization error: {e}")
            self.use_faiss = False

    def save_faiss_index(self):
        """Save FAISS index to disk."""
        try:
            data_dir = Path(__file__).parent.parent / "data"
            data_dir.mkdir(exist_ok=True)

            index_path = data_dir / "evidence_index.faiss"
            store_path = data_dir / "evidence_store.pkl"

            faiss.write_index(self.faiss_index, str(index_path))
            with open(store_path, "wb") as f:
                pickle.dump(self.evidence_store, f)

            logger.info("Saved FAISS index to disk")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")

    def add_evidence(self, evidence_list: List[Dict]):
        """
        Add evidence to retrieval service.

        Args:
            evidence_list: List of evidence dictionaries with 'text', 'source', 'url'
        """
        if not evidence_list:
            return

        logger.info(f"Adding {len(evidence_list)} evidence items")

        # Generate embeddings
        texts = [e.get("text", "") for e in evidence_list]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        embeddings = embeddings.astype("float32")

        # Add to FAISS if enabled
        if self.use_faiss and self.faiss_index is not None:
            self.faiss_index.add(embeddings)

            # Store metadata
            for i, evidence in enumerate(evidence_list):
                self.evidence_store.append(
                    {
                        "text": evidence.get("text", ""),
                        "source": evidence.get("source", ""),
                        "url": evidence.get("url", ""),
                        "credibility": evidence.get("credibility", 0.5),
                        "added_at": datetime.utcnow().isoformat(),
                    }
                )

            self.save_faiss_index()
            logger.info(f"Evidence store now has {len(self.evidence_store)} items")

    def search_evidence(
        self,
        query: str,
        top_k: int = 10,
        min_credibility: float = 0.5,
    ) -> List[Dict]:
        """
        Search for relevant evidence.

        Args:
            query: Search query
            top_k: Number of results to return
            min_credibility: Minimum credibility score

        Returns:
            List of relevant evidence items
        """
        logger.info(f"Searching for evidence: {query}")

        results = []

        # Try FAISS first if available
        if self.use_faiss and self.faiss_index is not None:
            results = self._search_faiss(query, top_k, min_credibility)

        # Fallback to mock if needed
        if not results:
            results = self._search_mock(query, top_k)

        logger.info(f"Found {len(results)} relevant evidence items")
        return results

    def _search_faiss(
        self, query: str, top_k: int = 10, min_credibility: float = 0.5
    ) -> List[Dict]:
        """
        Search using FAISS index.

        Args:
            query: Search query
            top_k: Number of results
            min_credibility: Minimum credibility threshold

        Returns:
            List of evidence items
        """
        if not self.evidence_store:
            logger.warning("Evidence store is empty")
            return []

        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(
                [query], show_progress_bar=False
            )
            query_embedding = query_embedding.astype("float32")

            # Search
            distances, indices = self.faiss_index.search(query_embedding, top_k * 2)

            # Extract results
            results = []
            for idx in indices[0]:
                if idx < len(self.evidence_store):
                    evidence = self.evidence_store[idx].copy()
                    credibility = evidence.get("credibility", 0.5)

                    if credibility >= min_credibility:
                        # Calculate relevance score (inverse of distance)
                        distance = distances[0][list(indices[0]).index(idx)]
                        relevance = 1 / (1 + distance)
                        evidence["relevance_score"] = float(relevance)
                        results.append(evidence)

                    if len(results) >= top_k:
                        break

            return results

        except Exception as e:
            logger.error(f"FAISS search error: {e}")
            return []

    def _search_mock(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Mock search for demonstration.

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of mock evidence items
        """
        mock_evidence = [
            {
                "text": f"Factual article about {query}",
                "source": "Reuters",
                "url": "https://reuters.com/article",
                "credibility": 0.98,
                "relevance_score": 0.95,
                "added_at": datetime.utcnow().isoformat(),
            },
            {
                "text": f"News report regarding {query}",
                "source": "BBC",
                "url": "https://bbc.com/news",
                "credibility": 0.96,
                "relevance_score": 0.87,
                "added_at": datetime.utcnow().isoformat(),
            },
            {
                "text": f"Analysis of {query} situation",
                "source": "AP",
                "url": "https://apnews.com",
                "credibility": 0.97,
                "relevance_score": 0.82,
                "added_at": datetime.utcnow().isoformat(),
            },
        ]

        return mock_evidence[:top_k]

    def calculate_evidence_score(self, evidence_items: List[Dict]) -> float:
        """
        Calculate aggregate evidence score.

        Args:
            evidence_items: List of evidence items

        Returns:
            Aggregate credibility score (0-1)
        """
        if not evidence_items:
            return 0.5

        credibility_scores = [e.get("credibility", 0.5) for e in evidence_items]
        relevance_scores = [e.get("relevance_score", 0.5) for e in evidence_items]

        # Weighted average
        aggregate = sum(
            c * r for c, r in zip(credibility_scores, relevance_scores)
        ) / sum(relevance_scores)

        return min(max(aggregate, 0), 1)  # Clamp to [0, 1]

    def retrieve_supporting_evidence(
        self, claim: str, top_k: int = 5
    ) -> List[Dict]:
        """
        Retrieve supporting evidence for a claim.

        Args:
            claim: Claim to find evidence for
            top_k: Number of results

        Returns:
            List of supporting evidence
        """
        evidence = self.search_evidence(claim, top_k)

        for item in evidence:
            # In production, this would use semantic similarity
            item["direction"] = "supporting"
            item["similarity"] = 0.85

        return evidence

    def retrieve_contradicting_evidence(
        self, claim: str, top_k: int = 5
    ) -> List[Dict]:
        """
        Retrieve contradicting evidence for a claim.

        Args:
            claim: Claim to find contradictions for
            top_k: Number of results

        Returns:
            List of contradicting evidence
        """
        # In production, this would search with negation
        evidence = self.search_evidence(f"NOT {claim}", top_k)

        for item in evidence:
            item["direction"] = "contradicting"
            item["similarity"] = 0.72

        return evidence

    def clear_index(self):
        """Clear all evidence from index."""
        self.faiss_index = faiss.IndexFlatL2(self.embedding_dim)
        self.evidence_store = []
        self.save_faiss_index()
        logger.info("Cleared evidence index")

    def get_index_stats(self) -> Dict:
        """Get statistics about the index."""
        return {
            "total_evidence_items": len(self.evidence_store) if self.evidence_store else 0,
            "index_type": "FAISS" if self.use_faiss else "Mock",
            "embedding_dimension": self.embedding_dim,
            "sources": (
                list(set(e.get("source", "") for e in self.evidence_store))
                if self.evidence_store
                else []
            ),
        }
