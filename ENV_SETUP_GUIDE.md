# Environment Configuration Setup Guide

## 📋 Overview

Your `.env` file has been properly configured and cleaned. It now contains:
- **Required**: OpenAI API Key (for core AI verification)
- **Optional**: Web search APIs
- **System**: Database, backend/frontend URLs, AWS S3

## 🔐 Secure API Key Setup

### 1. OpenAI API Key (REQUIRED)

This is the **critical** key needed for fact-checking verification.

**Steps to get your key:**
1. Go to: https://platform.openai.com/api-keys
2. Sign in to your OpenAI account (or create one)
3. Click "Create new secret key"
4. Copy the key immediately (you won't see it again)

**Add to `.env`:**
```bash
# In .env file, replace placeholder:
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

⚠️ **SECURITY CHECKLIST:**
- ✅ `.env` is in `.gitignore` (never commits)
- ✅ Never share this key in messages/chat
- ✅ Never commit to version control
- ✅ Rotate if accidentally exposed
- ✅ Use different keys for dev/prod

### 2. Optional: Web Search APIs

**Tavily API** (highly recommended for better search results):
1. Sign up: https://tavily.com/
2. Get API key from dashboard
3. Add to `.env`: `TAVILY_API_KEY=your-key-here`

**Google Custom Search** (optional fallback):
1. Create search engine: https://programmablesearchengine.google.com/
2. Get API key from Google Cloud Console
3. Add: `GOOGLE_SEARCH_API_KEY=` and `GOOGLE_SEARCH_ENGINE_ID=`

**Serper** (optional):
1. Sign up: https://serper.dev/
2. Get API key from dashboard
3. Add to `.env`: `SERPER_API_KEY=`

### 3. AWS S3 (Optional - only if using cloud storage)

If you want to store documents in AWS S3:
```
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1
```

## 🗂️ Your Current `.env` Structure

```
OPENAI_API_KEY=your_openai_api_key_here          ← SET THIS FIRST
TAVILY_API_KEY=                                    ← Optional
SERPER_API_KEY=                                    ← Optional
DATABASE_URL=sqlite:///./backend/truthlens.db    ← Auto-configured
PORT=8000                                          ← Auto-configured
NEXT_PUBLIC_API_URL=http://localhost:8000        ← Auto-configured
```

## ✅ Quick Start Checklist

- [ ] Open `.env` file
- [ ] Replace `your_openai_api_key_here` with actual OpenAI key
- [ ] (Optional) Add Tavily API key for better web search
- [ ] Save `.env` file
- [ ] **Never commit `.env` to Git** (already in .gitignore)
- [ ] Start your application

## 🚀 Verify Setup

Test your configuration:

```bash
# Backend - Python
source .venv/bin/activate
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OpenAI key set:', bool(os.getenv('OPENAI_API_KEY')))"

# Frontend - Node.js
npm run dev  # Will use NEXT_PUBLIC_API_URL from .env
```

## 📝 Environment Variables Reference

| Variable | Type | Required | Purpose |
|----------|------|----------|---------|
| `OPENAI_API_KEY` | String | ✅ **YES** | Core AI verification & reasoning |
| `TAVILY_API_KEY` | String | ❌ No | Enhanced web search results |
| `DATABASE_URL` | String | ✅ **YES** | Local SQLite database path |
| `PORT` | Integer | ✅ **YES** | Backend server port (8000) |
| `NEXT_PUBLIC_API_URL` | String | ✅ **YES** | Frontend API connection |
| `CORS_ORIGINS` | String | ✅ **YES** | Allowed frontend origins |
| `AWS_*` | String | ❌ No | Cloud storage (optional) |

## ⚠️ Security Best Practices

### DO:
✅ Store secrets only in `.env` (local only)
✅ Rotate keys if exposed
✅ Use separate keys for dev/prod/staging
✅ Enable key rotation policies
✅ Monitor API usage for suspicious activity
✅ Use limited-scope API keys when possible

### DON'T:
❌ Commit `.env` to version control
❌ Share keys in messages, emails, or chat
❌ Store keys in source code
❌ Use the same key across environments
❌ Hardcode secrets in configuration files
❌ Display keys in logs or error messages

## 🚀 Deployment (Production)

For production deployment on platforms like Railway, Vercel, or Heroku:

1. **Don't upload `.env` file**
2. Set environment variables in platform dashboard:
   - Railway: Project Settings → Variables
   - Vercel: Project Settings → Environment Variables
   - Heroku: Config Vars

Example platform config:
```
OPENAI_API_KEY = sk-proj-xxxxx...
TAVILY_API_KEY = tvly-xxxxx...
DATABASE_URL = postgresql://user:pass@host:5432/db
```

## ❓ Troubleshooting

**"OpenAI API key not found"**
- Check `.env` file exists in project root
- Verify `OPENAI_API_KEY=` is not empty
- Run: `python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"`

**"Module 'dotenv' not found"**
- Backend: `pip install python-dotenv`
- Frontend: Already included in Next.js

**Key no longer works**
- Check usage limits at https://platform.openai.com/account/usage/overview
- Verify key hasn't expired
- Try generating a new key

## 📞 Support

For issues:
1. Check this guide's troubleshooting section
2. Review API provider documentation
3. Check `backend/config/environment.py` for validation logs
4. Monitor API provider dashboards for errors

---

**Last Updated:** April 3, 2026
**Status:** ✅ Properly configured and secured
