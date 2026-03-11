# TruthLens AI - Deployment & Operations Guide

## Deployment Checklist

### Pre-Deployment Verification
- [ ] All tests passing (`pytest backend/`)
- [ ] E2E pipeline tests passing (`python e2e_test.py`)
- [ ] System health check green (`python system_check.py`)
- [ ] Requirements.txt frozen with versions
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] ML models downloaded and cached
- [ ] S3 bucket created and configured
- [ ] Redis instance running
- [ ] Sentry project created

### Development Deployment

**1. Start Local Stack**
```bash
# Terminal 1: Docker services
docker-compose up -d postgres redis

# Terminal 2: Backend server
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 3: Frontend (when ready)
cd frontend
npm run dev
```

**2. Verify Health**
```bash
curl http://localhost:8000/api/health
# Expected: {"status": "healthy", "version": "2.0.0"}
```

### Production Deployment

#### Option 1: AWS ECS with Load Balancer

**1. Build Docker image:**
```bash
docker build -t truthlens-api:2.0.0 .
docker tag truthlens-api:2.0.0 [AWS_ACCOUNT].dkr.ecr.us-east-1.amazonaws.com/truthlens-api:2.0.0
docker push [AWS_ACCOUNT].dkr.ecr.us-east-1.amazonaws.com/truthlens-api:2.0.0
```

**2. Create ECS task definition:**
```json
{
  "family": "truthlens-api",
  "container_definitions": [
    {
      "name": "truthlens-api",
      "image": "[AWS_ACCOUNT].dkr.ecr.us-east-1.amazonaws.com/truthlens-api:2.0.0",
      "portMappings": [{
        "containerPort": 8000,
        "hostPort": 8000,
        "protocol": "tcp"
      }],
      "environment": [
        { "name": "DATABASE_URL", "value": "postgresql://..." },
        { "name": "REDIS_URL", "value": "redis://..." }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/truthlens-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**3. Create ECS service:**
```bash
aws ecs create-service \
  --cluster truthlens-cluster \
  --service-name truthlens-api-service \
  --task-definition truthlens-api \
  --desired-count 3 \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=truthlens-api,containerPort=8000
```

#### Option 2: Kubernetes Deployment

**1. Create image:**
```bash
docker build -t truthlens-api:2.0.0 .
```

**2. Deploy:**
```bash
kubectl create namespace truthlens
kubectl apply -f deployment/kubernetes/ -n truthlens
```

**3. Verify:**
```bash
kubectl get pods -n truthlens
kubectl logs -f deployment/truthlens-api -n truthlens
```

#### Option 3: Heroku Deployment

**1. Create Procfile:**
```
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

**2. Deploy:**
```bash
heroku create truthlens-ai
heroku config:set DATABASE_URL=postgresql://...
git push heroku main
```

## Database Setup

### PostgreSQL Initialization

**1. Create database:**
```sql
CREATE DATABASE truthlens_db;
CREATE USER truthlens WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE truthlens_db TO truthlens;
```

**2. Run migrations:**
```bash
cd backend
alembic upgrade head
```

**3. Create indexes for performance:**
```sql
CREATE INDEX idx_analysis_verdict ON analysis(verdict);
CREATE INDEX idx_analysis_created_at ON analysis(created_at DESC);
CREATE INDEX idx_analysis_confidence ON analysis(confidence DESC);
CREATE INDEX idx_evidence_source ON evidence(source);
```

**4. Enable full-text search:**
```sql
CREATE INDEX idx_analysis_text_fts ON analysis USING GIN(to_tsvector('english', claim_text));
```

## Monitoring & Alerting

### Prometheus Scrape Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  
scrape_configs:
  - job_name: 'truthlens-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### Key Metrics to Monitor
```
# Request metrics
truthlens_requests_total{method, endpoint, status}
truthlens_request_duration_seconds{quantile, endpoint}

# Model metrics
truthlens_nlp_score_mean
truthlens_evidence_score_mean
truthlens_propagation_score_mean

# System metrics
truthlens_gpu_memory_usage_bytes
truthlens_model_inference_time_seconds
truthlens_evidence_cache_hit_ratio

# Error metrics
truthlens_errors_total{type}
truthlens_ocr_failures_total
truthlens_evidence_retrieval_failures_total
```

### Alert Rules
```yaml
groups:
  - name: truthlens
    rules:
      - alert: HighErrorRate
        expr: rate(truthlens_errors_total[5m]) > 0.05
        for: 5m
        
      - alert: SlowInference
        expr: truthlens_request_duration_seconds{quantile="0.95"} > 2
        for: 10m
        
      - alert: LowCacheHitRatio
        expr: truthlens_evidence_cache_hit_ratio < 0.7
        for: 30m
        
      - alert: DatabaseConnectionPoolExhausted
        expr: truthlens_db_pool_available_connections == 0
        for: 1m
```

## Scaling Strategy

### Horizontal Scaling (Load Balancing)

**Nginx Configuration:**
```nginx
upstream truthlens_backend {
    server api1.truthlens.com:8000;
    server api2.truthlens.com:8000;
    server api3.truthlens.com:8000;
}

server {
    listen 80;
    server_name api.truthlens.com;
    
    location / {
        proxy_pass http://truthlens_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;
    }
}
```

### Vertical Scaling (Caching)

**Redis Configuration:**
```bash
# Cache analysis results for 24 hours
SET analysis:{claim_hash} {result_json} EX 86400

# Preload popular claims
RPUSH popular_claims claim_1 claim_2 claim_3
MGET claim_1 claim_2 claim_3
```

### Model Optimization

**Model Quantization:**
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model = AutoModelForSequenceClassification.from_pretrained('roberta-base')
quantized = torch.quantization.quantize_dynamic(model, {torch.nn.Linear})
```

## Backup & Disaster Recovery

### Database Backup

**Daily automated backup:**
```bash
# Backup script
#!/bin/bash
BACKUP_DIR="/backups/truthlens"
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump postgresql://user:pass@localhost/truthlens_db | gzip > $BACKUP_DIR/truthlens_$DATE.sql.gz
aws s3 cp $BACKUP_DIR/truthlens_$DATE.sql.gz s3://truthlens-backups/
```

**Restore from backup:**
```bash
aws s3 cp s3://truthlens-backups/truthlens_20240115_000000.sql.gz .
gunzip truthlens_20240115_000000.sql.gz
psql postgresql://user:pass@localhost/truthlens_db < truthlens_20240115_000000.sql
```

### FAISS Index Backup

```bash
# Backup FAISS index
aws s3 cp backend/data/evidence_index.faiss s3://truthlens-backups/indices/
aws s3 cp backend/data/evidence_store.pkl s3://truthlens-backups/indices/

# Restore
aws s3 cp s3://truthlens-backups/indices/evidence_index.faiss backend/data/
aws s3 cp s3://truthlens-backups/indices/evidence_store.pkl backend/data/
```

## Security Hardening

### API Security Headers
```python
# In main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.truthlens.com", "app.truthlens.com"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.truthlens.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/analyze")
@limiter.limit("100/minute")
async def analyze(request: Request, claim: AnalyzeClaim):
    # Implementation
    pass
```

### Input Validation
```python
from pydantic import BaseModel, Field, validator

class AnalyzeClaim(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000)
    
    @validator('text')
    def sanitize_text(cls, v):
        # Remove HTML, SQL injection attempts
        return v.strip()
```

## Logging & Audit Trail

### Structured Logging
```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'user_id': getattr(record, 'user_id', None),
            'analysis_id': getattr(record, 'analysis_id', None),
        }
        return json.dumps(log_data)

handler = logging.FileHandler('app.log')
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

### Audit Trail
```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(50),
    resource_id INTEGER,
    changes JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Log all analysis changes
CREATE OR REPLACE FUNCTION log_analysis_change()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (user_id, action, resource_id, changes)
    VALUES (current_user_id(), TG_OP, NEW.id, row_to_json(NEW));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER analysis_audit_trigger
AFTER INSERT OR UPDATE ON analysis
FOR EACH ROW
EXECUTE FUNCTION log_analysis_change();
```

## Performance Tuning

### Database Query Optimization
```sql
-- Analyze query plans
EXPLAIN ANALYZE
SELECT * FROM analysis 
WHERE created_at > NOW() - INTERVAL '7 days'
AND confidence > 0.8;

-- Add missing indexes if needed
CREATE INDEX idx_analysis_date_confidence 
ON analysis(created_at DESC, confidence DESC);
```

### Caching Strategy
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def get_analysis_result(claim_hash):
    # Cache up to 1000 recent results
    return fetch_from_db(claim_hash)

def cache_key(text):
    return hashlib.md5(text.encode()).hexdigest()
```

## Rollback Procedure

```bash
# 1. Check current version
curl http://api.truthlens.com/api/health | jq '.version'

# 2. Identify previous stable version
aws ecr describe-images --repository-name truthlens-api | jq '.imageDetails | sort_by(.imagePushedAt) | reverse | .[0:3]'

# 3. Rollback ECS service
aws ecs update-service \
  --cluster truthlens-cluster \
  --service truthlens-api-service \
  --force-new-deployment \
  --task-definition truthlens-api:previous-version

# 4. Monitor rollback
aws ecs describe-services --cluster truthlens-cluster --services truthlens-api-service | jq '.services[0].deployments'

# 5. Verify
curl http://api.truthlens.com/api/health
```

## Cost Optimization

### Resource Allocation
- **API Servers**: t3.medium (2 CPU, 4GB RAM) × 3
- **Database**: db.t3.small (2 CPU, 2GB RAM)
- **Redis**: cache.t3.small (1 CPU, 1GB)
- **Estimated Monthly**: $150-200

### Cost Reduction Tips
- Use spot instances (30-70% savings)
- Enable S3 intelligent tiering
- Archive old analysis results to Glacier
- Use CloudFront CDN for static assets

## Maintenance Window

**Weekly Maintenance:**
```bash
# Backup verification
aws s3 ls s3://truthlens-backups/ | tail -5

# Cache cleanup
redis-cli FLUSHALL --ASYNC

# Log rotation
logrotate -f /etc/logrotate.d/truthlens
```

**Monthly Maintenance:**
```bash
# Database vacuum and analyze
VACUUM ANALYZE;

# FAISS index optimization
python backend/optimize_faiss_index.py

# Model updates check
huggingface-cli repo-info roberta-base
```

---

**Last Updated:** January 2024
**Version:** 2.0.0
