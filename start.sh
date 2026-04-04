#!/bin/bash
# TruthLens AI - Quick Startup Script
# Run this to start the complete system

set -e

echo "🚀 TruthLens AI - Production Startup"
echo "===================================================="
echo ""

VENV_PATH="/Users/pratyush/ai truthlens/.venv"
WORK_DIR="/Users/pratyush/ai truthlens"

# Check environment
if [ -d "$VENV_PATH" ]; then
    # Activate venv
    echo "📦 Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
else
    # Production mode - platform handles dependencies
    echo "⚠️ No local .venv found (production mode)"
fi

# Kill any existing processes on ports
echo "🔧 Cleaning up old processes..."
lsof -i :8000 2>/dev/null | grep -v COMMAND | awk '{print $2}' | xargs kill -9 2>/dev/null || true
lsof -i :3000 2>/dev/null | grep -v COMMAND | awk '{print $2}' | xargs kill -9 2>/dev/null || true

# Start backend in background
echo "📡 Starting Backend API (port 8000)..."
cd "$WORK_DIR/backend"
python -m uvicorn main:app --host 127.0.0.1 --port 8000 > /tmp/truthlens_backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
echo "⏳ Waiting for backend to initialize (this may take 30-60 seconds)..."
for i in {1..60}; do
    if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    sleep 1
    if [ $i -eq 60 ]; then
        echo "❌ Backend failed to start. Check logs:"
        echo "   tail -f /tmp/truthlens_backend.log"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
done

# Start frontend
echo ""
echo "🎨 Starting Frontend (port 3000)..."
cd "$WORK_DIR/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install -q
fi

npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "===================================================="
echo "🎉 TruthLens AI is running!"
echo "===================================================="
echo ""
echo "📡 Backend API:    http://localhost:8000"
echo "   - API Docs:    http://localhost:8000/docs"
echo "   - Health:      http://localhost:8000/health"
echo ""
echo "🎨 Frontend:       http://localhost:3000"
echo ""
echo "📊 Logs:"
echo "   - Backend:     tail -f /tmp/truthlens_backend.log"
echo ""
echo "🧪 Run tests:"
echo "   cd backend && pytest tests/ -v"
echo ""
echo "✓ Press Ctrl+C to stop both servers"
echo ""

# Wait for user interrupt
wait
