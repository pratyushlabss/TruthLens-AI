#!/bin/bash

# TruthLens AI - Simple Server Startup Script
# Shows output directly on screen

set -e

echo ""
echo "============================================================"
echo "🚀 TruthLens AI Backend - Server Startup"
echo "============================================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_ROOT/backend"
VENV="$PROJECT_ROOT/.venv/bin/python"

# Check if venv exists
if [ ! -f "$VENV" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Expected at: $VENV"
    echo ""
    echo "Please run: python -m venv .venv && source .venv/bin/activate && pip install -r backend/requirements.txt"
    exit 1
fi

# Kill any existing servers on port 8000
echo "🔍 Checking for existing servers on port 8000..."
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  Found existing process on port 8000, killing it..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

echo "✅ Port 8000 is clear"
echo ""

# Start the server
echo "🎬 Starting server..."
echo "   Backend directory: $BACKEND_DIR"
echo "   Python: $VENV"
echo "   Port: 8000"
echo ""
echo "============================================================"
echo "Server will show startup logs below:"
echo "============================================================"
echo ""

cd "$BACKEND_DIR"

# Run uvicorn and show output directly
$VENV -m uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info

# If we get here, the server stopped
echo ""
echo "============================================================"
echo "⚠️  Server has stopped"
echo "============================================================"
