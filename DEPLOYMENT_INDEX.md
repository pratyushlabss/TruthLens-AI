# 🚀 Deployment Files - Quick Reference Index

**All files ready for Vercel + Railway deployment!**

---

## 📋 YOUR DEPLOYMENT ROADMAP

### 🎯 START HERE
**File:** `DEPLOYMENT_CHECKLIST.md`
- Step-by-step guide (4 steps, 15 minutes)
- Checkboxes to track progress
- Copy-paste commands ready
- Best for: Beginners who want to deploy NOW

### 📖 DETAILED GUIDE
**File:** `DEPLOY_VERCEL_RAILWAY_GUIDE.md`
- Full explanations of each step
- Screenshots & URLs
- Troubleshooting section
- Best for: Understanding what's happening

### 📝 FILL-IN SHEET
**File:** `DEPLOYMENT_INFO_SHEET.md`
- Track all your URLs and API keys
- Print or screenshot to save
- Use for troubleshooting later
- Best for: Keeping organized

### 🏗️ CONFIGURATION FILES
Auto-included in your repo:
- `vercel.json` → Vercel settings
- `railway.json` → Railway settings
- `frontend/.env.vercel.template` → Frontend env vars template
- `backend/.env.railway.template` → Backend env vars template

---

## ⚡ 15-MINUTE QUICK START

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy frontend
cd frontend
vercel --prod
# SAVE THIS URL: https://yourapp.vercel.app

# 3. Go to Railway
# Visit: https://railway.app
# Sign up → Import GitHub → Select truthlens-ai repo
# Add PostgreSQL + Redis services
# Add environment variables

# 4. Connect frontend to backend
# In Vercel: set NEXT_PUBLIC_API_BASE_URL to Railway URL
# Redeploy

# 5. Test
curl https://your-railway-url.up.railway.app/health
# Open https://your-vercel-url.vercel.app/dashboard
```

Done! 🎉

---

## 📁 FILES YOU NEED

| File | Purpose | Must Read? |
|------|---------|-----------|
| ✅ `DEPLOYMENT_CHECKLIST.md` | Step-by-step guide | **YES** |
| ✅ `DEPLOY_VERCEL_RAILWAY_GUIDE.md` | Detailed instructions | If you need details |
| ✅ `DEPLOYMENT_INFO_SHEET.md` | Track your info | Recommended |
| ✅ `vercel.json` | Auto-config | Auto-used |
| ✅ `railway.json` | Auto-config | Auto-used |
| ✅ `frontend/.env.vercel.template` | Reference | For copy-paste |
| ✅ `backend/.env.railway.template` | Reference | For copy-paste |

---

## 🎯 DEPLOYMENT STEPS (TLDR)

1. **Vercel Frontend** (3 min)
   - `npm i -g vercel && vercel --prod` from frontend folder
   - Save URL

2. **Railway Backend** (10 min)
   - Sign up, import GitHub repo
   - Add PostgreSQL + Redis
   - Set environment variables

3. **Connect** (2 min)
   - Set `NEXT_PUBLIC_API_BASE_URL` in Vercel
   - Redeploy

4. **Test** (0 min)
   - `curl` backend health check
   - Open frontend in browser
   - Analyze a claim

---

## 🔑 YOU'LL NEED

Before starting, have these ready:
- [ ] OpenAI API Key (sk-...)
- [ ] Tavily API Key (tvly-...)
- [ ] GitHub account with your repo
- [ ] Command: `openssl rand -base64 32` (for NEXTAUTH_SECRET)

---

## 📊 COSTS

| Service | Free | Paid |
|---------|------|------|
| Vercel | ✅ 200k reqs/day | $20/mo |
| Railway | ✅ $5/mo credit | $20-40/mo |
| Total | **FREE** | **$40-60/mo** |

**Start free, pay only if you grow!**

---

## ✅ NEXT STEPS

### If You're Ready to Deploy
1. Open `DEPLOYMENT_CHECKLIST.md`
2. Follow the 4 steps
3. You're live in 15 minutes!

### If You Need Help
1. Read the full guide: `DEPLOY_VERCEL_RAILWAY_GUIDE.md`
2. Fill in: `DEPLOYMENT_INFO_SHEET.md`
3. Follow step-by-step in `DEPLOYMENT_CHECKLIST.md`

### If Something Goes Wrong
1. Check "Troubleshooting" in `DEPLOY_VERCEL_RAILWAY_GUIDE.md`
2. View logs in Vercel/Railway dashboard
3. Re-verify environment variables

---

## 🚀 QUICK LINKS

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Railway Dashboard:** https://railway.app/dashboard
- **Vercel Docs:** https://vercel.com/docs
- **Railway Docs:** https://docs.railway.app
- **OpenAI Docs:** https://platform.openai.com/docs
- **Tavily Docs:** https://docs.tavily.com

---

## 📞 SUPPORT

| Issue | Help |
|-------|------|
| Vercel won't deploy | Vercel Dashboard → Deployments → Logs |
| Backend won't start | Railway Dashboard → Logs |
| API error | Check OpenAI/Tavily account status |
| Database issue | Check PostgreSQL service in Railway |
| CORS error | Update CORS_ALLOWED_ORIGINS in Railway |

---

## 🎓 LEARNING PATH

1. **Just want to deploy?** → `DEPLOYMENT_CHECKLIST.md`
2. **Want to understand?** → `DEPLOY_VERCEL_RAILWAY_GUIDE.md` + `DEPLOYMENT_INFO_SHEET.md`
3. **Want architecture details?** → `DEPLOYMENT_COMPLETE_GUIDE.md`

---

## 💾 AFTER DEPLOYMENT

Auto-update your app:
```bash
git add .
git commit -m "Your message"
git push origin main
# Vercel + Railway auto-redeploy! ✅
```

---

**Ready to go live? Start with `DEPLOYMENT_CHECKLIST.md`** 🚀

Created: April 4, 2026  
Version: 3.2  
Status: ✅ Production Ready
