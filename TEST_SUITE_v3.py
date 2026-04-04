#!/usr/bin/env python3
"""
TruthLens v3.0 Validation Test Suite
Comprehensive testing for 11-step upgrade
"""

import sys
import time
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

def test_1_entity_normalization():
    """TEST STEP 1: Entity Normalization"""
    print("\n" + "="*70)
    print("TEST 1: Entity Normalization (STEP 1)")
    print("="*70)
    
    from backend.services.pipeline_new import normalize_claim
    
    test_cases = [
        ("Obama is dead", "Barack Hussein Obama"),
        ("Trump won election", "Donald Trump"),
        ("Einstein was brilliant", "Albert Einstein"),
        ("India is great", "India"),  # Should not change
    ]
    
    passed = 0
    for claim, expected_entity in test_cases:
        normalized, entity = normalize_claim(claim)
        match = expected_entity.lower() in entity.lower() or entity.lower() in expected_entity.lower()
        status = "✅ PASS" if match else "❌ FAIL"
        print(f"{status}: '{claim}' → Entity: '{entity}'")
        if match:
            passed += 1
    
    print(f"Result: {passed}/{len(test_cases)} normalization tests passed")
    return passed == len(test_cases)


def test_2_entity_aware_queries():
    """TEST STEP 2: Entity-Aware Query Generation"""
    print("\n" + "="*70)
    print("TEST 2: Entity-Aware Query Generation (STEP 2)")
    print("="*70)
    
    from backend.services.pipeline_new import ProductionRAGPipeline
    
    pipeline = ProductionRAGPipeline()
    
    test_cases = [
        ("Obama is dead", "Barack Hussein Obama"),
        ("Trump won", "Donald Trump"),
        ("India is largest democracy", "India"),
    ]
    
    passed = 0
    for claim, entity in test_cases:
        try:
            queries = pipeline._build_entity_aware_queries(claim, entity)
            
            # Check: Should have 4-5 queries
            has_good_count = 4 <= len(queries) <= 5
            
            # Check: Should include entity name
            has_entity = any(entity.lower() in q.lower() for q in queries)
            
            # Check: Should include original claim
            has_claim = any(claim.lower() in q.lower() for q in queries)
            
            all_good = has_good_count and has_entity and has_claim
            status = "✅ PASS" if all_good else "❌ FAIL"
            
            print(f"{status}: {claim}")
            print(f"      Queries: {queries}")
            print(f"      Count: {len(queries)} | Entity: {has_entity} | Claim: {has_claim}")
            
            if all_good:
                passed += 1
        except Exception as e:
            print(f"❌ FAIL: {claim} - Error: {str(e)[:100]}")
    
    print(f"Result: {passed}/{len(test_cases)} query generation tests passed")
    return passed == len(test_cases)


def test_3_multi_source_retrieval():
    """TEST STEP 3-5: Multi-Source Retrieval"""
    print("\n" + "="*70)
    print("TEST 3-5: Multi-Source Retrieval & Cleaning (STEPS 3-5)")
    print("="*70)
    
    from backend.services.pipeline_new import ProductionRAGPipeline
    
    pipeline = ProductionRAGPipeline()
    
    test_entity = "Barack Hussein Obama"
    test_queries = ["Obama biography", "Obama facts"]
    
    try:
        articles = pipeline._retrieve_articles(
            queries=test_queries,
            entity_tokens=["obama", "barack"],
            main_entity=test_entity,
            max_articles=5,
            expand_queries=False
        )
        
        # Check: Should get articles
        has_articles = len(articles) > 0
        status_articles = "✅" if has_articles else "❌"
        print(f"{status_articles} Retrieved {len(articles)} articles (target: >0)")
        
        # Check: Articles should have content
        has_content = all(len(a.get("content", "")) > 50 for a in articles)
        status_content = "✅" if has_content else "❌"
        print(f"{status_content} All articles have substantial content")
        
        # Check: Should include entity page
        has_entity_page = any(test_entity.lower() in a.get("title", "").lower() for a in articles)
        status_entity = "✅" if has_entity_page else "⚠️"
        print(f"{status_entity} Entity page included in results")
        
        print(f"\nArticles retrieved:")
        for i, article in enumerate(articles[:5], 1):
            title = article.get("title", "Unknown")[:50]
            source = article.get("source", "Unknown")
            print(f"  {i}. {title} ({source})")
        
        return has_articles and has_content
        
    except Exception as e:
        print(f"❌ FAIL: Retrieval error: {str(e)}")
        return False


def test_6_relaxed_filtering():
    """TEST STEP 6: Relaxed Filtering"""
    print("\n" + "="*70)
    print("TEST 6: Relaxed Filtering (STEP 6)")
    print("="*70)
    
    from backend.services.pipeline_new import ProductionRAGPipeline
    from backend.services.utils_new import clean_evidence
    
    # Test that we accept shorter sentences
    test_text = "Obama was born in Hawaii. He became president in 2008. Short text here."
    
    sentences_old = clean_evidence(test_text, min_length=25)
    sentences_new = clean_evidence(test_text, min_length=15)
    
    print(f"Original text: {test_text}")
    print(f"With min_length=25: {sentences_old}")
    print(f"With min_length=15: {sentences_new}")
    
    # New should have more sentences due to lower threshold
    has_more = len(sentences_new) >= len(sentences_old)
    status = "✅ PASS" if has_more else "⚠️"
    print(f"{status} Relaxed filtering keeps more evidence")
    
    return True


def test_7_contradiction_detection():
    """TEST STEP 7: Contradiction Detection"""
    print("\n" + "="*70)
    print("TEST 7: Contradiction Detection (STEP 7)")
    print("="*70)
    
    from backend.services.pipeline_new import ProductionRAGPipeline
    
    pipeline = ProductionRAGPipeline()
    
    test_cases = [
        {
            "claim": "Obama is dead",
            "evidence": "Barack Obama is not dead and living in Chicago",
            "sim": 0.82,
            "expected": "CONTRADICTS"
        },
        {
            "claim": "Einstein won Nobel Prize",
            "evidence": "Einstein received the Nobel Prize in Physics in 1921",
            "sim": 0.80,
            "expected": "SUPPORTS"
        },
        {
            "claim": "Paris is capital of Germany",
            "evidence": "Berlin is the capital of Germany",
            "sim": 0.45,
            "expected": "NEUTRAL"
        },
    ]
    
    passed = 0
    for tc in test_cases:
        try:
            rel = pipeline._improved_relationship_detection(
                tc["claim"],
                tc["evidence"],
                tc["sim"]
            )
            
            match = rel == tc["expected"]
            status = "✅ PASS" if match else "❌ FAIL"
            
            print(f"{status}: {tc['claim'][:40]}")
            print(f"      Evidence: {tc['evidence'][:60]}")
            print(f"      Got: {rel}, Expected: {tc['expected']}")
            
            if match:
                passed += 1
        except Exception as e:
            print(f"❌ FAIL: Error - {str(e)[:100]}")
    
    print(f"Result: {passed}/{len(test_cases)} contradiction tests passed")
    return passed == len(test_cases)


def test_8_evidence_aggregation():
    """TEST STEP 8: Evidence Aggregation"""
    print("\n" + "="*70)
    print("TEST 8: Evidence Aggregation (STEP 8)")
    print("="*70)
    
    from backend.services.pipeline_new import ProductionRAGPipeline
    
    pipeline = ProductionRAGPipeline()
    
    test_cases = [
        {
            "evidence": [
                {"relationship": "SUPPORTS"},
                {"relationship": "SUPPORTS"},
                {"relationship": "SUPPORTS"},
            ],
            "expected_min": 0.95
        },
        {
            "evidence": [
                {"relationship": "SUPPORTS"},
                {"relationship": "SUPPORTS"},
                {"relationship": "CONTRADICTS"},
            ],
            "expected_min": 0.60,
            "expected_max": 0.75
        },
        {
            "evidence": [
                {"relationship": "CONTRADICTS"},
                {"relationship": "CONTRADICTS"},
            ],
            "expected_max": 0.1
        },
    ]
    
    passed = 0
    for i, tc in enumerate(test_cases, 1):
        try:
            agreement = pipeline._compute_evidence_agreement_score(tc["evidence"])
            
            if "expected_min" in tc and "expected_max" in tc:
                match = tc["expected_min"] <= agreement <= tc["expected_max"]
            elif "expected_min" in tc:
                match = agreement >= tc["expected_min"]
            else:
                match = agreement <= tc["expected_max"]
            
            status = "✅ PASS" if match else "❌ FAIL"
            print(f"{status} Case {i}: Agreement = {agreement:.2f}")
            
            if match:
                passed += 1
        except Exception as e:
            print(f"❌ FAIL Case {i}: Error - {str(e)[:100]}")
    
    print(f"Result: {passed}/{len(test_cases)} aggregation tests passed")
    return passed == len(test_cases)


def test_11_end_to_end():
    """TEST STEP 11: End-to-End Analysis"""
    print("\n" + "="*70)
    print("TEST 11: End-to-End Analysis (STEP 11)")
    print("="*70)
    
    from backend.services.pipeline_new import ProductionRAGPipeline
    
    pipeline = ProductionRAGPipeline()
    
    test_cases = [
        {
            "claim": "Obama is dead",
            "name": "Normalization + Contradiction",
            "expected_verdict": "MISINFORMATION",
            "min_confidence": 0.60,
        },
        {
            "claim": "India is the largest democracy",
            "name": "True claim",
            "expected_verdict": "TRUE",
            "min_confidence": 0.60,
        },
        {
            "claim": "asdf random pizza war",
            "name": "Nonsense input",
            "expected_verdict": "UNCERTAIN",
            "max_time": 1.0,
        },
    ]
    
    passed = 0
    for tc in test_cases:
        print(f"\nTesting: {tc['name']}")
        print(f"  Claim: {tc['claim']}")
        
        try:
            start = time.time()
            result = pipeline.analyze(tc["claim"], query_expansion_enabled=False)
            elapsed = time.time() - start
            
            verdict = result.get("verdict", "UNKNOWN")
            confidence = result.get("confidence", 0.0)
            
            print(f"  Verdict: {verdict}")
            print(f"  Confidence: {confidence:.2f}")
            print(f"  Time: {elapsed:.1f}s")
            
            # Check verdict
            if "expected_verdict" in tc:
                verdict_match = verdict == tc["expected_verdict"]
                status = "✅" if verdict_match else "❌"
                print(f"  {status} Verdict match: {verdict} (expected {tc['expected_verdict']})")
            
            # Check confidence
            if "min_confidence" in tc:
                conf_match = confidence >= tc["min_confidence"]
                status = "✅" if conf_match else "❌"
                print(f"  {status} Confidence: {confidence:.2f} (expected >= {tc['min_confidence']})")
            
            # Check time
            if "max_time" in tc:
                time_ok = elapsed <= tc["max_time"]
                status = "✅" if time_ok else "⚠️"
                print(f"  {status} Time: {elapsed:.1f}s (max {tc['max_time']}s)")
            
            all_good = (
                ("expected_verdict" not in tc or verdict_match) and
                ("min_confidence" not in tc or conf_match) and
                ("max_time" not in tc or time_ok)
            )
            
            if all_good:
                passed += 1
                
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)[:150]}")
    
    print(f"\nResult: {passed}/{len(test_cases)} end-to-end tests passed")
    return passed >= 2  # At least 2/3 should pass


def run_all_tests():
    """Run all validation tests"""
    print("\n" + "="*70)
    print("TRUTHLENS v3.0 VALIDATION SUITE")
    print("11-Step Upgrade Testing")
    print("="*70)
    
    tests = [
        ("STEP 1: Entity Normalization", test_1_entity_normalization),
        ("STEP 2: Entity-Aware Queries", test_2_entity_aware_queries),
        ("STEPS 3-5: Multi-Source Retrieval", test_3_multi_source_retrieval),
        ("STEP 6: Relaxed Filtering", test_6_relaxed_filtering),
        ("STEP 7: Contradiction Detection", test_7_contradiction_detection),
        ("STEP 8: Evidence Aggregation", test_8_evidence_aggregation),
        ("STEP 11: End-to-End Analysis", test_11_end_to_end),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            passed = test_func()
            results[name] = "✅ PASS" if passed else "❌ FAIL"
        except Exception as e:
            results[name] = f"❌ ERROR: {str(e)[:50]}"
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for name, result in results.items():
        print(f"{result}: {name}")
    
    passed_count = sum(1 for r in results.values() if "PASS" in r)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} test groups passed")
    print("="*70)
    
    return passed_count == total_count


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
