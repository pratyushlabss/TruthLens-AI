#!/bin/bash
# TruthLens AI - Production Startup Script
# Deployment-ready with proper error handling

set -euo pipefail

WORK_DIR="/Users/pratyush/ai truthlens"
VENV_PATH="$WORK_DIR/.venv"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   TruthLens AI - Production Deployment    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"

# Step 1: Check environment
echo -e "\n${YELLOW}[1/5]${NC} Checking environment..."

# Skip venv check in production (Render/Railway will handle dependencies)
if [ -d "$VENV_PATH" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment found locally"
    source "$VENV_PATH/bin/activate"
    echo -e "${GREEN}✓${NC} Venv activated"
else
    echo -e "${YELLOW}⚠${NC} Running in production mode (no local .venv needed)"
    echo -e "${GREEN}✓${NC} Environment OK"
fi

# Step 3: Kill old processes
echo -e "\n${YELLOW}[3/5]${NC} Cleaning up old processes..."
pkill -f "uvicorn.*main:app" 2>/dev/null || true
pkill -f "npm.*dev" 2>/dev/null || true
sleep 2
echo -e "${GREEN}✓${NC} Old processes cleaned"

# Step 4: Start backend
echo -e "\n${YELLOW}[4/5]${NC} Starting Backend (port $BACKEND_PORT)..."
cd "$WORK_DIR/backend"
python -m uvicorn main:app \
    --host 0.0.0.0 \
    --port "$BACKEND_PORT" \
    --log-level info \
    > /tmp/truthlens_backend.log 2>&1 &

BACKEND_PID=$!
echo -e "${GREEN}✓${NC} Backend started (PID: $BACKEND_PID)"

# Step 5: Wait for backend to be ready AND start frontend
echo -e "\n${YELLOW}[5/5]${NC} Waiting for backend to initialize..."

# Wait up to 60 seconds for backend to respond
for i in {1..60}; do
    if curl -s "http://localhost:$BACKEND_PORT/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend is ready!"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${RED}✗${NC} Backend failed to start"
        echo "    Check logs: tail -f /tmp/truthlens_backend.log"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    echo -n "."
    sleep 1
done

# Start frontend
echo -e "\n${YELLOW}Starting Frontend (port $FRONTEND_PORT)...${NC}"
cd "$WORK_DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install --quiet
fi

npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✓${NC} Frontend started (PID: $FRONTEND_PID)"

# Print summary
echo -e "\n${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 TruthLens AI is Running!              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo -e "\n${YELLOW}Access Points:${NC}"
echo -e "  📡 Backend API:  ${GREEN}http://localhost:$BACKEND_PORT${NC}"
echo -e "     └ API Docs:  ${GREEN}http://localhost:$BACKEND_PORT/docs${NC}"
echo -e "     └ Health:    ${GREEN}http://localhost:$BACKEND_PORT/health${NC}"
echo -e ""
echo -e "  🎨 Frontend:     ${GREEN}http://localhost:$FRONTEND_PORT${NC}"
echo -e ""
echo -e "${YELLOW}Logs:${NC}"
echo -e "  Backend:  tail -f /tmp/truthlens_backend.log"
echo -e ""
echo -e "${YELLOW}Ctrl+C to stop${NC}\n"

# Wait for user interrupt
trap "echo -e \"\n${YELLOW}Shutting down...${NC}\"; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo -e \"${GREEN}✓ Stopped${NC}\"; exit 0" INT

wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
