#!/usr/bin/env python
"""Minimal app startup test - fast verification without model loading."""

import sys
import os

print("🚀 Starting TruthLens AI Backend...")
print("=" * 60)

# Step 1: Verify Python version
print(f"\n[1/4] Python version: {sys.version}")
if sys.version_info < (3, 9):
    print("❌ Python 3.9+ required")
    sys.exit(1)
print("✅ Python version OK")

# Step 2: Import FastAPI app (without loading models)
print("\n[2/4] Loading FastAPI application...")
try:
    from main import app
    print("✅ FastAPI app loaded successfully")
except Exception as e:
    print(f"❌ Failed to load app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Test health endpoint
print("\n[3/4] Testing health endpoint...")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/health")
    if response.status_code == 200:
        print(f"✅ Health endpoint OK: {response.json()}")
    else:
        print(f"❌ Health endpoint returned {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Failed to test health endpoint: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Start server
print("\n[4/4] Starting Uvicorn server...")
print("=" * 60)
print("\n🎉 TruthLens AI Backend is ready!\n")
print("📡 API Running on: http://0.0.0.0:8000")
print("📚 API Docs:      http://0.0.0.0:8000/docs")
print("💚 Health Check:  http://0.0.0.0:8000/health")
print("\n(Models will be loaded on first API request)\n")
print("=" * 60 + "\n")

# Import uvicorn and run
try:
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("ENV", "development") == "development"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=os.getenv("LOG_LEVEL", "info")
    )
except KeyboardInterrupt:
    print("\n\n🛑 Server stopped")
    sys.exit(0)
except Exception as e:
    print(f"❌ Failed to start server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
