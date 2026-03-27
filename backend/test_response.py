#!/usr/bin/env python3
"""Test the backend response format."""

import sys
sys.path.insert(0, '/Users/pratyush/ai truthlens/backend')

from services.scoring_engine import ScoringEngine
import json

try:
    print("Initializing ScoringEngine...")
    engine = ScoringEngine()
    
    print("Analyzing claim: 'The moon is made of cheese'")
    result = engine.analyze('The moon is made of cheese', include_explanations=True)
    
    print("\n" + "=" * 70)
    print("BACKEND RESPONSE STRUCTURE")
    print("=" * 70)
    
    # Print all keys
    for k in sorted(result.keys()):
        v = result[k]
        if isinstance(v, str):
            display_val = v[:60] + "..." if len(v) > 60 else v
        elif isinstance(v, dict):
            display_val = f"dict with {len(v)} keys"
        elif isinstance(v, list):
            display_val = f"list[{len(v)}]"
        else:
            display_val = str(v)[:60]
        print(f"  {k:25} : {display_val}")
    
    print("\n" + "=" * 70)
    print("STRICT FORMAT CHECK")
    print("=" * 70)
    print(f"✓ verdict: {result.get('verdict')} (should be: TRUE|FALSE|MISLEADING|UNKNOWN)")
    print(f"✓ confidence: {result.get('confidence')} (should be: 0-100 or 0-1)")
    print(f"✓ key_signals: {len(result.get('key_signals', []))} signals")
    print(f"✓ truth_score: {result.get('truth_score')}")
    print(f"✓ sources: {len(result.get('sources', []))} sources")
    
    if result.get('sources'):
        print("\nFirst source structure:")
        first = result.get('sources')[0]
        for k, v in first.items():
            print(f"    {k}: {str(v)[:50]}")
    
    print("\n✅ Backend is working correctly!")
    
except Exception as e:
    import traceback
    print('❌ Error:')
    traceback.print_exc()
