"""
Comprehensive test suite for new RAG pipeline.
Tests all modules: utils_new, ranking_new, retrieval_new, pipeline_new.
"""

import pytest
import numpy as np
from typing import List

# Import modules to test
from backend.services.utils_new import (
    extract_sentences,
    clean_text,
    deduplicate_evidence,
    format_evidence_dict,
    chunk_text,
    TextProcessingError
)
from backend.services.ranking_new import (
    SentenceTransformerEmbedder,
    RankingPipeline,
    RankingError
)
from backend.services.retrieval_new import (
    QueryExpander,
    WikipediaRetriever,
    RetrievalPipeline,
    RetrievalError
)
from backend.services.pipeline_new import (
    ProductionRAGPipeline,
    StreamlineRAGPipeline,
    RAGPipelineError
)


# ===================== FIXTURES =====================

@pytest.fixture
def sample_text():
    """Sample article text for testing."""
    return """
    The Earth is a sphere. It rotates around the Sun. The Earth has one moon.
    Scientists have confirmed that the Earth is approximately 4.5 billion years old.
    The atmosphere protects us from radiation. Water covers most of the Earth's surface.
    """

@pytest.fixture
def sample_html_text():
    """Sample HTML text for cleaning."""
    return "<p>Hello <b>world</b>! This is a &nbsp; test.</p><div>More text here.</div>"

@pytest.fixture
def sample_sentences():
    """Sample sentences for ranking."""
    return [
        "The Earth is a sphere orbiting the Sun.",
        "The atmosphere contains nitrogen and oxygen.",
        "Water covers approximately 71% of Earth's surface.",
        "The Moon orbits Earth approximately every 27 days.",
        "Gravity keeps objects bound to Earth."
    ]

@pytest.fixture
def embedder():
    """Initialize embedder for tests."""
    return SentenceTransformerEmbedder(device="cpu")

@pytest.fixture
def ranking_pipeline(embedder):
    """Initialize ranking pipeline."""
    return RankingPipeline(embedder=embedder)

@pytest.fixture
def retrieval_pipeline():
    """Initialize retrieval pipeline."""
    return RetrievalPipeline()

@pytest.fixture
def rag_pipeline():
    """Initialize main RAG pipeline (without NLI for speed)."""
    return ProductionRAGPipeline(use_nli=False, device="cpu")


# ===================== TEST UTILS_NEW =====================

class TestUtilsNew:
    """Tests for utils_new module."""
    
    def test_extract_sentences_basic(self, sample_text):
        """Test basic sentence extraction."""
        sentences = extract_sentences(sample_text)
        
        assert isinstance(sentences, list)
        assert len(sentences) > 0
        assert all(isinstance(s, str) for s in sentences)
        # Sentences should end with punctuation or be substantial
        assert all(len(s) > 10 for s in sentences)
    
    def test_extract_sentences_min_length(self, sample_text):
        """Test sentence filtering by minimum length."""
        sentences_short = extract_sentences(sample_text, min_length=5)
        sentences_long = extract_sentences(sample_text, min_length=100)
        
        assert len(sentences_short) >= len(sentences_long)
        assert all(len(s) >= 100 for s in sentences_long)
    
    def test_extract_sentences_empty(self):
        """Test with empty text."""
        with pytest.raises(TextProcessingError):
            extract_sentences("")
        
        with pytest.raises(TextProcessingError):
            extract_sentences(None)
    
    def test_clean_text(self, sample_html_text):
        """Test text cleaning."""
        cleaned = clean_text(sample_html_text)
        
        assert "<" not in cleaned
        assert ">" not in cleaned
        assert "&nbsp" not in cleaned
        assert "Hello world" in cleaned or "Hello" in cleaned
    
    def test_clean_text_whitespace(self):
        """Test whitespace normalization."""
        text = "Hello    world   \n\n   test"
        cleaned = clean_text(text)
        
        # Multiple spaces should be reduced
        assert "    " not in cleaned
        assert cleaned == "Hello world test" or cleaned == "Hello world test"
    
    def test_deduplicate_evidence_exact(self):
        """Test deduplication of exact duplicates."""
        texts = [
            "The Earth is a sphere.",
            "The Earth is a sphere.",  # Exact duplicate
            "The Moon orbits Earth.",
            "The Earth is a sphere."  # Another exact duplicate
        ]
        
        unique, indices = deduplicate_evidence(texts)
        
        # Should reduce to 2 unique strings
        assert len(unique) <= 2
        assert len(indices) == len(unique)
    
    def test_deduplicate_evidence_single(self):
        """Test with single sentence."""
        texts = ["Single sentence."]
        unique, indices = deduplicate_evidence(texts)
        
        assert unique == texts
        assert indices == [0]
    
    def test_deduplicate_evidence_empty(self):
        """Test with empty list."""
        unique, indices = deduplicate_evidence([])
        
        assert unique == []
        assert indices == []
    
    def test_format_evidence_dict(self):
        """Test evidence dictionary formatting."""
        evidence = format_evidence_dict(
            sentence="The Earth is round.",
            source_url="https://example.com",
            source_title="Example Article",
            similarity_score=0.85,
            nli_scores={"entailment": 0.8, "contradiction": 0.1, "neutral": 0.1}
        )
        
        assert evidence["sentence"] == "The Earth is round."
        assert evidence["url"] == "https://example.com"
        assert evidence["source"] == "Example Article"
        assert 0 <= evidence["similarity_score"] <= 1
        assert 0 <= evidence["nli_entailment"] <= 1
    
    def test_chunk_text(self, sample_text):
        """Test text chunking."""
        chunks = chunk_text(sample_text, chunk_size=50)
        
        assert len(chunks) > 0
        assert all(isinstance(c, str) for c in chunks)


# ===================== TEST RANKING_NEW =====================

class TestRankingNew:
    """Tests for ranking_new module."""
    
    def test_embedder_init(self):
        """Test embedder initialization."""
        embedder = SentenceTransformerEmbedder(device="cpu")
        assert embedder.model is not None
        assert embedder.model_name == "all-MiniLM-L6-v2"
    
    def test_embed_texts(self, embedder, sample_sentences):
        """Test text embedding."""
        embeddings = embedder.embed_texts(sample_sentences)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == len(sample_sentences)
        assert embeddings.shape[1] > 0  # Embedding dimension
    
    def test_embed_texts_empty(self, embedder):
        """Test embedding empty list."""
        with pytest.raises(RankingError):
            embedder.embed_texts([])
    
    def test_rank_by_similarity(self, embedder, sample_sentences):
        """Test similarity ranking."""
        query = "Is the Earth a sphere?"
        
        result = embedder.rank_by_similarity(query, sample_sentences, top_k=3)
        
        assert "ranked_evidence" in result
        assert "similarity_scores" in result
        assert "indices" in result
        
        assert len(result["ranked_evidence"]) == 3
        assert len(result["similarity_scores"]) == 3
        
        # Scores should be sorted descending
        scores = result["similarity_scores"]
        assert scores == sorted(scores, reverse=True)
        
        # All scores should be in [0, 1]
        assert all(0 <= s <= 1 for s in scores)
    
    def test_rank_by_similarity_top_k_exceeds_length(self, embedder, sample_sentences):
        """Test ranking when top_k exceeds available sentences."""
        result = embedder.rank_by_similarity("query", sample_sentences, top_k=100)
        
        # Should return all available sentences
        assert len(result["ranked_evidence"]) == len(sample_sentences)
    
    def test_compute_ranking_confidence(self, embedder):
        """Test confidence computation."""
        scores = [0.9, 0.8, 0.7]
        
        # Test different strategies
        conf_mean = embedder.compute_ranking_confidence(scores, strategy="mean")
        conf_median = embedder.compute_ranking_confidence(scores, strategy="median")
        conf_max = embedder.compute_ranking_confidence(scores, strategy="max")
        
        assert 0 <= conf_mean <= 1
        assert 0 <= conf_median <= 1
        assert 0 <= conf_max <= 1
        
        # Max should be the highest score
        assert conf_max == 0.9
        
        # Mean should be average of scores
        assert abs(conf_mean - 0.8) < 0.01
    
    def test_rank_and_score(self, embedder, sample_sentences):
        """Test combined ranking and scoring."""
        query = "Earth sphere moon"
        result = embedder.rank_and_score(query, sample_sentences, top_k=3)
        
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1
        assert len(result["ranked_evidence"]) == 3


# ===================== TEST RETRIEVAL_NEW =====================

class TestRetrievalNew:
    """Tests for retrieval_new module."""
    
    def test_query_expander_init(self):
        """Test query expander initialization."""
        expander = QueryExpander()
        assert expander.expansion_count > 0
    
    def test_query_expansion(self):
        """Test query expansion."""
        expander = QueryExpander()
        queries = expander.expand_query("Is the Earth flat?")
        
        assert isinstance(queries, list)
        assert len(queries) > 0
        assert len(queries) <= 5
        assert "Is the Earth flat?" in queries or all(len(q) > 0 for q in queries)
    
    def test_query_expansion_empty(self):
        """Test query expansion with empty input."""
        expander = QueryExpander()
        with pytest.raises(RetrievalError):
            expander.expand_query("")
    
    def test_wikipedia_retriever_init(self):
        """Test Wikipedia retriever initialization."""
        retriever = WikipediaRetriever()
        assert retriever.language == "en"
        assert retriever.timeout > 0
    
    @pytest.mark.slow  # Mark as slow since it makes API call
    def test_wikipedia_search(self):
        """Test Wikipedia search."""
        retriever = WikipediaRetriever()
        
        # Search for a common topic
        results = retriever.search("Wikipedia", max_results=1)
        
        # Should return results or empty list (graceful failure)
        assert isinstance(results, list)
        
        if results:
            assert "title" in results[0]
            assert "url" in results[0]
            assert "content" in results[0] or "summary" in results[0]
    
    def test_retrieval_pipeline_init(self):
        """Test retrieval pipeline initialization."""
        pipeline = RetrievalPipeline()
        assert pipeline.query_expander is not None
        assert pipeline.wikipedia_retriever is not None
        assert pipeline.fallback_retriever is not None


# ===================== TEST PIPELINE_NEW =====================

class TestPipelineNew:
    """Integration tests for pipeline_new module."""
    
    def test_rag_pipeline_init(self):
        """Test RAG pipeline initialization."""
        pipeline = ProductionRAGPipeline(use_nli=False, device="cpu")
        
        assert pipeline.retrieval_pipeline is not None
        assert pipeline.ranking_pipeline is not None
    
    @pytest.mark.slow
    def test_stage_query_expansion(self, rag_pipeline):
        """Test query expansion stage."""
        query = "Is water wet?"
        expanded, used = rag_pipeline._stage_query_expansion(query, expansion_enabled=True)
        
        assert isinstance(expanded, list)
        assert len(expanded) > 0
        assert all(isinstance(q, str) for q in expanded)
    
    def test_stage_extract_sentences(self, rag_pipeline):
        """Test sentence extraction stage."""
        articles = [
            {
                "title": "Test Article",
                "url": "https://example.com",
                "content": "The Earth is round. The Moon orbits Earth. Stars are far away.",
                "source": "Test"
            }
        ]
        
        sentences, sources = rag_pipeline._stage_extract_sentences(articles)
        
        assert len(sentences) > 0
        assert len(sentences) == len(sources)
        assert all("Earth" in s or "Moon" in s or "Stars" in s for s in sentences)
    
    def test_stage_extract_sentences_empty_content(self, rag_pipeline):
        """Test extraction with empty content."""
        articles = [{"title": "Empty", "url": "http://test.com", "content": "", "source": "Test"}]
        
        sentences, sources = rag_pipeline._stage_extract_sentences(articles)
        
        assert len(sentences) == 0
    
    def test_stage_deduplication(self, rag_pipeline):
        """Test deduplication stage."""
        sentences = [
            "The Earth is round.",
            "The Earth is round.",  # Duplicate
            "The Moon is rocky."
        ]
        
        unique, indices = rag_pipeline._stage_deduplication(sentences)
        
        assert len(unique) <= len(sentences)
        assert len(indices) == len(unique)


# ===================== DETERMINISM TESTS =====================

class TestDeterminism:
    """Test that outputs are deterministic and reproducible."""
    
    def test_embedding_determinism(self):
        """Test that embeddings are deterministic."""
        embedder1 = SentenceTransformerEmbedder(device="cpu")
        embedder2 = SentenceTransformerEmbedder(device="cpu")
        
        text = "The Earth is round."
        
        emb1 = embedder1.embed_texts([text])[0]
        emb2 = embedder2.embed_texts([text])[0]
        
        # Embeddings should be identical
        np.testing.assert_allclose(emb1, emb2, rtol=1e-5)
    
    def test_ranking_determinism(self):
        """Test that ranking is deterministic."""
        embedder = SentenceTransformerEmbedder(device="cpu")
        
        query = "Is water wet?"
        sentences = [
            "Water is a liquid.",
            "Water covers most of Earth.",
            "Water is essential for life."
        ]
        
        # Run ranking twice
        result1 = embedder.rank_by_similarity(query, sentences, top_k=2)
        result2 = embedder.rank_by_similarity(query, sentences, top_k=2)
        
        # Results should be identical
        assert result1["ranked_evidence"] == result2["ranked_evidence"]
        
        # Scores should be very close
        for s1, s2 in zip(result1["similarity_scores"], result2["similarity_scores"]):
            assert abs(s1 - s2) < 1e-5


# ===================== ERROR HANDLING TESTS =====================

class TestErrorHandling:
    """Test error handling across modules."""
    
    def test_invalid_embedder_model(self):
        """Test initialization with non-existent model."""
        with pytest.raises(RankingError):
            SentenceTransformerEmbedder(model_name="non-existent-model-xyz")
    
    def test_ranking_with_empty_sentences(self, embedder):
        """Test ranking with empty evidence list."""
        with pytest.raises(RankingError):
            embedder.rank_by_similarity("query", [], top_k=5)
    
    def test_utils_text_processing_error(self):
        """Test text processing error handling."""
        with pytest.raises(TextProcessingError):
            extract_sentences(None)


# ===================== PERFORMANCE BENCHMARKS =====================

class TestPerformance:
    """Performance benchmarking tests."""
    
    @pytest.mark.benchmark
    def test_embedding_performance(self, embedder):
        """Benchmark embedding speed."""
        sentences = [
            f"Sentence number {i}. " * 5 for i in range(50)
        ]
        
        import time
        start = time.time()
        embeddings = embedder.embed_texts(sentences)
        elapsed = time.time() - start
        
        # Should complete in reasonable time (adjust as needed)
        assert elapsed < 10  # 50 sentences in < 10 seconds
        assert embeddings.shape[0] == len(sentences)
    
    @pytest.mark.benchmark
    def test_ranking_performance(self, embedder):
        """Benchmark ranking speed."""
        query = "Test query"
        sentences = [f"Sentence {i}. " * 3 for i in range(100)]
        
        import time
        start = time.time()
        result = embedder.rank_by_similarity(query, sentences, top_k=10)
        elapsed = time.time() - start
        
        # Should complete quickly
        assert elapsed < 5
        assert len(result["ranked_evidence"]) == 10


# ===================== INTEGRATION TESTS =====================

class TestIntegration:
    """Full end-to-end integration tests."""
    
    @pytest.mark.slow
    def test_simple_fact_check(self, rag_pipeline):
        """Test simple fact-checking (integration test)."""
        # Skip if no Wikipedia available
        try:
            result = rag_pipeline.analyze(
                claim="The sky is blue",
                top_k_evidence=3,
                query_expansion_enabled=True
            )
            
            assert result["success"]
            assert "claim" in result
            assert "confidence" in result
            assert "evidence" in result
            assert isinstance(result["evidence"], list)
        except RAGPipelineError as e:
            # May fail if Wikipedia unavailable, which is ok for local testing
            pytest.skip(f"Wikipedia unavailable: {str(e)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not slow"])
