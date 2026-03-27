#!/bin/bash

# TruthLens AI - Server Startup Script
# This script starts both backend and frontend servers

set -e

echo "🚀 Starting TruthLens AI..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Kill any existing processes on ports 8000 and 3000
echo "📋 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2

# Start Backend
echo -e "${YELLOW}Starting Backend...${NC}"
cd "$DIR/backend"

# Check if virtual environment exists
if [ ! -d ".venv" ] && [ ! -d "../.venv" ]; then
    echo -e "${RED}Virtual environment not found!${NC}"
    echo "Please run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Use the venv from parent directory if it exists
if [ -f "../.venv/bin/python" ]; then
    PYTHON="../.venv/bin/python"
else
    PYTHON="python3"
fi

$PYTHON -m uvicorn main:app --host 0.0.0.0 --port 8000 > "$DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓${NC} Backend started (PID: $BACKEND_PID)"
echo "   Logs: $DIR/backend.log"

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is healthy${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Backend failed to start${NC}"
        echo "Check logs: tail -f $DIR/backend.log"
        exit 1
    fi
    sleep 1
done

# Start Frontend
echo ""
echo -e "${YELLOW}Starting Frontend...${NC}"
cd "$DIR/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

# Use npm from nvm if available
if [ -s "$HOME/.nvm/nvm.sh" ]; then
    source "$HOME/.nvm/nvm.sh"
fi

# Start frontend in production mode
npm run start > "$DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓${NC} Frontend started (PID: $FRONTEND_PID)"
echo "   Logs: $DIR/frontend.log"

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is running${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}⚠${NC} Frontend might still be starting. Check logs: tail -f $DIR/frontend.log"
        break
    fi
    sleep 1
done

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ TruthLens AI is running!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo "🌐 Frontend:  http://localhost:3000"
echo "📡 Backend:   http://localhost:8000"
echo "📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "📋 Process IDs:"
echo "   Backend:  $BACKEND_PID"
echo "   Frontend: $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f $DIR/backend.log"
echo "   Frontend: tail -f $DIR/frontend.log"
echo ""
echo "🛑 To stop servers, run:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "💡 Tips:"
echo "   - First time? Sign up at http://localhost:3000"
echo "   - Test API: curl -X POST http://localhost:8000/api/analyze -F 'text=Your claim here'"
echo "   - View metrics: curl http://localhost:8000/metrics"
echo ""
