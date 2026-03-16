# ⚡ TruthLens AI - Quick Reference Card

## 🚀 Start in 60 Seconds

```bash
cd /Users/pratyush/ai\ truthlens/frontend
npm install
npm run dev
# Visit: http://localhost:3000
```

---

## 📋 Project At a Glance

| What | Details |
|------|---------|
| **Type** | Full-Stack AI Application |
| **Frontend** | Next.js 14 + React 18 + TypeScript |
| **Backend** | Serverless (Vercel Functions) |
| **AI Models** | RoBERTa, BLIP, Sentence-BERT |
| **APIs** | Hugging Face, Pinecone, WebScraping.ai |
| **Deployment** | Vercel (free tier) |
| **Files** | 17 total (5 TS/TSX, 6 config, 6 docs) |
| **Lines of Code** | 2,500+ |
| **Time to Production** | 5-10 minutes |

---

## 🎯 Key Features

✅ **Multimodal Input**
- Text analysis
- URL scraping & analysis
- Image captioning & analysis

✅ **AI Fusion Engine**
```
Score = (NLP*60%) + (Evidence*25%) + (Image*15%)
```

✅ **Professional UI**
- Dark theme with gradients
- Responsive design
- Smooth animations
- Real-time processing

✅ **Production Ready**
- TypeScript strict mode
- Error handling
- Input validation
- Vercel deployment

---

## 📁 Important Files

| File | Purpose | Edit When |
|------|---------|-----------|
| `app/page.tsx` | Main UI & logic | Customize dashboard |
| `app/api/analyze/route.ts` | API endpoint | Change analysis logic |
| `tailwind.config.ts` | Colors & theme | Rebrand colors |
| `package.json` | Dependencies | Add libraries |
| `.env.local` | API keys | Add real API keys |
| `vercel.json` | Deployment config | Change memory/timeout |

---

## 🔑 Environment Variables

```env
HF_TOKEN=your_hugging_face_token
PINECONE_API_KEY=your_pinecone_key
SCRAPER_API_KEY=your_webscraping_key
```

**Get keys from**:
- Hugging Face: https://huggingface.co/settings/tokens
- Pinecone: https://app.pinecone.io
- WebScraping.ai: https://webscraping.ai

---

## 💻 Common Commands

```bash
npm run dev           # Start dev server (localhost:3000)
npm run build         # Create production build
npm start             # Run production server
npm run lint          # Check code quality
npm run type-check    # TypeScript validation
vercel --prod         # Deploy to Vercel
```

---

## 🔌 API Reference

### POST `/api/analyze`
```bash
# Text Analysis
curl -X POST http://localhost:3000/api/analyze \
  -F "text=5G causes COVID"

# URL Analysis
curl -X POST http://localhost:3000/api/analyze \
  -F "url=https://example.com"

# Image Analysis
curl -X POST http://localhost:3000/api/analyze \
  -F "image=@image.png"
```

**Response**:
```json
{
  "verdict": "FAKE",
  "confidence": 92,
  "scores": { "real": 2, "fake": 92, "rumor": 6 },
  "summary": "...",
  "signals": ["..."],
  "evidenceSources": [...]
}
```

### GET `/api/analyze`
```bash
curl http://localhost:3000/api/analyze
# Returns health status
```

---

## 🎨 Customize in 2 Minutes

### Change Colors
Edit `tailwind.config.ts`:
```typescript
colors: {
  primary: { 500: "#FF6B6B" },    // Change primary
  secondary: { 500: "#4ECDC4" }   // Change secondary
}
```

### Change App Name
Edit `app/page.tsx` → Find "TruthLens" → Replace it

### Change API Timeout
Edit `vercel.json`:
```json
"functions": {
  "api/analyze.ts": { "maxDuration": 120 }
}
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 3000 in use | `npm run dev -- -p 3001` |
| Module not found | `npm install` |
| API key error | Add to `.env.local` |
| Vercel deploy fails | Check Node 18+, env vars |
| UI not updating | Clear `.next/` folder |

---

## 📚 Documentation

| File | For |
|------|-----|
| **START_HERE.md** | 60-second setup |
| **SETUP.md** | Detailed local setup |
| **DEPLOYMENT.md** | Vercel deployment |
| **BUILD_SUMMARY.md** | What was built |
| **README.md** | Features overview |
| **ARCHITECTURE.md** | System design |

---

## 🚀 Deployment Steps

### 1. Get API Keys (5 min)
- Hugging Face token
- Pinecone API key
- WebScraping.ai key

### 2. Deploy to Vercel (2 min)
```bash
npm install -g vercel
vercel --prod
```

### 3. Add Environment Variables (1 min)
- Dashboard → Settings → Environment Variables
- Add 3 keys above

### 4. Test (1 min)
- Visit your deployment URL
- Try text/URL/image analysis

**Total Time: ~9 minutes**

---

## 🎯 What Each Tab Does

### Text Tab
- Paste any text or claim
- RoBERTa analyzes for fake news
- Returns verdict + confidence

### URL Tab
- Paste article URL
- WebScraping.ai extracts content
- System analyzes the article
- Shows evidence sources

### Image Tab
- Upload PNG/JPG image
- BLIP generates description
- System analyzes the caption
- Returns image-based signals

---

## 🔐 Security Notes

✅ API keys stored in Vercel environment variables (encrypted)
✅ No secrets committed to Git
✅ Input validation on all endpoints
✅ HTTPS enforced (automatic)
✅ CORS configured

---

## 📊 System Architecture

```
Browser (Next.js Frontend)
    ↓ (multipart/form-data)
Next.js API Route (/api/analyze)
    ↓
├─ Hugging Face API (RoBERTa + BLIP)
├─ Pinecone API (Evidence)
└─ WebScraping.ai API (URL content)
    ↓
JSON Response
    ↓
Dashboard Display
```

---

## 🎓 Learning Resources

- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev)
- [TypeScript](https://www.typescriptlang.org)
- [Tailwind CSS](https://tailwindcss.com)
- [Vercel Deployment](https://vercel.com/docs)

---

## ✨ Pro Tips

1. **Development**: Add `// @ts-ignore` for quick debugging
2. **Styling**: Use `className` for Tailwind classes
3. **API**: Always validate input in `/api/analyze`
4. **Performance**: Cache Hugging Face models locally
5. **Deployment**: Use Vercel Pro for longer timeouts

---

## 📞 Quick Support

**Issue?** Check:
1. Is Node 18+ installed? → `node --version`
2. Did you run `npm install`? → Check `node_modules/`
3. Are env vars set? → Check `.env.local`
4. Is port 3000 free? → `npm run dev -- -p 3001`

---

## ✅ Launch Checklist

- [ ] `npm install` completed
- [ ] `npm run dev` works
- [ ] Can load `http://localhost:3000`
- [ ] Can input text & analyze
- [ ] Can upload image
- [ ] Can enter URL
- [ ] Ready to add API keys? ✨

---

**You're all set!**

```bash
npm run dev    # 🚀 Launch now
vercel --prod  # 📡 Deploy when ready
```

---

**Built with ❤️ | Production Ready ✅**
