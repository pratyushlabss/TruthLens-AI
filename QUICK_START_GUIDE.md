# TruthLens AI - Quick Start Guide

## System Status: ✅ Production Ready

This guide gets you running in **5 minutes**.

---

## 1. Prerequisites

- Python 3.9+
- Node.js 16+
- macOS/Linux (or Windows with WSL)

---

## 2. One-Command Setup

```bash
cd "/Users/pratyush/ai truthlens"

# Make startup script executable
chmod +x start.sh

# Run everything
./start.sh
```

**That's it!** The script will:
- Activate your virtual environment
- Start the backend API (port 8000)
- Start the frontend (port 3000)
- Wait for backend initialization (~30-60 seconds)

---

## 3. Access the System

### 🎨 Frontend
- **URL**: http://localhost:3000
- Upload a claim or evidence image
- Get instant fact-check results with confidence and sources

### 📡 Backend API
- **Docs**: http://localhost:8000/docs (interactive Swagger UI)
- **Health**: http://localhost:8000/health

---

## 4. Key Endpoints

### Analyze a Claim
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The Earth revolves around the Sun",
    "evidence": "Scientific consensus from NASA and peer-reviewed studies"
  }'
```

**Response:**
```json
{
  "verdict": "VERIFIED",
  "confidence": 0.95,
  "confidence_label": "HIGH",
  "reasoning": "...",
  "sources": ["bbc.com", "nasa.gov", ...],
  "key_signals": ["...", "..."]
}
```

### Get Analysis History
```bash
curl http://localhost:8000/api/history
```

---

## 5. Run Tests

```bash
cd backend
pytest tests/ -v

# You should see:
# test_api_analyze.py::test_analyze_response_schema PASSED
# test_api_history.py::test_history_ordering PASSED
# etc.
```

---

## 6. Validation

```bash
cd /Users/pratyush/ai truthlens
python validate_production.py
```

**Expected output:**
```
✅ Alembic Migrations
✅ Requirements Cleanup
✅ Error Handling
✅ Logging System
✅ Caching Implementation
✅ Test Suite
✅ Security & Env
✅ Documentation

Total: 8/8 tests passed 🎉
```

---

## 7. Project Structure

```
backend/
  ├── main.py              # FastAPI app with error handling & logging
  ├── api/analyze.py       # Fact-checking endpoint with caching
  ├── services/            # Scoring, caching, explainability
  ├── models/              # RoBERTa, SBERT, propagation models
  ├── database/            # SQLAlchemy + Alembic migrations
  ├── tests/               # Regression test suite (pytest)
  └── requirements.txt     # 55 pinned dependencies

frontend/
  ├── app/page.tsx         # Main UI
  ├── app/api/analyze/     # API proxy route
  └── package.json         # Node dependencies

alembic/
  ├── versions/            # Database migrations
  └── env.py               # Migration configuration
```

---

## 8. What's New (Production Hardening)

✅ **Database Migrations** – Alembic versioning for ClaimHistory table  
✅ **Regression Tests** – pytest suite validating API contracts  
✅ **Error Handling** – Global exception middleware with structured responses  
✅ **Logging** – Request/response logging with performance timing  
✅ **Caching** – Thread-safe model cache + result deduplication  
✅ **Documentation** – Comprehensive README_PRODUCTION.md  
✅ **Security** – `.env` sanitized; no exposed API keys  
✅ **Validation** – Automated 8-check production validation  

---

## 9. Troubleshooting

### Backend won't start
```bash
# Check logs
tail -f /tmp/truthlens_backend.log

# Manually start for debugging
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Port 8000 already in use
```bash
# Kill process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Frontend shows "Failed to fetch"
```bash
# Ensure backend is running on port 8000
curl http://localhost:8000/health

# If it fails, backend crashed. Check logs above.
```

### Database migration issues
```bash
cd backend

# Check migration status
alembic current

# Rollback last migration
alembic downgrade -1

# Upgrade to latest
alembic upgrade head
```

---

## 10. Next Steps

### For Development
```bash
# In backend: watch for code changes
cd backend
python -m uvicorn main:app --reload

# In frontend: Next.js hot reload is automatic
```

### For Production Deployment
- See [README_PRODUCTION.md](README_PRODUCTION.md)
- Docker setup, environment variables, security checklist

### For MSc Portfolio
1. Run validation: `python validate_production.py`
2. Capture backend logs showing requests with timing
3. Take frontend screenshots showing fact-checking in action
4. Submit [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)

---

## 11. System Features

**ML Explainability**
- Attention visualization from RoBERTa model
- Key signals highlighting important text spans
- Confidence calibration (HIGH/MEDIUM/LOW)

**Evidence Retrieval**
- Pinecone vector DB for semantic search
- BBC Scraper integration for trusted sources
- Fact-checking claims against real-world data

**History Tracking**
- SQLite/PostgreSQL persistence
- Timestamp and claim tracking
- Query by timestamp or verdict

---

## 12. Performance

- **Model initialization**: ~5-10 seconds on first request (cached after)
- **Per-request latency**: 2-5 seconds (RoBERTa + evidence retrieval)
- **Memory usage**: ~2-3 GB (models loaded in memory)
- **Database**: SQLite local development, optionally PostgreSQL production

---

## Questions?

See detailed documentation:
- [README_PRODUCTION.md](README_PRODUCTION.md) – Full production guide
- [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) – Technical deep-dive
- [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) – Feature summary

---

**Last Updated**: After production hardening pass  
**Status**: All systems operational and validated ✅
