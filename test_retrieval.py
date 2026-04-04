#!/usr/bin/env python3
"""Test just the retrieval part to debug"""
import os
import sys
sys.path.insert(0, '/Users/pratyush/ai truthlens')

from dotenv import load_dotenv
load_dotenv()

print("📦 Importing retrieval...")
try:
    from backend.services.retrieval_new import RetrievalPipeline
    print("✅ Retrieval imported")
except Exception as e:
    print(f"❌ Failed to import: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🚀 Initializing retrieval...")
try:
    retrieval = RetrievalPipeline(top_k_sents=5, include_url=True)
    print("✅ Retrieval initialized")
except Exception as e:
    print(f"❌ Failed to initialize: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🔍 Testing retrieval with: 'Einstein won Nobel Prize'")
try:
    results = retrieval.search("Einstein won Nobel Prize", top_k_sentences=5)
    
    print(f"\n✅ Retrieval completed!")
    print(f"   Type: {type(results)}")
    print(f"   Length: {len(results) if results else 0}")
    
    if results:
        print(f"\n   Evidence sentences found: {len(results)}")
        for i, sent in enumerate(results[:3], 1):
            print(f"   [{i}] {sent[:100]}...")
    else:
        print("   ⚠️  No evidence found!")
        
except Exception as e:
    print(f"\n❌ Retrieval failed: {e}")
    import traceback
    traceback.print_exc()
