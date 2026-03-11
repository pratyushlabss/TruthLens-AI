# TruthLens AI - Production-Grade Misinformation Detection System

**An MSc-level AI system combining RoBERTa NLP, Sentence-BERT semantic search, and graph-based propagation analysis.**

---

## 🎯 System Overview

```
User Browser
    ↓
Next.js Frontend
    ↓
FastAPI Backend
    ↓
┌─────────────────────────────────────┐
│ 3-Model Fusion Scoring Engine      │
├─────────────────────────────────────┤
│ • RoBERTa Classifier (60%)         │
│ • SBERT Evidence Retrieval (25%)   │
│ • Propagation Risk Analysis (15%)  │
└─────────────────────────────────────┘
    ↓
PostgreSQL + Pinecone + AWS S3
```

---

## 📋 Tech Stack

### Backend
- **Framework**: FastAPI (async, ML-friendly)
- **ML Models**: PyTorch, HuggingFace, Sentence-BERT
- **Databases**: PostgreSQL (primary), Pinecone (vectors)
- **Cache**: Redis
- **Task Queue**: Celery
- **Deployment**: Docker, AWS EC2 + RDS

### Frontend
- **Framework**: Next.js + TypeScript
- **UI**: Tailwind CSS + Shadcn UI
- **Visualization**: Recharts, D3.js

### Cloud Infrastructure
- **Frontend**: Vercel
- **Backend**: AWS EC2
- **Database**: AWS RDS (PostgreSQL)
- **Vector DB**: Pinecone
- **Storage**: AWS S3
- **API Gateway**: AWS API Gateway

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone <repo>
cd TruthLens-AI

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 2. Set Up Environment

```bash
cp backend/.env.example backend/.env
# Edit .env with your credentials
```

### 3. Start with Docker

```bash
docker-compose -f deployment/docker-compose.yml up --build
```

This will start:
- PostgreSQL on `localhost:5432`
- Redis on `localhost:6379`
- FastAPI on `localhost:8000`

### 4. Run Backend Locally (Development)

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: `http://localhost:8000/docs`

### 5. Run Frontend Locally

```bash
cd frontend
npm run dev
```

Frontend available at: `http://localhost:3000`

---

## 📁 Project Structure

```
TruthLens-AI/
├── backend/
│   ├── api/
│   │   ├── analyze.py        # Analysis endpoint
│   │   ├── upload.py         # File upload
│   │   └── sessions.py       # Chat history
│   ├── models/
│   │   ├── roberta_classifier.py    # NLP model
│   │   ├── evidence_engine.py       # SBERT + Pinecone
│   │   └── propagation_model.py     # NetworkX
│   ├── services/
│   │   └── scoring_engine.py        # Fusion scoring
│   ├── database/
│   │   ├── models.py         # SQLAlchemy ORM
│   │   └── postgres.py       # DB connection
│   ├── main.py               # FastAPI app
│   └── requirements.txt
│
├── frontend/
│   ├── components/
│   │   ├── ChatSidebar.tsx
│   │   ├── Dashboard.tsx
│   │   ├── EvidencePanel.tsx
│   │   └── ProbabilityChart.tsx
│   ├── pages/
│   │   └── index.tsx
│   └── package.json
│
├── deployment/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml         # GitHub Actions
│
├── datasets/
├── notebooks/
└── README.md
```

---

## 🔬 Core Models

### 1. RoBERTa NLP Classifier (60% weight)

**Purpose**: Direct fake news classification

```python
from models.roberta_classifier import RoBERTaClassifier

classifier = RoBERTaClassifier()
result = classifier.classify("5G towers cause COVID")
# {
#   "verdict": "FAKE",
#   "confidence": 92.5,
#   "scores": {"real": 2.1, "rumor": 5.4, "fake": 92.5}
# }
```

### 2. Sentence-BERT Evidence Engine (25% weight)

**Purpose**: Retrieve corroborating/contradicting evidence

```python
from models.evidence_engine import EvidenceEngine

engine = EvidenceEngine()
evidence = engine.retrieve_evidence("Vaccine contains microchips")
# [
#   {
#     "name": "WHO",
#     "url": "https://who.int",
#     "relevance": 92,
#     "supports": "CONFIRMS"
#   },
#   ...
# ]
```

### 3. Propagation Risk Model (15% weight)

**Purpose**: Estimate misinformation spread likelihood

```python
from models.propagation_model import PropagationModel

model = PropagationModel()
risk = model.analyze_propagation_risk(claim, nlp_score=92)
# {
#   "propagation_risk": "HIGH",
#   "propagation_score": 78,
#   "tweet_velocity": 65,
#   "cluster_size": 2500
# }
```

### 4. Fusion Scoring Engine

**Final Score** = 0.6 × NLP + 0.25 × Evidence + 0.15 × Propagation

```python
from services.scoring_engine import ScoringEngine

engine = ScoringEngine()
result = engine.analyze("Bitcoin price will triple tomorrow")
# {
#   "verdict": "RUMOR",
#   "confidence": 67.3,
#   "scores": {"real": 15, "rumor": 67, "fake": 18},
#   "evidence_sources": [...],
#   "key_signals": ["Unsubstantiated financial claim", ...],
#   "summary": "Lacks sufficient evidence for verification..."
# }
```

---

## 📊 API Endpoints

### POST `/api/analyze`
Analyze a single claim

**Request**:
```json
{
  "text": "5G towers cause COVID-19",
  "session_id": "session-123"
}
```

**Response**:
```json
{
  "verdict": "FAKE",
  "confidence": 92.5,
  "scores": {"real": 2.1, "rumor": 5.4, "fake": 92.5},
  "propagation_risk": "HIGH",
  "evidence_sources": [...],
  "key_signals": ["Conspiracy language", "No credible sources"]
}
```

### POST `/api/upload`
Upload screenshot/document for analysis

### POST `/api/sessions`
Create new analysis session

### GET `/api/sessions/{session_id}`
Get session history

---

## 🎨 Frontend Features

- ✅ Responsive dashboard with verdict visualization
- ✅ Real-time probability charts (Recharts)
- ✅ Chat-style analysis history (sidebar)
- ✅ Evidence panel with source credibility
- ✅ Claim-by-claim breakdown
- ✅ Propagation risk visualization
- ✅ File upload for screenshots/articles

---

## 🐳 Docker Deployment

### Local Development

```bash
docker-compose -f deployment/docker-compose.yml up --build
```

### Production

```bash
# Build image
docker build -f deployment/Dockerfile -t truthlens-ai:latest .

# Push to registry
docker push ghcr.io/yourusername/truthlens-ai:latest

# Deploy to AWS/GCP/Azure
# (See .github/workflows/ci-cd.yml)
```

---

## ☁️ Cloud Deployment (AWS)

### 1. Database Setup

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier truthlens-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YOUR_PASSWORD
```

### 2. Backend Deployment

```bash
# Deploy to EC2
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key
```

### 3. Frontend Deployment

```bash
# Deploy to Vercel
vercel deploy --prod
```

---

## 📈 Performance Metrics

- **Analysis time**: 2-4 seconds per claim
- **Throughput**: ~100-150 claims/min (single instance)
- **Model size**: ~440MB (RoBERTa + SBERT)
- **Inference**: GPU-accelerated (optional CPU fallback)

---

## 🧪 Testing

```bash
cd backend
pytest tests/ -v --cov=backend
```

---

## 📚 Data Sources

- **Training Data**: LIAR, FakeNewsNet, CoAID datasets
- **Evidence Sources**: Reuters, WHO, Snopes, FactCheck.org
- **Vector DB**: Pinecone with sentence embeddings

---

## 🔐 Security

- ✅ API authentication (JWT)
- ✅ Input validation & sanitization
- ✅ Rate limiting
- ✅ CORS configuration
- ✅ Environment variable secrets
- ✅ SQL injection prevention (SQLAlchemy ORM)

---

## 📝 License

MIT License

---

## 👥 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📞 Support

For issues, questions, or contributions:
- 📧 Email: support@truthlens-ai.com
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

---

**Built for MSc Data Science students and AI enthusiasts. 🚀**
