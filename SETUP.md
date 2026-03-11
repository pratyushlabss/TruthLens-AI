# Setup Guide: TruthLens AI

Complete step-by-step guide to set up the TruthLens AI project locally and in production.

---

## ⚙️ Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **PostgreSQL 15+**
- **Redis 7+**
- **Git**

---

## 🔧 Local Development Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/TruthLens-AI.git
cd TruthLens-AI
```

### Step 2: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Key .env variables**:

```env
ENV=development
DATABASE_URL=postgresql://user:password@localhost:5432/truthlens_db
PINECONE_API_KEY=your_key_here
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Step 3: Frontend Setup

```bash
# Navigate to frontend
cd ../frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local

# Run development server
npm run dev
```

Frontend available at: `http://localhost:3000`

### Step 4: Database Setup

```bash
# Using Docker Compose (Recommended)
docker-compose -f deployment/docker-compose.yml up -d postgres redis

# Or manually
# Install PostgreSQL locally and create database:
createdb truthlens_db

# Apply migrations (if using Alembic)
cd backend
alembic upgrade head
```

### Step 5: Run Backend

```bash
# Terminal 1: Backend server
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Celery worker (optional, for async tasks)
cd backend
celery -A tasks worker --loglevel=info
```

API documentation: `http://localhost:8000/docs`

---

## 🐳 Docker Setup (Recommended for Testing)

### Quick Start with Docker Compose

```bash
# Start all services
docker-compose -f deployment/docker-compose.yml up --build

# View logs
docker-compose -f deployment/docker-compose.yml logs -f

# Stop services
docker-compose -f deployment/docker-compose.yml down

# Reset volumes (clear data)
docker-compose -f deployment/docker-compose.yml down -v
```

Services available:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

---

## 📦 Installation Troubleshooting

### PyTorch Installation Issues

```bash
# CPU only
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# GPU (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# GPU (CUDA 12.1)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
psql -h localhost -U user -d truthlens_db

# If using Docker:
docker exec truthlens-postgres psql -U user -d truthlens_db
```

### Model Download Issues

The first time you run the backend, it will download:
- `roberta-base` (~440 MB)
- `all-MiniLM-L6-v2` (~90 MB)

This may take a few minutes. Models are cached in `~/.cache/huggingface/`

---

## ☁️ AWS Deployment

### 1. Create AWS EC2 Instance

```bash
# Launch t3.medium instance (Ubuntu 22.04)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-groups default \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=truthlens-backend}]'
```

### 2. Set Up RDS PostgreSQL

```bash
aws rds create-db-instance \
  --db-instance-identifier truthlens-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password $(openssl rand -base64 32) \
  --allocated-storage 20 \
  --publicly-accessible
```

### 3. Deploy Backend to EC2

```bash
# SSH into EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone repository
git clone https://github.com/yourusername/TruthLens-AI.git
cd TruthLens-AI

# Create .env
cp backend/.env.example backend/.env
# Edit with your RDS endpoint, Pinecone key, etc.

# Run Docker
docker-compose -f deployment/docker-compose.yml up -d

# Check logs
docker-compose logs -f backend
```

### 4. Set Up Vercel Frontend

```bash
# Link Vercel
npm i -g vercel
vercel link

# Deploy
vercel deploy --prod

# Or push to GitHub and auto-deploy
git push origin main
```

### 5. Configure API Gateway

```bash
# Create API Gateway
aws apigateway create-rest-api --name truthlens-api

# Create resource
aws apigateway create-resource \
  --rest-api-id <api-id> \
  --parent-id <parent-id> \
  --path-part analyze
```

---

## 🧪 Testing

### Unit Tests

```bash
cd backend
pytest tests/unit -v
```

### Integration Tests

```bash
cd backend
pytest tests/integration -v
```

### E2E Tests (Frontend)

```bash
cd frontend
npm run test:e2e
```

---

## 📊 Monitoring & Logs

### View Backend Logs

```bash
# Docker
docker-compose logs backend -f

# Local
tail -f backend/logs/app.log
```

### Monitor Database

```bash
# Connect to database
psql -h localhost -U user -d truthlens_db

# View active connections
SELECT * FROM pg_stat_activity;

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 🚀 Performance Optimization

### 1. Enable Model Caching

```python
# backend/config.py
MODEL_CACHE_DIR = "/var/cache/truthlens/models"
BATCH_SIZE = 32
```

### 2. Redis Caching

```python
from redis import Redis
redis = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Cache results
redis.setex(cache_key, 86400, json.dumps(result))  # 24 hours
```

### 3. Database Optimization

```sql
-- Create indexes for faster queries
CREATE INDEX idx_queries_verdict ON queries(verdict);
CREATE INDEX idx_queries_created_at ON queries(created_at DESC);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
```

---

## 🔐 Security Checklist

- [ ] Change default database password
- [ ] Set strong Pinecone API key
- [ ] Configure AWS IAM roles
- [ ] Enable HTTPS on API Gateway
- [ ] Set up SSL certificate (Let's Encrypt)
- [ ] Restrict database access to backend IP
- [ ] Rotate API keys regularly
- [ ] Enable audit logging
- [ ] Set up firewall rules
- [ ] Use secrets manager (AWS Secrets Manager)

---

## 📝 Environment Variables Reference

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `ENV` | string | No | `development` | Environment (development/production) |
| `DATABASE_URL` | string | Yes | - | PostgreSQL connection string |
| `REDIS_URL` | string | No | `redis://localhost:6379` | Redis connection |
| `PINECONE_API_KEY` | string | No | - | Pinecone API key for vectors |
| `PINECONE_ENVIRONMENT` | string | No | `us-west1-gcp` | Pinecone environment |
| `AWS_ACCESS_KEY_ID` | string | No | - | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | string | No | - | AWS credentials |
| `AWS_S3_BUCKET` | string | No | `truthlens-ai` | S3 bucket name |
| `AWS_REGION` | string | No | `us-east-1` | AWS region |
| `CORS_ORIGINS` | string | No | `*` | CORS allowed origins |
| `PORT` | int | No | `8000` | Backend port |
| `HOST` | string | No | `0.0.0.0` | Backend host |

---

## 🆘 Support

- 📖 **Documentation**: [Read the full docs](./README.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/TruthLens-AI/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/TruthLens-AI/discussions)
- 📧 **Email**: support@truthlens-ai.com

---

**Last updated**: March 2026
