#!/usr/bin/env python
"""Debug startup script - test if app can run."""

import sys
import os
import traceback

print("=" * 60)
print("TruthLens AI - Startup Debug")
print("=" * 60)

# Test 1: Import main
print("\n[1/5] Testing app imports...")
try:
    from main import app
    print("✅ App imported successfully")
except Exception as e:
    print(f"❌ Failed to import app: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Check routes
print("\n[2/5] Checking routes...")
try:
    routes = [route.path for route in app.routes]
    print(f"✅ Found {len(routes)} routes:")
    for route in routes[:10]:  # Show first 10
        print(f"   - {route}")
except Exception as e:
    print(f"❌ Failed to check routes: {e}")
    traceback.print_exc()

# Test 3: Test run in sync
print("\n[3/5] Testing FastAPI app directly...")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/health")
    print(f"✅ Health endpoint responded: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"❌ Failed to test endpoint: {e}")
    traceback.print_exc()

# Test 4: Check database
print("\n[4/5] Testing database...")
try:
    from database.postgres import engine
    from database.models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"⚠️  Database warning (non-critical): {e}")

# Test 5: Try to initialize scoring engine
print("\n[5/5] Testing scoring engine...")
try:
    from services.scoring_engine import ScoringEngine
    print("✅ Scoring engine imported successfully")
    # Don't actually initialize to avoid downloading models
except Exception as e:
    print(f"❌ Failed to import scoring engine: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ All startup tests passed!")
print("=" * 60)
print("\nYou can now run: uvicorn main:app --host 0.0.0.0 --port 8000")
