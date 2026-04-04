# TruthLens AI - Vercel + Railway Deployment Guide

## Step-by-Step Deployment (15 minutes)

### PART 1: VERCEL SETUP (Frontend) - 3 minutes

#### Step 1: Install Vercel CLI
```bash
npm i -g vercel
```

#### Step 2: Deploy Frontend
```bash
cd /Users/pratyush/ai\ truthlens/frontend
vercel --prod
```

**Follow prompts:**
- Create new project? → `y`
- Project name → `truthlens` (or your choice)
- Link to existing project? → `n`
- Codebase location? → `./`

**Get your frontend URL:** (will be like `https://truthlens.vercel.app`)

---

### PART 2: RAILWAY SETUP (Backend + Database) - 10 minutes

#### Step 1: Sign Up to Railway
Visit: https://railway.app
- Sign up with GitHub
- Connect your GitHub account

#### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub"
3. Authorize Railway to access GitHub
4. Select your `truthlens-ai` repository
5. Click "Deploy"

#### Step 3: Add PostgreSQL Database
1. In Railway dashboard, click "Add Service"
2. Search for "PostgreSQL"
3. Click "PostgreSQL" → Create
4. Wait for it to be ready (green checkmark)

#### Step 4: Add Redis Cache
1. Click "Add Service" again
2. Search for "Redis"
3. Click "Redis" → Create
4. Wait for it to be ready

#### Step 5: Configure Environment Variables

**In Railway Dashboard:**
1. Click on your project
2. Go to "Variables" tab
3. Add these variables:

```
DATABASE_URL=<Copy from PostgreSQL service>
REDIS_URL=<Copy from Redis service>
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
LOG_LEVEL=INFO
ENVIRONMENT=production
DEBUG=false
CORS_ALLOWED_ORIGINS=https://yourfrontend.vercel.app
```

**How to get DATABASE_URL from PostgreSQL:**
- Click PostgreSQL service
- Go to "Connect" tab
- Copy PostgreSQL connection string
- Format: `postgresql://user:password@host:port/database`

**How to get REDIS_URL from Redis:**
- Click Redis service
- Go to "Connect" tab
- Copy Redis connection string
- Format: `redis://default:password@host:port`

#### Step 6: Set Build & Start Commands

1. Click your project
2. Go to "Settings" tab
3. Find "Build Command" → Set to:
   ```
   cd backend && pip install -r requirements.txt
   ```
4. Find "Start Command" → Set to:
   ```
   cd backend && uvicorn main:app --host 0.0.0.0 --port 8000
   ```

#### Step 7: Deploy
- Railway will auto-deploy from your GitHub repo
- Watch the logs for deployment status
- Should take ~2-3 minutes

**Get your backend URL:** (will be like `https://truthlens-api-prod.up.railway.app`)

---

### PART 3: CONNECT FRONTEND TO BACKEND - 2 minutes

#### Step 1: Set Frontend Environment Variable in Vercel

1. Go to Vercel Dashboard
2. Select your project
3. Go to "Settings" → "Environment Variables"
4. Add new variable:
   ```
   NEXT_PUBLIC_API_BASE_URL=<your-railway-backend-url>
   ```
   (e.g., `https://truthlens-api-prod.up.railway.app`)

5. Click "Save"
6. Redeploy: Click "Deployments" → "Redeploy"

#### Step 2: Set NEXTAUTH Variables in Vercel

1. In Vercel Environment Variables, add:
   ```
   NEXTAUTH_URL=https://yourfrontend.vercel.app
   NEXTAUTH_SECRET=<generate: openssl rand -base64 32>
   ```

2. Redeploy again

---

### PART 4: TEST YOUR DEPLOYMENT

#### Test Backend Health
```bash
curl https://yourbackend.up.railway.app/health
```
Expected response:
```json
{"status": "ok", "version": "3.2"}
```

#### Test Frontend
Open browser: `https://yourfrontend.vercel.app/dashboard`

#### Test Claim Analysis
1. Go to dashboard
2. Enter a test claim (e.g., "Paris is the capital of France")
3. Click "Analyze"
4. Should see results within 5-10 seconds

---

## Useful Commands

### Update After Git Push
```bash
# Railway auto-deploys when you push to GitHub
git add .
git commit -m "Update"
git push origin main

# Vercel auto-deploys too!
```

### View Backend Logs (Railway)
```bash
npm i -g @railway/cli
railway login
railway logs
```

### View Frontend Logs (Vercel)
- Vercel Dashboard → Your Project → "Function Logs"

### Rollback
**Vercel:**
- Dashboard → Deployments → Select previous → Click "Revert"

**Railway:**
- Dashboard → Deployments → Select previous → Click "Redeploy"

---

## Troubleshooting

### Frontend shows blank page
- Check browser console for errors
- Verify NEXT_PUBLIC_API_BASE_URL is set in Vercel
- Check that backend health check passes

### API calls fail (CORS error)
- Verify CORS_ALLOWED_ORIGINS in Railway matches Vercel URL
- Check frontend NEXT_PUBLIC_API_BASE_URL is correct
- Redeploy both services

### Claims show "Error" without processing
- Check Railway logs: `railway logs`
- Verify OPENAI_API_KEY and TAVILY_API_KEY are set
- Add more environment variables if needed

### Database connection fails
- Verify DATABASE_URL is correct
- Check PostgreSQL service is running in Railway
- Try copying connection string again

### Can't connect to Redis
- Verify REDIS_URL is correct
- Check Redis service is running in Railway
- Ensure password is correct

---

## Cost Estimate

| Service | Free Tier | Cost if Needed |
|---------|-----------|---|
| Vercel Frontend | Up to 200k requests/day | $20/month |
| Railway Backend | $5/month credit | ~$20-40/month |
| PostgreSQL (100GB) | Included | Included |
| Redis | Included | Included |
| **Total** | **FREE** | **~$40-60/month** |

---

## Domain Setup (Optional)

### Add Custom Domain to Vercel
1. Vercel Dashboard → Settings → Domains
2. Add your domain (e.g., truthlens.com)
3. Follow DNS instructions
4. Wait 24-48 hours for DNS propagation

### Add Custom Domain to Railway
1. Railway Dashboard → Your Project → Settings → Domains
2. Add your domain
3. Update DNS records as instructed

---

## Need Help?

**Vercel Support:** https://vercel.com/support  
**Railway Support:** https://railway.app/contact  
**TruthLens Issues:** Open issue on GitHub

---

**Status:** ✅ Ready for Deployment  
**Time to Deploy:** ~15 minutes  
**Difficulty:** ⭐⭐ (Very Easy)
