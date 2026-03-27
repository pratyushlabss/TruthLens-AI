#!/usr/bin/env python3
"""
Quick test of the new evidence-first pipeline.
"""

import sys
sys.path.insert(0, '/Users/pratyush/ai truthlens/backend')

from services.scoring_engine import ScoringEngine
import json

def test_pipeline():
    """Test the new evidence-first pipeline."""
    print("\n" + "="*80)
    print("TESTING EVIDENCE-FIRST PIPELINE")
    print("="*80 + "\n")
    
    # Initialize engine
    print("[1] Initializing ScoringEngine...")
    try:
        engine = ScoringEngine()
        print("✓ ScoringEngine initialized successfully\n")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}\n")
        return False
    
    # Test claim
    test_claim = "Water boils at 100 degrees Celsius"
    print(f"[2] Testing with claim: '{test_claim}'\n")
    
    # Run analysis
    print("[3] Running analysis (this may take 30-60s for web scraping)...")
    try:
        result = engine.analyze(test_claim, include_explanations=False)
        print("✓ Analysis completed\n")
    except Exception as e:
        print(f"✗ Analysis failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    
    # Check response structure
    print("[4] Checking response structure:\n")
    
    required_fields = [
        "verdict", "confidence", "confidence_label",
        "sources", "summary", "reasoning", "metrics",
        "model_breakdown"
    ]
    
    for field in required_fields:
        if field in result:
            print(f"  ✓ {field}: present")
            if field == "sources" and isinstance(result[field], list):
                print(f"    └─ {len(result[field])} sources")
                if result[field]:
                    first_source = result[field][0]
                    print(f"    └─ First source: {first_source.get('name', 'N/A')} (credibility: {first_source.get('credibility', 'N/A')})")
            elif field == "metrics" and isinstance(result[field], dict):
                print(f"    └─ {json.dumps(result[field], indent=6)}")
        else:
            print(f"  ✗ {field}: MISSING")
    
    print("\n[5] Verdict Summary:")
    print(f"  Verdict: {result.get('verdict', 'N/A')}")
    print(f"  Confidence: {result.get('confidence', 'N/A')} ({result.get('confidence_label', 'N/A')})")
    print(f"\n  Summary: {result.get('summary', 'N/A')[:200]}...")
    print(f"\n  Reasoning: {result.get('reasoning', 'N/A')[:200]}...")
    
    print("\n" + "="*80)
    print("✓ PIPELINE TEST PASSED!")
    print("="*80 + "\n")
    
    return True

if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)
