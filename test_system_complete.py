#!/usr/bin/env python3
"""Complete system test for TruthLens AI"""

import requests
import json
import time
import sys
import os

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def log_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def log_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def log_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

def log_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            log_success(f"Health check: {data['status']}")
            return True
        else:
            log_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Health check error: {e}")
        return False

def test_signup(email, password, username):
    """Test user signup"""
    try:
        payload = {
            "email": email,
            "password": password,
            "username": username
        }
        response = requests.post(
            f"{BACKEND_URL}/auth/signup",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user = data.get("user")
            log_success(f"Signup successful: {user['email']}")
            return token, user
        else:
            log_error(f"Signup failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        log_error(f"Signup error: {e}")
        return None, None

def test_login(email, password):
    """Test user login"""
    try:
        payload = {
            "email": email,
            "password": password
        }
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user = data.get("user")
            log_success(f"Login successful: {user['email']}")
            return token, user
        else:
            log_error(f"Login failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        log_error(f"Login error: {e}")
        return None, None

def test_me(token):
    """Test get current user"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BACKEND_URL}/auth/me",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user = response.json()
            log_success(f"Get user successful: {user['email']}")
            return user
        else:
            log_error(f"Get user failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        log_error(f"Get user error: {e}")
        return None

def test_analyze(token, claim):
    """Test claim analysis"""
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        data = {"text": claim}
        
        response = requests.post(
            f"{BACKEND_URL}/api/analyze",
            data=data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            verdict = result.get("verdict", "UNKNOWN")
            confidence = result.get("confidence", 0)
            log_success(f"Analysis successful: {verdict} ({confidence}% confidence)")
            return result
        else:
            log_error(f"Analysis failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        log_error(f"Analysis error: {e}")
        return None

def main():
    print(f"\n{BLUE}{'='*60}")
    print("TruthLens AI - Complete System Test")
    print(f"{'='*60}{RESET}\n")
    
    # Test 1: Health check
    print(f"{BLUE}[Test 1] Health Check{RESET}")
    if not test_health():
        log_error("Backend not responding. Please start the server:")
        log_info("cd backend && python3 -m uvicorn main:app --port 8000")
        return False
    print()
    
    # Test 2: Signup
    print(f"{BLUE}[Test 2] User Signup{RESET}")
    test_email = f"test{int(time.time())}@example.com"
    test_password = "TestPassword123!"
    test_username = f"testuser{int(time.time())}"
    
    signup_token, signup_user = test_signup(test_email, test_password, test_username)
    if not signup_token:
        log_error("Signup failed. Exiting tests.")
        return False
    print()
    
    # Test 3: Login
    print(f"{BLUE}[Test 3] User Login{RESET}")
    login_token, login_user = test_login(test_email, test_password)
    if not login_token:
        log_error("Login failed. Exiting tests.")
        return False
    print()
    
    # Test 4: Get current user
    print(f"{BLUE}[Test 4] Get Current User{RESET}")
    current_user = test_me(login_token)
    if not current_user:
        log_error("Get user failed. Exiting tests.")
        return False
    print()
    
    # Test 5: Analyze claim
    print(f"{BLUE}[Test 5] Analyze Claim{RESET}")
    test_claim = "The Earth is flat"
    analysis = test_analyze(login_token, test_claim)
    if not analysis:
        log_error("Analysis failed. Exiting tests.")
        return False
    
    # Print analysis details
    log_info(f"Verdict: {analysis.get('verdict')}")
    log_info(f"Confidence: {analysis.get('confidence')}")
    log_info(f"Explanation: {analysis.get('explanation', 'N/A')}")
    log_info(f"Signals: {analysis.get('signals', [])}")
    log_info(f"Sources: {len(analysis.get('sources', []))} sources found")
    print()
    
    # Test 6: Anonymous analysis
    print(f"{BLUE}[Test 6] Anonymous Analysis (no token){RESET}")
    anon_analysis = test_analyze(None, "COVID-19 is a hoax")
    if not anon_analysis:
        log_warning("Anonymous analysis failed (might be expected if auth required)")
    else:
        log_success("Anonymous analysis works")
    print()
    
    # Summary
    print(f"{BLUE}{'='*60}")
    print("Test Summary")
    print(f"{'='*60}{RESET}")
    log_success("✅ All critical tests passed!")
    print(f"\n{GREEN}System is operational!{RESET}\n")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        sys.exit(1)
