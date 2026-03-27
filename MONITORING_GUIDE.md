# Production Monitoring Guide

## Overview

The TruthLens AI backend now includes comprehensive production monitoring with:
- **Structured JSON logging** for all requests and events
- **Request timing middleware** that tracks all requests with response times
- **ML inference tracking** that measures model analysis time separately
- **Metrics collection** for performance monitoring and debugging
- **Error tracking** with full stack traces and error details

---

## Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "TruthLens AI",
  "timestamp": "2026-03-17T12:34:56.789123"
}
```

---

### Comprehensive Metrics
```bash
curl http://localhost:8000/metrics | python -m json.tool
```

**Response:**
```json
{
  "total_requests": 150,
  "total_errors": 3,
  "error_rate": 2.0,
  "avg_response_time": 5.234,
  "avg_response_time_ms": 5234.12,
  "avg_ml_inference_time": 3.845,
  "avg_ml_inference_time_ms": 3845.67,
  "total_ml_inference_time": 576.75,
  "endpoint_hits": {
    "/api/analyze": 145,
    "/health": 4,
    "/metrics": 1
  },
  "recent_errors": [
    {
      "timestamp": "2026-03-17T12:30:00.000Z",
      "endpoint": "/api/analyze",
      "method": "POST",
      "status_code": 500,
      "error": "Database connection failed",
      "response_time": 0.234
    }
  ],
  "timestamp": "2026-03-17T12:34:56.789123Z"
}
```

**Metrics Explained:**
- `total_requests` - Total number of requests since app start
- `total_errors` - Total number of requests that resulted in status 4xx or 5xx
- `error_rate` - Percentage of requests that errored
- `avg_response_time` - Average response time in seconds
- `avg_response_time_ms` - Average response time in milliseconds
- `avg_ml_inference_time` - Average ML model inference time (how long /api/analyze takes to run models)
- `total_ml_inference_time` - Total accumulated ML inference time
- `endpoint_hits` - Count of requests per endpoint
- `recent_errors` - Last 10 errors with timestamps and details

---

### Simplified Metrics
```bash
curl http://localhost:8000/metrics/simple
```

**Response:**
```json
{
  "total_requests": 150,
  "avg_response_time": 5.234,
  "errors": 3
}
```

This is a lightweight endpoint suitable for monitoring dashboards.

---

## Structured Logging

All logs are output as structured JSON for easy parsing by log aggregation systems.

### Request Log Example
```json
{
  "timestamp": "2026-03-17T12:30:15.123Z",
  "level": "INFO",
  "logger": "backend.services.monitoring",
  "message": "request_completed",
  "endpoint": "/api/analyze",
  "method": "POST",
  "status_code": 200,
  "response_time_ms": 3456.78,
  "ml_time_ms": 3200.45,
  "error": null
}
```

### ML Inference Log Example
```json
{
  "timestamp": "2026-03-17T12:30:15.456Z",
  "level": "INFO",
  "logger": "backend.api.analyze",
  "message": "ML inference completed",
  "text_length": 125,
  "ml_time_ms": 3200.45,
  "verdict": "REAL"
}
```

### Error Log Example
```json
{
  "timestamp": "2026-03-17T12:30:15.789Z",
  "level": "ERROR",
  "logger": "backend.api.analyze",
  "message": "Analysis failed",
  "error": "NoneType object is not subscriptable",
  "text_length": 85,
  "response_time_ms": 2340.12,
  "stack_trace": "Traceback (most recent call last):\n  File \"backend/api/analyze.py\", line 95, in analyze_claim\n    result = scoring_engine.analyze(request.text)\n..."
}
```

---

## Log Aggregation

For production deployment, pipe logs to a log aggregation system:

### ELK Stack (Elasticsearch, Logstash, Kibana)
```bash
# In your logging config, send logs to Logstash
# The structured JSON format works perfectly with ELK
```

### CloudWatch (AWS)
```bash
# CloudWatch can parse JSON logs natively
# Subscribe to the log group and create metrics from logs
```

### Datadog
```bash
# Datadog has native JSON log parsing
# Metrics will appear automatically in your Datadog dashboard
```

### Splunk
```bash
# Splunk can ingest and parse JSON logs
# Create dashboards from the structured fields
```

---

## Key Metrics to Monitor

### Performance
- **avg_response_time** - Should be < 10 seconds for cached requests, 30-60s for first requests
- **avg_ml_inference_time** - Should be 2-5 seconds for cached models, 30-60 seconds on first request

### Reliability
- **error_rate** - Should be < 2% in production
- **total_errors** - Monitor for spikes

### Usage
- **endpoint_hits** - Track which endpoints are used most
- **total_requests** - Monitor traffic patterns

---

## Monitoring Best Practices

### 1. Set Up Alerts
```yaml
# Example alert configuration
alerts:
  - name: "High Error Rate"
    condition: "error_rate > 5%"
    severity: "warning"
  
  - name: "Slow Responses"
    condition: "avg_response_time_ms > 10000"
    severity: "info"
  
  - name: "Service Down"
    condition: "/health returns non-200"
    severity: "critical"
```

### 2. Create Dashboards
Track these metrics:
- Response time over time (p50, p95, p99)
- Error rate over time
- Requests per second
- ML inference time distribution
- Endpoint usage breakdown

### 3. Log Retention
- Keep logs for at least 30 days
- Archive to cheaper storage after 7 days
- Extract metrics daily

### 4. Monitoring Stack
Recommended setup:
```
FastAPI App (metrics)
    ↓
Prometheus (scrape /metrics)
    ↓
Grafana (visualize)
    ↓
AlertManager (send alerts)
```

---

## Example Prometheus Integration

### 1. Install Prometheus Client
```bash
pip install prometheus-client
```

### 2. Update monitoring.py to export Prometheus metrics
```python
from prometheus_client import Counter, Histogram, Gauge

request_count = Counter('truthlens_requests_total', 'Total requests')
response_time = Histogram('truthlens_response_time_seconds', 'Response time')
errors = Counter('truthlens_errors_total', 'Total errors')
```

### 3. Expose /metrics in Prometheus format
```bash
curl http://localhost:8000/metrics
# Returns Prometheus format metrics
```

---

## Troubleshooting

### Metrics Not Updating
1. Check that requests are being made to monitored endpoints
2. Verify middleware is running: `curl -i http://localhost:8000/health`
3. Check logs for errors

### High Error Rate
1. Check `/metrics` for recent errors
2. Look at error stack traces
3. Review response times for bottlenecks
4. Check database connectivity

### Slow Responses
1. Check `avg_ml_inference_time` - if high, models are slow
2. Check database query times in logs
3. Monitor CPU and memory usage on server
4. Check network latency to dependencies

### Memory Usage
1. Monitor ML inference time - first request loads models
2. Models should stay in memory after first request
3. Restart app if memory grows unbounded (memory leak)
4. Check for large result objects in logs

---

## Performance Tuning

Based on metrics data:

### If avg_ml_inference_time is high:
1. Models are slow - expected on first request
2. Cache is working if subsequent requests are faster
3. Consider GPU acceleration for production

### If error_rate is high:
1. Check recent errors in /metrics
2. Review error logs for patterns
3. Increase retry logic or add circuit breaker

### If response_time_ms is high:
1. Check if it's inference time or database time
2. Look for slow database queries
3. Add caching for frequently analyzed text

---

## Production Deployment

### Docker Monitoring
```dockerfile
# Expose metrics port
EXPOSE 8000

# Health check uses /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Docker Compose
```yaml
backend:
  image: truthlens-backend:latest
  ports:
    - "8000:8000"
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
  environment:
    - LOG_LEVEL=INFO
```

### Kubernetes
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

---

## Monitoring Stack Example

Complete example with Docker Compose:

```yaml
version: '3.8'

services:
  backend:
    image: truthlens-backend:latest
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  prometheus_data:
  grafana_data:
```

---

## Next Steps

1. **Deploy monitoring** - Use this setup in production
2. **Configure alerts** - Set up alert thresholds
3. **Create dashboards** - Visualize key metrics
4. **Log aggregation** - Send logs to ELK/Datadog/etc
5. **Performance tuning** - Use metrics to optimize

For questions or issues, check the logs at `/tmp/truthlens_backend.log`.
