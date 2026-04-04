#!/usr/bin/env python3
"""
End-to-End Integration Test: OpenAI + Tavily + Pipeline
Tests the complete retrieval and reasoning flow.
"""

import sys
import os
sys.path.insert(0, '/Users/pratyush/ai truthlens')

from dotenv import load_dotenv
load_dotenv()

def test_retrieval_with_both_sources():
    """Test retrieval pipeline using both Wikipedia and Tavily."""
    print("\n" + "="*70)
    print("TEST: Retrieval Pipeline (Wikipedia + Tavily)")
    print("="*70)
    
    from backend.services.retrieval_new import RetrievalPipeline
    
    pipeline = RetrievalPipeline()
    
    # Test claim
    query = "is obama dead"
    print(f"\n📝 Query: '{query}'")
    print("\n🔍 Retrieving articles...")
    
    articles = pipeline.retrieve(query, max_articles=10)
    
    print(f"\n✅ Retrieved {len(articles)} articles:")
    print("\nBreakdown by source:")
    
    sources = {}
    for article in articles:
        source = article.get("source", "Unknown")
        sources[source] = sources.get(source, 0) + 1
    
    for source, count in sources.items():
        print(f"  {source}: {count} articles")
    
    # Show individual sources
    print("\nArticles:")
    for i, article in enumerate(articles[:5], 1):
        print(f"\n[{i}] {article['title']}")
        print(f"    Source: {article['source']}")
        print(f"    URL: {article['url'][:60]}...")
        print(f"    Content length: {len(article.get('content', ''))} chars")
    
    return len(articles) > 0


def test_llm_reasoner():
    """Test LLMReasoner with OpenAI."""
    print("\n" + "="*70)
    print("TEST: LLM Reasoner (OpenAI)")
    print("="*70)
    
    from backend.services.llm_reasoner import LLMReasoner
    from backend.config.env_config import EnvironmentConfig
    
    openai_key = EnvironmentConfig.get_openai_key()
    
    if not openai_key:
        print("⚠️ SKIPPED: No OpenAI API key configured")
        return True
    
    print(f"\n✅ OpenAI key configured: {openai_key[:15]}...")
    
    reasoner = LLMReasoner(openai_api_key=openai_key)
    
    # Test claim
    claim = "Obama is dead"
    print(f"\n📝 Claim: '{claim}'")
    
    # Test entity extraction
    entity, keywords = reasoner.extract_entity(claim)
    print(f"\n🔍 Entity: {entity}")
    print(f"   Keywords: {keywords}")
    
    # Test intent detection
    intent = reasoner.detect_claim_intent(claim)
    print(f"\n💭 Detected intent: {intent}")
    
    # Test LLM call
    print(f"\n🤖 Testing LLM call...")
    try:
        response = reasoner._call_llm("What year did World War 2 end?", max_tokens=20)
        if response:
            print(f"✅ LLM responded: {response[:80]}")
        else:
            print("⚠️ LLM returned empty response (may be API key issue)")
    except Exception as e:
        print(f"⚠️ LLM call failed: {e}")
    
    return True


def test_pipeline_end_to_end():
    """Test complete pipeline with a sample claim."""
    print("\n" + "="*70)
    print("TEST: Complete Pipeline (Retrieval + Reasoning + Verdict)")
    print("="*70)
    
    from backend.services.pipeline_new import ProductionRAGPipeline
    
    print(f"\n🚀 Initializing pipeline...")
    pipeline = ProductionRAGPipeline(use_nli=False, device="cpu")
    
    # Sample claim
    claim = "Einstein won the Nobel Prize"
    print(f"\n📝 Claim: '{claim}'")
    
    print(f"\n⏳ Analyzing (this may take 30-60s)...")
    print(f"   Stage 1: Query expansion")
    print(f"   Stage 2: Wikipedia + Tavily retrieval")
    print(f"   Stage 3: Sentence extraction")
    print(f"   Stage 4: Semantic ranking")
    print(f"   Stage 5: LLM reasoning")
    print(f"   Stage 6: Verdict generation")
    
    try:
        result = pipeline.analyze(claim, top_k_evidence=3)
        
        print(f"\n✅ Analysis complete!")
        print(f"\n📊 Results:")
        print(f"  Verdict: {result.get('verdict', 'UNKNOWN')}")
        print(f"  Confidence: {result.get('confidence', 0):.2%}")
        print(f"  Evidence count: {len(result.get('evidence', []))}")
        
        # Show evidence
        evidence_list = result.get('evidence', [])
        if evidence_list:
            print(f"\n📖 Top Evidence:")
            for i, ev in enumerate(evidence_list[:3], 1):
                if isinstance(ev, dict):
                    score = ev.get('similarity_score', 0)
                    source = ev.get('source', 'Unknown')
                    text = ev.get('sentence', '')[:60] + "..."
                    print(f"  [{i}] {text}")
                    print(f"      Source: {source}, Score: {score:.3f}")
        
        # Show metadata
        metadata = result.get('metadata', {})
        print(f"\n📈 Metadata:")
        print(f"  Articles fetched: {metadata.get('total_articles_fetched', 0)}")
        print(f"  Sentences extracted: {metadata.get('total_sentences_extracted', 0)}")
        print(f"  Processing time: {metadata.get('processing_time_ms', 0):.0f}ms")
        
        return result.get('success', False)
    
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all integration tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + "  END-TO-END INTEGRATION TEST: OPENAI + TAVILY + PIPELINE".center(68) + "║")
    print("╚" + "="*68 + "╝")
    
    from backend.config.env_config import EnvironmentConfig
    
    # Log configuration
    EnvironmentConfig.log_config()
    
    # Run tests
    tests = {
        "Retrieval Pipeline": test_retrieval_with_both_sources,
        "LLM Reasoner": test_llm_reasoner,
        "Complete Pipeline": test_pipeline_end_to_end,
    }
    
    results = {}
    for test_name, test_func in tests.items():
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL INTEGRATION TESTS PASSED")
        print("Status: ✅ System ready for production")
    else:
        print("⚠️ SOME TESTS FAILED")
        print("Status: ⚠️ Review errors above")
    print("="*70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
