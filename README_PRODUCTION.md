# TruthLens AI - Production-Grade Misinformation Detection System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**TruthLens AI** is a production-ready, end-to-end misinformation detection and fact-checking system powered by advanced machine learning models and explainable AI. It analyzes claims and articles to determine veracity with confidence scores, sources, and detailed reasoning.

---

## 🎯 Features

### Core Capabilities
- **Multimodal Analysis**: Process text, URLs, and images
- **Fusion Scoring**: Combines 3 specialized ML models:
  - 🤖 **RoBERTa Classification** (60%): NLP-based verdict prediction
  - 📚 **Evidence Engine** (25%): Semantic search for supporting/contradicting evidence
  - 📊 **Propagation Model** (15%): Social network risk analysis
  
### Explainability & Transparency
- **Structured Verdicts**: REAL, RUMOR, or FAKE with confidence 0-100
- **Key Signals**: Highlights linguistic patterns indicating misinformation
- **Source Attribution**: Top credible sources with credibility scores
- **Detailed Reasoning**: AI-generated explanations for each verdict
- **Highlighted Terms**: Visual identification of suspicious language

### Production Features
- **Database Persistence**: Full history tracking with Alembic migrations
- **API Caching**: 1-hour in-memory cache for repeated claims
- **Error Handling**: Structured error responses across all endpoints
- **Structured Logging**: Request/response/performance metrics
- **Test Suite**: Comprehensive pytest regression tests
- **FastAPI Documentation**: Interactive `/docs` endpoint with Swagger UI

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 3000)                 │
│  - Interactive UI with verdict colors and confidence bars   │
│  - History dashboard for past analyses                      │
│  - Real-time explainability visualization                      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼ (JSON REST API)
┌─────────────────────────────────────────────────────────────┐
│             Backend API Layer (FastAPI 8000)                │
│  POST /api/analyze       - Analyze claims                   │
│  GET  /api/history       - Retrieve past analyses           │
│  GET  /api/sessions      - Session management              │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
   ┌────────┐ ┌──────────┐ ┌──────────────┐
   │RoBERTa │ │Evidence  │ │ Propagation  │
   │Model   │ │Engine    │ │ Risk Model   │
   └────────┘ └──────────┘ └──────────────┘
        │          │          │
        └──────────┴──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ Scoring Engine      │
        │ (Fusion & Cache)    │
        └──────────┬──────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   ┌──────────────┐   ┌─────────────┐
   │ SQLite Local │   │Pinecone/    │
   │ DB           │   │ Vector DB   │
   └──────────────┘   └─────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+ (for frontend)
- Git

### 1. Clone & Setup Backend

```bash
git clone https://github.com/yourusername/truthlens-ai.git
cd truthlens-ai

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Apply database migrations
alembic upgrade head

# Start backend API
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Backend running at**: `http://localhost:8000`
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 2. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

**Frontend running at**: `http://localhost:3000`

---

## 📖 API Reference

### POST `/api/analyze` - Analyze a Claim

**Request:**
```json
{
  "text": "Artificial intelligence will replace all human jobs by 2030",
  "session_id": "optional-session-id"
}
```

**Response (200 OK):**
```json
{
  "verdict": "RUMOR",
  "confidence": 72.5,
  "confidence_label": "MEDIUM",
  "scores": {
    "real": 18.3,
    "rumor": 72.5,
    "fake": 9.2
  },
  "reasoning": "While AI is advancing rapidly, the claim of total job replacement is overstated...",
  "key_signals": [
    "absolute_claim",
    "temporal_certainty",
    "lacks_nuance"
  ],
  "sources": [
    {
      "title": "WEF Future of Jobs Report 2023",
      "url": "https://example.com/report",
      "credibility_score": 0.92
    }
  ],
  "highlighted_text": [
    "will replace",
    "all",
    "by 2030"
  ],
  "model_breakdown": {
    "nlp_score": 68.0,
    "evidence_credibility": 0.75,
    "propagation_risk": 0.72
  }
}
```

**Error Response (422):**
```json
{
  "error": "Validation Error",
  "status": 422,
  "detail": "Text must be at least 5 characters",
  "timestamp": "2026-03-17T10:30:45.123456"
}
```

### GET `/api/history` - Retrieve Analysis History

**Query Parameters:**
- `limit` (optional, default 50): Number of records to return

**Response (200 OK):**
```json
[
  {
    "id": "uuid-1",
    "text": "Artificial intelligence will...",
    "verdict": "RUMOR",
    "confidence": 72.5,
    "confidence_label": "MEDIUM",
    "timestamp": "2026-03-17T10:30:45Z"
  },
  {
    "id": "uuid-2",
    "text": "Water boils at 100 degrees Celsius",
    "verdict": "REAL",
    "confidence": 98.2,
    "confidence_label": "HIGH",
    "timestamp": "2026-03-17T10:25:30Z"
  }
]
```

---

## 🧪 Testing

### Run API Tests

```bash
cd backend

# Run all tests with coverage
pytest tests/ -v --cov=services --cov=api

# Run specific test file
pytest tests/test_api_analyze.py -v

# Run single test
pytest tests/test_api_analyze.py::TestAnalyzeEndpoint::test_analyze_response_structure -v

# Run with verbose output
pytest tests/ -vv -s

# Generate coverage report
pytest tests/ --cov=services --cov=api --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Suites

#### 1. API Analysis Tests (`test_api_analyze.py`)
- ✅ Basic claim analysis
- ✅ Response structure validation
- ✅ Score normalization (sum to 100)
- ✅ Edge cases (empty text, special characters, very long text)
- ✅ Error handling
- ✅ Consistency across multiple requests

#### 2. History Endpoint Tests (`test_api_history.py`)
- ✅ History retrieval and ordering
- ✅ Persistence verification
- ✅ Deadline consistency with analysis
- ✅ Integration tests

---

## 🔧 Database Migrations

All database changes are managed with **Alembic**:

```bash
cd backend

# View migration status
alembic current
alembic history

# Create new migration (auto-detect changes)
alembic revision --autogenerate -m "your_migration_name"

# Apply migrations
alembic upgrade head           # Apply all pending migrations
alembic upgrade +1            # Apply next migration
alembic downgrade -1          # Rollback last migration

# View pending migrations
alembic downgrade base        # Rollback to initial state
```

**Current Schema**: See [migrations/versions/](backend/migrations/versions/) for detailed migration history.

---

## 📊 Performance Optimization

### Model Loading
- **Singleton Pattern**: Models loaded once on startup, reused across requests
- **Thread-Safe Caching**: Prevents duplicate model loads in concurrent requests

### Analysis Caching
- **In-Memory Cache**: Caches results for 1 hour with SHA256 hashing
- **Cache Stats**: View performance metrics via logging

### Database
- **Connection Pooling**: Efficient database connection management
- **Indexes**: Optimized query performance on frequently accessed columns
- **SQLite Local**: Zero setup for development, switchable to PostgreSQL

---

## 🔒 Security & Production Hardening

### Environment Variables
All sensitive data goes in `.env` (**never commit**):
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### Error Handling
- ✅ Global exception handlers for all endpoints
- ✅ Structured error responses
- ✅ No stack traces in production responses
- ✅ Validation error messages

### Logging
- ✅ Structured logs with timestamps
- ✅ Request/response logging
- ✅ Performance metrics (inference time)
- ✅ Error tracing with full context

### CORS & Security
- ✅ Configurable CORS origins
- ✅ Request validation with Pydantic
- ✅ JWT token support for authentication
- ✅ Password hashing with bcrypt

---

## 📝 Configuration

### Environment Variables

```bash
# API Server
HOST=0.0.0.0
PORT=8000
ENV=development  # or production

# Database
DATABASE_URL=sqlite:///./truthlens.db
# PostgreSQL example:
# DATABASE_URL=postgresql://user:password@localhost:5432/truthlens_db

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# External APIs (optional)
HF_TOKEN=your_huggingface_token
PINECONE_API_KEY=your_pinecone_key
SCRAPER_KEY=your_scraper_api_key
```

### Frontend `.env.local`

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🛠 Development Workflow

### Hot Reload
```bash
# Backend (auto-reload on code changes)
cd backend && python -m uvicorn main:app --reload

# Frontend (auto-reload on code changes)
cd frontend && npm run dev
```

### Code Quality
```bash
# Format code (Black)
black backend/

# Type checking (mypy)
mypy backend/

# Linting (flake8)
flake8 backend/
```

---

## 📦 Deployment

### Docker Deployment

```bash
# Build backend image
cd backend
docker build -t truthlens-ai-backend .

# Build frontend image
cd frontend
docker build -t truthlens-ai-frontend .

# Run with docker-compose
cd ..
docker-compose up -d
```

### Production Checklist
- [ ] Set `ENV=production`
- [ ] Configure PostgreSQL database
- [ ] Add real API keys to `.env`
- [ ] Update `CORS_ORIGINS` with your domain
- [ ] Enable HTTPS/SSL certificates (nginx/load balancer)
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure log aggregation (optional)
- [ ] Run full test suite
- [ ] Performance test with production-like load

---

## 📚 Model Details

### RoBERTa Classifier
- **Purpose**: NLP-based text classification (REAL/RUMOR/FAKE)
- **Architecture**: Transformer-based fine-tuned RoBERTa
- **Input**: Full claim text
- **Output**: Confidence scores for each class

### Evidence Engine
- **Purpose**: Retrieve credible sources for/against claim
- **Architecture**: Semantic search using sentence-transformers + Pinecone
- **Input**: Claim embedding
- **Output**: Top K credible sources with relevance scores

### Propagation Model
- **Purpose**: Assess viralability and information spread risk
- **Architecture**: Graph-based analysis of claim characteristics
- **Input**: Claim text + linguistic features
- **Output**: Propagation risk level + score

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check port is not in use
lsof -i :8000

# Kill existing process
pkill -f "uvicorn"

# Check Python dependencies
pip install -r requirements.txt --upgrade
```

### Database Issues
```bash
# Reset database (WARNING: deletes all data)
rm backend/truthlens.db
cd backend && alembic upgrade head
```

### Model Loading Errors
```bash
# Clear model cache
rm -rf ~/.cache/huggingface/
rm -rf ~/.cache/torch/

# Reinstall transformers
pip install --upgrade transformers huggingface-hub
```

---

## 📞 Support & Contributing

### Issue Reporting
Please include:
- Command/code that triggered the error
- Full error message and stack trace
- Python version and OS
- Requirements installed (`pip freeze`)

### Contributing
1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- FastAPI framework for excellent API documentation
- Hugging Face for transformers library
- Original authors of RoBERTa, SBERT, and LIME/SHAP
- All contributors and researchers in misinformation detection

---

## 📞 Contact

- **Email**: contact@truthlens-ai.com
- **Documentation**: https://docs.truthlens-ai.com
- **Issues**: https://github.com/yourusername/truthlens-ai/issues

---

**Last Updated**: March 17, 2026  
**Version**: 1.0.0 (Production)
