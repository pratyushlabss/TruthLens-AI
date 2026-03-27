#!/usr/bin/env python3
"""Test database persistence"""

import sys
import os
sys.path.insert(0, '/Users/pratyush/ai truthlens/backend')

from database.postgres import SessionLocal
from database.models import User, Session, Query, Base
from database.postgres import engine
import uuid

print("Testing database persistence...\n")

# Initialize database
print("1. Initializing database tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("   ✅ Database tables created/verified")
except Exception as e:
    print(f"   ❌ Failed to create tables: {e}")
    sys.exit(1)

# Create database session
db = SessionLocal()

# Test 1: Create a user
print("\n2. Creating a test user...")
try:
    user_id = str(uuid.uuid4())
    test_user = User(
        user_id=user_id,
        email="dbtest@example.com",
        password_hash="hashed_password_123",
        username="dbtest_user"
    )
    db.add(test_user)
    db.commit()
    print(f"   ✅ User created: {test_user.email} (ID: {user_id})")
except Exception as e:
    print(f"   ❌ Failed to create user: {e}")
    db.rollback()
    sys.exit(1)

# Test 2: Retrieve the user
print("\n3. Retrieving user from database...")
try:
    retrieved_user = db.query(User).filter(User.email == "dbtest@example.com").first()
    if retrieved_user:
        print(f"   ✅ User retrieved: {retrieved_user.email}")
        print(f"      - User ID: {retrieved_user.user_id}")
        print(f"      - Username: {retrieved_user.username}")
    else:
        print("   ❌ User not found in database")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Failed to retrieve user: {e}")
    sys.exit(1)

# Test 3: Create a session
print("\n4. Creating a session for the user...")
try:
    session_id = str(uuid.uuid4())
    test_session = Session(
        session_id=session_id,
        user_id=user_id,
        title="Test Session"
    )
    db.add(test_session)
    db.commit()
    print(f"   ✅ Session created: {test_session.title} (ID: {session_id})")
except Exception as e:
    print(f"   ❌ Failed to create session: {e}")
    db.rollback()
    sys.exit(1)

# Test 4: Create a query
print("\n5. Creating a query in the session...")
try:
    query_id = str(uuid.uuid4())
    test_query = Query(
        query_id=query_id,
        session_id=session_id,
        input_text="Test claim: The Earth is round",
        verdict="TRUE",
        confidence=95.0,
        score_real=95.0,
        score_rumor=2.0,
        score_fake=3.0,
        propagation_risk="LOW",
        propagation_score=5.0,
        evidence_score=95.0,
        summary="The claim is well-supported by scientific evidence",
        key_signals=["Scientific consensus", "Multiple sources"],
        claims=["The Earth is round"],
        evidence_sources=["NASA", "Scientific journals"]
    )
    db.add(test_query)
    db.commit()
    print(f"   ✅ Query created: {test_query.input_text[:50]}... (ID: {query_id})")
except Exception as e:
    print(f"   ❌ Failed to create query: {e}")
    db.rollback()
    sys.exit(1)

# Test 5: Retrieve all data
print("\n6. Retrieving all queries for user...")
try:
    user_sessions = db.query(Session).filter(Session.user_id == user_id).all()
    all_queries = []
    for session in user_sessions:
        queries = db.query(Query).filter(Query.session_id == session.session_id).all()
        all_queries.extend(queries)
    
    print(f"   ✅ Found {len(user_sessions)} session(s) and {len(all_queries)} query/queries")
    for query in all_queries:
        print(f"      - {query.input_text[:50]}... (Verdict: {query.verdict})")
except Exception as e:
    print(f"   ❌ Failed to retrieve queries: {e}")
    sys.exit(1)

# Test 6: Test user relationships
print("\n7. Testing relationship navigation...")
try:
    # Get user with sessions
    user_with_sessions = db.query(User).filter(User.user_id == user_id).first()
    if user_with_sessions and user_with_sessions.sessions:
        session = user_with_sessions.sessions[0]
        print(f"   ✅ Navigation: User → Session: {session.title}")
        if session.queries:
            query = session.queries[0]
            print(f"   ✅ Navigation: Session → Query: {query.input_text[:50]}...")
    else:
        print("   ⚠️  No sessions found via relationship")
except Exception as e:
    print(f"   ❌ Failed to navigate relationships: {e}")
    sys.exit(1)

# Cleanup
print("\n8. Cleaning up test data...")
try:
    db.query(Query).filter(Query.query_id == query_id).delete()
    db.query(Session).filter(Session.session_id == session_id).delete()
    db.query(User).filter(User.user_id == user_id).delete()
    db.commit()
    print("   ✅ Test data cleaned up")
except Exception as e:
    print(f"   ❌ Failed to cleanup: {e}")
    db.rollback()

db.close()

print("\n" + "="*60)
print("✅ Database persistence test PASSED!")
print("="*60 + "\n")
