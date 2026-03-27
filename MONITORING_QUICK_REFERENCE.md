# Monitoring Quick Reference

## Quick Start

### Check System Health
```bash
curl http://localhost:8000/health
```

### View Metrics
```bash
# Full metrics with detailed breakdown
curl http://localhost:8000/metrics | python -m json.tool

# Lightweight metrics (for dashboards)
curl http://localhost:8000/metrics/simple
```

---

## Key Metrics at a Glance

| Metric | Endpoint | Description |
|--------|----------|-------------|
| `total_requests` | `/metrics/simple` | Total API requests since startup |
| `avg_response_time` | `/metrics/simple` | Average response time (seconds) |
| `errors` | `/metrics/simple` | Total failed requests |
| `avg_ml_inference_time_ms` | `/metrics` | Average ML model time (milliseconds) |
| `error_rate` | `/metrics` | Percentage of failed requests |
| `endpoint_hits` | `/metrics` | Requests per endpoint |
| `recent_errors` | `/metrics` | Last 10 errors with details |

---

## Expected Performance

### First Request (Models Loading)
- **Response Time**: 30-60 seconds
- **ML Inference Time**: 30-60 seconds
- **Status**: Normal - models are initializing

### Subsequent Requests (Cached Models)
- **Response Time**: 2-5 seconds
- **ML Inference Time**: 1-3 seconds
- **Status**: Optimal - models in memory

### Health Check
- **Response Time**: <10ms
- **Status**: Always instant, no models needed

---

## Common Queries

### Monitor in Real Time
```bash
# Refresh every 5 seconds
watch -n 5 'curl -s http://localhost:8000/metrics | python -m json.tool | head -20'
```

### Check Error Details
```bash
curl -s http://localhost:8000/metrics | python -m json.tool | grep -A 30 "recent_errors"
```

### Get Just Request Count
```bash
curl -s http://localhost:8000/metrics/simple | python -m json.tool
```

### Track ML Performance
```bash
curl -s http://localhost:8000/metrics | python -c "
import sys, json
data = json.load(sys.stdin)
print(f'ML Avg Time: {data[\"avg_ml_inference_time_ms\"]:.0f}ms')
print(f'Total ML Time: {data[\"total_ml_inference_time\"]:.1f}s')
"
```

---

## Log Monitoring

### View Live Logs
```bash
# OpenAI terminal
tail -f /tmp/truthlens_backend.log

# Or via Docker
docker logs -f truthlens-backend
```

### Filter Logs by Type
```bash
# Just request completions
grep "request_completed" /tmp/truthlens_backend.log

# Just ML inferences
grep "ML inference completed" /tmp/truthlens_backend.log

# Just errors
grep "ERROR" /tmp/truthlens_backend.log
```

### Parse JSON Logs
```bash
# Extract response times
cat /tmp/truthlens_backend.log | grep "request_completed" | \
  python -c "
import sys, json
times = []
for line in sys.stdin:
    data = json.loads(line)
    if 'response_time_ms' in data:
        times.append(data['response_time_ms'])
print(f'Avg: {sum(times)/len(times):.0f}ms')
print(f'Max: {max(times):.0f}ms')
"
```

---

## Alert Rules

Create alerts when:

| Condition | Severity | Action |
|-----------|----------|--------|
| `error_rate > 5%` | Warning | Check logs for errors |
| `avg_response_time_ms > 10000` | Warning | Scale up or optimize |
| `health check fails` | Critical | Restart service |
| `recent_errors.length > 5` | Warning | Investigate error patterns |

---

## Integration Examples

### Send to Slack
```bash
# Extract metrics and send to Slack webhook
curl -s http://localhost:8000/metrics/simple | python -c "
import sys, json, urllib.request
data = json.load(sys.stdin)
msg = f'TruthLens Stats: {data[\"total_requests\"]} requests, {data[\"errors\"]} errors, {data[\"avg_response_time\"]:.2f}s avg'
# Send to Slack webhook...
"
```

### Log to CloudWatch
```bash
# Configure Python logging to send to CloudWatch
# See MONITORING_GUIDE.md for full setup
```

### Export to Prometheus
```bash
# TODO: Add Prometheus exporter endpoint
# /metrics returns JSON, can convert to Prometheus format
```

---

## Troubleshooting Checklist

- [ ] Is service running? `curl http://localhost:8000/health`
- [ ] Are requests being made? `curl http://localhost:8000/metrics/simple | grep total_requests`
- [ ] Are errors occurring? `curl http://localhost:8000/metrics | grep error_rate`
- [ ] Is ML slow? `curl http://localhost:8000/metrics | grep avg_ml_inference_time`
- [ ] Check recent errors: `curl http://localhost:8000/metrics | grep -A 5 recent_errors`

---

## Performance Baselines

### Healthy System
```
total_requests: > 100
error_rate: < 2%
avg_response_time_ms: < 5000 (cached)
avg_ml_inference_time_ms: 1500-4000 (cached)
```

### Warning Signs
```
error_rate > 5%
avg_response_time_ms > 10000
recent_errors growing
specific endpoint failing
```

### Critical
```
health check failing
error_rate > 20%
all recent endpoints failing
service unresponsive
```

---

**Need detailed info? See [MONITORING_GUIDE.md](MONITORING_GUIDE.md)**
