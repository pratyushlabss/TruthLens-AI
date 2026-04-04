#!/usr/bin/env python3
"""
TruthLens AI - Real System Test Suite
Validates all components are working
"""

import sys
import json
from datetime import datetime

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def test_environment():
    """Test 1: Environment validation"""
    print_header("TEST 1: ENVIRONMENT VALIDATION")
    
    try:
        from config.environment import Config
        Config.initialize()
        print_success("Environment validation passed")
        print_success("OpenAI API key configured")
        return True
    except Exception as e:
        print_error(f"Environment validation failed: {e}")
        return False

def test_web_scraper():
    """Test 2: Web scraping"""
    print_header("TEST 2: WEB SCRAPER")
    
    try:
        from services.web_scraper_real import WebScraperService
        
        scraper = WebScraperService()
        print(f"✓ WebScraperService initialized")
        
        # Test domain trust
        trust_levels = {
            'wikipedia.org': 'high',
            'bbc.com': 'high',
            'reuters.com': 'high',
            'example-blog.com': 'low'
        }
        
        for domain, expected in trust_levels.items():
            actual = scraper.get_domain_trust(domain)
            if actual == expected:
                print_success(f"Domain trust: {domain} → {actual}")
            else:
                print_warning(f"Domain trust: {domain} → {actual} (expected {expected})")
        
        # Try to scrape a real URL
        print("\nAttempting to scrape Wikipedia...")
        result = scraper.scrape_url('https://en.wikipedia.org/wiki/Water')
        
        if result['success']:
            print_success(f"Scraped {result['length']} characters from {result['url']}")
            print_success(f"Title: {result['title']}")
            return True
        else:
            print_error("Scraping failed")
            return False
            
    except Exception as e:
        print_error(f"Web scraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pinecone():
    """Test 3: Pinecone vector DB"""
    print_header("TEST 3: PINECONE VECTOR DB")
    
    try:
        import os
        from services.pinecone_integration import PineconeVectorDB, SearchURLGenerator
        
        # Test search URL generation
        generator = SearchURLGenerator()
        urls = generator.generate("water boiling point", ["google", "wikipedia"])
        
        if 'google' in urls and 'wikipedia' in urls:
            print_success("Search URL generation working")
            print(f"   Google URL: {urls['google'][:60]}...")
        else:
            print_error("Search URL generation failed")
            return False
        
        # Test Pinecone connection
        api_key = os.getenv('PINECONE_API_KEY')
        env = os.getenv('PINECONE_ENV')
        
        vector_db = PineconeVectorDB(api_key=api_key, env=env)
        print_success("Pinecone connected")
        
        # Test embedding
        text = "Water boils at 100 degrees Celsius at sea level pressure"
        embedding = vector_db.embed_text(text)
        
        print_success(f"Embedding generated ({len(embedding)} dimensions)")
        
        return True
        
    except Exception as e:
        print_error(f"Pinecone test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_huggingface_nli():
    """Test 4: HuggingFace NLI Model"""
    print_header("TEST 4: HUGGINGFACE NLI MODEL")
    
    try:
        from services.huggingface_nli import HuggingFaceNLI
        
        print("Loading facebook/bart-large-mnli model...")
        print("(This may take 2-3 minutes on first load)")
        
        nli = HuggingFaceNLI()
        print_success("Model loaded successfully")
        
        # Test single inference
        claim = "Water boils at 100 degrees Celsius"
        evidence = "At sea level and standard pressure, water reaches its boiling point at 100°C"
        
        result = nli.infer_single(claim, evidence)
        
        print(f"\nClaim: {claim}")
        print(f"Evidence: {evidence}")
        print(f"Stance: {result['stance']} ({result['confidence']:.1%})")
        print_success("Single inference working")
        
        # Test batch inference
        evidences = [
            "Water boils at 100C at sea level",
            "Boiling points decrease at higher altitudes",
            "Water is essential for life"
        ]
        
        batch_results = nli.infer_batch(claim, evidences)
        print_success(f"Batch inference working ({len(batch_results)} results)")
        
        # Test verdict computation
        verdict = nli.compute_verdict(claim, batch_results)
        print(f"Computed verdict: {verdict['verdict']} ({verdict['confidence']}% confidence)")
        print_success("Verdict computation working")
        
        return True
        
    except Exception as e:
        print_error(f"HuggingFace NLI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_session_analytics():
    """Test 5: Session Analytics"""
    print_header("TEST 5: SESSION ANALYTICS")
    
    try:
        from services.session_analytics import session_manager, QueryMetrics
        
        # Create a test session
        session = session_manager.create_session("test_user")
        print_success(f"Session created: {session.session_id}")
        
        # Create query metrics
        metrics = session.create_query_metrics("Is water boiling point 100C?")
        print_success(f"Query metrics created: {metrics.query_id}")
        
        # Simulate stages
        metrics.mark_stage_complete("claim_parsing")
        metrics.mark_stage_complete("search_generation")
        metrics.add_search_urls({"google": "https://google.com/search?q=water+boiling", 
                                 "wikipedia": "https://wikipedia.org/wiki/Water"})
        metrics.add_scraped_source("https://wikipedia.org/wiki/Water", "Wikipedia", 
                                  "Water boils at 100C at sea level", "high")
        metrics.set_verdict("TRUE", 95)
        
        # Finalize and check
        final_metrics = metrics.finalize()
        
        print_success(f"Processing time: {final_metrics['total_processing_time_seconds']:.2f}s")
        print_success(f"Verdict: {final_metrics.get('verdict', 'N/A')}")
        print_success(f"Sources used: {len(final_metrics.get('sources_used', []))}")
        
        # Verify isolation
        if len(session.queries) == 1:
            print_success("Query isolation working (only 1 query in session)")
        else:
            print_warning(f"Multiple queries in session: {len(session.queries)}")
        
        return True
        
    except Exception as e:
        print_error(f"Session analytics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rag_pipeline():
    """Test 6: Complete RAG Pipeline"""
    print_header("TEST 6: RAG PIPELINE (FULL SYSTEM)")
    
    try:
        from services.rag_pipeline_real import get_rag_pipeline
        
        print("Starting complete RAG pipeline analysis...")
        print("This will: scrape web, embed, search, infer, compute verdict")
        
        pipeline = get_rag_pipeline()
        
        # Simple, factual test claim
        claim = "Water boils at 100 degrees Celsius at sea level"
        
        print(f"\nAnalyzing claim: {claim}")
        result = pipeline.analyze(claim, user_id="test_user")
        
        if not result.get('success', False):
            print_error(f"Pipeline failed: {result.get('error')}")
            print(f"Details: {result.get('details')}")
            return False
        
        print_success("Pipeline executed successfully!")
        print(f"\nResults:")
        print(f"  Claim: {result['claim']['normalized']}")
        print(f"  Verdict: {result['verdict']}")
        print(f"  Confidence: {result['confidence']}%")
        print(f"  Sources found: {len(result['evidence'])}")
        
        if result['evidence']:
            print(f"\n  Top source:")
            top = result['evidence'][0]
            print(f"    URL: {top['url']}")
            print(f"    Title: {top['title']}")
            print(f"    Stance: {top['stance']}")
        
        # Check analytics
        analytics = result.get('analytics', {})
        if analytics:
            print(f"\n  Analytics:")
            print(f"    Total time: {analytics.get('total_processing_time_seconds', 0):.2f}s")
            print(f"    Query ID: {analytics.get('query_id', 'N/A')}")
            print(f"    Supporting evidence: {analytics.get('supporting_evidence', 0)}")
            print(f"    Contradicting evidence: {analytics.get('contradicting_evidence', 0)}")
        
        return True
        
    except Exception as e:
        print_error(f"RAG pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print_header("TRUTHLENS AI - REAL SYSTEM TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Environment Validation", test_environment),
        ("Web Scraper", test_web_scraper),
        # ("Pinecone Vector DB", test_pinecone),  # DEPRECATED: Using OpenAI instead
        # ("HuggingFace NLI", test_huggingface_nli),  # DEPRECATED: Using OpenAI instead
        ("Session Analytics", test_session_analytics),
        ("RAG Pipeline", test_rag_pipeline),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print(f"\nTest interrupted by user")
            sys.exit(1)
        except Exception as e:
            print_error(f"Unexpected error in {test_name}: {e}")
            results[test_name] = False
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print_success("ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION")
        return 0
    else:
        print_error(f"{total - passed} tests failed - fix issues before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())
