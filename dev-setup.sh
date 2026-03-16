#!/bin/bash

# TruthLens AI - Development Setup Script
# Automatically sets up both frontend and backend for local development

set -e

echo "🚀 TruthLens AI - Development Setup"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "❌ Error: frontend and backend directories not found"
    echo "Please run this script from the ai truthlens root directory"
    exit 1
fi

echo -e "${BLUE}Step 1: Setting up Backend${NC}"
echo "------------------------"

cd backend

# Create Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.local .env
    echo -e "${GREEN}✓ .env file created${NC}"
fi

cd ..

echo ""
echo -e "${BLUE}Step 2: Setting up Frontend${NC}"
echo "------------------------"

cd frontend

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file..."
    cp .env.example .env.local
    echo -e "${GREEN}✓ .env.local file created${NC}"
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install -q
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

cd ..

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. Start the Backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python -m app.main"
echo ""
echo "2. In another terminal, start the Frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "Backend will be running on http://localhost:5000"
echo ""
