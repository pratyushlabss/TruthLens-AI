# Integration Guide: Strict Fact-Checking into API

## Goal
Replace current response format with the strict fact-checking format in the `/api/analyze` endpoint.

---

## Current Architecture

```
User Input (text/image/url)
    ↓
/api/analyze endpoint
    ↓
ScoringEngine.analyze()
    ↓
(Returns: verdict, confidence, key_signals, etc.)
    ↓
HTTP Response
    ↓
Frontend Display
```

## New Architecture (With Strict Checking)

```
User Input (text/image/url)
    ↓
/api/analyze endpoint
    ↓
Retrieve Evidence (Pinecone + Web Scraping)
    ↓
StrictFactCheckResponse (NEW!)
    ├─ Analyze evidence
    ├─ Validate responses
    └─ Enforce all strict rules
    ↓
ScoringEngine.analyze() [if still using]
    ↓
HTTP Response (Strict Format)
    ├─ verdict: TRUE | FALSE | MISLEADING | UNKNOWN
    ├─ confidence: 0-100
    ├─ key_signals: [...verified patterns...]
    └─ top_sources: [...with real URLs only...]
    ↓
Frontend Display (Updated)
```

---

## Step-by-Step Integration

### Step 1: Import the Module

**File:** `backend/api/analyze.py`

**Add at top:**
```python
from services.strict_fact_checker import StrictFactCheckResponse, Verdict

# Keep existing imports
from services.scoring_engine import ScoringEngine
from services.analysis_cache import analysis_cache
# ... etc
```

---

### Step 2: Extract Evidence Function

**Add new helper function:**

```python
def get_retrieved_documents(text: str) -> list:
    """
    Retrieve evidence documents from Pinecone + web scraping.
    
    Returns:
        List of dicts with: url, title, content, credibility
    """
    try:
        # Get from Pinecone semantic search
        pinecone_results = search_pinecone(text)
        
        # Get from web scraping
        web_results = scrape_web_evidence(text)
        
        # Combine and format
        all_docs = []
        
        # Add Pinecone results
        for result in pinecone_results:
            all_docs.append({
                "url": result.get("url"),
                "title": result.get("title"),
                "content": result.get("content"),
                "credibility": "High"  # Pinecone sources are pre-vetted
            })
        
        # Add web results
        for result in web_results:
            all_docs.append({
                "url": result.get("url"),
                "title": result.get("title"),
                "content": result.get("content"),
                "credibility": determine_credibility(result.get("domain"))
            })
        
        return all_docs
    
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}")
        return []  # Return empty if retrieval fails


def determine_credibility(domain: str) -> str:
    """Determine source credibility based on domain."""
    high_credibility = [
        "nasa.gov", "noaa.gov", "nih.gov", "cdc.gov",
        "bbc.com", "reuters.com", "apnews.com", "nytimes.com"
    ]
    
    medium_credibility = [
        "wikipedia.org", "medium.com", "substack.com"
    ]
    
    if any(d in domain for d in high_credibility):
        return "High"
    elif any(d in domain for d in medium_credibility):
        return "Medium"
    else:
        return "Low"
```

---

### Step 3: Modify Analyze Endpoint

**Replace the response handling in `/api/analyze`:**

```python
@router.post("/analyze")
async def analyze_claim(
    text: str = Form(...),
    session_id: Optional[str] = Form(None),
    use_cache: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Analyze a claim using strict fact-checking system.
    
    Returns response in strict format (TRUE | FALSE | MISLEADING | UNKNOWN).
    NEVER hallucinated sources. Enforces all strict rules.
    """
    try:
        logger.info(f"Analyzing: {text[:100]}...")
        
        # ────────────────────────────────────────────────────────
        # STEP 1: Retrieve evidence from Pinecone + web
        # ────────────────────────────────────────────────────────
        retrieved_docs = get_retrieved_documents(text)
        
        logger.info(f"Retrieved {len(retrieved_docs)} evidence sources")
        
        # ────────────────────────────────────────────────────────
        # STEP 2: Create strict fact-checking response
        # ────────────────────────────────────────────────────────
        fact_check = StrictFactCheckResponse(text, retrieved_docs)
        
        # ────────────────────────────────────────────────────────
        # STEP 3: Run ScoringEngine for detailed analysis
        # ────────────────────────────────────────────────────────
        scoring_engine = get_scoring_engine()
        engine_result = scoring_engine.analyze(text, include_explanations=True)
        
        # ────────────────────────────────────────────────────────
        # STEP 4: Determine if evidence supports/contradicts claim
        # ────────────────────────────────────────────────────────
        
        # Check for supporting evidence
        supporting_count = 0
        contradicting_count = 0
        
        for doc in retrieved_docs:
            content = doc.get("content", "").lower()
            if any(word in content for word in ["confirm", "verify", "support", "true"]):
                supporting_count += 1
            elif any(word in content for word in ["refute", "contradict", "false", "deny"]):
                contradicting_count += 1
        
        # ────────────────────────────────────────────────────────
        # STEP 5: Build verdict
        # ────────────────────────────────────────────────────────
        
        has_supporting = supporting_count > 0
        has_contradicting = contradicting_count > 0
        evidence_strength = min(
            0.95,
            (len(retrieved_docs) * 0.3 + 
             engine_result.get("confidence", 0) / 100)
        ) if retrieved_docs else 0
        
        fact_check.add_evidence(
            has_supporting_evidence=has_supporting,
            has_contradicting_evidence=has_contradicting,
            evidence_strength=evidence_strength,
            patterns_detected=engine_result.get("key_signals", [])
        )
        
        # ────────────────────────────────────────────────────────
        # STEP 6: Extract keywords
        # ────────────────────────────────────────────────────────
        fact_check.extract_keywords()
        
        # ────────────────────────────────────────────────────────
        # STEP 7: Select top sources (only real ones, no hallucination)
        # ────────────────────────────────────────────────────────
        top_sources = []
        for doc in retrieved_docs[:3]:  # Top 3 sources
            top_sources.append({
                "title": doc.get("title", "Unknown"),
                "url": doc.get("url", ""),
                "credibility": doc.get("credibility", "Low"),
                "evidence": doc.get("content", "")[:200]  # First 200 chars
            })
        
        fact_check.top_sources = top_sources
        
        # ────────────────────────────────────────────────────────
        # STEP 8: Validate (critical!) - enforces all strict rules
        # ────────────────────────────────────────────────────────
        if not fact_check.validate_response():
            logger.warning("Validation failed - returning UNKNOWN")
            # Fallback to UNKNOWN if validation fails
            fact_check = StrictFactCheckResponse(text, [])
        
        # ────────────────────────────────────────────────────────
        # STEP 9: Build final response
        # ────────────────────────────────────────────────────────
        response_data = fact_check.to_dict()
        
        # Add backend-specific fields if needed (optional)
        response_data.update({
            "model_breakdown": engine_result.get("model_breakdown", {}),
            "evidence_sources": engine_result.get("evidence_sources", []),
            "summary": response_data.get("final_explanation"),
        })
        
        # ────────────────────────────────────────────────────────
        # STEP 10: Cache and persist to database
        # ────────────────────────────────────────────────────────
        try:
            analysis_cache.set(text, response_data)
            
            history = ClaimHistory(
                text=text,
                verdict=response_data["verdict"],
                confidence=response_data["confidence"],
                key_signals=response_data.get("key_signals", []),
                reasoning=response_data.get("reasoning", ""),
            )
            db.add(history)
            db.commit()
        except Exception as db_error:
            logger.warning(f"DB save failed: {db_error}")
            db.rollback()
        
        logger.info(f"Analysis complete: {response_data['verdict']} ({response_data['confidence']:.1f}%)")
        
        return response_data
    
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        import traceback
        traceback.print_exc()
        
        # Graceful fallback to UNKNOWN
        return StrictFactCheckResponse(text, []).to_dict()
```

---

### Step 4: Update Response Model

**File:** `backend/api/analyze.py`

**Replace `AnalyzeResponse` class:**

```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AnalyzeResponse(BaseModel):
    """Strict fact-checking response format."""
    
    # Core fields (from StrictFactCheckResponse)
    verdict: str  # "TRUE" | "FALSE" | "MISLEADING" | "UNKNOWN"
    confidence: float  # 0-100
    reasoning: str
    key_signals: List[str]
    highlighted_terms: List[str]
    top_sources: List[Dict[str, Any]]
    source_summary: str
    final_explanation: str
    
    # Optional backend fields
    model_breakdown: Optional[Dict[str, Any]] = None
    evidence_sources: Optional[List] = None
    summary: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "verdict": "FALSE",
                "confidence": 95,
                "reasoning": "3 sources contradict this claim",
                "key_signals": ["Contradicted by NASA", "Unsubstantiated"],
                "highlighted_terms": ["moon", "cheese"],
                "top_sources": [
                    {
                        "title": "NASA - Moon Composition",
                        "url": "https://nasa.gov/moon",
                        "credibility": "High",
                        "evidence": "The moon is made of rock and dust"
                    }
                ],
                "source_summary": "All sources refute the claim",
                "final_explanation": "This claim is contradicted by credible sources."
            }
        }
```

---

### Step 5: Update Frontend Types

**File:** `frontend/types/index.ts`

```typescript
export interface StrictAnalysisResult {
  verdict: "TRUE" | "FALSE" | "MISLEADING" | "UNKNOWN";
  confidence: number;  // 0-100
  reasoning: string;
  key_signals: string[];
  highlighted_terms: string[];
  top_sources: Source[];
  source_summary: string;
  final_explanation: string;
}

export interface Source {
  title: string;
  url: string;
  credibility: "High" | "Medium" | "Low";
  evidence: string;
}
```

---

### Step 6: Update Frontend Display

**File:** `frontend/app/page.tsx`

```typescript
import { StrictAnalysisResult } from "@/types";

// Color mapping for verdicts
const verdictColor = {
  "TRUE": "bg-green-500/20 text-green-200 border-green-500/50",
  "FALSE": "bg-red-500/20 text-red-200 border-red-500/50",
  "MISLEADING": "bg-yellow-500/20 text-yellow-200 border-yellow-500/50",
  "UNKNOWN": "bg-gray-500/20 text-gray-200 border-gray-500/50"
};

export default function Results() {
  const result: StrictAnalysisResult = useResult();
  
  return (
    <div className={`rounded-lg border p-4 ${verdictColor[result.verdict]}`}>
      <h2 className="text-2xl font-bold">{result.verdict}</h2>
      <p className="text-sm">Confidence: {result.confidence}%</p>
      <p className="mt-4">{result.final_explanation}</p>
      
      {/* Key Signals */}
      <div className="mt-4">
        {result.key_signals.map(signal => (
          <span key={signal} className="inline-block mr-2 px-2 py-1 bg-white/10 rounded text-sm">
            {signal}
          </span>
        ))}
      </div>
      
      {/* Top Sources */}
      <div className="mt-6">
        <h3>Sources</h3>
        {result.top_sources.map(source => (
          <div key={source.url} className="mt-2 p-3 bg-white/5 rounded">
            <a href={source.url} target="_blank" className="font-semibold text-blue-400">
              {source.title}
            </a>
            <p className="text-sm text-gray-300">{source.evidence}</p>
            <p className="text-xs mt-1">Credibility: {source.credibility}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Testing the Integration

### Unit Test

```python
# Test the endpoint returns strict format
def test_analyze_endpoint_strict_format():
    from backend.api.analyze import analyze_claim
    
    response = analyze_claim(
        text="Water boils at 100 degrees",
        db=get_test_db()
    )
    
    # Check structure
    assert "verdict" in response
    assert response["verdict"] in ["TRUE", "FALSE", "MISLEADING", "UNKNOWN"]
    assert "confidence" in response
    assert 0 <= response["confidence"] <= 100
    assert "key_signals" in response
    assert isinstance(response["key_signals"], list)
    assert "top_sources" in response
    for source in response["top_sources"]:
        assert "url" in source
        assert source["url"].startswith("https://")
```

### Integration Test

```bash
# Test with live API
curl -X POST http://localhost:8000/api/analyze \
  -F "text=Water boils at 100 degrees" \
  | python3 -m json.tool

# Verify response format
{
  "verdict": "TRUE",
  "confidence": 95,
  "reasoning": "...",
  "key_signals": [...],
  "top_sources": [...],
  "final_explanation": "..."
}
```

---

## Rollout Plan

1. **Phase 1:** Implement strict_fact_checker module ✅ DONE
2. **Phase 2:** Add to `/api/analyze` endpoint (this guide)
3. **Phase 3:** Test thoroughly (unit + integration)
4. **Phase 4:** Update frontend display
5. **Phase 5:** Deploy to production
6. **Phase 6:** Monitor for any issues

---

## Backward Compatibility

If you need to keep old format temporarily:

```python
# Add query parameter to switch formats
@router.post("/analyze")
async def analyze_claim(
    text: str = Form(...),
    use_strict: bool = Form(True),  # NEW parameter
):
    fact_check = StrictFactCheckResponse(text, retrieved_docs)
    fact_check.add_evidence(...)
    
    if use_strict:
        return fact_check.to_dict()  # New format
    else:
        return engine_result  # Old format (deprecated)
```

---

## Files to Modify

| File | Change | Priority |
|------|--------|----------|
| `backend/api/analyze.py` | Add integration code | HIGH |
| `backend/services/strict_fact_checker.py` | Already done ✅ | - |
| `frontend/types/index.ts` | Update interfaces | HIGH |
| `frontend/app/page.tsx` | Update display | HIGH |

---

## Validation Checklist

- [ ] `StrictFactCheckResponse` imported
- [ ] `get_retrieved_documents()` working
- [ ] Endpoint returns strict verdict enum
- [ ] All URLs in `top_sources` are from `retrieved_documents`
- [ ] No hallucinated sources detected
- [ ] Empty retrieval returns UNKNOWN, not FALSE
- [ ] Confidence 0-100 range enforced
- [ ] Frontend displays new verdict values
- [ ] Tests pass (unit + integration)
- [ ] No regressions in existing functionality

---

Done! This guide shows exactly what to change to integrate strict fact-checking.
