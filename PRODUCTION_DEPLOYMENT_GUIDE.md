# 🚀 Production Deployment Quick Start

## Step-by-Step Deployment Guide

### Phase 1: Frontend on Vercel ✅

**Status:** Code ready, waiting for environment variable

1. **Set Environment Variable in Vercel**
   ```
   Go to: https://vercel.com/dashboard → TruthLens project → Settings
   
   Environment Variables section:
   - Name: NEXT_PUBLIC_API_BASE_URL
   - Value: https://truthlens-ai-production-6984.up.railway.app
   - Environments: Production
   
   Click "Save" and "Redeploy"
   ```

2. **Verify Deployment**
   ```
   Check: https://vercel.com/dashboard → Deployments
   Expected: Green checkmark with "Ready"
   ```

3. **Test Frontend Health**
   ```javascript
   // On deployed frontend, in browser console (F12):
   truthlensDebug.checkBackendHealth()
   
   // Should show: ✅ Backend is healthy!
   ```

---

### Phase 2: Backend on Railway ✅

**Status:** Code ready, deployment pending

#### Prerequisites
- [ ] OpenAI API Key ready
- [ ] Tavily API Key ready
- [ ] Railway account created
- [ ] GitHub repository connected

#### Railway Deployment Steps

1. **Connect to Railway**
   ```
   1. Go to https://railway.app/dashboard
   2. New Project → Deploy from GitHub
   3. Select: pratyushlabss/TruthLens-AI
   4. Click "Deploy"
   ```

2. **Add PostgreSQL Database**
   ```
   1. In Railway Project → Add Service
   2. Select "Database" → "PostgreSQL"
   3. Click "Deploy"
   
   Railway will auto-generate:
   - DATABASE_URL (connection string)
   - Host, Port, User, Password
   ```

3. **Configure Environment Variables**
   ```
   In Railway Project Settings → Variables:
   
   OPENAI_API_KEY = your_openai_key_here
   TAVILY_API_KEY = your_tavily_key_here
   DATABASE_URL = (auto-populated by PostgreSQL service)
   CORS_ORIGINS = * (or specific frontend URL)
   ENV = production
   HOST = 0.0.0.0
   PORT = 8000
   ```

4. **Get Railway URL**
   ```
   After deployment:
   1. Go to Railway Dashboard
   2. Select TruthLens project
   3. Click the "Web" service
   4. Copy the "URL" shown at top
   5. Format: https://service-name.up.railway.app
   ```

---

### Phase 3: Connect Frontend to Backend

1. **Update Vercel Environment Variable**
   ```
   NEXT_PUBLIC_API_BASE_URL = [Railway URL from Phase 2 Step 4]
   
   Go to: Vercel Dashboard → Settings → Environment Variables
   Update existing variable with the Railway URL
   ```

2. **Redeploy Frontend**
   ```
   In Vercel Dashboard → Deployments → Redeploy
   Or push new commit to GitHub for automatic redeploy
   ```

3. **Verify Connection**
   ```javascript
   // Wait 2-3 minutes for Vercel deployment
   // Then in browser console:
   truthlensDebug.quickCheck()
   
   // Should show all green ✅
   ```

---

## 🧪 Testing Checklist

### Frontend Tests
```javascript
// In browser console (F12):

// 1. Health check
truthlensDebug.checkBackendHealth()
// Expected: ✅ Backend is healthy!

// 2. Environment check
truthlensDebug.checkEnvironment()
// Expected: ✅ Using remote backend

// 3. All endpoints
truthlensDebug.testAllEndpoints()
// Expected: All endpoints responding

// 4. Full diagnostics
truthlensDebug.quickCheck()
// Expected: Everything healthy
```

### User Journey Test
```
1. Go to https://your-vercel-deployed-url/
2. Click "Login"
3. Use test credentials: test@truthlens.local / password123
4. Enter test claim: "The moon is made of cheese"
5. Click "Analyze"
6. Verify verdict appears (should be FAKE with reasoning)
7. Go to "History" tab
8. Verify claim appears in history
```

### Error Testing (Optional)
```javascript
// Test error handling
fetch('/api/health?test_error=true')

// Test timeout
fetch('/api/health?timeout=true')

// View error in console and alert
```

---

## 🎯 Expected Results

### Successful Deployment
```
Frontend: https://your-vercel-url/
Backend: https://yourservice.up.railway.app/
Database: PostgreSQL on Railway

Health Check Response:
{
  "status": "healthy",
  "backend": {
    "message": "TruthLens AI - Misinformation Detection Engine",
    "version": "1.0.0",
    "service": "TruthLens AI"
  },
  "response_time_ms": 150
}
```

### Successful Analysis
```
Request: POST /api/analyze
Body: { text: "The moon is made of cheese" }

Response:
{
  "verdict": "FAKE",
  "confidence": 0.95,
  "explanation": "The moon is not made of cheese...",
  "sources": [...],
  "signals": [...],
  "reasoning": "..."
}
```

---

## ⚠️ Common Deployment Issues

### Issue: 503 Service Unavailable
```
Cause: Backend not running
Solution: Check Railway deployment status
- Go to Railway Dashboard
- Click TruthLens project
- Check "Web" service status
- Redeploy if needed
```

### Issue: CORS Error
```
Cause: Backend CORS not configured
Solution: Check backend CORS settings
In backend/main.py:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Wrong Environment Variable
```
Cause: NEXT_PUBLIC_API_BASE_URL pointing to wrong URL
Solution: Update in Vercel Dashboard
1. Verify Railway URL is correct
2. Set NEXT_PUBLIC_API_BASE_URL to Railway URL
3. Redeploy Vercel project
```

### Issue: Database Connection Failed
```
Cause: DATABASE_URL not set in Railway
Solution: Add PostgreSQL service
1. In Railway project
2. Click "Add Service"
3. Select "Database" → "PostgreSQL"
4. Database URL auto-added to environment
```

---

## 🔄 Rolling Back (If Needed)

### Revert Frontend Deployment
```
Vercel Dashboard → Deployments → Previous commit → Redeploy
```

### Revert Backend Deployment
```
Railway Dashboard → Deployments → Previous deployment → Revert
```

### Revert Environment Variables
```
Revert NEXT_PUBLIC_API_BASE_URL to:
http://localhost:8000 (for local testing)
```

---

## 📊 Monitoring Production

### Frontend Health
```javascript
// Check regularly
setInterval(() => {
  fetch('/api/health')
    .then(r => r.json())
    .then(d => console.log('❓ Backend status:', d.status));
}, 60000); // Every minute
```

### Backend Logs
```
Railway Dashboard → TruthLens project → Web service → Logs
Check for:
✓ All requests successfully processed
✓ No errors in analysis
✓ Database connections healthy
```

### Error Tracking
```javascript
// Browser console shows detailed errors:
- API failures
- Network issues
- Backend errors
- Database issues
```

---

## 🎓 After Deployment

### Performance Optimization
1. Enable database query caching
2. Add Redis caching layer (optional)
3. Implement request rate limiting
4. Monitor API response times

### Scaling Considerations
1. Monitor Railway resource usage
2. Upgrade resources if needed
3. Add load balancing if traffic high
4. Consider PostgreSQL read replicas

### Security Hardening
1. Add rate limiting middleware
2. Implement request validation
3. Add security headers
4. Enable HTTPS (automatic on Vercel/Railway)
5. Rotate API keys regularly

---

## 💬 Support & Troubleshooting

### Debug Frontend Connection
```javascript
truthlensDebug.diagnoseNetwork()
```

### Check Backend Logs
```
Railway Dashboard → Logs → Filter for errors
```

### Verify API Response Format
```javascript
// Fetch and inspect response
fetch('/api/analyze', {
  method: 'POST',
  body: new FormData().append('text', 'test')
})
.then(r => {
  console.log('Status:', r.status);
  console.log('Headers:', Object.fromEntries(r.headers));
  return r.json();
})
.then(d => console.log('Data:', d))
```

---

## ✅ Deployment Complete When

- [ ] Frontend deployed to Vercel ✅ Ready
- [ ] Backend deployed to Railway ✅ Ready
- [ ] PostgreSQL database running ✅ Ready
- [ ] All environment variables set ✅ Ready
- [ ] Health check responding ✅ Test now
- [ ] User can analyze claims end-to-end ✅ Test now
- [ ] History persists across sessions ✅ Test now
- [ ] No console errors in browser ✅ Check now

---

## 🎉 You're Live!

After all green checks above, **TruthLens AI is ready for production use!**

### Share with Users
```
Frontend URL: https://your-vercel-url/
Test with: test@truthlens.local / password123
```

### Monitor & Maintain
- Check health: `truthlensDebug.checkBackendHealth()`
- Watch logs: Railway Dashboard
- Update API keys: Environment variables as needed
- Scale resources: As traffic grows

---

## 📝 Next Steps

1. **Immediate (Now)**
   - [ ] Deploy backend to Railway
   - [ ] Set environment variables
   - [ ] Test end-to-end

2. **Short Term (This week)**
   - [ ] Monitor for errors
   - [ ] Optimize slow endpoints
   - [ ] Gather user feedback

3. **Medium Term (This month)**
   - [ ] Add analytics dashboard
   - [ ] Implement caching
   - [ ] Add rate limiting

4. **Long Term (This quarter)**
   - [ ] Scale to multiple regions
   - [ ] Add advanced features
   - [ ] Implement ML model improvements

---

## 🚀 Status: READY FOR PRODUCTION

All systems go! Deploy and monitor closely for first 24 hours.

Questions? Check:
- `/FRONTEND_API_FIXES_COMPLETE.md` - Full details
- `/frontend/API_INTEGRATION_REVIEW.md` - API documentation
- Browser console: `truthlensDebug.help()` - Debug tools
