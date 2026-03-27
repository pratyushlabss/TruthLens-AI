# AI Evidence Engine - API & Integration Guide

## Quick Start

### 1. Server Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "TruthLens AI",
  "version": "1.0"
}
```

### 2. Analyze Text-Only Claim

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "text=The moon is made of cheese"
```

**Response (key fields):**
```json
{
  "verdict": "FAKE",
  "confidence": 95.0,
  "truth_score": 0.95,
  "explanation_map": {
    "cheese": 0.88,
    "moon": 0.42,
    "made": 0.15
  },
  "top_evidence_sources": [
    {
      "name": "NASA",
      "url": "https://nasa.gov",
      "relevance": 98,
      "supports": "CONFIRMS"
    }
  ],
  "propagation_risk": "HIGH"
}
```

### 3. Analyze Claim with Image

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "text=Trump wins the election" \
  -F "image=@screenshot.jpg"
```

**New Response Field:**
```json
{
  "image_analysis": {
    "caption": "Screenshot showing fabricated news headline",
    "mismatch_score": 0.81,
    "is_suspicious": true
  }
}
```

### 4. Analyze Claim with Session ID

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "text=Water boils at 100 degrees Celsius" \
  -F "session_id=user_session_123"
```

---

## Model Weights & Fusion Logic

The final verdict is computed as:

```
Final Score = (60% × NLP_Score) + (25% × Evidence_Score) + (15% × Propagation_Score)
```

### Weight Breakdown

| Model | Weight | Input | Output |
|-------|--------|-------|--------|
| **RoBERTa** (60%) | 0.60 | Claim text | Classification (REAL/RUMOR/FAKE) |
| **SBERT Evidence** (25%) | 0.25 | Evidence sources | Credibility score (0-100) |
| **Propagation Risk** (15%) | 0.15 | Claim + NLP score | Risk level + score (0-100) |

### Propagation Risk Score Calculation

```python
Base velocity = (nlp_score / 100) * 50
Keyword boost = sensational_keywords_count * 5
Reshare factor = network_multiplier * 20

propagation_score = min(100, 
    base_velocity + keyword_boost + reshare_factor
)

Risk Level:
  - LOW:    < 30
  - MEDIUM: 30-70
  - HIGH:   > 70
```

---

## Explainability Map (SHAP Word Impact)

### What It Shows

Each word's impact on the "FAKE" diagnosis (0-1 scale)

```python
# Example: "The moon is made of cheese"

# Algorithm:
1. Baseline: predict("The moon is made of cheese") = 0.95 (HIGH FAKE)
2. Mask "cheese": predict("The moon is made of [MASK]") = 0.30
3. Impact = |0.95 - 0.30| = 0.65
4. Normalize = 0.65 / max_impact = 0.88 (for "cheese")
```

### Frontend Highlighting Rules

```typescript
if (explanation_map[word] > 0.7) {
  // Highly suspicious words - RED highlight
  highlightWord(word, "red");
} else if (explanation_map[word] > 0.3) {
  // Mildly suspicious - YELLOW highlight
  highlightWord(word, "yellow");
} else {
  // Not suspicious - no highlight
}
```

### Example Response

```json
{
  "explanation_map": {
    "microchips": 0.92,
    "vaccines": 0.45,
    "tracking": 0.88,
    "are": 0.05,
    "in": 0.08
  }
}
```

---

## Top Evidence Sources

Returns top 3 credible sources that support or refute the claim.

### Response Structure

```json
{
  "top_evidence_sources": [
    {
      "name": "World Health Organization",
      "url": "https://who.int/fact-check/...",
      "relevance": 98,
      "supports": "CONFIRMS"
    },
    {
      "name": "Reuters Fact Check",
      "url": "https://reuters.com/fact-check/...",
      "relevance": 94,
      "supports": "CONFIRMS"
    },
    {
      "name": "Snopes",
      "url": "https://snopes.com/article/...",
      "relevance": 87,
      "supports": "CONFIRMS"
    }
  ]
}
```

### Source Types

| Supports | Meaning |
|----------|---------|
| CONFIRMS | Evidence agrees with claim |
| NEUTRAL | Evidence is unrelated |
| CONTRADICTS | Evidence disagrees |

---

## Image Analysis

When image is provided, BLIP generates caption and checks alignment with claim.

### Response Structure

```json
{
  "image_analysis": {
    "caption": "Screenshot of news article with fake headline",
    "mismatch_score": 0.78,
    "is_suspicious": true,
    "analysis": "Image shows: Screenshot... Claim context: ..."
  }
}
```

### Mismatch Score Interpretation

```
0.0-0.3  : Image aligns with claim (low risk)
0.3-0.6  : Image somewhat related (medium risk)
0.6-1.0  : Image contradicts claim (HIGH RISK - manipulated?)
```

---

## Hardware Optimization

### GPU Device Selection

The backend automatically selects optimal device:

```
1. Metal Performance Shaders (MPS) - MacBook Pro M1/M2
2. NVIDIA CUDA - GPU-equipped systems
3. CPU - Fallback (2-3x slower)
```

### Check Detected Device

```bash
# Will log device during first request
tail -f backend.log | grep "Using\|GPU\|MPS"
```

**Expected Log:**
```
✓ Using Metal Performance Shaders (MPS) for Mac GPU acceleration
✓ Using NVIDIA GPU: NVIDIA RTX 3090
✓ Using CPU for inference
```

---

## Lazy Loading Details

Models are NOT loaded at server startup, only on first request.

### First Request Timeline

```
Server startup: 0.5s (instant)
Database init: 1.2s
API ready: 1.7s ← Server starts listening

First /api/analyze request:
  - Download/load RoBERTa: 3-4s
  - Load SBERT: 1-2s
  - Load BLIP: 4-5s
  - First inference: 2-3s
  - Total: 10-15s
  
Second request:
  - Models cached: 1-2s
```

---

## Error Handling

### Image Processing Failures

If image can't be processed, analysis continues without image data:

```json
{
  "image_analysis": {
    "error": "Unsupported image format"
  },
  "verdict": "REAL",  // Still analyzed from text
  "confidence": 85.0
}
```

### Evidence Database Offline

If Pinecone is unavailable, system uses mock evidence:

```json
{
  "top_evidence_sources": [
    {
      "name": "mock_source_1",
      "reliability_note": "defaulting to mock evidence"
    }
  ]
}
```

### GPU Fallback

If MPS/CUDA fails, automatically switches to CPU:

```
Error log: "MPS not available: ..."
Fallback: "✓ Using CPU for inference"
```

---

## Performance Monitoring

### Response Time Benchmarks

```bash
# First request (with model loading)
time curl -X POST http://localhost:8000/api/analyze \
  -F "text=Test claim" \
  -F "image=@image.jpg"
# Expected: 10-15 seconds

# Second request (cached models)
time curl -X POST http://localhost:8000/api/analyze \
  -F "text=Another claim"
# Expected: 1-2 seconds
```

### Memory Usage Check

```bash
# Monitor during inference
top -p $(ps aux | grep "uvicorn\|python" | grep -v grep | awk '{print $2}')

# Expected:
#   RES: 1.1-1.3 GB (models in memory)
#   CPU: 40-80% (during inference)
```

---

## Integration Checklist

- [ ] Backend running: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000`
- [ ] Health check returns 200: `curl http://localhost:8000/health`
- [ ] Models loaded on first request visible in logs
- [ ] GPU device correctly detected (MPS/CUDA/CPU)
- [ ] Test text-only claim analysis
- [ ] Test image + text analysis
- [ ] Verify explanation_map field populated
- [ ] Verify top_evidence_sources field populated
- [ ] Image analysis runs without errors
- [ ] Response includes truth_score (0-1 normalized)
- [ ] Caching works (second request < 2s)
- [ ] Error handling graceful (no crashes)

---

## Common Issues & Solutions

### Issue: "Models not found" error

**Solution:** First request will download models (2GB).
- Ensure internet connection
- Be patient: 10-15 seconds normal
- Check disk space: >2GB free

### Issue: MPS not being used on Mac

**Solution:** Verify PyTorch MPS support:
```bash
python -c "import torch; print(torch.backends.mps.is_built(), torch.backends.mps.is_available())"
# Both should be True
```

### Issue: Image analysis very slow

**Solution:** BLIP is large model (140M params). Expected 4-5s first request.

### Issue: Evidence sources empty

**Solution:** Pinecone not configured. Check API key:
```bash
grep "PINECONE_API_KEY" .env
```

---

## Response Schema Reference

Full `AnalyzeResponse` object fields:

```python
{
    # Original fields (backward compatible)
    "verdict": str,                  # REAL, FAKE, RUMOR
    "confidence": float,             # 0-100
    "scores": dict,                  # {real: %, rumor: %, fake: %}
    "confidence_label": str,         # LOW, MEDIUM, HIGH
    "reasoning": str,                # Human explanation
    "highlighted_text": list,        # Suspicious passages
    "propagation_risk": str,         # LOW, MEDIUM, HIGH
    "propagation_score": float,      # 0-100
    "evidence_score": float,         # 0-100
    "summary": str,                  # Brief summary
    "claims": list,                  # Extracted claims
    "evidence_sources": list,        # All sources
    "sources": list,                 # Formatted sources
    "key_signals": list,             # Important signals
    "model_breakdown": dict,         # Score breakdown
    
    # NEW: Fusion & XAI
    "truth_score": float,            # Normalized 0-1
    "explanation_map": dict,         # {word: impact, ...}
    "top_evidence_sources": list,    # Top 3 sources
    "image_analysis": dict,          # {caption, mismatch_score, ...}
}
```

---

**API Version:** 1.0  
**Last Updated:** 2026-03-17  
**Status:** Production Ready

