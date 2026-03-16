# TruthLens AI Backend

Backend API server for TruthLens misinformation detection system.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your API credentials
```

### 3. Run development server

```bash
python -m app.main
```

Server will start on `http://localhost:5000`

### 4. Run with Gunicorn (production)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app.main:app
```

## API Endpoints

### Health Check
- **GET** `/api/health` - Server health status

### Analysis
- **POST** `/api/analyze` - Analyze text/URL/image
  - FormData:
    - `text` (string, optional) - Text to analyze
    - `url` (string, optional) - URL to scrape and analyze
    - `image` (file, optional) - Image file to process
  - Returns: Analysis result with verdict and confidence

### Sessions
- **GET** `/api/sessions` - Get recent analysis sessions

### Export
- **GET** `/api/export/<result_id>` - Export analysis result

## Features

✅ **Multimodal Analysis**
- Text analysis using RoBERTa
- Image captioning using BLIP
- URL content extraction using WebScraping.ai

✅ **Evidence Retrieval**
- Pinecone vector search for corroborating evidence
- Evidence source attribution
- Support/contradiction scoring

✅ **Fusion Scoring**
- NLP score (60% weight)
- Evidence score (25% weight)
- Image sentiment score (15% weight)

✅ **Verdict Classification**
- FAKE: Score >= 70
- RUMOR: Score 30-70
- REAL: Score <= 30

## Testing

### Test with cURL

```bash
# Analyze text
curl -X POST http://localhost:5000/api/analyze \
  -F "text=The earth is flat"

# Analyze URL
curl -X POST http://localhost:5000/api/analyze \
  -F "url=https://example.com/article"

# Analyze image
curl -X POST http://localhost:5000/api/analyze \
  -F "image=@/path/to/image.jpg"

# Analyze with text and image
curl -X POST http://localhost:5000/api/analyze \
  -F "text=Some claim" \
  -F "image=@/path/to/image.jpg"
```

## Architecture

```
backend/
├── app/
│   ├── main.py                    # Flask application
│   ├── __init__.py               # Package init
│   └── services/
│       ├── nlp_analyzer.py        # Text analysis
│       ├── image_processor.py     # Image processing
│       ├── web_scraper.py         # URL scraping
│       └── evidence_retriever.py  # Evidence search
├── requirements.txt               # Python dependencies
└── .env.example                   # Environment template
```

## Environment Variables

- `HF_TOKEN` - Hugging Face API token
- `PINECONE_KEY` - Pinecone API key
- `SCRAPER_KEY` - WebScraping.ai API key
- `FLASK_ENV` - Environment (development/production)
- `BACKEND_PORT` - Server port (default: 5000)

## Error Handling

- **400** - Invalid request (missing required fields)
- **413** - File too large (max 10MB)
- **500** - Server error during analysis
- **501** - Feature not implemented

## CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:3000` (frontend dev server)
- `http://localhost:5000` (local testing)

Update `CORS_ORIGINS` in `.env` for production deployments.
