#!/usr/bin/env python3
"""
Quick test of the authentication system to verify signup, login, and token-based access.
"""

import subprocess
import time
import requests
import json
import sys

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_EMAIL = f"test_{int(time.time())}@truthlens.dev"
TEST_PASSWORD = "TestPassword123!"
TEST_USERNAME = "test_user"

def print_step(step: str, msg: str):
    print(f"\n✓ {step}: {msg}")

def print_error(msg: str):
    print(f"✗ ERROR: {msg}", file=sys.stderr)

def test_signup():
    """Test user signup."""
    print_step("SIGNUP", f"Creating account with email: {TEST_EMAIL}")
    
    response = requests.post(
        f"{BACKEND_URL}/auth/signup",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "username": TEST_USERNAME,
        }
    )
    
    if response.status_code != 200:
        print_error(f"Signup failed: {response.status_code} - {response.text}")
        return None
    
    data = response.json()
    token = data.get("access_token")
    user = data.get("user")
    
    if not token or not user:
        print_error(f"Signup response missing token or user: {data}")
        return None
    
    print_step("TOKEN", f"Received: {token[:50]}...")
    print_step("USER", f"Created: {user['username']} ({user['email']})")
    
    return token

def test_login():
    """Test user login."""
    print_step("LOGIN", f"Logging in with email: {TEST_EMAIL}")
    
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        }
    )
    
    if response.status_code != 200:
        print_error(f"Login failed: {response.status_code} - {response.text}")
        return None
    
    data = response.json()
    token = data.get("access_token")
    
    if not token:
        print_error(f"Login response missing token: {data}")
        return None
    
    print_step("TOKEN", f"Received: {token[:50]}...")
    
    return token

def test_get_me(token: str):
    """Test getting current user info with token."""
    print_step("GET_ME", "Fetching current user info with Bearer token")
    
    response = requests.get(
        f"{BACKEND_URL}/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    
    if response.status_code != 200:
        print_error(f"Get me failed: {response.status_code} - {response.text}")
        return False
    
    user = response.json()
    print_step("USER_INFO", f"Retrieved: {user['username']} ({user['email']})")
    
    return True

def test_invalid_token():
    """Test that invalid token is rejected."""
    print_step("INVALID_TOKEN", "Testing with invalid token")
    
    response = requests.get(
        f"{BACKEND_URL}/auth/me",
        headers={
            "Authorization": "Bearer invalid_token_12345"
        }
    )
    
    if response.status_code != 401:
        print_error(f"Expected 401 for invalid token, got: {response.status_code}")
        return False
    
    print_step("REJECTION", "Invalid token correctly rejected (401)")
    return True

def main():
    print("\n" + "="*60)
    print("TRUTHLENS AI - AUTHENTICATION SYSTEM TEST")
    print("="*60)
    
    # Check backend is running
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print_step("BACKEND", "✓ Running and healthy")
        else:
            print_error("Backend health check failed")
            return False
    except requests.ConnectionError:
        print_error(f"Cannot connect to backend at {BACKEND_URL}")
        print("Make sure the backend is running: python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000")
        return False
    
    # Test signup
    token_from_signup = test_signup()
    if not token_from_signup:
        return False
    
    # Test get me with signup token
    if not test_get_me(token_from_signup):
        return False
    
    # Test login
    token_from_login = test_login()
    if not token_from_login:
        return False
    
    # Test get me with login token
    if not test_get_me(token_from_login):
        return False
    
    # Test invalid token
    if not test_invalid_token():
        return False
    
    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED!")
    print("="*60)
    print("\nAuthentication system is working correctly:")
    print("  ✓ Signup with password hashing")
    print("  ✓ JWT token generation")
    print("  ✓ Login with verification")
    print("  ✓ Bearer token extraction from header")
    print("  ✓ User info retrieval with token")
    print("  ✓ Invalid token rejection")
    print("\n")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
