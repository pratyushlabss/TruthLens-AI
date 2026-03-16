# Quick Start - TruthLens AI

## 🚀 Start Everything with Docker (Easiest)

```bash
cd /Users/pratyush/ai\ truthlens
docker-compose up --build
```

Then open:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api/health

---

## 🛠️ Manual Development Setup

### Terminal 1: Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```
Backend runs on: http://localhost:5000

### Terminal 2: Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on: http://localhost:3000

---

## 📝 Test the API

```bash
# Check backend health
curl http://localhost:5000/api/health

# Analyze text
curl -X POST http://localhost:5000/api/analyze \
  -F "text=The earth is flat"

# Analyze image
curl -X POST http://localhost:5000/api/analyze \
  -F "image=@/path/to/image.jpg"

# Analyze URL
curl -X POST http://localhost:5000/api/analyze \
  -F "url=https://example.com"
```

---

## 🔑 Credentials (Already Configured)

- ✅ HF_TOKEN: `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`
- ✅ PINECONE_KEY: `pcsk_4GpH3o_LT2E8HvMKk1n2eR3ZAbFqiFD3xS5TxxMcDYujatBNZvcMYpvzrZP3dGj9qeHj9p`
- ✅ SCRAPER_KEY: `eb66d83d-416a-4f5e-8c7c-d5c2b6f89541`

---

## 📂 Project Structure

```
/Users/pratyush/ai truthlens/
├── frontend/               # React Next.js UI
│   ├── services/api.ts     # API client
│   └── .env.local          # Set NEXT_PUBLIC_API_URL
├── backend/                # Flask API
│   ├── app/main.py         # Flask app
│   ├── app/services/       # AI services
│   └── requirements.txt
├── docker-compose.yml      # Docker orchestration
└── SETUP_GUIDE.md          # Full documentation
```

---

## ✨ Features

| Feature | Backend | Frontend |
|---------|---------|----------|
| **Text Analysis** | ✅ RoBERTa NLP | ✅ Input form |
| **Image Processing** | ✅ BLIP captioning | ✅ File upload |
| **URL Scraping** | ✅ WebScraping.ai | ✅ URL input |
| **Evidence Search** | ✅ Pinecone | ✅ Results display |
| **Verdict** | ✅ Fusion scoring | ✅ Visual card |

---

## 🔗 API Response Example

```json
{
  "verdict": "FAKE",
  "confidence": 87,
  "details": {
    "nlpScore": 92,
    "evidenceScore": 78,
    "summary": "This claim has an 87% likelihood of being fake.",
    "keySignals": [
      "NLP model indicates likely misinformation",
      "Found contradicting evidence"
    ],
    "evidenceSources": [
      {
        "name": "Reuters Fact Check",
        "relevance": 85,
        "supports": "CONTRADICTS"
      }
    ]
  },
  "processingTime": 2400
}
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| CORS error | Check `NEXT_PUBLIC_API_URL` in frontend/.env.local |
| Connection refused | Ensure backend is running on port 5000 |
| Docker fails | Run `docker-compose down` then `docker-compose up --build` |
| Module not found | Run `pip install -r requirements.txt` or `npm install` |

---

## 📖 More Info

- Full setup: See `SETUP_GUIDE.md`
- Backend docs: See `backend/README.md`
- Integration complete: See `INTEGRATION_COMPLETE.md`

---

**Ready to analyze misinformation!** 🎯
