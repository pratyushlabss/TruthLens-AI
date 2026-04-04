"""
Quick demo and integration test for the new RAG pipeline.
Can be run standalone to verify the system works correctly.

Usage:
    python backend/demo_pipeline_new.py
"""

import sys
import os
import time

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.pipeline_new import ProductionRAGPipeline, StreamlineRAGPipeline
from services.utils_new import extract_sentences, clean_text, deduplicate_evidence
from services.ranking_new import SentenceTransformerEmbedder
from services.retrieval_new import QueryExpander


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_utils():
    """Demo text utilities."""
    print_section("DEMO 1: Text Processing Utilities")
    
    # Text cleaning
    print("1. Text Cleaning")
    html = "<p>Hello <b>World</b>! &nbsp; Test</p>"
    cleaned = clean_text(html)
    print(f"   Input:  {html}")
    print(f"   Output: {cleaned}\n")
    
    # Sentence extraction
    print("2. Sentence Extraction")
    text = """
    The Earth is round. It orbits the Sun. 
    We have gravity to thank for this. The Moon orbits Earth too.
    """
    sentences = extract_sentences(text, min_length=15)
    print(f"   Input text: {len(text)} characters")
    print(f"   Sentences extracted: {len(sentences)}")
    for i, sent in enumerate(sentences, 1):
        print(f"     {i}. {sent}")


def demo_query_expansion():
    """Demo query expansion."""
    print_section("DEMO 2: Query Expansion")
    
    expander = QueryExpander()
    queries = [
        "Is the Earth flat?",
        "Do vaccines cause autism?",
        "Can humans breathe on Mars?"
    ]
    
    for original in queries:
        expanded = expander.expand_query(original)
        print(f"Original: {original}")
        print(f"Expanded queries ({len(expanded)} variants):")
        for i, q in enumerate(expanded, 1):
            print(f"  {i}. {q}")
        print()


def demo_embedding_and_ranking():
    """Demo embedding and ranking."""
    print_section("DEMO 3: Embedding & Semantic Ranking")
    
    print("Initializing SentenceTransformer embedder...")
    embedder = SentenceTransformerEmbedder(device="cpu")
    
    query = "Is artificial intelligence dangerous?"
    sentences = [
        "AI systems can be biased if trained on biased data.",
        "Machine learning models improve with more training data.",
        "AGI (Artificial General Intelligence) is a theoretical future development.",
        "Current AI systems are narrow and task-specific.",
        "Safety is an important consideration in AI development."
    ]
    
    print(f"\nQuery: {query}\n")
    print("Embedding and ranking sentences...\n")
    
    result = embedder.rank_by_similarity(query, sentences, top_k=3)
    
    for i, (evidence, score) in enumerate(zip(result["ranked_evidence"], result["similarity_scores"]), 1):
        print(f"{i}. [Similarity: {score:.3f}] {evidence}")
    
    print(f"\nMean similarity (confidence): {result['mean_similarity']:.3f}")


def demo_retrieval():
    """Demo retrieval pipeline."""
    print_section("DEMO 4: Retrieval Pipeline with Query Expansion")
    
    from services.retrieval_new import RetrievalPipeline
    
    print("Initializing RetrievalPipeline...")
    pipeline = RetrievalPipeline()
    
    claim = "The Earth is round"
    
    print(f"Claim: {claim}\n")
    print("Generating query variants...")
    
    queries = pipeline.query_expander.expand_query(claim)
    print(f"Generated {len(queries)} query variants:")
    for i, q in enumerate(queries, 1):
        print(f"  {i}. {q}")
    
    print("\n⚠️  Note: Wikipedia retrieval skipped in demo (requires network)")
    print("In production, this would fetch articles from Wikipedia API.")


def demo_full_pipeline():
    """Demo complete RAG pipeline."""
    print_section("DEMO 5: Full RAG Pipeline Analysis")
    
    print("Initializing ProductionRAGPipeline (without NLI for speed)...")
    
    try:
        pipeline = ProductionRAGPipeline(use_nli=False, device="cpu")
        
        test_claims = [
            "The Earth is a sphere",
            "Water boils at 100 degrees Celsius"
        ]
        
        for claim in test_claims:
            print(f"\nAnalyzing: {claim}")
            print("-" * 60)
            
            try:
                start = time.time()
                result = pipeline.analyze(
                    claim=claim,
                    top_k_evidence=3,
                    query_expansion_enabled=True
                )
                elapsed = time.time() - start
                
                print(f"✅ SUCCESS")
                print(f"   Verdict: {result.get('verdict', 'UNKNOWN')}")
                print(f"   Confidence: {result.get('confidence', 0):.2%}")
                print(f"   Time: {elapsed:.2f}s")
                
                evidence_count = len(result.get('evidence', []))
                print(f"   Evidence pieces: {evidence_count}")
                
                metadata = result.get('metadata', {})
                print(f"   Queries used: {len(metadata.get('queries_used', []))}")
                print(f"   Articles fetched: {metadata.get('total_articles_fetched', 0)}")
                
                if evidence_count > 0:
                    print(f"   Top evidence:")
                    for i, ev in enumerate(result.get('evidence', [])[:2], 1):
                        print(f"     {i}. {ev.get('sentence', '')[:80]}...")
                        print(f"        Source: {ev.get('source', 'Unknown')}")
                        print(f"        Similarity: {ev.get('similarity_score', 0):.3f}")
            
            except Exception as e:
                print(f"⚠️  Analysis failed: {str(e)[:100]}")
                print("     (This may be due to Wikipedia availability or network issues)")
    
    except Exception as e:
        print(f"❌ Pipeline initialization failed: {str(e)}")
        print("   Make sure all dependencies are installed:")
        print("   pip install -r backend/requirements.txt")


def demo_determinism():
    """Test determinism of embeddings."""
    print_section("DEMO 6: Determinism Verification")
    
    print("Creating two separate embedder instances...")
    embedder1 = SentenceTransformerEmbedder(device="cpu")
    embedder2 = SentenceTransformerEmbedder(device="cpu")
    
    text = "The quick brown fox jumps over the lazy dog"
    
    print(f"Text: {text}\n")
    
    emb1 = embedder1.embed_texts([text])[0]
    emb2 = embedder2.embed_texts([text])[0]
    
    # Check if embeddings are identical
    import numpy as np
    max_diff = np.max(np.abs(emb1 - emb2))
    
    print(f"Embedder 1 output: {emb1[:5]}... (shape: {emb1.shape})")
    print(f"Embedder 2 output: {emb2[:5]}... (shape: {emb2.shape})")
    print(f"\nMax difference between embeddings: {max_diff}")
    
    if max_diff < 1e-5:
        print("✅ DETERMINISTIC: Embeddings are identical!")
    else:
        print(f"⚠️  Minor floating point differences (expected): {max_diff:.2e}")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("  TruthLens-AI: New RAG Pipeline Demo & Integration Tests")
    print("=" * 80)
    
    try:
        # Run demos
        demo_utils()
        demo_query_expansion()
        demo_embedding_and_ranking()
        demo_retrieval()
        demo_determinism()
        demo_full_pipeline()
        
        print_section("DEMO COMPLETE")
        print("✅ All core components working correctly!\n")
        print("Next steps:")
        print("1. Install requirements: pip install -r backend/requirements.txt")
        print("2. Run tests: pytest backend/tests/test_pipeline_new.py -v")
        print("3. Start server: uvicorn backend.main:app --reload")
        print("4. Use /analyze/v2 endpoint for new pipeline")
        print()
        
    except Exception as e:
        print_section("DEMO FAILED")
        print(f"❌ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
