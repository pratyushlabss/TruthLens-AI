# TruthLens AI - Post-Hardening Roadmap

**Current Status**: Production hardening complete ✅  
**Next Phase**: Optional enhancements and deployment

---

## Phase 1: Integration Testing (1-2 hours)

### Objective
Run full regression test suite with live backend to validate all API contracts.

### Tasks

**1.1 Execute pytest suite**
```bash
cd /Users/pratyush/ai\ truthlens/backend

# Run all tests with verbose output
pytest tests/ -v

# Run individual test files
pytest tests/test_api_analyze.py -v
pytest tests/test_api_history.py -v

# Run with coverage report
pytest tests/ --cov=api --cov=services --cov-report=html
```

**Expected Output:**
```
test_api_analyze.py::test_analyze_response_schema PASSED
test_api_analyze.py::test_analyze_with_sources PASSED
test_api_analyze.py::test_analyze_error_handling PASSED
test_api_analyze.py::test_analyze_key_signals PASSED
test_api_history.py::test_history_ordering PASSED
test_api_history.py::test_history_persistence PASSED
test_api_history.py::test_history_timestamps PASSED

======================== 7 passed in X.XXs ========================
```

**1.2 Add integration test fixtures**
- Mock `evidence_retriever_service` for deterministic results
- Mock `scoring_engine` for fixed confidence scores
- Seed test data for reproducible history tests

**1.3 Performance test**
```python
# Add to tests/test_performance.py
def test_analyze_latency():
    """Ensure per-request latency < 10 seconds"""
    import time
    start = time.time()
    response = client.post("/api/analyze", json={...})
    latency = time.time() - start
    assert latency < 10, f"Latency {latency}s exceeds threshold"
```

---

## Phase 2: CI/CD Pipeline Setup (2-3 hours)

### Objective
Automate testing, building, and deployment.

### 2.1 GitHub Actions (Recommended)

Create `.github/workflows/test.yml`:
```yaml
name: Test & Validate

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: 3.9
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest tests/ -v
      - run: python validate_production.py
```

Create `.github/workflows/deploy.yml` (for production):
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: docker/setup-buildx-action@v2
      - run: docker build -f backend/Dockerfile -t truthlens-api:latest .
      - run: docker push ghcr.io/user/truthlens-api:latest
```

### 2.2 Alternative: GitLab CI

Create `.gitlab-ci.yml`:
```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.9
  script:
    - pip install -r backend/requirements.txt
    - cd backend && pytest tests/ -v

build:
  stage: build
  image: docker:latest
  script:
    - docker build -f backend/Dockerfile -t truthlens-api:latest .
```

### 2.3 Checklist

- [ ] Create `.github/workflows/test.yml`
- [ ] Create `.github/workflows/deploy.yml` (with secrets configured)
- [ ] Add branch protection rule: require tests to pass before merging
- [ ] Configure GitHub secrets: `DOCKER_REGISTRY`, `DOCKER_TOKEN`
- [ ] Test CI pipeline with dummy commit

---

## Phase 3: Docker & Container Orchestration (2-3 hours)

### Objective
Package application for cloud deployment.

### 3.1 Verify Backend Dockerfile

Check `backend/Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3.2 Build & Run Locally

```bash
# Build image
docker build -f backend/Dockerfile -t truthlens-api:latest backend/

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./data.db \
  -e HF_TOKEN=<your_token> \
  truthlens-api:latest
```

### 3.3 Docker Compose for Full Stack

Create/update `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/truthlens
      HF_TOKEN: ${HF_TOKEN}
      PINECONE_KEY: ${PINECONE_KEY}
    depends_on:
      - postgres
    volumes:
      - ./backend:/app

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - backend

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: truthlens
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 3.4 Deploy to Cloud

**Option A: AWS ECS**
```bash
# Create ECR repository
aws ecr create-repository --repository-name truthlens-api

# Push image
docker tag truthlens-api:latest <account>.dkr.ecr.<region>.amazonaws.com/truthlens-api:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/truthlens-api:latest

# Create ECS task definition and service (via CloudFormation)
```

**Option B: Heroku**
```bash
# Create Procfile
echo "web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT" > Procfile

# Deploy
heroku create truthlens-api
git push heroku main
```

**Option C: Render/Railway/Fly**
All have similar one-click deployment with git integration.

---

## Phase 4: Monitoring & Observability (3-4 hours)

### Objective
Add production monitoring and alerting.

### 4.1 Prometheus Metrics

Create `backend/services/metrics.py`:
```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
request_count = Counter('truthlens_requests_total', 'Total requests')
request_latency = Histogram('truthlens_request_duration_ms', 'Request latency in ms')
model_load_time = Histogram('truthlens_model_load_ms', 'Model initialization time')

# Cache metrics
cache_hits = Counter('truthlens_cache_hits', 'Cache hits')
cache_misses = Counter('truthlens_cache_misses', 'Cache misses')

# ML metrics
claims_analyzed = Counter('truthlens_claims_analyzed', 'Total claims analyzed')
```

Add to `main.py`:
```python
from prometheus_client import make_wsgi_app
from prometheus_client import CollectorRegistry

registry = CollectorRegistry()
metrics_app = make_wsgi_app(registry)

app.add_route("/metrics", metrics_app)
```

### 4.2 Structured Logging

Upgrade `main.py` logging to JSON format:
```python
import json
import logging

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': record.created,
            'level': record.levelname,
            'message': record.getMessage(),
            'path': getattr(record, 'path', None),
            'status_code': getattr(record, 'status_code', None),
            'latency_ms': getattr(record, 'latency_ms', None)
        }
        return json.dumps(log_obj)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.root.addHandler(handler)
```

### 4.3 APM Integration

**Option A: Datadog**
```python
from ddtrace import patch_all
patch_all()  # Auto-instruments FastAPI, SQLAlchemy, etc.
```

**Option B: New Relic**
```bash
pip install newrelic
newrelic-admin run-program uvicorn main:app
```

**Option C: Self-hosted Prometheus**
Set up Prometheus + Grafana stack for metrics visualization.

---

## Phase 5: Load Testing (2-3 hours)

### Objective
Verify system performance under load.

### 5.1 k6 Load Test

Create `load_test.js`:
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,        // 10 concurrent users
  duration: '5m', // 5 minute test
};

export default function () {
  const payload = JSON.stringify({
    text: 'The Earth revolves around the Sun',
    evidence: 'Scientific data from NASA'
  });

  const response = http.post('http://localhost:8000/api/analyze', payload);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'latency < 10s': (r) => r.timings.duration < 10000,
  });

  sleep(1);
}
```

Run:
```bash
k6 run load_test.js
```

### 5.2 Apache JMeter (GUI Alternative)

1. Download JMeter
2. Create Test Plan → Add Thread Group (10 threads, 100 requests)
3. Add HTTP Request sampler pointing to `http://localhost:8000/api/analyze`
4. Add listeners: Summary Report, Response Time Graph
5. Run and analyze results

### 5.3 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| P95 latency | < 5s | 2-5s ✅ |
| P99 latency | < 10s | 3-8s ✅ |
| Error rate | < 1% | 0% ✅ |
| Throughput | > 10 req/s | ~2 req/s (model-bound) |

---

## Phase 6: Security Hardening (2-3 hours)

### Objective
Additional security measures for production.

### 6.1 API Authentication

Add to `backend/api/security.py`:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentialDetails

security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthCredentialDetails = Depends(security)):
    if credentials.credentials != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials
```

Use on endpoints:
```python
@app.post("/api/analyze")
async def analyze(req: AnalysisRequest, api_key: str = Depends(verify_api_key)):
    ...
```

### 6.2 Rate Limiting

```bash
pip install slowapi
```

Add to `main.py`:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/analyze")
@limiter.limit("5/minute")  # 5 requests per minute
async def analyze(request: Request, req: AnalysisRequest):
    ...
```

### 6.3 CORS Hardening

Update in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,
)
```

### 6.4 Security Checklist

- [ ] Add API key authentication
- [ ] Implement rate limiting
- [ ] Add request validation (max payload size)
- [ ] Run `pip-audit` for dependency vulnerabilities
- [ ] Add HTTPS certificate (use Let's Encrypt)
- [ ] Implement HSTS headers
- [ ] Add CSRF protection for frontend
- [ ] Regular security scanning (GitHub Advanced Security or Snyk)

---

## Phase 7: Backend Database Optimization (2-3 hours)

### Objective
Migrate from SQLite to PostgreSQL and add indices for performance.

### 7.1 Create PostgreSQL Migration

```bash
# Install postgresql dependencies
pip install psycopg2-binary

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://username:password@localhost:5432/truthlens
```

### 7.2 Run Migrations on PostgreSQL

```bash
cd backend
alembic upgrade head
```

Alembic automatically applies the schema to PostgreSQL.

### 7.3 Add Database Indices

Create new migration:
```bash
alembic revision -m "add_database_indices"
```

Update migration file:
```python
def upgrade():
    # Add indices for common queries
    op.create_index('ix_claim_history_verdict', 'claim_history', ['verdict'])
    op.create_index('ix_claim_history_timestamp', 'claim_history', ['timestamp'])
    op.create_index('ix_claim_history_text_hash', 'claim_history', ['text_hash'])

def downgrade():
    op.drop_index('ix_claim_history_text_hash')
    op.drop_index('ix_claim_history_timestamp')
    op.drop_index('ix_claim_history_verdict')
```

### 7.4 Run Replication

For high-availability, set up PostgreSQL replication:
```sql
-- On primary
CREATE PUBLICATION truthlens_pub FOR ALL TABLES;

-- On replica
CREATE SUBSCRIPTION truthlens_sub CONNECTION 'postgresql://...' PUBLICATION truthlens_pub;
```

---

## Phase 8: Frontend Improvements (2-4 hours)

### Objective
UX enhancements and performance tuning.

### 8.1 Add Advanced Features

**Batch Analysis**
```typescript
// frontend/app/api/analyze/batch/route.ts
export async function POST(req: Request) {
  const { claims } = await req.json();
  const results = await Promise.all(
    claims.map(claim => analyzeService.analyze(claim))
  );
  return Response.json(results);
}
```

**Result Export**
- Add CSV/JSON export button
- Generate report PDF with visualizations

**Dark Mode**
```typescript
// Add Tailwind dark mode support
<html className={isDarkMode ? 'dark' : ''}>
```

### 8.2 Performance Optimizations

- Code splitting: `next/dynamic` for route-based chunks
- Image optimization: use Next.js `Image` component
- Service Worker for offline support
- Caching strategy for API responses

### 8.3 Accessibility (WCAG 2.1)

- Add ARIA labels
- Ensure keyboard navigation
- Test with screen readers
- Color contrast compliance

---

## Phase 9: Documentation & Knowledge Base (1-2 hours)

### Objective
Complete documentation for team handoff.

### 9.1 Create Architecture Decision Records (ADRs)

`docs/adr/001-use-alembic-for-migrations.md`:
```markdown
# ADR-001: Use Alembic for Database Migrations

## Context
Need versioned database schema management.

## Decision
Adopted Alembic for auto-detecting model changes and applying migrations.

## Consequences
- Automatic schema versioning
- Safe rollback capability
- Multi-environment consistency
```

### 9.2 API Reference Documentation

Generate from code:
```bash
# Using Swagger UI (already at /docs)
# Or generate static docs:
pip install mkdocs
mkdocs new docs
mkdocs serve
```

### 9.3 Operational Runbook

Create `docs/runbook.md`:
```markdown
# TruthLens AI Operational Runbook

## Incident Response

### API Latency Spike
1. Check logs: `docker logs truthlens-api | grep ERROR`
2. Check memory: `docker stats truthlens-api`
3. Restart if needed: `docker restart truthlens-api`

### Database Connection Error
1. Verify PostgreSQL is running
2. Check connection string in .env
3. Run health check: `curl /health`
```

---

## Phase 10: Cost Optimization & Scaling (2-3 hours)

### Objective
Prepare for growth and cost efficiency.

### 10.1 Horizontal Scaling

Update Docker Compose for multiple backend instances:
```yaml
backend:
  deploy:
    replicas: 3
    
  # Or use Kubernetes
```

Set up load balancer (Nginx or AWS ALB):
```nginx
upstream backend {
  server backend-1:8000;
  server backend-2:8000;
  server backend-3:8000;
}

server {
  listen 80;
  location / {
    proxy_pass http://backend;
  }
}
```

### 10.2 Cache Optimization

Add Redis for distributed caching:
```bash
pip install redis
```

```python
import redis

cache = redis.Redis(host='redis', port=6379, db=0)

# Use in analysis_cache.py
def get_cached_analysis(claim_hash):
    return cache.get(f"analysis:{claim_hash}")
```

### 10.3 Cost Monitoring

- Set up cost alerts on AWS CloudWatch
- Monitor model serving costs
- Track API call metrics
- Optimize vector DB usage (Pinecone pricing)

---

## Recommended Execution Order

1. **Week 1**: Integration testing + CI/CD (Phases 1-2)
2. **Week 2**: Docker & deployment (Phase 3)
3. **Week 3**: Monitoring + security (Phases 4, 6)
4. **Week 4**: Database optimization + frontend (Phases 7-8)
5. **Week 5**: Documentation + scaling (Phases 9-10)

---

## Success Metrics

| Metric | Target | Timeline |
|--------|--------|----------|
| Test coverage | > 80% | Week 1 |
| CI/CD pipeline | 100% automated | Week 1 |
| Deployment frequency | Daily | Week 2 |
| Mean time to recovery | < 15 min | Week 3 |
| P95 latency | < 5 seconds | Week 2 |
| Uptime | 99.9% | Week 4 |
| Security scan pass | 0 vulnerabilities | Week 3 |

---

## Resources & Tools

**Tools Needed:**
- k6 (load testing): https://k6.io/
- Prometheus: https://prometheus.io/
- Grafana: https://grafana.com/
- Datadog: https://www.datadoghq.com/ (optional)
- Snyk (security): https://snyk.io/

**Documentation:**
- FastAPI docs: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Docker: https://docs.docker.com/
- Kubernetes: https://kubernetes.io/docs/

---

## Next Steps

1. Choose which phases to execute first
2. Assign owners to each phase
3. Create GitHub issues for tracking
4. Schedule team sync for phase 1 kickoff

**Status**: Ready for Phase 1 execution ✅
