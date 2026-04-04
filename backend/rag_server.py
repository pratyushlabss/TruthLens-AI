"""TruthLens RAG v2 API Server"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.pipeline_new import ProductionRAGPipeline
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="TruthLens RAG v2",
    description="Production RAG pipeline for fact-checking",
    version="1.0.0"
)

# Allow frontend to call API from localhost dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
)

# Initialize pipeline
pipeline = None
threadpool = ThreadPoolExecutor(max_workers=2)

@app.on_event("startup")
async def startup():
    """Initialize pipeline on server startup."""
    global pipeline
    try:
        print("Initializing RAG pipeline... (this may take a minute)")
        pipeline = ProductionRAGPipeline(use_nli=False, device="cpu")
        print("✅ Pipeline initialized successfully")
    except Exception as e:
        print(f"❌ Pipeline initialization issue: {e}")
        pipeline = None

class AnalyzeRequest(BaseModel):
    claim: str
    top_k_evidence: int = 5

@app.get("/")
async def root():
    """API documentation endpoint."""
    return {
        "title": "TruthLens RAG v2 API",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze": "Fact-check a claim",
            "GET /health": "Health check status",
            "GET /docs": "Interactive Swagger UI",
            "GET /redoc": "ReDoc documentation"
        },
        "example_request": {
            "endpoint": "POST /analyze",
            "body": {
                "claim": "Paris is the capital of France",
                "top_k_evidence": 5
            }
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "TruthLens RAG v2",
        "pipeline_ready": pipeline is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """Fact-check a claim using RAG pipeline."""
    if not pipeline:
        return {
            "success": False,
            "error": "Pipeline not initialized",
            "claim": request.claim
        }
    
    # Run analysis in thread pool to avoid blocking event loop
    loop = __import__('asyncio').get_event_loop()
    result = await loop.run_in_executor(
        threadpool,
        pipeline.analyze,
        request.claim,
        request.top_k_evidence
    )
    return result

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 TruthLens RAG v2 API Server")
    print("=" * 80)
    print("\n📡 Server address: http://127.0.0.1:8000")
    print("\n🔗 Quick Links:")
    print("   • Interactive API (Swagger UI): http://127.0.0.1:8000/docs")
    print("   • ReDoc Documentation: http://127.0.0.1:8000/redoc")
    print("   • Health Check: http://127.0.0.1:8000/health")
    print("\n📝 Example curl command:")
    print("   curl -X POST http://127.0.0.1:8000/analyze \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"claim\": \"Paris is the capital of France\"}'")
    print("\n⏸️  Press Ctrl+C to stop\n")
    print("=" * 80 + "\n")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
