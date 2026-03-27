#!/bin/bash
# TruthLens AI - Deployment Testing Script
# Run this to verify everything works

set -e

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║   TruthLens AI - Deployment Test Suite        ║"
echo "║   March 17, 2026                              ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

VENV="/Users/pratyush/ai truthlens/.venv"
BACKEND="/Users/pratyush/ai truthlens/backend"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test 1: Python version
echo -e "${YELLOW}[TEST 1]${NC} Checking Python version..."
PYTHON_VERSION=$("$VENV/bin/python" --version 2>&1)
if [[ "$PYTHON_VERSION" == *"3."* ]]; then
    echo -e "${GREEN}✓${NC} $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3.x required"
    exit 1
fi

# Test 2: Virtual environment
echo -e "\n${YELLOW}[TEST 2]${NC} Checking virtual environment..."
if [ -d "$VENV" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists"
else
    echo -e "${RED}✗${NC} Virtual environment not found"
    exit 1
fi

# Test 3: App imports
echo -e "\n${YELLOW}[TEST 3]${NC} Testing app imports (no model loading)..."
"$VENV/bin/python" -c "from $BACKEND.main import app; print('✓ App loaded')" 2>/dev/null && echo -e "${GREEN}✓${NC} FastAPI app imports OK" || (echo -e "${RED}✗${NC} Import failed"; exit 1)

# Test 4: Deployment readiness test
echo -e "\n${YELLOW}[TEST 4]${NC} Running deployment readiness checks..."
if "$VENV/bin/python" "$BACKEND/test_deployment_ready.py" 2>/dev/null | grep -q "ALL DEPLOYMENT TESTS PASSED"; then
    echo -e "${GREEN}✓${NC} All deployment tests passed"
else
    echo -e "${RED}✗${NC} Deployment tests failed"
    exit 1
fi

# Test 5: Check if port 8000 is available
echo -e "\n${YELLOW}[TEST 5]${NC} Checking port 8000 availability..."
if ! lsof -i :8000 &>/dev/null; then
    echo -e "${GREEN}✓${NC} Port 8000 is available"
else
    echo -e "${YELLOW}!${NC} Port 8000 in use (will kill old processes)"
    lsof -i :8000 | grep -v COMMAND | awk '{print $2}' | xargs kill -9 2>/dev/null
    sleep 1
    echo -e "${GREEN}✓${NC} Port cleared"
fi

# Summary
echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║   ✓ ALL TESTS PASSED - READY TO DEPLOY        ║"
echo "╚════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Quick Start:${NC}"
echo "  ./deploy.sh              # Local with frontend"
echo "  ./start-backend.sh       # Backend only"
echo "  docker-compose -f docker-compose.prod.yml up  # Docker"
echo ""
echo -e "${GREEN}Testing:${NC}"
echo "  curl http://localhost:8000/health"
echo "  curl -X POST http://localhost:8000/api/analyze \\"
echo '    -H "Content-Type: application/json" \\'
echo '    -d '"'"'{"text": "Test claim"}'"'"
echo ""
echo -e "${YELLOW}Note:${NC} First API request takes 30-60s (models load)"
echo "         Subsequent requests will be fast (cached)"
echo ""
