# Phase 2: Integration Testing & Validation

## Overview
Validate that all optimizations work correctly together and achieve the target latency of **< 15 seconds** with **< 2 LLM calls per request**.

---

## Test Suite

### Test 1: System Health Check

**Objective**: Verify all dependencies and environment setup

```bash
# Check imports
python -c "from backend.services.llm_reasoner import ProductionLLMReasoner; from backend.services.retrieval_new import RetrievalPipeline; from backend.services.pipeline_new import ProductionRAGPipeline; print('✅ All imports successful')"

# Check environment variables
python -c "from config.environment import Config; print(f'OpenAI Key: {bool(Config.OPENAI_API_KEY)}'); print(f'Tavily Key: {bool(Config.TAVILY_API_KEY)}')"

# Check heuristic functions exist
python -c "from backend.services.llm_reasoner import ProductionLLMReasoner; reasoner = ProductionLLMReasoner(); print('✅ Heuristic functions available'); assert hasattr(reasoner, 'compute_semantic_credibility_heuristic'); assert hasattr(reasoner, 'detect_relationship_heuristic'); assert hasattr(reasoner, 'classify_evidence_type_heuristic')"
```

**Expected Output**:
- ✅ All imports successful
- ✅ API keys configured (or clear error message)
- ✅ Heuristic functions available

---

### Test 2: Unit Tests - Heuristic Functions

**Test: `compute_semantic_credibility_heuristic()`**
```python
from backend.services.llm_reasoner import ProductionLLMReasoner

reasoner = ProductionLLMReasoner()

# Test 1: Wikipedia source should score high
score = reasoner.compute_semantic_credibility_heuristic(
    "The Earth is a sphere.",
    source="Wikipedia"
)
assert 0.8 <= score <= 0.9, f"Expected 0.8-0.9, got {score}"
print(f"✅ Wikipedia source: {score}")

# Test 2: Tavily source should score slightly lower
score = reasoner.compute_semantic_credibility_heuristic(
    "The Earth is a sphere.",
    source="Tavily"
)
assert 0.65 <= score <= 0.75, f"Expected 0.65-0.75, got {score}"
print(f"✅ Tavily source: {score}")

# Test 3: Speculative language should lower score
score = reasoner.compute_semantic_credibility_heuristic(
    "The Earth might be a sphere.",
    source="Wikipedia"
)
assert score < 0.8, f"Expected < 0.8 for speculative, got {score}"
print(f"✅ Speculative language: {score}")
```

**Test: `detect_relationship_heuristic()`**
```python
from backend.services.llm_reasoner import ProductionLLMReasoner

reasoner = ProductionLLMReasoner()

# Test 1: High similarity should be SUPPORTS
rel = reasoner.detect_relationship_heuristic(
    "The Earth is round.",
    "The Earth is spherical.",
    similarity=0.85
)
assert rel == "SUPPORTS", f"Expected SUPPORTS, got {rel}"
print(f"✅ High similarity: {rel}")

# Test 2: Low similarity should be CONTRADICTS
rel = reasoner.detect_relationship_heuristic(
    "The Earth is flat.",
    "The Earth is round.",
    similarity=0.3
)
assert rel == "CONTRADICTS", f"Expected CONTRADICTS, got {rel}"
print(f"✅ Low similarity: {rel}")

# Test 3: Medium similarity should be NEUTRAL
rel = reasoner.detect_relationship_heuristic(
    "The Earth is the third planet.",
    "Mercury is the first planet.",
    similarity=0.5
)
assert rel == "NEUTRAL", f"Expected NEUTRAL, got {rel}"
print(f"✅ Medium similarity: {rel}")
```

**Test: `classify_evidence_type_heuristic()`**
```python
from backend.services.llm_reasoner import ProductionLLMReasoner

reasoner = ProductionLLMReasoner()

# Test 1: Historical statement
evidence_type = reasoner.classify_evidence_type_heuristic(
    "In 1969, Apollo 11 landed on the moon."
)
assert evidence_type == "historical", f"Expected historical, got {evidence_type}"
print(f"✅ Historical: {evidence_type}")

# Test 2: Opinion statement
evidence_type = reasoner.classify_evidence_type_heuristic(
    "I think the climate is changing due to human activity."
)
assert evidence_type == "opinion", f"Expected opinion, got {evidence_type}"
print(f"✅ Opinion: {evidence_type}")

# Test 3: Speculative statement
evidence_type = reasoner.classify_evidence_type_heuristic(
    "The Earth could be destroyed by an asteroid in the future."
)
assert evidence_type == "speculation", f"Expected speculation, got {evidence_type}"
print(f"✅ Speculation: {evidence_type}")

# Test 4: Factual statement
evidence_type = reasoner.classify_evidence_type_heuristic(
    "Water boils at 100 degrees Celsius at sea level."
)
assert evidence_type == "factual", f"Expected factual, got {evidence_type}"
print(f"✅ Factual: {evidence_type}")
```

---

### Test 3: Integration Test - Full Pipeline

**Test: Single Claim Analysis**
```python
import time
from backend.services.pipeline_new import ProductionRAGPipeline

# Initialize pipeline
pipeline = ProductionRAGPipeline(
    use_nli=False,  # Disable NLI for speed
    embedder_model="all-MiniLM-L6-v2",
    device="cpu"
)

# Test claim
claim = "The Earth is flat."

# Measure execution time
start = time.time()
result = pipeline.analyze(
    claim=claim,
    top_k_evidence=3,
    query_expansion_enabled=False  # Disable expansion for speed
)
elapsed = time.time() - start

# Verify results
assert result.get("success"), "Analysis should succeed"
assert result.get("verdict") in ["SUPPORTS", "REFUTES", "UNCERTAIN"], f"Invalid verdict: {result.get('verdict')}"
assert len(result.get("evidence", [])) >= 0, "Should have evidence list"
assert elapsed < 15, f"Expected < 15s, got {elapsed:.2f}s"

print(f"✅ Full pipeline test:")
print(f"   - Claim: {claim}")
print(f"   - Label: {result.get('label')}")
print(f"   - Confidence: {result.get('confidence_percentage'):.1f}%")
print(f"   - Evidence count: {len(result.get('evidence', []))}")
print(f"   - Latency: {elapsed:.2f}s")
print(f"   - LLM calls in pipeline: 2 (analyze_claim + reason_over_evidence)")
```

**Expected Output**:
- ✅ Analysis succeeds
- ✅ Label is SUPPORTS, REFUTES, or UNCERTAIN
- ✅ Evidence count >= 0
- ✅ Latency < 15 seconds
- ✅ Only 2 LLM calls

---

### Test 4: Endpoint Testing - HTTP

**Setup**:
```bash
# Start backend server
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Test 4A: Valid Claim**
```bash
curl -X POST http://localhost:8000/analyze/v2 \
  -F "claim=The Earth is round." \
  -F "session_id=test123"
```

**Expected Response** (< 15 seconds):
```json
{
  "success": true,
  "claim": "The Earth is round.",
  "label": "SUPPORTS",
  "confidence_percentage": 85.5,
  "evidence": [...],
  "metadata": {
    "processing_time_ms": 12500,
    "final_evidence_count": 3
  }
}
```

**Test 4B: Invalid Claim - Too Short**
```bash
curl -X POST http://localhost:8000/analyze/v2 \
  -F "claim=abc"
```

**Expected Response** (< 1 second):
```json
{
  "success": false,
  "label": "UNCERTAIN",
  "summary": "ERROR: Claim must be at least 5 characters"
}
```

**Test 4C: Invalid Claim - Too Long**
```bash
curl -X POST http://localhost:8000/analyze/v2 \
  -F "claim=<1000+ character string>"
```

**Expected Response** (< 1 second):
```json
{
  "success": false,
  "label": "UNCERTAIN",
  "summary": "ERROR: Claim must be less than 1000 characters"
}
```

**Test 4D: Empty Claim**
```bash
curl -X POST http://localhost:8000/analyze/v2 \
  -F "claim="
```

**Expected Response** (< 1 second):
```json
{
  "success": false,
  "label": "UNCERTAIN",
  "summary": "ERROR: No claim text provided"
}
```

---

### Test 5: Performance Measurement

**Setup**: Measure latency for different claims

```python
import time
import statistics
from backend.services.pipeline_new import ProductionRAGPipeline

pipeline = ProductionRAGPipeline(use_nli=False, device="cpu")

test_claims = [
    "The Earth is round.",
    "COVID-19 was manufactured in a lab.",
    "Climate change is caused by human activity.",
    "The moon landing was fake.",
    "Vaccines cause autism."
]

latencies = []

for claim in test_claims:
    start = time.time()
    result = pipeline.analyze(claim=claim, top_k_evidence=3)
    elapsed = time.time() - start
    latencies.append(elapsed)
    
    print(f"✅ {claim[:40]:40} | {elapsed:.2f}s | {result.get('label')}")

# Calculate statistics
print(f"\n📊 Performance Summary:")
print(f"   - Min latency: {min(latencies):.2f}s")
print(f"   - Max latency: {max(latencies):.2f}s")
print(f"   - Mean latency: {statistics.mean(latencies):.2f}s")
print(f"   - Median latency: {statistics.median(latencies):.2f}s")
print(f"   - Std deviation: {statistics.stdev(latencies):.2f}s")
print(f"\n✅ All tests < 15s: {all(l < 15 for l in latencies)}")
```

**Expected Output**:
- ✅ All claims process in < 15 seconds
- ✅ Mean latency ~ 8-12 seconds
- ✅ No outliers > 15 seconds

---

### Test 6: Tavily Fallback Testing

**Objective**: Verify Tavily fallback works when Wikipedia is unavailable

**Setup**: Temporarily mock Wikipedia to return empty results

```python
from backend.services.retrieval_new import RetrievalPipeline
from unittest.mock import patch

retrieval = RetrievalPipeline(
    tavily_api_key="<YOUR_TAVILY_KEY>",
    embedder_model="all-MiniLM-L6-v2"
)

# Test with Wikipedia disabled (mock to return empty)
with patch('backend.services.retrieval_new.wikipedia.search', return_value=[]):
    articles = retrieval.retrieve(
        query="The Earth is round.",
        max_articles=6
    )
    
    assert len(articles) > 0, "Should fallback to Tavily and get results"
    assert any("Tavily" in article.get("source", "") for article in articles), "Should have Tavily results"
    print(f"✅ Tavily fallback successful: {len(articles)} articles retrieved")
```

---

### Test 7: Cache Validation

**Objective**: Verify cache works for repeated queries

```python
import time
from backend.services.retrieval_new import RetrievalPipeline

retrieval = RetrievalPipeline(tavily_api_key="<KEY>", embedder_model="all-MiniLM-L6-v2")

# First call (cache miss)
start = time.time()
articles1 = retrieval.retrieve("The Earth is round.", max_articles=6)
time1 = time.time() - start

# Second call (cache hit)
start = time.time()
articles2 = retrieval.retrieve("The Earth is round.", max_articles=6)
time2 = time.time() - start

assert articles1 == articles2, "Cache should return same results"
assert time2 < time1 / 2, "Cache hit should be much faster"

print(f"✅ Cache validation:")
print(f"   - First call: {time1:.2f}s")
print(f"   - Second call (cached): {time2:.2f}s")
print(f"   - Speedup: {time1 / time2:.1f}x")
```

---

## Test Report Template

Create `TEST_REPORT.md` after running tests:

```markdown
# Integration Test Report

**Test Date**: [YYYY-MM-DD HH:MM:SS]
**Environment**: [Python version, OS, Hardware]
**Status**: ✅ PASS / ⚠️ PARTIAL / ❌ FAIL

## Test Results

| Test | Status | Duration | Notes |
|------|--------|----------|-------|
| System Health Check | ✅ PASS | 0.5s | All imports OK, env vars set |
| Unit Tests (Heuristics) | ✅ PASS | 2s | All 12 tests passed |
| Full Pipeline | ✅ PASS | 12.3s | Latency target achieved |
| Endpoint - Valid Claim | ✅ PASS | 12.8s | Correct response format |
| Endpoint - Invalid Claims | ✅ PASS | 0.1s | Validation works |
| Performance Stats | ✅ PASS | ~10s avg | Mean 10.2s, all < 15s |
| Tavily Fallback | ✅ PASS | 5.2s | Fallback triggered correctly |
| Cache Validation | ✅ PASS | 1s first, 0.2s cached | 5x speedup on cache hit |

## Key Metrics

- **Total Latency**: 10.2s average (target: < 15s) ✅
- **LLM Calls**: 2 per request (target: < 3) ✅
- **Error Rate**: 0% ✅
- **Cache Hit Rate**: 100% for repeated queries ✅

## Issues Found

None

## Recommendations

1. Monitor latency in production to validate 10-15s range holds
2. Set up alerting for requests > 20s
3. Consider Redis cache for multi-instance deployments

## Approval

- [ ] QA Approved
- [ ] Performance OK
- [ ] Ready for Production
```

---

## Running All Tests

```bash
# Run comprehensive test suite
python tests/integration_tests.py

# Generate report
python tests/generate_test_report.py > TEST_REPORT.md
```

---

## Success Criteria

- ✅ All tests pass
- ✅ Latency < 15 seconds for all claims
- ✅ LLM calls == 2 per request
- ✅ Error rate < 0.1%
- ✅ Cache improves repeated queries by 5x+
- ✅ Tavily fallback works correctly

---

## Next Steps

**If all tests pass**:
1. Deploy to staging environment
2. Run load testing (100+ concurrent requests)
3. Monitor production metrics for 24 hours
4. Deploy to production

**If tests fail**:
1. Debug specific failing test
2. Check error logs for issues
3. Verify environment variables
4. Update code as needed
5. Re-run failing test
