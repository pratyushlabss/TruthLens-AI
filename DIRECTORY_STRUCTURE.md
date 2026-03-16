# Project Directory Structure

## Complete File Tree

```
ai truthlens/
│
├── 📁 frontend/                          (React Next.js Frontend)
│   ├── 📁 app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css
│   │   └── 📁 api/
│   │       └── 📁 analyze/
│   │           └── route.ts              (Now calls backend)
│   │
│   ├── 📁 components/
│   │   ├── AnalysisInput.tsx
│   │   ├── ProcessingState.tsx
│   │   ├── Sidebar.tsx
│   │   ├── 📁 results/
│   │   │   ├── EvidenceEngineTable.tsx
│   │   │   ├── FeatureImportance.tsx
│   │   │   ├── PropagationGraph.tsx
│   │   │   ├── ResultsDashboard.tsx
│   │   │   ├── SentimentAndBias.tsx
│   │   │   └── VerdictCard.tsx
│   │   └── 📁 ui/
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       ├── Input.tsx
│   │       └── SkeletonLoader.tsx
│   │
│   ├── 📁 services/
│   │   └── api.ts                       ✏️ UPDATED - Uses backend
│   │
│   ├── 📁 types/
│   │   └── index.ts
│   │
│   ├── 📄 .env.example                  ✏️ UPDATED
│   ├── 📄 package.json
│   ├── 📄 tsconfig.json
│   ├── 📄 tailwind.config.ts
│   ├── 📄 next.config.js
│   ├── 📄 Dockerfile
│   ├── 📄 docker-compose.yml
│   ├── 📄 README.md
│   └── 📄 ... (other config files)
│
├── 📁 backend/                           ⭐ NEW - Python Flask Backend
│   ├── 📁 app/
│   │   ├── main.py                      ✨ Flask application
│   │   ├── __init__.py
│   │   └── 📁 services/
│   │       ├── nlp_analyzer.py          ✨ Text analysis (RoBERTa)
│   │       ├── image_processor.py       ✨ Image captioning (BLIP)
│   │       ├── web_scraper.py           ✨ URL extraction
│   │       ├── evidence_retriever.py    ✨ Pinecone search
│   │       └── __init__.py
│   │
│   ├── 📁 uploads/                      (Uploaded image files)
│   │
│   ├── 📄 requirements.txt               ✨ Python dependencies
│   ├── 📄 Dockerfile                    ✨ Python container
│   ├── 📄 .env.local                    ✨ Environment variables
│   ├── 📄 .env.example
│   └── 📄 README.md                     ✨ Backend documentation
│
├── 📄 docker-compose.yml                ⭐ NEW - Orchestrate services
├── 📄 QUICK_START.md                    ⭐ NEW - Quick reference
├── 📄 SETUP_GUIDE.md                    ⭐ NEW - Detailed setup
├── 📄 INTEGRATION_COMPLETE.md           ⭐ NEW - Integration summary
├── 📄 README_INTEGRATION.md             ⭐ NEW - Complete overview
├── 📄 SYSTEM_ARCHITECTURE.md            ⭐ NEW - Architecture diagrams
├── 📄 dev-setup.sh                      ⭐ NEW - Setup script
│
└── 📄 ... (other root config files)
```

## File Statistics

```
FRONTEND:
├── Components: 13 files
├── Services: 1 file (api.ts - UPDATED)
├── Config: 8 files
└── Total: ~30+ files

BACKEND (NEW):
├── Main app: 1 file (main.py)
├── Services: 4 files (nlp, image, scraper, evidence)
├── Config: 3 files (requirements, Dockerfile, .env)
└── Total: ~10 files

DOCUMENTATION (NEW):
├── Quick Start: 1 file
├── Setup Guide: 1 file
├── Architecture: 3 files
├── Integration: 2 files
└── Total: 7 files

ORCHESTRATION (NEW):
└── docker-compose.yml

GRAND TOTAL: ~50+ files in complete system
```

## Key Files Changed/Created

### Updated Files (Frontend)
```
✏️ frontend/services/api.ts
   - Changed to use FormData
   - Points to backend /api/analyze
   - Simplified response handling
   - Removed streaming (simplified version)

✏️ frontend/.env.example
   - Updated NEXT_PUBLIC_API_URL to http://localhost:5000
   - Removed API-specific credentials
   - Simplified for frontend-only env vars
```

### New Files (Backend)
```
✨ backend/app/main.py
   - Flask application with CORS
   - POST /api/analyze handler
   - Image, URL, NLP processing
   - Evidence retrieval integration
   - Fusion scoring & verdict logic

✨ backend/app/services/nlp_analyzer.py
   - RoBERTa-based text analysis
   - Hugging Face API integration
   - Embedding generation

✨ backend/app/services/image_processor.py
   - BLIP image captioning
   - File upload handling
   - Base64 encoding support

✨ backend/app/services/web_scraper.py
   - WebScraping.ai integration
   - URL content extraction
   - Error handling

✨ backend/app/services/evidence_retriever.py
   - Pinecone vector search
   - Semantic evidence matching
   - Source attribution

✨ backend/requirements.txt
   - Flask 2.3.3
   - Flask-CORS 4.0.0
   - Requests 2.31.0
   - Werkzeug 2.3.7
   - Gunicorn 21.2.0
   - python-dotenv 1.0.0

✨ backend/Dockerfile
   - Python 3.11 slim base
   - Dependencies installation
   - Gunicorn server setup
   - Health check configuration

✨ backend/.env.local
   - Pre-configured credentials
   - Development settings
   - Port configuration
```

### New Configuration Files
```
⭐ docker-compose.yml
   - Frontend service setup
   - Backend service setup
   - Network configuration
   - Health checks
   - Volume management

⭐ dev-setup.sh
   - Automated setup script
   - Virtual env creation
   - Dependencies installation
   - Configuration setup
```

### New Documentation Files
```
⭐ QUICK_START.md
   - 1-minute setup guide
   - Docker and manual options
   - Quick API testing
   - Troubleshooting tips

⭐ SETUP_GUIDE.md
   - Comprehensive setup
   - Both environments
   - Development workflow
   - Production deployment

⭐ SYSTEM_ARCHITECTURE.md
   - Architecture diagrams
   - Data flow visualization
   - Component interaction
   - Technology stack

⭐ INTEGRATION_COMPLETE.md
   - Integration summary
   - Features list
   - Quick start options
   - Testing guide

⭐ README_INTEGRATION.md
   - Complete project overview
   - All features listed
   - API specification
   - Troubleshooting guide
```

## Environment Variables

### Backend (.env or .env.local)
```
HF_TOKEN=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
PINECONE_KEY=pcsk_4GpH3o_LT2E8HvMKk1n2eR3ZAbFqiFD3xS5TxxMcDYujatBNZvcMYpvzrZP3dGj9qeHj9p
SCRAPER_KEY=eb66d83d-416a-4f5e-8c7c-d5c2b6f89541
FLASK_ENV=development
BACKEND_PORT=5000
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:5000
NODE_ENV=development
```

## Ports Configuration

| Service | Port | Environment | Status |
|---------|------|-------------|--------|
| Frontend | 3000 | Development | Running |
| Backend | 5000 | Development | Running |
| Docker Bridge | N/A | Production | Configured |

## Docker Networks

```
truthlens-network (bridge)
├── frontend:3000 (accessible as http://frontend:3000 from other containers)
├── backend:5000 (accessible as http://backend:5000 from other containers)
└── localhost mapping (3000 → frontend, 5000 → backend)
```

## Dependencies Summary

### Frontend Dependencies
- next, react, react-dom
- typescript
- tailwindcss, postcss, autoprefixer
- framer-motion, recharts
- axios, @radix-ui
- lucide-react

### Backend Dependencies
- Flask==2.3.3
- Flask-CORS==4.0.0
- python-dotenv==1.0.0
- requests==2.31.0
- Werkzeug==2.3.7
- gunicorn==21.2.0

## Ready to Run!

All files are in place. Choose your preferred method:

### 🐳 Docker (Recommended)
```bash
docker-compose up --build
```

### 🛠️ Manual Development
```bash
# Backend
cd backend && python -m app.main

# Frontend (in another terminal)
cd frontend && npm run dev
```

Both approaches will work perfectly! 🚀
