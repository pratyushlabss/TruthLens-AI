# 🎓 TruthLens AI - Quick Navigation Guide

Welcome! This guide helps you navigate the TruthLens AI project.

---

## 🚀 Start Here

**New to the project?** Start with these in order:

1. **[GETTING_STARTED.md](GETTING_STARTED.md)** ← **START HERE** (10 min read)
   - What's been built
   - Quick setup instructions
   - Common issues

2. **[README.md](README.md)** (15 min read)
   - Full project overview
   - Architecture diagram
   - How to use it

3. **[SETUP.md](SETUP.md)** (30 min read)
   - Detailed installation
   - Local development
   - AWS deployment

---

## 📚 Documentation Map

### By Role

**👨‍💻 Developer** (Building the project)
1. [GETTING_STARTED.md](GETTING_STARTED.md) - Quick setup
2. [backend/main.py](backend/main.py) - Start here for code
3. [backend/services/scoring_engine.py](backend/services/scoring_engine.py) - Core logic

**🔬 Data Scientist** (Training models)
1. [ARCHITECTURE.md](ARCHITECTURE.md#-model-architecture) - Model details
2. [notebooks/README.md](notebooks/README.md) - Training notebooks
3. [backend/models/](backend/models/) - Model implementations

**☁️ DevOps/Cloud** (Deployment)
1. [SETUP.md](SETUP.md#-aws-deployment) - AWS setup
2. [deployment/docker-compose.yml](deployment/docker-compose.yml) - Docker config
3. [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml) - CI/CD pipeline

**📋 Project Manager** (Overview)
1. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project stats
2. [FILE_INVENTORY.md](FILE_INVENTORY.md) - What's included
3. [README.md](README.md) - Full scope

---

## 🗂️ File Quick Reference

### 📖 Documentation (Read These)
| File | Purpose | Time | Read If... |
|------|---------|------|-----------|
| [README.md](README.md) | Main overview | 15 min | You want project summary |
| [GETTING_STARTED.md](GETTING_STARTED.md) | Quick start | 10 min | You want to start now |
| [SETUP.md](SETUP.md) | Installation | 30 min | You want detailed setup |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical details | 20 min | You want to understand design |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Phase 1 summary | 10 min | You want what's been done |
| [FILE_INVENTORY.md](FILE_INVENTORY.md) | Complete inventory | 5 min | You want to see everything |

### 💻 Backend Code (Run These)
| File | Purpose | Priority |
|------|---------|----------|
| [backend/main.py](backend/main.py) | FastAPI app | **CRITICAL** |
| [backend/services/scoring_engine.py](backend/services/scoring_engine.py) | Core logic | **CRITICAL** |
| [backend/api/analyze.py](backend/api/analyze.py) | API endpoint | **HIGH** |
| [backend/models/roberta_classifier.py](backend/models/roberta_classifier.py) | NLP model | **HIGH** |
| [backend/models/evidence_engine.py](backend/models/evidence_engine.py) | Evidence retrieval | **HIGH** |
| [backend/models/propagation_model.py](backend/models/propagation_model.py) | Propagation analysis | **HIGH** |
| [backend/database/models.py](backend/database/models.py) | Database schema | **MEDIUM** |

### 🐳 Deployment (Configure These)
| File | Purpose |
|------|---------|
| [deployment/Dockerfile](deployment/Dockerfile) | Container image |
| [deployment/docker-compose.yml](deployment/docker-compose.yml) | Local services |
| [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml) | CI/CD pipeline |
| [backend/.env.example](backend/.env.example) | Configuration template |

---

## ⚡ Common Tasks

### I want to...

**...run the project locally**
→ [GETTING_STARTED.md - Quick Start](GETTING_STARTED.md#-what-ive-accomplished) + [SETUP.md - Local Dev](SETUP.md#-local-development-setup)

**...understand the architecture**
→ [ARCHITECTURE.md](ARCHITECTURE.md) + [README.md - System Overview](README.md#-system-overview)

**...deploy to AWS**
→ [SETUP.md - AWS Deployment](SETUP.md#%EF%B8%8F-aws-deployment)

**...modify the scoring**
→ [backend/services/scoring_engine.py](backend/services/scoring_engine.py)

**...add a new API endpoint**
→ [backend/api/analyze.py](backend/api/analyze.py) as template

**...understand the models**
→ [ARCHITECTURE.md - Model Architecture](ARCHITECTURE.md#model-architecture)

**...see what's been built**
→ [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

**...check code quality**
→ [FILE_INVENTORY.md - Code Stats](FILE_INVENTORY.md#-code-statistics)

---

## 🎯 Development Workflow

### Phase 1: Foundation ✅ (DONE)
```
✅ Project structure
✅ Backend scaffold
✅ ML models
✅ API endpoints
✅ Database setup
✅ Docker configuration
```

### Phase 2: Frontend (NEXT)
```
⏳ Initialize Next.js
⏳ Build components
⏳ Connect API
⏳ Add styling
⏳ User testing
```

### Phase 3: Deployment
```
⏳ Set up AWS
⏳ Deploy backend
⏳ Deploy frontend
⏳ Configure monitoring
```

---

## 🔧 Setup Checklist

- [ ] Read [GETTING_STARTED.md](GETTING_STARTED.md)
- [ ] Run `./setup.sh`
- [ ] Create `.env` file
- [ ] Run Docker: `docker-compose up`
- [ ] Test: `curl http://localhost:8000/health`
- [ ] View docs: http://localhost:8000/docs
- [ ] Build frontend

---

## 📞 Need Help?

| Problem | Solution |
|---------|----------|
| Don't know where to start | Read [GETTING_STARTED.md](GETTING_STARTED.md) |
| Need technical details | Read [ARCHITECTURE.md](ARCHITECTURE.md) |
| Installation problems | Check [SETUP.md](SETUP.md) troubleshooting |
| Want to see what's built | Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) |
| Looking for specific file | Check [FILE_INVENTORY.md](FILE_INVENTORY.md) |
| Want full project overview | Read [README.md](README.md) |

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Files Created** | 31 |
| **Lines of Code** | 3,200+ |
| **API Endpoints** | 8 |
| **ML Models** | 3 |
| **Database Tables** | 3 |
| **Setup Time** | ~30 min |
| **MVP Time** | 1-2 weeks |

---

## ✨ What's Included

✅ **Backend**: FastAPI with 3 ML models  
✅ **Database**: PostgreSQL + Vector DB ready  
✅ **API**: 8 complete endpoints  
✅ **Docker**: Local & production configs  
✅ **CI/CD**: GitHub Actions pipeline  
✅ **Documentation**: 6 comprehensive guides  

---

## 🚀 Next Step

**Ready to start?**

1. Open [GETTING_STARTED.md](GETTING_STARTED.md)
2. Follow the setup steps
3. Run the backend
4. Test at http://localhost:8000/docs
5. Build the frontend

**Questions?** Check the documentation table above.

---

**Status**: Phase 1 Complete ✅  
**Version**: 1.0  
**Last Updated**: March 2026

Happy Building! 🚀
