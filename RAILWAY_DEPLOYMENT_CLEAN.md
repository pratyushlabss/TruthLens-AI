# 🚀 TruthLens AI - Railway Deployment Guide (Clean PostgreSQL)

## Overview
Deploy TruthLens AI backend to Railway using **PostgreSQL only** - no Supabase needed.

---

## Step 1: Create Railway Project

1. Go to [Railway](https://railway.app)
2. Create new project → Select "From GitHub"
3. Connect to your GitHub repo (`TruthLens-AI`)
4. Select `main` branch

---

## Step 2: Add PostgreSQL Database

1. In Railway dashboard → Click "Add Service"
2. Select "PostgreSQL"
3. Railway will:
   - Create a PostgreSQL database
   - Provide `DATABASE_URL` environment variable automatically

---

## Step 3: Configure Backend Environment Variables

In Railway dashboard → Variables tab, add:

### **Required API Keys** ⚠️
```
OPENAI_API_KEY=sk-your-actual-openai-key
TAVILY_API_KEY=tvly-your-actual-tavily-key
```

**Get these from:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Tavily**: https://tavily.com/api

### **Auto-Populated by Railway** ✅
```
DATABASE_URL=postgresql://...  (Auto-set when PostgreSQL service added)
```

### **Optional Configuration**
```
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false
OPENAI_MODEL=gpt-4
API_TIMEOUT=30
ANALYSIS_TIMEOUT=45
MAX_SEARCH_RESULTS=5
```

### **CORS Setup** ⚠️
Update with your actual Vercel frontend URL:
```
CORS_ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
ALLOWED_HOSTS=your-railway-backend.up.railway.app
```

---

## Step 4: Deploy

1. Click "Deploy" in Railway dashboard
2. Watch build logs
3. Once deployed, get your backend URL from Railway (e.g., `https://truthlens-api.railway.app`)

---

## Step 5: Connect Frontend to Backend

Go to **Vercel Dashboard** → Your App → Settings → Environment Variables

Add:
```
NEXT_PUBLIC_API_BASE_URL=https://your-railway-backend.up.railway.app
```

Vercel auto-redeploys. ✅

---

## Step 6: Test Integration

1. Open your Vercel frontend
2. Log in with test credentials:
   ```
   Email: test@truthlens.local
   Password: password123
   ```
3. Go to Dashboard → Analyze
4. Test a claim
5. Should see analysis from backend

---

## Database Management

### Connect to Railway PostgreSQL
```bash
# Get credentials from Railway dashboard
psql postgresql://user:password@your-railway-host:5432/railway
```

### View tables
```sql
SELECT * FROM analyses;
SELECT * FROM sessions;
```

---

## Troubleshooting

### Build Fails
- Check logs in Railway → Deploy logs
- Ensure `requirements.txt` not corrupted
- Verify startup scripts are executable

### Backend 500 Error
- Check Railway logs
- Verify API keys (OPENAI_API_KEY, TAVILY_API_KEY)
- Verify DATABASE_URL is set

### Frontend Can't Reach Backend
- Verify `CORS_ALLOWED_ORIGINS` includes your Vercel URL
- Check Network tab in browser DevTools
- Verify `NEXT_PUBLIC_API_BASE_URL` is correct in Vercel

---

## Your Backend is Ready! 🎉
No Supabase, no Redis, just pure PostgreSQL + FastAPI on Railway.
