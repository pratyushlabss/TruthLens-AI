# TruthLens AI - Full Stack Setup & Connection Guide

Complete guide to set up and run both frontend and backend, and ensure they're properly connected.

## Project Structure

```
ai truthlens/
├── frontend/               # Next.js 14 React frontend
│   ├── app/
│   ├── components/
│   ├── services/
│   │   └── api.ts          # API client (UPDATED)
│   ├── Dockerfile
│   ├── .env.example        # (UPDATED)
│   └── ...
├── backend/                # Flask Python API server (NEW)
│   ├── app/
│   │   ├── main.py         # Flask app
│   │   └── services/       # AI services
│   │       ├── nlp_analyzer.py
│   │       ├── image_processor.py
│   │       ├── web_scraper.py
│   │       └── evidence_retriever.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.local
│   └── README.md
└── docker-compose.yml      # Orchestrate both services
```

## Quick Start (Docker)

### 1. Start both services with Docker Compose

```bash
cd /Users/pratyush/ai\ truthlens

docker-compose up --build
```

This will:
- ✅ Build and run the **Backend** on `http://localhost:5000`
- ✅ Build and run the **Frontend** on `http://localhost:3000`
- ✅ Automatically configure `NEXT_PUBLIC_API_URL=http://backend:5000`
- ✅ Set up networking between containers

### 2. Access the application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api/health
- **Backend Docs**: http://localhost:5000

## Manual Setup (Development)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API credentials (or use defaults)

# Run development server
python -m app.main
```

**Backend will run on**: `http://localhost:5000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with backend URL:
# NEXT_PUBLIC_API_URL=http://localhost:5000

# Run development server
npm run dev
```

**Frontend will run on**: `http://localhost:3000`

## Architecture & Connection

### Frontend → Backend Flow

```
User Action (e.g., "Analyze this text")
         ↓
  Component (AnalysisInput.tsx)
         ↓
  services/api.ts (TruthLensAPI class)
         ↓
  FormData to POST /api/analyze
         ↓
  Backend Flask API
         ↓
  Response: { verdict, confidence, details }
         ↓
  Display results (ResultsDashboard.tsx)
```

### API Connection Config

#### Frontend Environment Variable
```env
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:5000
```

#### API Client (frontend/services/api.ts)
```typescript
async analyze(params: { text?, url?, image? }): Promise<AnalysisResult> {
  const formData = new FormData();
  if (params.text) formData.append("text", params.text);
  if (params.url) formData.append("url", params.url);
  if (params.image) formData.append("image", params.image);
  
  const response = await this.api.post("/api/analyze", formData);
  return response.data;
}
```

#### Backend Routes
```
POST /api/analyze      → Analyze text/URL/image
GET  /api/health       → Health check
GET  /api/sessions     → Recent analyses
```

## API Endpoints

### POST /api/analyze

**Request (FormData):**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "text=The earth is flat"
```

**Response:**
```json
{
  "verdict": "FAKE",
  "confidence": 85,
  "details": {
    "nlpScore": 90,
    "evidenceScore": 75,
    "summary": "This claim has an 85% likelihood of being fake...",
    "keySignals": ["NLP model indicates likely misinformation"],
    "evidenceSources": [...]
  },
  "processingTime": 2500
}
```

### GET /api/health

**Response:**
```json
{
  "status": "healthy",
  "service": "TruthLens AI Backend",
  "timestamp": "2026-03-16T12:34:56.789Z"
}
```

## Testing the Connection

### 1. Check Backend Health

```bash
curl http://localhost:5000/api/health
# Should return: { "status": "healthy", ... }
```

### 2. Test Analysis Endpoint

```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "text=Testing the backend connection"
```

### 3. Frontend Integration Test

Open browser console and run:
```javascript
const { truthLensAPI } = await import('/services/api.ts');
const result = await truthLensAPI.analyzeText('Test text');
console.log(result);
```

## Environment Variables

### Backend (.env or .env.local)
```env
HF_TOKEN=your_hugging_face_token_here
PINCONE_KEY=your_pinecone_key_here
SCRAPER_KEY=your_scraper_key_here
FLASK_ENV=development
BACKEND_PORT=5000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:5000
NODE_ENV=development
```

## Troubleshooting

### Frontend can't reach backend

**Problem**: `CORS error` or `Connection refused`

**Solutions**:
1. Check backend is running: `curl http://localhost:5000/api/health`
2. Verify `NEXT_PUBLIC_API_URL` is correct in `.env.local`
3. Restart frontend: `npm run dev`
4. Check backend logs for errors

### Backend returns 500 error

**Problem**: Analysis fails with server error

**Solutions**:
1. Check API credentials in `.env`:
   - `HF_TOKEN` - Hugging Face token
   - `PINECONE_KEY` - Pinecone API key
   - `SCRAPER_KEY` - WebScraping.ai key
2. Check internet connection for external APIs
3. Check backend logs: `python -m app.main`

### Docker container won't start

**Problem**: `docker-compose up` fails

**Solutions**:
1. Check Docker is running: `docker --version`
2. Remove old containers: `docker-compose down`
3. Rebuild: `docker-compose up --build`
4. Check logs: `docker-compose logs -f backend`

## Development Workflow

### 1. Make Changes

**Backend**: Edit Python files in `backend/app/`
- Changes auto-reload in development mode

**Frontend**: Edit React components in `frontend/components/`
- Changes auto-reload with Next.js dev server

### 2. Test API Integration

Use curl or Postman to test backend:
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "text=Your test text here"
```

### 3. Update Frontend UI

The frontend already expects the correct response format from backend:
```typescript
{
  verdict: 'FAKE' | 'REAL' | 'RUMOR',
  confidence: number,
  details: {
    nlpScore: number,
    evidenceScore: number,
    summary: string,
    keySignals: string[],
    evidenceSources: Array<{...}>
  }
}
```

## Production Deployment

### Using Docker

```bash
# Build and push images
docker build -t truthlens-backend ./backend
docker build -t truthlens-frontend ./frontend

# Run with docker-compose
docker-compose -f docker-compose.yml up -d
```

### Manual Deployment

**Backend (Gunicorn + Nginx)**:
```bash
pip install -r requirements.txt
gunicorn -w 4 -b 0.0.0.0:5000 app.main:app
```

**Frontend (Next.js)**:
```bash
npm install
npm run build
npm start
```

## Key Features

✅ **Multimodal Analysis**
- Text analysis via NLP
- Image captioning via BLIP
- URL scraping via WebScraping.ai

✅ **Evidence Retrieval**
- Pinecone semantic search
- Source attribution
- Support/contradiction scoring

✅ **Fusion Scoring**
- Combines NLP (60%), Evidence (25%), Image (15%)
- Intelligent verdict classification

✅ **Seamless Frontend-Backend Integration**
- FormData submission from React
- Automatic CORS handling
- Error handling and retry logic

## Support

For issues or questions:
1. Check the logs: `npm run dev` or `python -m app.main`
2. Review API responses with curl
3. Verify environment variables
4. Check external API status (Hugging Face, Pinecone, WebScraping.ai)

---

**Ready to analyze!** 🚀
