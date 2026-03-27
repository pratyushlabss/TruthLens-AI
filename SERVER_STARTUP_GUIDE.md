# 🚀 Server Startup Guide

## Current Status: ✅ SERVER IS RUNNING!

Your TruthLens AI backend is currently running on **http://localhost:8000**

---

## Quick Commands

### Start Server (Show Output)
```bash
cd "/Users/pratyush/ai truthlens/backend"
/Users/pratyush/ai\ truthlens/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```
This will start the server and show all logs directly on your screen.

### Start Server (Background)
```bash
nohup /Users/pratyush/ai\ truthlens/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/truthlens_server.log 2>&1 &
```
This starts the server in the background. View logs with:
```bash
tail -f /tmp/truthlens_server.log
```

### Stop Server
```bash
pkill -f "uvicorn"
```

### Check if Server is Running
```bash
curl http://localhost:8000/health
```

---

## Server Response

When you start the server, you should see output like this:

```
[nltk_data] Downloading package wordnet to /Users/pratyush/nltk_data...
[nltk_data]   Package wordnet is already up-to-date!

INFO:     Started server process [75640]
INFO:     Waiting for application startup.

{"timestamp": "2026-03-17T04:47:44.816526Z", "level": "INFO", "logger": "main", "message": "Backend starting", "status": "startup"}

{"timestamp": "2026-03-17T04:47:44.818341Z", "level": "INFO", "logger": "main", "message": "Database initialized", "database": "postgresql"}

INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## Available Endpoints

Once the server is running, you can test these endpoints:

### 1. Health Check
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "TruthLens AI",
  "timestamp": "2026-03-17T04:48:11.207753"
}
```

### 2. Simple Metrics
```bash
curl http://localhost:8000/metrics/simple
```

**Response:**
```json
{
  "total_requests": 0,
  "avg_response_time": 0,
  "errors": 0
}
```

### 3. Detailed Metrics
```bash
curl http://localhost:8000/metrics | python -m json.tool
```

### 4. API Documentation
Open in browser:
```
http://localhost:8000/docs
```

### 5. Analyze (with sample data)
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Climate change is caused by human activity"}'
```

---

## Complete Startup Script

Save this as `start_server.sh`:

```bash
#!/bin/bash

# Kill any existing servers
pkill -f "uvicorn" 2>/dev/null
sleep 2

# Start the server with visible output
cd "/Users/pratyush/ai truthlens/backend"

echo "============================================================"
echo "🚀 Starting TruthLens AI Backend Server..."
echo "============================================================"
echo ""

/Users/pratyush/ai\ truthlens/.venv/bin/python -m uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000

# The server will run in the foreground and you'll see all logs
```

Make it executable:
```bash
chmod +x start_server.sh
```

Run it:
```bash
./start_server.sh
```

---

## Using the Easy Deploy Script

You already have `deploy.sh` in the root directory which starts both backend and frontend:

```bash
cd "/Users/pratyush/ai truthlens"
./deploy.sh
```

This will:
1. Activate the virtual environment
2. Start the backend on port 8000
3. Start the frontend on port 3000
4. Show health check status

---

## Troubleshooting

### Port Already in Use
If you get "Address already in use":
```bash
pkill -f "uvicorn"
sleep 2
# Then try starting again
```

### Can't Connect to Server
1. Check if it's running: `curl http://localhost:8000/health`
2. Check port: `lsof -i :8000`
3. Check logs: `tail -f /tmp/truthlens_server.log`

### Server Crashes
1. Look at the error in the terminal output
2. Check logs: `cat /tmp/truthlens_server.log`
3. Common issues:
   - Port blocked: Use different port with `--port 8001`
   - Memory: Server needs ~2GB RAM for models
   - Dependencies: Run `pip install -r requirements.txt`

### Nothing Shows on Screen
1. The server is likely running in the background
2. Try: `curl http://localhost:8000/health`
3. If that works, the server IS running
4. To see logs: `tail -f /tmp/truthlens_server.log`
5. To see it start: Kill background process and start with foreground output shown above

---

## How to See Output on Screen (Real-Time)

### Method 1: Direct Start (Recommended for Testing)
```bash
cd "/Users/pratyush/ai truthlens/backend"
/Users/pratyush/ai\ truthlens/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```
Leave this terminal open to see all logs in real-time.

### Method 2: Background + Watch Logs
```bash
# Terminal 1: Start server
nohup /Users/pratyush/ai\ truthlens/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/truthlens_server.log 2>&1 &

# Terminal 2: Watch logs
tail -f /tmp/truthlens_server.log
```

### Method 3: Using `deploy.sh` (Starts Both Backend + Frontend)
```bash
cd "/Users/pratyush/ai truthlens"
./deploy.sh
```

---

## API Test Examples

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

### Test 2: Get Metrics
```bash
curl http://localhost:8000/metrics/simple | python -m json.tool
```

### Test 3: Analyze Text (First request takes 30-60s to load models)
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Water boils at 100 degrees Celsius"}'
```

### Test 4: Watch Real-Time Requests
```bash
# Terminal 1: Monitor metrics
watch -n 5 'curl -s http://localhost:8000/metrics/simple | python -m json.tool'

# Terminal 2: Start doing requests
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Test claim"}'
```

---

## Key Points

✅ **Server IS running** - You can verify with `curl http://localhost:8000/health`

✅ **To see output on screen** - Don't use `&` at the end, just run the uvicorn command directly

✅ **Startup takes ~1 second** - Wait for "Application startup complete" message

✅ **First API request takes 30-60 seconds** - Models are loading for the first time

✅ **Subsequent requests are fast** - 2-5 seconds after models are cached

---

## Summary

Your server is working! Now you need to decide how to run it:

1. **See output on screen (best for development):**
   ```bash
   cd /Users/pratyush/ai\ truthlens/backend && /Users/pratyush/ai\ truthlens/.venv/bin/python -m uvicorn main:app --port 8000
   ```

2. **Run in background:**
   ```bash
   nohup /Users/pratyush/ai\ truthlens/.venv/bin/python -m uvicorn main:app --port 8000 > /tmp/truthlens_server.log 2>&1 &
   tail -f /tmp/truthlens_server.log  # in another terminal
   ```

3. **Use deploy script (with frontend):**
   ```bash
   cd /Users/pratyush/ai\ truthlens && ./deploy.sh
   ```

Pick whichever works best for you! 🎉
