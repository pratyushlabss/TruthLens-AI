#!/usr/bin/env python3
"""Test the complete auth flow without HTTP"""

import sys
sys.path.insert(0, '/Users/pratyush/ai truthlens/backend')

print("=" * 60)
print("Testing Complete Auth Flow")
print("=" * 60)

# Test 1: Database initialization
print("\n1. Testing Database...")
try:
    from database.postgres import SessionLocal, engine, DATABASE_URL
    from database.models import Base, User
    
    print(f"   Database URL: {DATABASE_URL}")
    print(f"   Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("   ✓ Database ready")
except Exception as e:
    print(f"   ✗ Database error: {e}")
    sys.exit(1)

# Test 2: Create test user if needed
print("\n2. Testing User Creation...")
try:
    from utils.security import hash_password, verify_password
    
    db = SessionLocal()
    # Clear existing
    db.query(User).filter(User.email == "test@test.com").delete()
    db.commit()
    
    # Create new
    hashed = hash_password("test123")
    user = User(email="test@test.com", password_hash=hashed, username="testuser")
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"   ✓ Test user created: {user.email}, ID: {user.user_id}")
    test_user_id = user.user_id
    db.close()
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# Test 3: Simulate login
print("\n3. Testing Login Flow...")
try:
    db = SessionLocal()
    
    # Find user
    user = db.query(User).filter(User.email == "test@test.com").first()
    if not user:
        print("   ✗ User not found")
        sys.exit(1)
    print(f"   ✓ User found: {user.email}")
    
    # Verify password
    if not verify_password("test123", user.password_hash):
        print("   ✗ Password verification failed")
        sys.exit(1)
    print(f"   ✓ Password verified")
    
    # Create token
    from utils.security import create_access_token
    token = create_access_token(user.user_id)
    print(f"   ✓ JWT token created")
    
    # Verify token
    from utils.security import verify_token
    payload = verify_token(token)
    print(f"   ✓ Token verified, user_id: {payload.get('user_id')}")
    
    db.close()
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED - Auth is working!")
print("=" * 60)
