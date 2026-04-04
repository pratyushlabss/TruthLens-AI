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


class RankingError(Exception):
    """Raised when ranking fails."""


class SentenceTransformerEmbedder:
    """Handles text embeddings using SentenceTransformer."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        """Initialize embedder with transformer model."""
        self.model_name = model_name
        self.device = device
        self._embedding_cache = {}
        self._cache_order = []
        self._cache_max = 5000
        # Re-ranking weights for intent-aware evaluation
        self.weight_semantic = 0.35
        self.weight_keyword = 0.25
        self.weight_entity = 0.20
        self.weight_relevance = 0.20
        try:
            self.model = SentenceTransformer(model_name, device=device)
            logger.info(f"Loaded embedder: {model_name} on {device}")
        except Exception as e:
            logger.error(f"Failed to load embedder: {e}")
            raise RankingError(str(e))

    def _get_cached_embedding(self, text: str) -> np.ndarray:
        return self._embedding_cache.get(text)

    def _store_embedding(self, text: str, embedding: np.ndarray) -> None:
        if text in self._embedding_cache:
            return
        self._embedding_cache[text] = embedding
        self._cache_order.append(text)
        if len(self._cache_order) > self._cache_max:
            oldest = self._cache_order.pop(0)
            self._embedding_cache.pop(oldest, None)
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Embed multiple texts using the model."""
        if not texts:
            raise RankingError("No texts provided")
        try:
            cached = []
            missing = []
            missing_indices = []
            for idx, text in enumerate(texts):
                cached_emb = self._get_cached_embedding(text)
                if cached_emb is None:
                    missing.append(text)
                    missing_indices.append(idx)
                    cached.append(None)
                else:
                    cached.append(cached_emb)

            if missing:
                new_embeddings = self.model.encode(
                    missing,
                    batch_size=batch_size,
                    convert_to_numpy=True,
                    show_progress_bar=False
                )
                for idx, text in enumerate(missing):
                    self._store_embedding(text, new_embeddings[idx])
                for slot, emb in zip(missing_indices, new_embeddings):
                    cached[slot] = emb

            return np.vstack(cached)
        except Exception as e:
            logger.error(f"Error embedding texts: {e}")
            raise RankingError(str(e))
    
    def _normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        """Normalize similarity scores to 0-1 range."""
        if scores.size == 0:
            return scores
        min_val = float(np.min(scores))
        max_val = float(np.max(scores))
        if max_val - min_val < 1e-6:
            return np.clip(scores, 0.0, 1.0)
        normalized = (scores - min_val) / (max_val - min_val)
        return np.clip(normalized, 0.0, 1.0)

    def _penalize_weak_matches(self, normalized: np.ndarray, raw: np.ndarray) -> np.ndarray:
        """Penalize weak raw matches to reduce noisy evidence."""
        if normalized.size == 0:
            return normalized
        penalties = np.where(raw < 0.35, 0.6, 1.0)
        penalties = np.where(raw < 0.25, 0.3, penalties)
        return np.clip(normalized * penalties, 0.0, 1.0)
    
    def _extract_keywords(self, text: str, num_keywords: int = 5) -> List[str]:
        """
        Extract noun phrases/keywords from text for keyword matching.
        
        Uses simple heuristic: keep capitalized words + nouns.
        Falls back to splitting if NLTK not available.
        """
        try:
            import nltk
            from nltk import pos_tag, word_tokenize
            
            try:
                tokens = word_tokenize(text)
                pos_tagged = pos_tag(tokens)
                
                # Extract noun phrases
                keywords = [
                    word for word, pos in pos_tagged 
                    if pos.startswith('NN') or pos.startswith('NNP')
                ]
                return keywords[:num_keywords] if keywords else text.split()[:num_keywords]
            except:
                # NLTK not fully initialized
                return text.split()[:num_keywords]
        except:
            # NLTK not available, use simple split
            return text.split()[:num_keywords]
    
    def rerank_by_intent(self, sentences: List[str], claim: str, entity: str, intent: str) -> List[Dict]:
        """
        MULTI-SIGNAL RE-RANKING: Combine 4 weighted signals for evidence ranking.
        
        Signals:
        1. Semantic similarity (SBERT): 35% weight
        2. Keyword matching (TF-based): 25% weight
        3. Entity presence: 20% weight
        4. Intent-specific relevance: 20% weight
        
        Returns: Sorted list of dicts with score breakdown
        """
        if not sentences:
            return []
        
        try:
            # Get claim/entity embeddings
            claim_emb = self.model.encode(claim, convert_to_numpy=True)
            entity_emb = self.model.encode(entity, convert_to_numpy=True)
            
            # Get sentence embeddings
            sentence_embs = self.embed_texts(sentences, batch_size=32)
            
            # Extract keywords from claim and entity
            claim_keywords = set(word.lower() for word in self._extract_keywords(claim))
            entity_keywords = set(word.lower() for word in self._extract_keywords(entity))
            all_keywords = claim_keywords | entity_keywords
            
            ranked = []
            for idx, (sentence, sent_emb) in enumerate(zip(sentences, sentence_embs)):
                # Signal 1: Semantic similarity
                semantic_sim = float(np.dot(claim_emb, sent_emb) / (
                    np.linalg.norm(claim_emb) * np.linalg.norm(sent_emb) + 1e-8
                ))
                semantic_sim = np.clip(semantic_sim, 0.0, 1.0)
                
                # Signal 2: Keyword matching
                sentence_words = set(word.lower() for word in sentence.split())
                keyword_matches = len(sentence_words & all_keywords)
                keyword_score = min(1.0, keyword_matches / max(1, len(all_keywords)))
                
                # Signal 3: Entity presence (binary)
                entity_present = 1.0 if entity.lower() in sentence.lower() else 0.0
                
                # Signal 4: Intent-specific relevance
                relevance_score = self._compute_intent_relevance(sentence, intent)
                
                # Combine signals
                combined_score = (
                    self.weight_semantic * semantic_sim +
                    self.weight_keyword * keyword_score +
                    self.weight_entity * entity_present +
                    self.weight_relevance * relevance_score
                )
                
                ranked.append({
                    'sentence': sentence,
                    'score': float(combined_score),
                    'semantic_similarity': float(semantic_sim),
                    'keyword_score': float(keyword_score),
                    'entity_present': float(entity_present),
                    'relevance_score': float(relevance_score),
                })
            
            # Sort by combined score
            ranked.sort(key=lambda x: x['score'], reverse=True)
            logger.debug(f"[Ranking] Re-ranked {len(ranked)} sentences for {intent} intent")
            return ranked
            
        except Exception as e:
            logger.error(f"Re-ranking failed: {e}")
            # Fallback: return with basic similarity scores
            return [{'sentence': s, 'score': 0.5} for s in sentences]
    
    def _compute_intent_relevance(self, sentence: str, intent: str) -> float:
        """
        Compute relevance score for intent-specific signals.
        
        High score if sentence matches patterns typical for the intent type.
        """
        sentence_lower = sentence.lower()
        
        if intent == "life_status":
            # High relevance for current status, present tense
            status_patterns = {'alive', 'dead', 'living', 'is', 'remains', 'current', 'today', '2024'}
            matches = sum(1 for p in status_patterns if p in sentence_lower)
            return min(1.0, matches / max(1, len(status_patterns)))
        
        elif intent == "historical":
            # High relevance for past events, dates, founding
            historical_patterns = {'founded', 'established', 'created', 'won', 'elected', '19', '20'}
            matches = sum(1 for p in historical_patterns if p in sentence_lower)
            return min(1.0, matches / max(1, len(historical_patterns)))
        
        else:  # general
            # General relevance (not very discriminative)
            return 0.5


    def rank_by_similarity(self, query: str, sentences: List[str], top_k: int = 5) -> Dict:
        """Rank sentences by similarity to query with normalization."""
        if not sentences or not query:
            raise RankingError("Query and sentences are required")
        
        try:
            query_emb = self.model.encode([query], convert_to_numpy=True)
            text_emb = self.embed_texts(sentences)
            
            similarities = cosine_similarity(query_emb, text_emb)[0]
            normalized = self._normalize_scores(similarities)
            penalized = self._penalize_weak_matches(normalized, similarities)
            top_indices = np.argsort(penalized)[::-1][:min(top_k, len(sentences))]
            
            return {
                "ranked_evidence": [sentences[i] for i in top_indices],
                "similarity_scores": penalized[top_indices].tolist(),
                "indices": top_indices.tolist(),
                "mean_similarity": float(np.mean(penalized[top_indices])),
                "raw_similarity_scores": similarities[top_indices].tolist()
            }
        except Exception as e:
            logger.error(f"Error ranking sentences: {e}")
            raise RankingError(str(e))

    def compute_similarity_scores(self, query: str, sentences: List[str]) -> List[float]:
        """Compute normalized similarity scores for all sentences."""
        if not sentences or not query:
            raise RankingError("Query and sentences are required")
        try:
            query_emb = self.model.encode([query], convert_to_numpy=True)
            text_emb = self.embed_texts(sentences)
            similarities = cosine_similarity(query_emb, text_emb)[0]
            normalized = self._normalize_scores(similarities)
            return normalized.tolist()
        except Exception as e:
            logger.error(f"Error computing similarity scores: {e}")
            raise RankingError(str(e))

    def compute_ranking_confidence(self, scores: List[float], strategy: str = "mean") -> float:
        """Compute confidence from similarity scores."""
        if not scores:
            raise RankingError("No scores provided")
        if strategy == "median":
            return float(np.median(scores))
        if strategy == "max":
            return float(np.max(scores))
        return float(np.mean(scores))

    def rank_and_score(self, query: str, sentences: List[str], top_k: int = 5) -> Dict:
        """Rank sentences and return a confidence score."""
        result = self.rank_by_similarity(query, sentences, top_k)
        confidence = self.compute_ranking_confidence(result["similarity_scores"], strategy="mean")
        result["confidence"] = confidence
        return result


class RankingPipeline:
    """Orchestrates evidence ranking."""
    
    def __init__(self, embedder: SentenceTransformerEmbedder = None, embedder_model: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        """Initialize ranking pipeline."""
        self.embedder = embedder or SentenceTransformerEmbedder(embedder_model, device)
    
    def rank_evidence(self, query: str, evidence_list: List[str], top_k: int = 5) -> Dict:
        """Rank evidence list and return results."""
        return self.embedder.rank_by_similarity(query, evidence_list, top_k)
