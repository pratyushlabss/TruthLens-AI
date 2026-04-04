#!/usr/bin/env python3
"""Test: Evidence list is never empty and processing_time > 0"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.pipeline_new import ProductionRAGPipeline
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def test_evidence_never_empty():
    """Test that evidence is never empty even with over-filtering."""
    pipeline = ProductionRAGPipeline(use_nli=False, device="cpu")
    
    test_claims = [
        "Obama is dead",
        "Einstein invented the light bulb",
        "Biden is the president",
        "Tesla founded in 1903",
    ]
    
    print("\n" + "="*80)
    print("TEST: Evidence Never Empty + Processing Time > 0")
    print("="*80)
    
    failed = []
    passed = []
    
    for claim in test_claims:
        print(f"\n📝 Testing: '{claim}'")
        
        try:
            result = pipeline.analyze(claim)
            
            # CHECK 1: Evidence list should not be empty
            evidence = result.get("evidence", [])
            evidence_count = len(evidence)
            
            if evidence_count == 0:
                logger.error(f"❌ FAIL: Evidence list is EMPTY!")
                failed.append((claim, "Empty evidence"))
                continue
            else:
                logger.info(f"✅ PASS: Evidence count = {evidence_count}")
            
            # CHECK 2: Processing time should be > 0
            processing_ms = result.get("metadata", {}).get("processing_time_ms", 0)
            
            if processing_ms <= 0:
                logger.error(f"❌ FAIL: Processing time = {processing_ms}ms (should be > 0)")
                failed.append((claim, f"Processing time = {processing_ms}"))
                continue
            else:
                logger.info(f"✅ PASS: Processing time = {processing_ms:.1f}ms")
            
            # CHECK 3: Confidence should be set
            confidence = result.get("confidence_percentage", 0)
            logger.info(f"✅ Confidence = {confidence}%")
            
            # CHECK 4: Verdict should not be ERROR
            verdict = result.get("verdict", "")
            if verdict == "ERROR":
                logger.error(f"❌ FAIL: Verdict is ERROR")
                failed.append((claim, "Verdict = ERROR"))
                continue
            else:
                logger.info(f"✅ Verdict = {verdict}")
            
            passed.append(claim)
            
        except Exception as e:
            logger.error(f"❌ EXCEPTION: {e}")
            failed.append((claim, str(e)))
    
    # Summary
    print("\n" + "="*80)
    print(f"RESULTS: {len(passed)}/{len(test_claims)} PASSED")
    print("="*80)
    
    if passed:
        print("\n✅ PASSED:")
        for claim in passed:
            print(f"  • {claim}")
    
    if failed:
        print("\n❌ FAILED:")
        for claim, reason in failed:
            print(f"  • {claim}")
            print(f"    Reason: {reason}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_evidence_never_empty()
    sys.exit(0 if success else 1)
