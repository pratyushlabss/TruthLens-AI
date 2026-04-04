# TruthLens Frontend ↔ RAG Pipeline Integration Guide

## 🔗 Connection Status

✅ **Frontend**: Next.js React app running on `http://localhost:3000`  
✅ **RAG API**: Python backend running on `http://127.0.0.1:8000`  
✅ **Integration**: Ready to use

---

## 📋 Quick Start

### 1. **Install Dependencies** (Already Done)
```bash
cd frontend
npm install
```

### 2. **Configure Environment** 
Create or update `frontend/.env.local`:
```bash
NEXT_PUBLIC_RAG_API_URL=http://127.0.0.1:8000
```

### 3. **Start Frontend**
```bash
cd frontend
npm run dev
```

The app will run at: **http://localhost:3000**

### 4. **Use RAG Integration**

Navigate to Dashboard → Click "Fact Check with RAG" button and enter a claim.

---

## 📁 Files Created/Modified

### New Files

1. **`frontend/lib/rag-service.ts`**
   - API client for RAG pipeline
   - Request/response interfaces
   - Health check function
   - Response conversion utilities

2. **`frontend/components/input/AnalysisInputWithRAG.tsx`**
   - New input component with RAG integration
   - Forms requests to RAG API
   - Displays analysis results
   - Error handling

### Configuration

3. **`frontend/.env.example`**
   - Environment variable template
   - Shows RAG API URL configuration

---

## 🔄 Data Flow

```
User Input (Frontend)
        ↓
AnalysisInputWithRAG Component
        ↓
analyzeClaimWithRAG() → HTTP POST to /analyze
        ↓
RAG Pipeline (Python)
        ↓
Wikipedia Retrieval + Semantic Ranking + NLI
        ↓
RAGResponse (JSON)
        ↓
convertRAGResponseToAnalysisResult()
        ↓
Display Results (Dashboard)
```

---

## 🚀 Usage Examples

### Example 1: Simple Claim Analysis

```typescript
import { analyzeClaimWithRAG } from '@/lib/rag-service';

const result = await analyzeClaimWithRAG("Paris is the capital of France");

console.log(result.verdict);      // "TRUE"
console.log(result.confidence);   // 0.95
console.log(result.evidence.length); // 5
```

### Example 2: Using the Component

```typescript
import AnalysisInputWithRAG from '@/components/input/AnalysisInputWithRAG';

export default function Dashboard() {
  const handleResults = (results: any) => {
    console.log('Verdict:', results.verdict);
    console.log('Confidence:', results.confidence);
    console.log('Evidence:', results.sources);
  };

  return (
    <AnalysisInputWithRAG 
      onResultsReady={handleResults}
    />
  );
}
```

### Example 3: Check RAG Health

```typescript
import { checkRAGHealth } from '@/lib/rag-service';

const isHealthy = await checkRAGHealth();
console.log(isHealthy ? '✅ RAG API Online' : '❌ RAG API Offline');
```

---

## 🔌 API Endpoints

### POST /analyze
**Fact-check a claim**

Request:
```json
{
  "claim": "Paris is the capital of France",
  "top_k_evidence": 5
}
```

Response:
```json
{
  "success": true,
  "claim": "Paris is the capital of France",
  "verdict": "TRUE",
  "confidence": 0.95,
  "evidence": [
    {
      "sentence": "Paris is the capital of France...",
      "source": "Paris (Wikipedia)",
      "url": "https://en.wikipedia.org/wiki/Paris",
      "similarity_score": 0.98,
      "nli_entailment": 0.87,
      "nli_contradiction": 0.02,
      "nli_neutral": 0.11
    }
  ],
  "metadata": {
    "total_articles_fetched": 5,
    "total_sentences_extracted": 150,
    "final_evidence_count": 5,
    "processing_time_ms": 2450,
    "nli_enabled": false,
    "timestamp": "2026-03-27T10:30:00Z"
  }
}
```

### GET /health
**Check API status**

Response:
```json
{
  "status": "healthy",
  "service": "TruthLens RAG v2",
  "timestamp": "2026-03-27T10:30:00Z"
}
```

---

## 🎨 Component Integration

### Replace Old Input Component

In `frontend/app/dashboard/page.tsx`:

**Before:**
```typescript
import AnalysisInput from '@/components/input/AnalysisInput';
```

**After:**
```typescript
import AnalysisInputWithRAG from '@/components/input/AnalysisInputWithRAG';
```

Then use:
```typescript
<AnalysisInputWithRAG onResultsReady={handleAnalysisComplete} />
```

---

## 🔧 Troubleshooting

### 1. "RAG API not responding"

**Check if Python server is running:**
```bash
curl http://127.0.0.1:8000/health
```

**If not, start the server:**
```bash
cd backend
python3 rag_server.py
```

### 2. CORS Errors

**Add CORS middleware to FastAPI:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost:3000", "127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Network Issues

- Ensure both services are on same network
- Check firewall settings
- Try updating `.env.local` with server IP instead of localhost

---

## 📊 Understanding RAG Response

Each analysis returns:

- **verdict**: TRUE, FALSE, or UNCERTAIN
- **confidence**: 0.0 - 1.0 score (higher = more confident)
- **evidence**: Array of top-K evidence pieces with scores
- **metadata**: Processing details and timing

---

## 🚀 Production Deployment

### Update Environment Variable
```bash
# In production, use your actual backend URL
NEXT_PUBLIC_RAG_API_URL=https://rag-api.yourdomain.com
```

### Update Frontend Config
```typescript
// frontend/next.config.js
const nextConfig = {
  env: {
    RAG_API_URL: process.env.NEXT_PUBLIC_RAG_API_URL,
  },
};
```

---

## 📚 Related Files

- Backend API: [`backend/rag_server.py`]
- RAG Pipeline: [`backend/services/pipeline_new.py`]
- Core Modules:
  - [`backend/services/utils_new.py`] - Text utilities
  - [`backend/services/ranking_new.py`] - Semantic ranking
  - [`backend/services/retrieval_new.py`] - Wikipedia retrieval

---

## ✅ Testing

### Test in Browser Console

```javascript
// Fetch from frontend
fetch('http://127.0.0.1:8000/health')
  .then(r => r.json())
  .then(data => console.log('RAG API:', data));
```

### Test in Next.js

```typescript
// In any component or page
import { analyzeClaimWithRAG, checkRAGHealth } from '@/lib/rag-service';

// Check health
const healthy = await checkRAGHealth();
console.log('API Status:', healthy);

// Analyze claim
const result = await analyzeClaimWithRAG('Your claim here');
console.log('Result:', result);
```

---

## 🎯 Next Steps

1. ✅ Start frontend: `npm run dev`
2. ✅ Test RAG component in Dashboard
3. ✅ Monitor API calls in browser DevTools (Network tab)
4. ✅ Integrate saved analyses with Supabase
5. ✅ Add analytics tracking for claims analyzed

---

**Status: Frontend ↔ RAG Pipeline Connected and Ready to Use** ✨
