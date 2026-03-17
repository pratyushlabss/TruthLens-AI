#!/bin/bash

###########################################################################
# TruthLens v2.0 - Multi-Level Verification Pipeline Testing Suite
# 
# Tests the three critical scenarios:
# 1. Death/Breaking News Hoax Detection
# 2. Evidence Override (Mixed Evidence)
# 3. Unverified Rumor Classification
###########################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

API_URL="http://localhost:3001/api/analyze"
PAUSE_BETWEEN_TESTS=3

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  TruthLens v2.0 - Fact-Check Pipeline Test Suite${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"

# Function to test a single claim
test_claim() {
    local test_name=$1
    local claim=$2
    local url=${3:-""}
    local expected_verdict=$4
    
    echo -e "${YELLOW}Test: ${test_name}${NC}"
    echo -e "Claim: \"${claim}\""
    
    if [ -n "$url" ]; then
        echo -e "URL: ${url}"
    fi
    
    echo -e "Expected Verdict: ${expected_verdict}\n"
    
    # Build curl command
    if [ -n "$url" ]; then
        response=$(curl -s -X POST "$API_URL" \
            -F "text=${claim}" \
            -F "url=${url}")
    else
        response=$(curl -s -X POST "$API_URL" \
            -F "text=${claim}")
    fi
    
    # Parse response
    verdict=$(echo "$response" | jq -r '.verdict')
    confidence=$(echo "$response" | jq -r '.confidence')
    reasoning=$(echo "$response" | jq -r '.reasoning' | head -c 150)
    
    # Color-code based on verdict
    if [ "$verdict" == "FAKE" ]; then
        verdict_color="${RED}${verdict}${NC}"
    elif [ "$verdict" == "REAL" ]; then
        verdict_color="${GREEN}${verdict}${NC}"
    else
        verdict_color="${YELLOW}${verdict}${NC}"
    fi
    
    echo -e "Result:"
    echo -e "  Verdict: ${verdict_color} (${confidence})"
    echo -e "  Reasoning: ${reasoning}...\n"
    
    # Verify result
    if [ "$verdict" == "$expected_verdict" ]; then
        echo -e "${GREEN}✓ PASS${NC}\n"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Got ${verdict}, expected ${expected_verdict})\n"
        return 1
    fi
}

# Scenario 1: Death/Breaking News Hoax
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo -e "${BLUE}SCENARIO 1: Death/Breaking News Hoax Detection${NC}"
echo -e "${BLUE}Detects death/arrest keywords with zero supporting evidence${NC}"
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}\n"

test_claim \
    "Elon Musk Death Hoax" \
    "Elon Musk confirmed dead in tragic car accident - breaking news" \
    "" \
    "FAKE"

sleep $PAUSE_BETWEEN_TESTS

# Scenario 2: Mixed Evidence Override
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo -e "${BLUE}SCENARIO 2: Evidence Override (Contradictory Evidence)${NC}"
echo -e "${BLUE}Evidence contradicts NLP - verdict forced to FAKE${NC}"
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}\n"

test_claim \
    "Climate Change Denial" \
    "Climate change is not caused by human activity" \
    "https://www.ipcc.ch/report/ar6/wg1/" \
    "FAKE"

sleep $PAUSE_BETWEEN_TESTS

# Scenario 3: Unverified Rumor
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo -e "${BLUE}SCENARIO 3: Unverified Rumor (No Evidence)${NC}"
echo -e "${BLUE}No online sources found → classified as RUMOR${NC}"
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}\n"

test_claim \
    "Local Politician Rumor" \
    "A local politician secretly owns three luxury mansions worth millions" \
    "" \
    "RUMOR"

sleep $PAUSE_BETWEEN_TESTS

# Bonus: Control Test - Real Claim
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo -e "${BLUE}CONTROL TEST: Factual Scientific Claim${NC}"
echo -e "${BLUE}Should be classified as REAL with high confidence${NC}"
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}\n"

test_claim \
    "Water Boils at 100°C" \
    "Water boils at 100 degrees Celsius at sea level" \
    "" \
    "REAL"

sleep $PAUSE_BETWEEN_TESTS

# Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Test Suite Complete${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}Notes:${NC}"
echo -e "  • First request may take 30-60 seconds (model loading)"
echo -e "  • Subsequent requests will be faster (3-8 seconds)"
echo -e "  • Ensure frontend is running: npm run dev"
echo -e "  • Backend API at localhost:3001/api/analyze\n"

