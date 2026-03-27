# Strict Fact-Checking API - Quick Reference

## TL;DR

**Your strict fact-checking system is implemented in:**  
📁 `backend/services/strict_fact_checker.py`

**Key Classes:**
- `StrictFactCheckResponse` - Main response builder
- `Verdict` - Enum with TRUE | FALSE | MISLEADING | UNKNOWN
- `CredibilityLevel` - High | Medium | Low

---

## Quick Test

```bash
# Run the test suite (all tests pass ✅)
cd "/Users/pratyush/ai truthlens"
python3 backend/services/strict_fact_checker.py
```

**Output:**
```
STRICT FACT-CHECKING SYSTEM
[TEST 1] Empty Context → UNKNOWN verdict ✓ PASSED
[TEST 2] Sources Contradict → FALSE verdict ✓ PASSED  
[TEST 3] Source Validation (no hallucination) ✓ PASSED
✅ All tests passed!
```

---

## Usage Example

### Scenario: Verify a claim

```python
from backend.services.strict_fact_checker import StrictFactCheckResponse, Verdict

# Step 1: Get retrieved documents from Pinecone/web scraping
retrieved_docs = [
    {
        "url": "https://nasa.gov/moon",
        "title": "NASA - Moon Composition",
        "content": "The moon is made of rock and dust",
        "credibility": "High"
    }
]

# Step 2: Create response
response = StrictFactCheckResponse(
    claim="The moon is made of cheese",
    retrieved_documents=retrieved_docs
)

# Step 3: Analyze evidence
response.add_evidence(
    has_supporting_evidence=False,
    has_contradicting_evidence=True,  # NASA says it's NOT cheese
    evidence_strength=0.95,           # Very strong evidence
    patterns_detected=["Factual inaccuracy", "Popular misconception"]
)

# Step 4: Extract keywords
response.extract_keywords()

# Step 5: Validate (enforces ALL strict rules)
if response.validate_response():
    result = response.to_dict()
    # {
    #   "verdict": "FALSE",
    #   "confidence": 95.0,
    #   "reasoning": "Based on NASA sources...",
    #   "key_signals": ["Factual inaccuracy", "Popular misconception"],
    #   "highlighted_terms": ["moon", "cheese"],
    #   "top_sources": [...],
    #   "source_summary": "All sources refute the claim",
    #   "final_explanation": "This claim is contradicted by credible sources."
    # }
else:
    # Fallback to UNKNOWN if validation fails
    result = StrictFactCheckResponse(claim, []).to_dict()

return result
```

---

## Response Mapping

### Verdict Values (Strict Enum)

```
┌─────────────┬──────────────┬──────────────┐
│  Verdict    │  Confidence  │  When to Use │
├─────────────┼──────────────┼──────────────┤
│ TRUE        │  70-100      │ Claim supported by sources    │
│ FALSE       │  70-100      │ Claim contradicted by sources │
│ MISLEADING  │  40-70       │ Mixed/partial evidence       │
│ UNKNOWN     │  0-40        │ No evidence or weak evidence │
└─────────────┴──────────────┴──────────────┘
```

### Confidence Rules

```python
EMPTY_RETRIEVAL:     confidence = 0          # No sources
SINGLE_SOURCE:       confidence = 60-80      # Limited evidence
MULTIPLE_SOURCES:    confidence = 80-95      # Strong evidence
CONFLICTING_SOURCES: confidence = 40-60      # Mixed evidence
```

---

## Integration Checklist

- [ ] Import in `/api/analyze`:
  ```python
  from backend.services.strict_fact_checker import StrictFactCheckResponse
  ```

- [ ] Modify analyze endpoint:
  ```python
  @router.post("/analyze")
  async def analyze_claim(text: str, ...):
      retrieved_docs = get_evidence_sources(text)  # From Pinecone
      
      response = StrictFactCheckResponse(text, retrieved_docs)
      response.add_evidence(...)
      response.extract_keywords()
      
      if response.validate_response():
          return response.to_dict()
      else:
          return StrictFactCheckResponse(text, []).to_dict()
  ```

- [ ] Update response model:
  ```python
  class AnalyzeResponse(BaseModel):
      verdict: str      # "TRUE" | "FALSE" | "MISLEADING" | "UNKNOWN"
      confidence: float # 0-100
      reasoning: str
      key_signals: List[str]
      highlighted_terms: List[str]
      top_sources: List[Dict]
      source_summary: str
      final_explanation: str
  ```

- [ ] Update frontend:
  ```typescript
  interface AnalysisResult {
    verdict: "TRUE" | "FALSE" | "MISLEADING" | "UNKNOWN";
    confidence: number;
    key_signals: string[];
    final_explanation: string;
  }
  ```

---

## The 5 Strict Rules (Remember!)

| # | Rule | Enforce |
|---|------|---------|
| 1 | Never hallucinate sources | `validate_response()` checks URLs |
| 2 | Empty context = UNKNOWN | Constructor handles this |
| 3 | No confidence if no sources | Always set confidence = 0 |
| 4 | Weak evidence = UNKNOWN | Don't force FALSE verdict |
| 5 | Prefer high-credibility domains | Tag source credibility |

---

## Common Mistakes

❌ **WRONG:**
```python
# Returning FALSE when no sources exist
response = StrictFactCheckResponse("Claim", [])
response.verdict = Verdict.FALSE  # ❌ Should be UNKNOWN!
```

✅ **RIGHT:**
```python
response = StrictFactCheckResponse("Claim", [])
# verdict is ALREADY UNKNOWN by default
assert response.verdict == Verdict.UNKNOWN  # ✓
```

---

❌ **WRONG:**
```python
# Inventing a source
response.top_sources = [{
    "url": "https://made-up-source.com",  # ❌ Not in retrieved_documents!
}]
assert response.validate_response()  # Fails!
```

✅ **RIGHT:**
```python
# Only use URLs from retrieved_documents
response.top_sources = [{
    "url": "https://real-source.com",  # ✓ From retrieved_documents
}]
assert response.validate_response()  # Passes!
```

---

## Testing Commands

```bash
# Run module tests
python3 backend/services/strict_fact_checker.py

# Test with live API (after integration)
curl -X POST http://localhost:8000/api/analyze \
  -F "text=Water boils at 100 degrees"

# Expected response with new format
{
  "verdict": "TRUE",
  "confidence": 95,
  "key_signals": ["Scientifically verified"],
  "highlighted_terms": ["water", "boils"],
  "final_explanation": "This claim is supported by credible sources."
}
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `backend/services/strict_fact_checker.py` | Core implementation |
| `STRICT_FACT_CHECKING_SPEC.md` | Full specification |
| `STRICT_FACT_CHECKING_QUICK_REF.md` | This file |

---

## Next Steps

1. **Today:** Understand the strict rules ✓
2. **Integration:** Import in `/api/analyze` endpoint
3. **Testing:** Run unit tests, verify no hallucination
4. **Frontend:** Update to display new verdict enum
5. **Deployment:** Go live with strict fact-checking

---

## Support

Questions? Check:
1. `STRICT_FACT_CHECKING_SPEC.md` - Full details
2. `strict_fact_checker.py` - Code comments
3. Unit tests in the module - Working examples

**Golden Rule:** When unsure, return `UNKNOWN` - it's honest!
