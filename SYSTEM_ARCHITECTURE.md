# TruthLens Architecture & Data Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRUTHLENS AI SYSTEM                          │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────┐    ┌──────────────────────────────┐
│    FRONTEND (Next.js 14)     │    │   BACKEND (Flask Python)     │
│     Port 3000                │    │     Port 5000                │
├──────────────────────────────┤    ├──────────────────────────────┤
│                              │    │                              │
│  components/                 │    │  app/                        │
│  ├── AnalysisInput.tsx       │    │  ├── main.py (Flask app)     │
│  ├── ResultsDashboard.tsx    │    │  └── services/               │
│  ├── VerdictCard.tsx         │    │      ├── nlp_analyzer.py     │
│  ├── EvidenceEngineTable.tsx │    │      ├── image_processor.py  │
│  └── ...                     │    │      ├── web_scraper.py      │
│                              │    │      └── evidence_retriever  │
│  services/                   │    │                              │
│  └── api.ts (TruthLensAPI)   │    │  External APIs:              │
│      ↓                       │    │  • Hugging Face (HF)         │
│    POST /api/analyze         │◄───┤  • Pinecone                  │
│    (FormData)                │    │  • WebScraping.ai            │
│                              │    │                              │
│  .env.local:                 │    │  .env:                       │
│  NEXT_PUBLIC_API_URL=        │    │  HF_TOKEN=...               │
│  http://localhost:5000       │    │  PINECONE_KEY=...           │
│                              │    │  SCRAPER_KEY=...            │
└──────────────────────────────┘    └──────────────────────────────┘
         HTTP/REST                           HTTP/JSON
            ↕                                   ↕
        AXIOS                              REQUESTS
```

## Data Flow - Analysis Pipeline

```
┌──────────────────┐
│   User Input     │
│  • Text          │
│  • URL           │
│  • Image         │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────┐
│  Frontend Component          │
│  AnalysisInput.tsx           │
└────────┬─────────────────────┘
         │
         │ FormData
         │ text/url/image
         │
         ▼
┌──────────────────────────────┐
│  API Client                  │
│  services/api.ts             │
│  POST /api/analyze           │
└────────┬─────────────────────┘
         │
         │ HTTP Request
         │ FormData
         │
         ▼
    [NETWORK]
         │
         ▼
┌──────────────────────────────┐
│  Backend Flask Server        │
│  app/main.py                 │
│  POST /api/analyze           │
└────────┬─────────────────────┘
         │
         ├─────────────────────────────────────────┐
         │                                         │
         ▼                                         ▼
    ┌─────────────┐                        ┌─────────────┐
    │   Image?    │ YES                    │   URL?      │
    └──┬──────────┘                        └──┬──────────┘
       │                                       │ YES
       │ YES                                   │
       ▼                                       ▼
  ┌──────────────────┐              ┌──────────────────┐
  │ Image Processing │              │  URL Scraping    │
  │ (BLIP Model)     │              │ (WebScraping.ai) │
  │ Hugging Face API │              │                  │
  └────────┬─────────┘              └────────┬─────────┘
           │                                 │
           │ Caption                        │ Text
           ▼                                 ▼
    ┌─────────────────────────────────────────────┐
    │  Analyze Text Content                       │
    │  ✓ NLP Analysis (RoBERTa)                   │
    │  ✓ Generate Embeddings                      │
    └────────┬──────────────────────┬─────────────┘
             │                      │
             │ NLP Score            │ Embeddings
             │ (0-100)              │ (384D vector)
             │                      │
             ▼                      ▼
    ┌──────────────┐        ┌──────────────────┐
    │ Score: 75    │        │ Vector Search    │
    │ Label: FAKE  │        │ Pinecone         │
    └──────┬───────┘        │ (Evidence DB)    │
           │                └────────┬─────────┘
           │                         │
           │                         │ Evidence Sources
           │                         │ [Reuters, Snopes, ...]
           │                         ▼
           │                 ┌──────────────────┐
           │                 │ Evidence Score   │
           │                 │ Relevance: 78%   │
           │                 └────────┬─────────┘
           │                          │
           └──────────┬───────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  Fusion Scoring             │
        │  NLP (60%) + Evidence (25%) │
        │  + Image (15%)              │
        │  Final Score: 82%           │
        └────────┬────────────────────┘
                 │
                 ▼
        ┌─────────────────────────────┐
        │  Determine Verdict          │
        │  >= 70: FAKE                │
        │  30-70: RUMOR               │
        │  <= 30: REAL                │
        └────────┬────────────────────┘
                 │
                 ▼
        ┌─────────────────────────────┐
        │  Prepare Response           │
        │  {                          │
        │    verdict: "FAKE",         │
        │    confidence: 82,          │
        │    details: {...},          │
        │    processingTime: 2400ms   │
        │  }                          │
        └────────┬────────────────────┘
                 │
                 │ HTTP 200 OK
                 │ JSON Response
                 │
         [NETWORK]
                 │
                 ▼
    ┌─────────────────────────┐
    │ Frontend Receives       │
    │ Analysis Result         │
    └────────┬────────────────┘
             │
             ▼
    ┌─────────────────────────┐
    │ Display Results         │
    │ ResultsDashboard.tsx    │
    │ • VerdictCard           │
    │ • EvidenceTable         │
    │ • SentimentChart        │
    │ • PropagationGraph      │
    └─────────────────────────┘
```

## Component Interaction Diagram

```
Frontend                          Backend
========                          =======

┌─────────────────┐              ┌──────────────────┐
│ AnalysisInput   │──── (1) ────→│ main.py          │
│ Component       │  FormData    │ /api/analyze     │
│                 │              │                  │
│ • Text input    │              │ (2) Process      │
│ • File upload   │              │ ├─ NLP Analysis  │
│ • URL input     │              │ ├─ Image Caption │
└────────┬────────┘              │ ├─ URL Scraping  │
         │                       │ └─ Evidence      │
         │ State update          │                  │
         ▼                       │ (3) Call APIs    │
┌─────────────────────┐          │ ├─ Hugging Face  │
│ services/api.ts     │          │ ├─ Pinecone      │
│ TruthLensAPI        │          │ └─ WebScraping.ai│
│                     │          │                  │
│ analyzeText()       │          │ (4) Fuse Scores  │
│ analyzeImage()      │          │ └─ Calculate     │
│ analyzeURL()        │          │    Verdict       │
│ analyzeMultimodal() │          │                  │
└────────┬────────────┘          └────────┬─────────┘
         │                                │
         │ (5) Receive Response           │
         │←─────────────────────────────  │
         │ JSON with verdict/details      │
         │                                │
         ▼                                │
┌─────────────────────────────────┐      │
│ ResultsDashboard.tsx            │      │
│                                 │      │
│ ┌──────────────────────────────┐│      │
│ │ VerdictCard                  ││      │
│ │ • Display verdict: FAKE      ││      │
│ │ • Show confidence: 82%       ││      │
│ │ • Visual gauge               ││      │
│ └──────────────────────────────┘│      │
│                                 │      │
│ ┌──────────────────────────────┐│      │
│ │ EvidenceEngineTable          ││      │
│ │ • Show sources               ││      │
│ │ • Relevance scores           ││      │
│ │ • CONFIRMS/CONTRADICTS       ││      │
│ └──────────────────────────────┘│      │
│                                 │      │
│ ┌──────────────────────────────┐│      │
│ │ SentimentAndBias             ││      │
│ │ • NLP score chart            ││      │
│ │ • Emotion analysis           ││      │
│ └──────────────────────────────┘│      │
│                                 │      │
│ ┌──────────────────────────────┐│      │
│ │ PropagationGraph             ││      │
│ │ • Network visualization      ││      │
│ │ • Spread pattern             ││      │
│ └──────────────────────────────┘│      │
└─────────────────────────────────┘      │
```

---

This architecture ensures:
✅ Clean separation of concerns
✅ Scalability (backend can be scaled independently)
✅ Easy testing (each component can be tested separately)
✅ Production-ready (Docker containerization)
✅ Secure credential management (environment variables)
✅ Robust error handling and recovery
