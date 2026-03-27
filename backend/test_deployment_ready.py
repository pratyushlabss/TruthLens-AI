#!/usr/bin/env python3
"""Deployment Readiness Verification Test"""

import sys
import logging

logging.basicConfig(level=logging.INFO)

def main():
    print("\n" + "="*70)
    print("  TRUTHLENS AI - DEPLOYMENT READINESS CHECK")
    print("="*70)
    
    # Test 1: App imports without models
    print("\n[TEST 1] Checking app imports (no eager model loading)...")
    try:
        from main import app
        print("        ✓ PASS - FastAPI app loaded successfully")
    except Exception as e:
        print(f"        ✗ FAIL - {e}")
        return False
    
    # Test 2: Models aren't loaded at startup
    print("\n[TEST 2] Verifying models are lazy-loaded...")
    try:
        from services.scoring_engine import ScoringEngine
        engine = ScoringEngine()
        if engine.nlp_model is None:
            print("        ✓ PASS - Models are lazy (None until first request)")
        else:
            print("        ✗ FAIL - Models loaded at startup (not lazy)")
            return False
    except Exception as e:
        print(f"        ✗ FAIL - {e}")
        return False
    
    # Test 3: Health endpoint works
    print("\n[TEST 3] Testing health endpoint (no models needed)...")
    try:
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/health")
        if response.status_code == 200:
            data = response.json()
            print(f"        ✓ PASS - Health check OK")
            print(f"              Service: {data.get('service', 'Unknown')}")
            print(f"              Status: {data.get('status', 'Unknown')}")
        else:
            print(f"        ✗ FAIL - Got HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"        ✗ FAIL - {e}")
        return False
    
    # Test 4: Check routes
    print("\n[TEST 4] Checking API routes...")
    try:
        routes = [r.path for r in app.routes]
        analyze_route = "/api/analyze" in routes
        if analyze_route:
            print(f"        ✓ PASS - Found {len(routes)} routes")
            print(f"              Including /api/analyze endpoint")
        else:
            print(f"        ✗ FAIL - /api/analyze route not found")
            return False
    except Exception as e:
        print(f"        ✗ FAIL - {e}")
        return False
    
    # All tests passed
    print("\n" + "="*70)
    print("  ✓ ALL DEPLOYMENT TESTS PASSED!")
    print("="*70)
    print("\n  🚀 System is ready for deployment\n")
    print("  Quick Start Options:")
    print("  ──────────────────")
    print("  1. Local development:  ./deploy.sh")
    print("  2. Docker production:  docker-compose -f docker-compose.prod.yml up")
    print("  3. Manual backend:     python -m uvicorn main:app --port 8000")
    print("\n  📝 First API request will take 30-60 seconds (models load)")
    print("  💚 All subsequent requests will be fast (cached models)")
    print("\n" + "="*70 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
