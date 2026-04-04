# 🚀 TruthLens AI - Vercel + Railway Quick Deployment Checklist

**Estimated Time:** 15 minutes  
**Difficulty:** ⭐⭐ (Very Easy)  
**All Done?** You'll have a live, production app! ✨

---

## ✅ PRE-DEPLOYMENT (Do First!)

- [ ] Ensure GitHub repo is up to date
  ```bash
  git add .
  git commit -m "Ready for deployment"
  git push origin main
  ```

- [ ] Get your API keys ready:
  - [ ] OpenAI API Key (sk-...)
  - [ ] Tavily API Key (tvly-...)

- [ ] Generate NEXTAUTH_SECRET
  ```bash
  openssl rand -base64 32
  # Save this value!
  ```

---

## 🔷 STEP 1: VERCEL FRONTEND (3 minutes)

### 1.1 Install & Login to Vercel
```bash
npm i -g vercel
vercel login
```
Follow the browser prompt to authorize

### 1.2 Deploy Frontend
```bash
cd frontend
vercel --prod
```

**When prompted:**
- "Set up & deploy?" → `y`
- "Which scope?" → Your personal account
- "Link to existing project?" → `n`
- "What's your project's name?" → `truthlens`
- "In which directory is your code?" → `./`
- "Want to modify vercel.json?" → `n`

**Wait for deployment (~1-2 min)**

### 1.3 Save Your Frontend URL
```
https://truthlens.vercel.app  (or your custom)
```

**Status:** ✅ Frontend live!

---

## 🔴 STEP 2: RAILWAY BACKEND (10 minutes)

### 2.1 Create Railway Account
Visit: https://railway.app
- Click "Sign Up"
- Use GitHub to sign up
- Authorize Railway to access GitHub

### 2.2 Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub"
3. Authorize Railway
4. Select `truthlens-ai` repository
5. **⚠️ Choose template:**
   - Select "Python" (or "Other")
   - **Build Command:** `cd backend && pip install -r requirements.txt`
   - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port 8000`
   - Click "Deploy"

**Wait for initial deployment (~2-3 min)**

### 2.3 Add PostgreSQL Database
1. In Railway dashboard (your project)
2. Click the "+" button → "Add Service"
3. Search for "PostgreSQL"
4. Click "PostgreSQL" → "Create"
5. Wait for status to be ✅ green

### 2.4 Add Redis Cache
1. Click the "+" button again → "Add Service"
2. Search for "Redis"
3. Click "Redis" → "Create"
4. Wait for status to be ✅ green

### 2.5 Get Database Connection Strings

**Get PostgreSQL URL:**
1. Click "PostgreSQL" service
2. Click "Connect" tab
3. Under "Postgres Connection String" copy the value
4. Should look like: `postgresql://user:password@host:port/database`

**Get Redis URL:**
1. Click "Redis" service
2. Click "Connect" tab
3. Copy the "Redis Connection String"
4. Should look like: `redis://default:password@host:port`

**Save these!** You'll need them.

### 2.6 Add Backend Environment Variables

1. Click your main project service (your-app-xxx)
2. Click "Variables" tab
3. Add these variables **one by one**:

```
DATABASE_URL = postgresql://...  (paste PostgreSQL URL)
REDIS_URL = redis://...           (paste Redis URL)
OPENAI_API_KEY = sk-...           (your OpenAI key)
TAVILY_API_KEY = tvly-...         (your Tavily key)
LOG_LEVEL = INFO
ENVIRONMENT = production
DEBUG = false
CORS_ALLOWED_ORIGINS = https://truthlens.vercel.app
```

### 2.7 Get Your Backend URL

1. In your project, click your main service
2. Go to "Deployments" tab
3. Look for "Domains" section
4. Copy your Railway URL
5. Should look like: `https://truthlens-production-xxxx.up.railway.app`

**Save this!** You need it for frontend.

**Status:** ✅ Backend + Database + Cache live!

---

## 🔗 STEP 3: CONNECT FRONTEND TO BACKEND (2 minutes)

### 3.1 Update Frontend Environment Variables

1. Go to Vercel Dashboard: https://vercel.com
2. Select your `truthlens` project
3. Go to "Settings" → "Environment Variables"
4. Add these variables:

```
Key: NEXT_PUBLIC_API_BASE_URL
Value: https://truthlens-production-xxxx.up.railway.app  (your Railway URL)

Key: NEXTAUTH_URL
Value: https://truthlens.vercel.app  (your Vercel URL)

Key: NEXTAUTH_SECRET
Value: abc123def456...  (the one you generated earlier)
```

### 3.2 Redeploy Frontend

1. Go to "Deployments" tab
2. Find the latest deployment
3. Click "..." menu → "Redeploy"
4. Wait ~1 minute

**Status:** ✅ Frontend connected to Backend!

---

## 🧪 STEP 4: TEST DEPLOYMENT (2 minutes)

### 4.1 Test Backend Health
```bash
curl https://your-railway-url.up.railway.app/health
```

Expected response:
```json
{"status": "ok", "version": "3.2"}
```

### 4.2 Test Frontend
Open in browser:
```
https://truthlens.vercel.app/dashboard
```

You should see the TruthLens dashboard!

### 4.3 Test Full Analysis
1. In dashboard, enter a test claim:
   ```
   "Paris is the capital of France"
   ```
2. Click "Analyze" button
3. Wait 5-10 seconds
4. You should see:
   - Verdict (TRUE/FALSE/UNCERTAIN)
   - Confidence score
   - Evidence sources
   - Explanation

**Status:** ✅ Everything Working!

---

## 📝 FINAL CHECKLIST

✅ **Deployment Complete:**
- [ ] Vercel frontend deployed
- [ ] Railway backend deployed
- [ ] PostgreSQL database created
- [ ] Redis cache created
- [ ] Environment variables set
- [ ] Frontend & backend connected
- [ ] Health check passes
- [ ] Can analyze claims in dashboard

✅ **Your Live URLs:**
```
Frontend:  https://truthlens.vercel.app
Backend:   https://your-railway-url.up.railway.app
Dashboard: https://truthlens.vercel.app/dashboard
```

---

## 🆘 TROUBLESHOOTING

### Frontend loads but shows error
1. Check browser console (F12)
2. Verify NEXT_PUBLIC_API_BASE_URL in Vercel is correct
3. Redeploy Vercel frontend

### API calls fail / CORS error
1. Check CORS_ALLOWED_ORIGINS in Railway matches your Vercel URL
2. Verify backend is running (check Railway logs)

### "Database connection failed"
1. Verify DATABASE_URL in Railway is set correctly
2. Check PostgreSQL service status (should be ✅ green)
3. Copy connection string again

### Claims fail to analyze
1. Check OPENAI_API_KEY is set correctly
2. Check TAVILY_API_KEY is set correctly
3. View Railway logs: `railway logs`

### Can't connect to Redis
1. Verify REDIS_URL in Railway is correct
2. Check Redis service is running (should be ✅ green)

---

## 🎉 WHAT'S NEXT?

✅ Your app is live!

Optional next steps:
- [ ] Add custom domain (Vercel settings)
- [ ] Setup monitoring/alerts
- [ ] Invite team members
- [ ] Backup database configuration

---

**You're Done!** 🎉

Your production app is now live 24/7 with automatic scaling, backups, and monitoring!

Need help? Check the full guide: `DEPLOY_VERCEL_RAILWAY_GUIDE.md`
