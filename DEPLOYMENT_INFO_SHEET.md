# 📋 Deployment Information Sheet (Fill In As You Go)

**Keep this sheet handy during deployment!**

---

## 🔑 API Keys (Keep Secure!)

```
OpenAI API Key:  sk-_____________________________________________________
Tavily API Key:  tvly-__________________________________________________
NEXTAUTH_SECRET: ________________________________________________________
```

**Generate NEXTAUTH_SECRET:**
```bash
openssl rand -base64 32
```

---

## 🔷 VERCEL FRONTEND

**Sign Up URL:** https://vercel.com

```
Vercel Account Email: ____________________________________________________
Project Name:         truthlens
Frontend URL:         https://______________________.vercel.app
GitHub Repo:          https://github.com/[username]/truthlens-ai
```

**Deployment Status:**
- [ ] Successfully deployed to Vercel
- [ ] Frontend URL is live

---

## 🔴 RAILWAY BACKEND

**Sign Up URL:** https://railway.app

```
Railway Account Email: ____________________________________________________
Project Name:          truthlens-ai
Backend URL:           https://______________________.up.railway.app
GitHub Repo:           https://github.com/[username]/truthlens-ai
```

**Services Created:**
- [ ] Main App Service (Python Backend)
- [ ] PostgreSQL Database
- [ ] Redis Cache

### Database Information

**PostgreSQL:**
```
Connection String: postgresql://____________________________________________________
Host:              ____________________________________________________
Port:              5432
Database:          railway
Username:          postgres
Password:          ____________________________________________________
```

**Redis:**
```
Connection String: redis://________________________________________________________
Host:              ____________________________________________________
Port:              6379
Password:          ____________________________________________________
```

---

## 🔗 ENVIRONMENT VARIABLES

### Frontend (Vercel Dashboard → Settings → Environment Variables)

```
NEXT_PUBLIC_API_BASE_URL = https://______________________.up.railway.app
NEXTAUTH_URL = https://______________________.vercel.app
NEXTAUTH_SECRET = ________________________________________________________
```

### Backend (Railway Dashboard → Variables tab)

```
DATABASE_URL = postgresql://____________________________________________________
REDIS_URL = redis://________________________________________________________
OPENAI_API_KEY = sk-_____________________________________________________
TAVILY_API_KEY = tvly-__________________________________________________
LOG_LEVEL = INFO
ENVIRONMENT = production
DEBUG = false
CORS_ALLOWED_ORIGINS = https://______________________.vercel.app
```

---

## ✅ DEPLOYMENT STAGES

### Stage 1: Vercel Frontend
- [ ] Created Vercel account
- [ ] Installed Vercel CLI: `npm i -g vercel`
- [ ] Ran: `vercel --prod` from frontend folder
- [ ] Frontend URL created: `https://______________________.vercel.app`
- [ ] Verified frontend loads in browser

### Stage 2: Railway Backend
- [ ] Created Railway account
- [ ] Connected GitHub repository
- [ ] Initial deployment started
- [ ] PostgreSQL service created
- [ ] Redis service created
- [ ] Backend URL created: `https://______________________.up.railway.app`

### Stage 3: Environment Variables
- [ ] Copied PostgreSQL connection string
- [ ] Copied Redis connection string
- [ ] Added DATABASE_URL to Railway
- [ ] Added REDIS_URL to Railway
- [ ] Added OPENAI_API_KEY to Railway
- [ ] Added TAVILY_API_KEY to Railway
- [ ] Added CORS_ALLOWED_ORIGINS to Railway
- [ ] Added NEXT_PUBLIC_API_BASE_URL to Vercel
- [ ] Added NEXTAUTH_URL to Vercel
- [ ] Added NEXTAUTH_SECRET to Vercel

### Stage 4: Testing
- [ ] Backend health check passes: `curl https://....../health`
- [ ] Frontend dashboard loads: `https://....../dashboard`
- [ ] Can analyze test claim successfully
- [ ] Analytics dashboard shows data

---

## 🧪 TEST COMMANDS

Copy and paste these commands:

**Test Backend Health:**
```bash
curl https://your-railway-backend-url.up.railway.app/health
```

**Test Frontend:**
Open in browser:
```
https://your-vercel-url.vercel.app/dashboard
```

**Test Analysis:**
1. Enter claim: "Paris is the capital of France"
2. Click "Analyze"
3. Should return within 5-10 seconds

---

## 📞 Support Links

| Service | Link | Issue Type |
|---------|------|-----------|
| Vercel | https://vercel.com/support | Frontend deployment |
| Railway | https://railway.app/contact | Backend/database issues |
| OpenAI | https://help.openai.com | API key/billing issues |
| Tavily | https://docs.tavily.com | Search API issues |

---

## 🔄 FUTURE UPDATES

When you make changes to your code:

```bash
# Stage changes
git add .

# Commit with message
git commit -m "Update: description of changes"

# Push to GitHub
git push origin main
```

✅ **Auto-Deploy:**
- Vercel will auto-redeploy frontend (~2-3 min)
- Railway will auto-redeploy backend (~2-3 min)

---

## 📊 MONITORING

### Vercel Dashboard
- **URL:** https://vercel.com/dashboard
- Check: Deployments, Functions, Environment Variables

### Railway Dashboard
- **URL:** https://railway.app/dashboard
- Check: Deployments, Logs, Services, Variables

### View Live Logs

**Railway Backend Logs:**
```bash
npm i -g @railway/cli
railway login
railway logs
```

**Vercel Frontend Function Logs:**
- Vercel Dashboard → Your Project → Function Logs tab

---

## 🚨 ROLLBACK PROCEDURE

**If something breaks:**

### Vercel Rollback
1. Go to Vercel Dashboard
2. Select project
3. Go to "Deployments"
4. Click previous deployed version
5. Click "Redeploy"

### Railway Rollback
1. Go to Railway Dashboard
2. Go to "Deployments"
3. Select previous working deployment
4. Click "Redeploy"

---

## 💾 BACKUP YOUR INFO

**Print or screenshot this page after filling it in!**

You'll need this info for:
- Future updates
- Troubleshooting
- Team onboarding
- Disaster recovery

---

**Last Updated:** ________________  
**Deployment Status:** ________________  
**Notes:** ________________________________________________________________

---

✅ Good luck with your deployment! You've got this! 🚀
