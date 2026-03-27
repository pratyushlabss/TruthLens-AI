# ✅ SERVER IS RUNNING - Here's How to Use It

## 🎉 Good News!

Your TruthLens AI backend server **IS WORKING** and **IS RUNNING** right now!

The server is currently running on: **http://localhost:8000**

---

## ✅ Proof - Server is Responding

Test it right now:

```bash
curl http://localhost:8000/health
```

**You will see:**
```json
{"status":"healthy","version":"1.0.0","service":"TruthLens AI","timestamp":"2026-03-17T..."}
```

---

## 🚀 How to Start Server with Output Visible

You have 3 easy options:

### Option 1: Use the Quick Start Script (EASIEST) ⭐
```bash
./start_server_visible.sh
```
This is the easiest way - the script uses the exact right paths and shows all output on screen.

### Option 2: Manual Start (Show Output Directly)
```bash
cd "/Users/pratyush/ai truthlens/backend"
/Users/pratyush/ai\ truthlens/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```
Leave this terminal open to see all logs live.

### Option 3: Use deploy.sh (Starts Backend + Frontend)
```bash
cd "/Users/pratyush/ai truthlens"
./deploy.sh
```
This starts both the backend AND frontend together.

---

## 📊 What You'll See When Server Starts

```
===============================================================
INFO:     Started server process [75640]
INFO:     Waiting for application startup.

{"timestamp": "2026-03-17T04:47:44.816526Z", "level": "INFO", "logger": "main", 
"message": "Backend starting", "status": "startup"}

{"timestamp": "2026-03-17T04:47:44.818341Z", "level": "INFO", "logger": "main", 
"message": "Database initialized", "database": "postgresql"}

INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
===============================================================
```

That's it! Your server is ready.

---

## 🧪 Test the Server

### 1. Check Health ✅
```bash
curl http://localhost:8000/health
```
Should respond instantly with healthy status.

### 2. View Metrics 📊
```bash
curl http://localhost:8000/metrics/simple | python -m json.tool
```
Shows request counts, errors, and performance.

### 3. Try the API 🤖
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Climate change is caused by human activity"}'
```
First request takes 30-60 seconds (loading models). Subsequent requests are fast (2-5s).

### 4. View API Docs 📖
Open in browser:
```
http://localhost:8000/docs
```

---

## 🛑 Stop the Server

If running in foreground:
```bash
Press CTRL+C in the terminal
```

If running in background:
```bash
pkill -f "uvicorn"
```

---

## 📍 What's Running

The server includes:

- **Health Check**: `GET http://localhost:8000/health`
- **Analyze Endpoint**: `POST http://localhost:8000/api/analyze`
- **Metrics**: `GET http://localhost:8000/metrics`
- **Docs**: `http://localhost:8000/docs`
- **Production Monitoring**: Full request/response logging

---

## 🔍 How to See Logs

### If Running in Foreground
Logs appear directly in the terminal where you started it.

### If Running in Background
```bash
tail -f /tmp/truthlens_server.log
```

### Filter Logs
```bash
# Just request completions
grep "request_completed" /tmp/truthlens_server.log

# Just errors
grep "ERROR" /tmp/truthlens_server.log

# Just ML inference
grep "ML inference" /tmp/truthlens_server.log
```

---

## ⚡ Quick Start (TL;DR)

Just run this to see the server with output:

```bash
./start_server_visible.sh
```

That's it! You'll see:
1. Which port it's on
2. When it starts
3. When it's ready to accept requests
4. All logs in real-time

---

## 🎯 Summary

| What | Status | How to Check |
|------|--------|-------------|
| Server Running | ✅ YES | `curl http://localhost:8000/health` |
| Port 8000 | ✅ READY | Get instant health response |
| Backend | ✅ WORKING | Shows JSON response |
| Monitoring | ✅ ACTIVE | `curl http://localhost:8000/metrics/simple` |
| Logs | ✅ VISIBLE | Run with `./start_server_visible.sh` |

---

## 📚 Documentation

For detailed information, see:
- [SERVER_STARTUP_GUIDE.md](SERVER_STARTUP_GUIDE.md) - Complete startup guide
- [MONITORING_README.md](MONITORING_README.md) - Monitoring guide
- [README.md](README.md) - Project overview

---

## 🚀 Next Steps

1. **Right now:** Start the server
   ```bash
   ./start_server_visible.sh
   ```

2. **In another terminal:** Test the server
   ```bash
   curl http://localhost:8000/health
   ```

3. **View the API docs:** Open in browser
   ```
   http://localhost:8000/docs
   ```

4. **Try analyzing a claim:**
   ```bash
   curl -X POST http://localhost:8000/api/analyze \
     -H "Content-Type: application/json" \
     -d '{"text": "Test claim"}'
   ```

---

## ❓ FAQ

**Q: The server won't start**
A: Run `./start_server_visible.sh` - it handles all the paths automatically.

**Q: I don't see any output**
A: Don't use `&` at the end of commands. Run without background mode to see logs.

**Q: Port 8000 is already in use**
A: Kill the old process: `pkill -f "uvicorn"` then start again.

**Q: How do I see the startup output?**
A: Use `./start_server_visible.sh` or start without `&` or `nohup`.

**Q: Is my server really running?**
A: Yes! Test with: `curl http://localhost:8000/health`

---

## ✨ You're All Set!

Your server is operational and ready for use. 

**To see it with output on screen:**
```bash
./start_server_visible.sh
```

**That's it!** 🎉
