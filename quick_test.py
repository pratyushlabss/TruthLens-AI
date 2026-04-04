#!/usr/bin/env python3
"""Quick focused test of one claim to verify bugs are fixed"""
import os
import sys
sys.path.insert(0, '/Users/pratyush/ai truthlens')

from dotenv import load_dotenv
load_dotenv()

# Verify API key
api_key = os.getenv('OPENAI_API_KEY', '')
print(f"🔑 OpenAI API Key: {api_key[:20] if api_key else 'NOT SET'}...")

if not api_key:
    print("❌ OPENAI_API_KEY not found in .env")
    sys.exit(1)

print("\n📦 Importing pipeline...")
try:
    from backend.services.pipeline_new import ProductionRAGPipeline
    print("✅ Pipeline imported successfully")
except Exception as e:
    print(f"❌ Failed to import pipeline: {e}")
    sys.exit(1)

print("\n🚀 Initializing pipeline...")
try:
    pipeline = ProductionRAGPipeline(use_nli=False, device="cpu", top_k_evidence=3)
    print("✅ Pipeline initialized")
except Exception as e:
    print(f"❌ Failed to initialize pipeline: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test ONE claim
print("\n" + "="*70)
print("TESTING: Einstein won Nobel Prize")
print("="*70)

try:
    result = pipeline.analyze("Einstein won Nobel Prize", top_k_evidence=3)
    
    print(f"\n✅ Analysis completed!")
    print(f"   Verdict: {result.get('verdict', 'UNKNOWN')}")
    print(f"   Confidence: {result.get('confidence', 'N/A')}")
    print(f"   Evidence returned: {len(result.get('evidence', []))}")
    
    # Show evidence
    evidence = result.get('evidence', [])
    if evidence:
        print(f"\n   Evidence details:")
        for i, ev in enumerate(evidence[:2], 1):
            print(f"   [{i}] {type(ev)} - Keys: {list(ev.keys()) if isinstance(ev, dict) else 'not a dict'}")
            if isinstance(ev, dict):
                print(f"        Sentence: {ev.get('sentence', '')[:60]}...")
    else:
        print(f"\n   Full result dict: {result}")
    
    # Check if verdict is correct (should be TRUE)
    if result.get('verdict') == 'TRUE':
        print("\n✅ TEST PASSED - Verdict is TRUE (as expected)")
    else:
        print(f"\n❌ TEST FAILED - Expected TRUE, got {result.get('verdict')}")
        
except Exception as e:
    print(f"\n❌ Analysis failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
