#!/usr/bin/env python3
"""Test TruthLens AI with 5 sample claims"""
import os
import sys
sys.path.insert(0, '/Users/pratyush/ai truthlens')

from dotenv import load_dotenv
load_dotenv()

print("=" * 80)
print("TRUTHLENS AI - TESTING ALL 5 CLAIMS")
print("=" * 80)

# Verify API key
api_key = os.getenv('OPENAI_API_KEY', '')
if not api_key:
    print("❌ OPENAI_API_KEY not found in .env")
    sys.exit(1)

print(f"✅ OpenAI API Key loaded: {api_key[:15]}...")

# Import and initialize pipeline
print("\n📦 Initializing RAG Pipeline...")
try:
    from backend.services.pipeline_new import ProductionRAGPipeline
    pipeline = ProductionRAGPipeline(
        use_nli=False,
        embedder_model="all-MiniLM-L6-v2",
        device="cpu",
        top_k_evidence=5
    )
    print("✅ Pipeline initialized")
except Exception as e:
    print(f"❌ Pipeline init failed: {e}")
    sys.exit(1)

# Test claims
test_claims = [
    ("Obama is dead", "MISINFORMATION", "❌"),
    ("Earth is flat", "MISINFORMATION", "❌"),
    ("Einstein won Nobel Prize", "TRUE", "✅"),
    ("Water is wet", "TRUE", "✅"),
    ("asdfgh jkl", "UNCERTAIN", "❓"),
]

print("\n" + "=" * 80)
print("RUNNING TESTS")
print("=" * 80)

results = []
for i, (claim, expected, emoji) in enumerate(test_claims, 1):
    print(f"\n[TEST {i}] {emoji} {claim}")
    print(f"  Expected: {expected}")
    
    try:
        result = pipeline.analyze(claim, top_k_evidence=3)
        
        if result.get('success'):
            verdict = result.get('verdict', 'UNKNOWN')
            confidence = result.get('confidence', 0.0)
            evidence_count = len(result.get('evidence', []))
            
            passed = verdict == expected
            status = "✅ PASS" if passed else "❌ FAIL"
            
            print(f"  Actual:   {verdict} (confidence: {confidence:.1%})")
            print(f"  Evidence: {evidence_count} sources")
            print(f"  Status:   {status}")
            
            results.append((claim, expected, verdict, passed))
        else:
            error = result.get('metadata', {}).get('error', 'Unknown')
            print(f"  ❌ Failed: {error}")
            results.append((claim, expected, "ERROR", False))
            
    except Exception as e:
        print(f"  ❌ Exception: {str(e)[:80]}")
        results.append((claim, expected, "EXCEPTION", False))

# Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

passed_count = sum(1 for _, _, _, p in results if p)
total_count = len(results)

for claim, expected, actual, passed in results:
    emoji = "✅" if passed else "❌"
    print(f"{emoji} {claim[:35]:35} → {actual:15} (expected: {expected})")

print(f"\n📊 Results: {passed_count}/{total_count} tests passed")

if passed_count == total_count:
    print("🎉 ALL TESTS PASSED!")
else:
    print(f"⚠️  {total_count - passed_count} test(s) need attention")
