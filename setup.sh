#!/bin/bash

# TruthLens AI - Quick Start Script
# Run this after cloning to set up the project

set -e

echo "🚀 TruthLens AI - Setup Script"
echo "==============================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found. Install from https://docker.com"
fi

if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js not found. Install from https://nodejs.org"
fi

echo "✅ Prerequisites checked"
echo ""

# Backend setup
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependencies installed"

# Create .env file
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env file created (please edit with your credentials)"
fi

cd ..
echo ""

# Frontend setup
echo "🎨 Setting up frontend..."
if [ ! -d "frontend" ]; then
    echo "⚠️  Frontend directory not found"
else
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        npm install > /dev/null 2>&1
        echo "✅ Node dependencies installed"
    fi
    
    if [ ! -f ".env.local" ]; then
        echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local
        echo "✅ .env.local file created"
    fi
    
    cd ..
fi

echo ""

# Docker setup
echo "🐳 Docker setup..."
if command -v docker &> /dev/null; then
    echo "✅ Docker found"
    echo ""
    echo "To start services, run:"
    echo "  docker-compose -f deployment/docker-compose.yml up --build"
fi

echo ""
echo "==============================="
echo "✅ Setup complete!"
echo ""
echo "📖 Next steps:"
echo "1. Edit backend/.env with your credentials"
echo "2. Run: docker-compose -f deployment/docker-compose.yml up --build"
echo "3. Backend API: http://localhost:8000"
echo "4. API Docs: http://localhost:8000/docs"
echo "5. Frontend: http://localhost:3000"
echo ""
echo "📚 Documentation:"
echo "- README.md - Project overview"
echo "- SETUP.md - Detailed installation"
echo "- GETTING_STARTED.md - Quick start guide"
echo "- ARCHITECTURE.md - Technical details"
echo ""
