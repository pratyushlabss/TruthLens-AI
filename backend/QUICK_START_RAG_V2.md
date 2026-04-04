"""
QUICK START: NEW RAG PIPELINE
=============================

Use this as a quick reference to get started with the new pipeline.
For full details, see RAG_PIPELINE_IMPLEMENTATION_GUIDE.md
"""

# ============================================================================
# 5-MINUTE SETUP
# ============================================================================

"""
STEP 1: Install Dependencies
$ cd backend
$ pip install -r requirements.txt

STEP 2: Verify Installation
$ python demo_pipeline_new.py

STEP 3: Test Pipeline
$ pytest tests/test_pipeline_new.py -v -m "not slow" -x

STEP 4: Configure (Optional)
Add to .env file:
  USE_NEW_RAG_PIPELINE=true
  NEW_RAG_DEVICE=cpu              # or cuda for GPU
  NEW_RAG_USE_NLI=true
  NEW_RAG_TOP_K_EVIDENCE=5

DONE! Pipeline is ready.
"""

# ============================================================================
# PYTHON API EXAMPLES
# ============================================================================

"""
EXAMPLE 1: Basic Usage
-----

from backend.services.pipeline_new import ProductionRAGPipeline

# Initialize (first time takes ~2-3s to load models)
pipeline = ProductionRAGPipeline(use_nli=False, device="cpu")

# Analyze a claim
result = pipeline.analyze("The Earth is round")

# Extract results
print(f"Verdict: {result['verdict']}")                # 'TRUE'
print(f"Confidence: {result['confidence']:.2%}")      # 92.50%
print(f"Evidence: {len(result['evidence'])} pieces")  # 5 pieces

# View top evidence
for i, ev in enumerate(result['evidence'][:2], 1):
    print(f"{i}. {ev['sentence']}")
    print(f"   Source: {ev['source']}")
    print(f"   Similarity: {ev['similarity_score']:.3f}")

---

EXAMPLE 2: With NLI Inference (More Accurate)
-----

from backend.services.pipeline_new import ProductionRAGPipeline

pipeline = ProductionRAGPipeline(
    use_nli=True,      # Enable BART-large-MNLI
    device="cpu"       # Use 'cuda' if GPU available
)

result = pipeline.analyze(
    claim="Is artificial intelligence dangerous?",
    top_k_evidence=5,
    query_expansion_enabled=True
)

print(f"Verdict: {result['verdict']}")
print(f"Evidence pieces: {len(result['evidence'])}")

# Access NLI scores
for ev in result['evidence']:
    print(f"Entailment: {ev['nli_entailment']:.3f}")
    print(f"Contradiction: {ev['nli_contradiction']:.3f}")

---

EXAMPLE 3: Fast, Deterministic (No NLI)
-----

from backend.services.pipeline_new import StreamlineRAGPipeline

# Faster version, purely deterministic
pipeline = StreamlineRAGPipeline(device="cpu")

result = pipeline.analyze(
    claim="Water is H2O",
    top_k_evidence=3
)

# Same confidence if run again (deterministic!)
# No randomness from NLI model

---

EXAMPLE 4: Component-by-Component
-----

# Just retrieval
from backend.services.retrieval_new import RetrievalPipeline
retrieval = RetrievalPipeline()
articles = retrieval.retrieve("climate change")

# Just ranking
from backend.services.ranking_new import RankingPipeline
ranking = RankingPipeline()
ranked = ranking.rank_evidence_batch(
    query="Is climate change real?",
    evidence_batch=... 
)

# Just utilities
from backend.services.utils_new import extract_sentences, clean_text
sentences = extract_sentences(article_text)
clean = clean_text(html_text)
"""

# ============================================================================
# HTTP API EXAMPLES
# ============================================================================

"""
EXAMPLE 1: Basic Endpoint
-----

curl -X POST http://localhost:8000/analyze/v2 \\
  -F "claim=Is the Earth flat?" \\
  -F "session_id=user123"

Response:
{
  "success": true,
  "claim": "Is the Earth flat?",
  "answer": "FALSE: The Earth is an oblate spheroid...",
  "verdict": "FALSE",
  "confidence": 0.92,
  "evidence": [
    {
      "sentence": "The Earth is approximately an oblate spheroid.",
      "source": "Wikipedia",
      "url": "https://en.wikipedia.org/wiki/Earth",
      "similarity_score": 0.89,
      "nli_entailment": 0.95,
      "nli_contradiction": 0.02,
      "nli_neutral": 0.03
    },
    ...
  ],
  "metadata": {
    "queries_used": ["Is the Earth flat?", "Earth sphere", ...],
    "total_articles_fetched": 12,
    "total_sentences_extracted": 245,
    "total_unique_sentences": 198,
    "final_evidence_count": 5,
    "processing_time_ms": 5420.5,
    "nli_enabled": true,
    "timestamp": "2026-03-27T12:30:45.123456"
  }
}

---

EXAMPLE 2: Using Python Requests
-----

import requests

response = requests.post(
    "http://localhost:8000/analyze/v2",
    data={
        "claim": "Do vaccines cause autism?",
        "session_id": "session_abc123"
    }
)

result = response.json()
print(f"Verdict: {result['verdict']}")
print(f"Confidence: {result['confidence']}")
print(f"Evidence pieces: {len(result['evidence'])}")

---

EXAMPLE 3: Batch Analysis
-----

claims = [
    "The sky is blue",
    "Water boils at 100°C",
    "AI is dangerous"
]

response = requests.post(
    "http://localhost:8000/analyze/v2/batch",
    json={"claims": claims}
)

results = response.json()["results"]
for result in results:
    print(f"{result['claim']}: {result['verdict']} ({result['confidence']:.0%})")

---

EXAMPLE 4: Health Check
-----

curl http://localhost:8000/analyze/v2/health

{
  "status": "healthy",
  "version": "v2",
  "timestamp": "2026-03-27T12:30:45.123456",
  "config": {
    "use_nli": true,
    "embedder": "all-MiniLM-L6-v2",
    "device": "cpu",
    "top_k": 5,
    "query_expansion": true
  }
}

---

EXAMPLE 5: Streamlined (Fast) Version
-----

curl -X POST http://localhost:8000/analyze/v2/streamlined \\
  -F "claim=Is Python a programming language?"

# Same response format, but:
# - Faster (no NLI inference)
# - Deterministic (no model randomness)
# - Uses only semantic similarity for confidence
"""

# ============================================================================
# CONFIGURATION OPTIONS
# ============================================================================

"""
ENVIRONMENT VARIABLES (.env):

# Enable new v2 endpoint
USE_NEW_RAG_PIPELINE=true

# Model selection
NEW_RAG_EMBEDDER_MODEL=all-MiniLM-L6-v2
  Options:
    - all-MiniLM-L6-v2 (fast, 80M params) [DEFAULT]
    - all-mpnet-base-v2 (accurate, larger)
    - distiluse-base-multilingual-cased-v2 (multilingual)

# NLI model enable/disable
NEW_RAG_USE_NLI=true
  - true: More accurate, slower (~5-8s per claim)
  - false: Faster, deterministic (~2-3s per claim)

# Number of top evidence pieces to return
NEW_RAG_TOP_K_EVIDENCE=5
  - Recommended: 3-10
  - More evidence = more context but slower

# Query expansion enable/disable
NEW_RAG_QUERY_EXPANSION=true
  - true: 3-5 search variants (better coverage)
  - false: Single query (faster)

# GPU/CPU selection
NEW_RAG_DEVICE=cpu
  - cpu: Always available
  - cuda: If NVIDIA GPU present (faster)

EXAMPLE .env:
---
# New RAG Pipeline Config
USE_NEW_RAG_PIPELINE=true
NEW_RAG_EMBEDDER_MODEL=all-MiniLM-L6-v2
NEW_RAG_USE_NLI=true
NEW_RAG_TOP_K_EVIDENCE=5
NEW_RAG_QUERY_EXPANSION=true
NEW_RAG_DEVICE=cpu

# Existing config (still required)
HUGGINGFACE_API_KEY=hf_xxxxx...
PINECONE_API_KEY=pc_xxxxx...
...
---
"""

# ============================================================================
# COMMON PATTERNS
# ============================================================================

"""
PATTERN 1: Fact-Check Multiple Claims
-----

claims = [
    "The sky is blue",
    "Water boils at 100 degrees",
    "The sun is hot"
]

from backend.services.pipeline_new import ProductionRAGPipeline
pipeline = ProductionRAGPipeline(use_nli=False)

for claim in claims:
    result = pipeline.analyze(claim)
    print(f"{claim}: {result['verdict']} ({result['confidence']:.0%})")

---

PATTERN 2: Get Detailed Evidence
-----

result = pipeline.analyze("Climate change is real")

for i, evidence in enumerate(result['evidence'], 1):
    print(f"Evidence {i}:")
    print(f"  Claim: {evidence['sentence']}")
    print(f"  Source: {evidence['source']}")
    print(f"  URL: {evidence['url']}")
    print(f"  Similarity: {evidence['similarity_score']:.3f}")
    if result['metadata']['nli_enabled']:
        print(f"  Supports claim: {evidence['nli_entailment']:.3f}")
        print(f"  Contradicts: {evidence['nli_contradiction']:.3f}")

---

PATTERN 3: Handle Errors Gracefully
-----

from backend.services.pipeline_new import ProductionRAGPipeline, RAGPipelineError

pipeline = ProductionRAGPipeline(use_nli=False)

try:
    result = pipeline.analyze("Some claim")
    print(result['verdict'])
except RAGPipelineError as e:
    print(f"Analysis failed: {e}")
    # Provide fallback response
    print("Unable to verify claim at this time")

---

PATTERN 4: Performance Tuning
-----

# Fast mode (for high-volume analysis)
fast_pipeline = ProductionRAGPipeline(
    use_nli=False,           # Disable NLI
    embedder_model="all-MiniLM-L6-v2",  # Small model
    device="cpu"
)
result = fast_pipeline.analyze(claim, top_k_evidence=3)

# Accurate mode (for critical claims)
accurate_pipeline = ProductionRAGPipeline(
    use_nli=True,            # Enable NLI
    embedder_model="all-mpnet-base-v2",  # Larger model
    device="cuda"            # Use GPU
)
result = accurate_pipeline.analyze(claim, top_k_evidence=7)

---

PATTERN 5: Caching Claims
-----

cache = {}

def analyze_with_cache(claim):
    if claim in cache:
        return cache[claim]
    
    result = pipeline.analyze(claim)
    cache[claim] = result
    return result

# First call: 5s (includes retrieval)
result1 = analyze_with_cache("Is AI dangerous?")

# Second call: instant (from cache)
result2 = analyze_with_cache("Is AI dangerous?")
"""

# ============================================================================
# MONITORING & OBSERVABILITY
# ============================================================================

"""
METRICS TO TRACK:

1. Latency
   - Total analysis time
   - Per-stage breakdown (retrieval, ranking, NLI)
   - Query expansion time

2. Accuracy
   - Confidence distribution
   - Verdict accuracy (via manual review)
   - False positive/negative rates

3. Coverage
   - Successful analyses vs failures
   - Wikipedia hit rate (queries with results)
   - Fallback usage (when Wikipedia insufficient)

4. Resource Usage
   - Memory consumption
   - GPU utilization (if applicable)
   - Model load time

LOGGING:

All components use Python logging.
Check DEBUG logs for step-by-step execution:

import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
# Now see DEBUG messages from pipeline

Key log messages:
  [V2] Stage 1: Query expansion
  [V2] Stage 2: Retrieval
  [V2] Retrieved 12 articles
  [V2] Stage 3: Sentence extraction
  [V2] Extracted 245 total sentences
  ...
"""

# ============================================================================
# NEXT STEPS
# ============================================================================

"""
NOW:
✓ Run: python backend/demo_pipeline_new.py
✓ Test: pytest backend/tests/test_pipeline_new.py -v -m "not slow" -x
✓ Review: backend/RAG_PIPELINE_IMPLEMENTATION_GUIDE.md

SOON:
→ Deploy new endpoint: /analyze/v2
→ Monitor accuracy and latency
→ Compare with old pipeline
→ Gradually migrate traffic to v2

LATER:
→ Optimize embedder for domain
→ Add multi-language support
→ Integrate with Pinecone for scale
→ Multi-hop reasoning
→ User feedback loop

ISSUES/QUESTIONS:
→ Check RAG_PIPELINE_IMPLEMENTATION_GUIDE.md#TROUBLESHOOTING
→ Review test cases for examples
→ Check demo_pipeline_new.py for code samples
"""

print("QUICK START REFERENCE - Ready to use!")
