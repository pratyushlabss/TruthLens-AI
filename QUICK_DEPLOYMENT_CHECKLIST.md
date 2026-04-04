# ✅ QUICK DEPLOYMENT CHECKLIST

## 🎯 OBJECTIVE
Fix backend crashes causing "Analysis failed" on frontend.

**Status**: 🟢 5 Safe modules  created + Ready to deploy

---

## 📋 PRE-DEPLOYMENT (5 minutes)

### 1. Verify Files Exist
```bash
ls -la /Users/pratyush/ai\ truthlens/backend/api/analyze_v2_safe.py
ls -la /Users/pratyush/ai\ truthlens/backend/services/llm_reasoner_safe.py
ls -la /Users/pratyush/ai\ truthlens/backend/services/retrieval_safe.py
ls -la /Users/pratyush/ai\ truthlens/backend/services/pipeline_safe.py
```

Expected: ✅ All 4 files exist

### 2. Backup Current Files
```bash
cd /Users/pratyush/ai\ truthlens/backend

# Backup
cp api/analyze_v2.py api/analyze_v2.py.backup.$(date +%s)
cp services/llm_reasoner.py services/llm_reasoner.py.backup.$(date +%s)
cp services/retrieval_new.py services/retrieval_new.py.backup.$(date +%s)
cp services/pipeline_new.py services/pipeline_new.py.backup.$(date +%s)

# Verify backups
ls -la api/analyze_v2.py.backup.*
ls -la services/llm_reasoner.py.backup.*
ls -la services/retrieval_new.py.backup.*
ls -la services/pipeline_new.py.backup.*
```

Expected: ✅ 4 backup files created with timestamps

---

## 🚀 DEPLOYMENT (2 minutes)

### 3. Deploy Safe Versions

**Option A: Replace original files (RECOMMENDED)**
```bash
cd /Users/pratyush/ai\ truthlens/backend

# Deploy safe versions
cp api/analyze_v2_safe.py api/analyze_v2.py
cp services/llm_reasoner_safe.py services/llm_reasoner.py
cp services/retrieval_safe.py services/retrieval_new.py
cp services/pipeline_safe.py services/pipeline_new.py

echo "✅ Safe versions deployed"
```

**Option B: Keep both versions (if you want to keep original for reference)**
```bash
# No action needed - originals are still there
# Just note: you may need to update imports in main.py if not using originals

# Verify safe versions are present
ls -la api/analyze_v2_safe.py
ls -la services/llm_reasoner_safe.py
ls -la services/retrieval_safe.py
ls -la services/pipeline_safe.py
```

### 4. Restart Backend

```bash
# Option A: If using systemctl
systemctl restart ai-truthlens-backend

# Option B: If using supervisor
supervisorctl restart ai-truthlens-backend

# Option C: If running manually
# Press Ctrl+C in terminal, then restart:
cd /Users/pratyush/ai\ truthlens
python -m backend.main  # or your startup command

# Option D: Docker
docker restart ai-truthlens-backend
```

Wait 10-15 seconds for server to restart.

### 5. Verify Server is Running

```bash
# Check if backend is responding
curl -X GET http://localhost:8000/health

# Expected response:
# {"status":"ok"} or similar healthy response
```

✅ Server responding = Deployment successful

---

## 🧪 TESTING (10 minutes)

### 6. Run Basic Tests

**Test 1: Normal claim**
```bash
curl -X POST http://localhost:8000/analyze/v2 \
  -F "claim=Is the Earth round?"

# Expected: Valid JSON with verdict and evidence
# ✅ If you get JSON response (not error), test passes
```

**Test 2: Empty claim**
```bash
curl -X POST http://localhost:8000/analyze/v2 \
  -F "claim="

# Expected: Valid JSON with error message
# ✅ NOT a 500 error, but valid error response
```

**Test 3: Very long claim**
```bash
curl -X POST http://localhost:8000/analyze/v2 \
  -F "claim=$(python3 -c "print('a'*5000)")"

# Expected: Valid JSON (truncated gracefully)
# ✅ NOT a crash, but handled safely
```

### 7. Check Logs

```bash
# Monitor logs in real-time
tail -f /Users/pratyush/ai\ truthlens/logs/app.log | grep "\[PIPELINE\]"

# Expected output pattern:
# [PIPELINE] 🚀 STARTING ANALYSIS
# [PIPELINE] STEP 1: Validate input ✅
# [PIPELINE] STEP 2: Analyze claim ✅
# [PIPELINE] STEP 3: Generate queries ✅
# [PIPELINE] STEP 4: Retrieve evidence ✅
# [PIPELINE] STEP 5: Rank evidence ✅
# [PIPELINE] STEP 6: Generate verdict ✅
# [PIPELINE] STEP 7: Build response ✅
# [PIPELINE] ✅ ANALYSIS COMPLETE

# ✅ If you see multiple STEPs, system is working
```

### 8. Frontend Test

**In your frontend application:**
```javascript
// Make a claim
fetch('http://localhost:8000/analyze/v2', {
  method: 'POST',
  body: new FormData({ claim: 'Your test claim' })
})
.then(r => r.json())
.then(data => {
  console.log('Response:', data);
  // ✅ If data is JSON object (not error), system works
  console.log('Label:', data.label);
  console.log('Evidence:', data.evidence.length);
})
```

Expected: ✅ Frontend receives valid JSON, not "Analysis failed"

---

## 🔍 TROUBLESHOOTING

### Issue: Server won't restart

**Solution:**
```bash
# Check if process is still running
lsof -i :8000

# Kill it if stuck
kill -9 <PID>

# Wait 5 seconds, then restart
sleep 5
systemctl restart ai-truthlens-backend  # or your restart command
```

### Issue: Still getting "Analysis failed"

**Solution:**
```bash
# Check logs for errors
tail -100 /Users/pratyush/ai\ truthlens/logs/app.log

# Look for lines starting with [PIPELINE] ❌
# Find the exact step that fails

# Example:
# [PIPELINE-S4] ❌ Retrieval error: Connection timeout
# → Problem: Wikipedia API timeout
# Solution: Not a crash - should have fallback, check logs for details

# Report the exact [PIPELINE] error line for debugging
```

### Issue: Got timeout errors

**Solution:**
```bash
# This is EXPECTED during high load
# System should still recover and return response (not crash)

# If you see in logs:
# [PIPELINE] ⚠️ Analysis exceeded 60 second timeout
# → System detected long analysis, returned error response
# → This is SAFE (not a crash)

# Increase timeout in analyze_v2.py if needed:
# timeout_seconds=60  ← Change to 120
```

### Issue: LLM api key errors

**Solution:**
```bash
# Check logs for:
# [LLM-OpenAI] ⚠️ HTTP error: 401
# → Invalid OpenAI key

# Fix:
# 1. Update .env with correct OPENAI_API_KEY
# 2. Restart backend
# 3. System will fallback to HuggingFace, then heuristics
```

---

## ✅ SUCCESS CRITERIA

After deployment, verify:

| Check | Method | Expected Result |
|-------|--------|-----------------|
| 🔴 Normal claims work | `curl -F "claim=test"` | Get JSON response with evidence |
| 🔴 Empty claim handled | `curl -F "claim="` | Get error JSON (not 500) |
| 🔴 API errors don't crash | Kill APIs, make request | Get fallback response |
| 🔴 No timeout crashes | Make slow request | Get timeout JSON (not 500) |
| 🔴 Logs show steps | `tail logs/app.log` | See [PIPELINE] STEP 1-7 |
| 🔴 Frontend works | Browser request | See response (not error) |

---

## 🔄 ROLLBACK (If Needed)

```bash
cd /Users/pratyush/ai\ truthlens/backend

# Restore from backup
cp api/analyze_v2.py.backup.* api/analyze_v2.py
cp services/llm_reasoner.py.backup.* services/llm_reasoner.py
cp services/retrieval_new.py.backup.* services/retrieval_new.py
cp services/pipeline_new.py.backup.* services/pipeline_new.py

# Restart
systemctl restart ai-truthlens-backend

echo "✅ Rolled back to previous version"
```

---

## 📊 EXPECTED IMPROVEMENTS

| Before | After |
|--------|-------|
| ❌ Frontend shows "Analysis failed" | ✅ Frontend shows actual verdict |
| ❌ Backend crashes frequently | ✅ Backend NEVER crashes |
| ❌ No error details in response | ✅ Clear error messages |
| ❌ Sparse logging | ✅ 7+ debug checkpoints per request |
| ❌ Timeout hangs forever | ✅ 60s timeout with error response |
| ❌ Wikipedia/Tavily failures crash | ✅ Graceful fallbacks |
| ❌ Entity extraction crashes | ✅ Always returns valid string |

---

## 📞 SUPPORT

If issues persist after deployment:

1. **Check logs**
   ```bash
   tail -200 /Users/pratyush/ai\ truthlens/logs/app.log
   ```

2. **Find the exact error line** (look for ❌)
   ```
   [PIPELINE-S4] ❌ Retrieval error: Connection timeout
   ↑ This tells you Wikipedia API call failed
   ```

3. **Verify all 4 files deployed correctly**
   ```bash
   grep -l "SAFE\|NEVER CRASHES" \
     api/analyze_v2.py \
     services/llm_reasoner.py \
     services/retrieval_new.py \
     services/pipeline_new.py
   ```

4. **System should NEVER crash**
   - If you see 500 errors → not deployed correctly
   - If you see JSON responses with errors → deployed correctly ✅

---

## ⏱️ TIMELINE

| Phase | Duration | Action |
|-------|----------|--------|
| Pre-deployment | 5 min | Backup files, verify safe versions |
| Deployment | 2 min | Copy files, restart server |
| Testing | 10 min | Run 8 verification tests |
| Monitoring | Ongoing | Watch logs, ensure no crashes |

**Total: ~20 minutes**

---

## 🎉 COMPLETION

✅ **When you see this in logs:**
```
[PIPELINE] 🚀 STARTING ANALYSIS
[PIPELINE] STEP 1: Validate input ✅
[PIPELINE] STEP 2: Analyze claim ✅
[PIPELINE] STEP 3: Generate queries ✅
[PIPELINE] STEP 4: Retrieve evidence ✅
[PIPELINE] STEP 5: Rank evidence ✅
[PIPELINE] STEP 6: Generate verdict ✅
[PIPELINE] STEP 7: Build response ✅
[PIPELINE] ✅ ANALYSIS COMPLETE
```

**Then frontend successfully receives:**
```json
{
  "success": true,
  "claim": "your claim",
  "label": "SUPPORTS or REFUTES or UNCERTAIN",
  "confidence_percentage": 75.5,
  "evidence": [...],
  "metadata": {...}
}
```

🎯 **Goal achieved: No more "Analysis failed"!**
