#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, '/Users/pratyush/ai truthlens/backend')

print("=== Testing Database Connection ===")

# Test 1: Check file paths
backend_dir = Path("/Users/pratyush/ai truthlens/backend")
project_root = backend_dir.parent
db_dir = project_root / "data"
db_file = db_dir / "truthlens.db"

print(f"\n1. File paths:")
print(f"   Project root: {project_root}")
print(f"   DB dir: {db_dir}")
print(f"   DB file: {db_file}")
print(f"   DB file exists: {db_file.exists()}")

# Test 2: Direct SQLite conn
print(f"\n2. Direct sqlite3 connection:")
try:
    import sqlite3
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    print("   ✓ Direct sqlite3 works")
    conn.close()
except Exception as e:
    print(f"   ✗ Direct sqlite3 failed: {e}")

# Test 3: PostgreSQL module
print(f"\n3. Loading database module:")
try:
    # Force fresh import
    if 'database.postgres' in sys.modules:
        del sys.modules['database.postgres']
    from database.postgres import DATABASE_URL, engine
    print(f"   DATABASE_URL: {DATABASE_URL}")
    
    # Try to connect
    connection = engine.connect()
    print("   ✓ SQLAlchemy engine connection works")
    connection.close()
except Exception as e:
    print(f"   ✗ SQLAlchemy connection failed: {type(e).__name__}: {e}")

print("\n=== Done ===")
