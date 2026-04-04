#!/usr/bin/env python3
"""Quick end-to-end integration test with real API keys"""

import sys
sys.path.insert(0, '/Users/pratyush/ai truthlens')

from dotenv import load_dotenv
load_dotenv()

def test_quick():
    """Quick test of pipeline"""
    from backend.config.env_config import EnvironmentConfig
    from backend.services.pipeline_new import ProductionRAGPipeline
    
    print("\n" + "="*70)
    print("QUICK END-TO-END TEST")
    print("="*70)
    
    # Show config
    print("\n✅ Configuration:")
    print(f"  OPENAI: {EnvironmentConfig.OPENAI_API_KEY[:20]}...")
    print(f"  TAVILY: {EnvironmentConfig.TAVILY_API_KEY[:20]}...")
    
    # Initialize pipeline
    print("\n⏳ Initializing pipeline...")
    pipeline = ProductionRAGPipeline(use_nli=False, device="cpu")
    
    # Test claim
    claim = "is obama dead"
    print(f"\n📝 Testing with claim: '{claim}'")
    print(f"⏳ Analyzing (this may take 30-60s)...")
    
    result = pipeline.analyze(claim, top_k_evidence=3)
    
    print(f"\n✅ Analysis complete!")
    print(f"   Verdict: {result.get('verdict', '?')}")
    print(f"   Confidence: {result.get('confidence', 0):.2%}")
    print(f"   Evidence count: {len(result.get('evidence', []))}")
    
    # Breakdown
    metadata = result.get('metadata', {})
    print(f"\n📊 Evidence sources:")
    print(f"   Wikipedia articles: {metadata.get('total_articles_fetched', 0)}")
    print(f"   Sentences extracted: {metadata.get('total_sentences_extracted', 0)}")
    
    success = result.get('success', False)
    verdict_ok = result.get('verdict') in ['TRUE', 'MISINFORMATION', 'UNCERTAIN']
    
    print(f"\n{'✅' if success else '❌'} Pipeline success: {success}")
    print(f"{'✅' if verdict_ok else '❌'} Verdict format valid: {verdict_ok}")
    
    return success and verdict_ok

if __name__ == "__main__":
    try:
        success = test_quick()
        print("\n" + "="*70)
        if success:
            print("🎉 END-TO-END TEST PASSED")
            print("Status: ✅ System fully operational")
        else:
            print("❌ END-TO-END TEST FAILED")
            print("Status: ❌ Issues detected")
        print("="*70 + "\n")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
