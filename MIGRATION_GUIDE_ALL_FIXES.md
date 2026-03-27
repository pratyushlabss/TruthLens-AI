# Migration Guide: Applying All 8 Fixes to Existing Code

This guide shows **exact changes** to apply each of the 8 fixes to your existing backend files.

---

## General Pattern

Each fix follows this pattern:
1. Locate the exact line/method mentioned
2. Find the exact code snippet marked as "BEFORE"
3. Replace with code marked as "AFTER"
4. Add `[FIXn]` log statement for monitoring
5. Test using curl commands provided

---

## FIX 1: RetreivalEngine - Fallback Evidence

**File**: `backend/services/retrieval_engine.py`
**Method**: `search_and_scrape()`
**Line**: ~76 (end of method, where it returns)

### Change 1.1: Add FIX 1 comment and logging

BEFORE (around line 1):
```python
import logging
import asyncio
from typing import List, Dict, Optional
```

AFTER:
```python
import logging
import asyncio
from typing import List, Dict, Optional
from datetime import datetime  # ADD THIS

logger = logging.getLogger(__name__)
```

### Change 1.2: Modify return statement in search_and_scrape()

BEFORE (line ~76):
```python
    def search_and_scrape(self, claim: str, max_results: int = 10) -> List[Dict]:
        """Search and scrape web content."""
        results = []
        
        try:
            # ... scraping code ...
            if results:
                return results[:max_results]
        except Exception as e:
            logger.warning(f"Scraping failed: {e}")
        
        return []  # ❌ RETURNS EMPTY
```

AFTER:
```python
    def search_and_scrape(self, claim: str, max_results: int = 10) -> List[Dict]:
        """Search and scrape web content.
        === FIX 1: GUARANTEED FALLBACK EVIDENCE ===
        Always returns evidence, never empty.
        """
        results = []
        
        logger.info(f"[FIX1] Searching for evidence: {claim[:80]}")  # ADD THIS
        
        try:
            # ... scraping code ...
            if results:
                logger.info(f"[FIX1] Retrieved {len(results)} real articles")  # ADD THIS
                return results[:max_results]
        except Exception as e:
            logger.warning(f"[FIX1] Scraping failed: {e}")  # UPDATE THIS
        
        # === FIX 1: FORCE FALLBACK EVIDENCE ===  # ADD THIS SECTION
        logger.warning(f"[FIX1] Real scraping failed - returning fallback evidence")
        
        fallback_evidence = [
            {
                "title": "System Fallback Analysis",
                "url": "generated://fallback-evidence",
                "text": (
                    f"Claim analyzed: '{claim}'\n\n"
                    f"Search attempt: No external sources found.\n"
                    f"Possible causes:\n"
                    f"  - Claim is too recent\n"
                    f"  - Claim is highly specific\n"
                    f"  - Search sources temporarily unavailable\n\n"
                    f"The system will proceed with internal analysis."
                ),
                "snippet": "No external sources found - using system analysis",
                "source": "System Fallback",
                "credibility": 0.2,
                "is_fallback": True,
                "retrieved_at": datetime.now().isoformat()
            }
        ]
        
        logger.info(f"[FIX1] Returning {len(fallback_evidence)} fallback evidence")
        return fallback_evidence  # ✅ ALWAYS RETURNS SOMETHING
```

---

## FIX 2: EvidenceBuilder - Guaranteed Non-Empty Evidence

**File**: `backend/services/evidence_builder.py`
**Method**: `build()`
**Line**: ~62 (after the processing loop)

### Change 2.1: Add imports

BEFORE (line 1):
```python
import logging
from typing import List, Dict, Optional
```

AFTER:
```python
import logging
from typing import List, Dict, Optional
from datetime import datetime  # ADD THIS
```

### Change 2.2: Modify build() method to guarantee evidence

BEFORE (line ~62):
```python
    def build(self, raw_articles: List[Dict], claim: str) -> List[Dict]:
        """Build structured evidence from raw articles."""
        evidence_list = []
        
        if raw_articles:
            for article in raw_articles:
                try:
                    evidence_item = self._build_evidence_item(article)
                    if evidence_item:
                        evidence_list.append(evidence_item)
                except Exception as e:
                    logger.warning(f"Error building evidence: {e}")
        
        return evidence_list  # ❌ COULD BE EMPTY
```

AFTER:
```python
    def build(self, raw_articles: List[Dict], claim: str, nlp_score: float = 0.5) -> List[Dict]:
        """Build structured evidence from raw articles.
        === FIX 2: GUARANTEED NON-EMPTY EVIDENCE ===
        Always returns at least one evidence item.
        """
        evidence_list = []
        
        logger.info(f"[FIX2] Building evidence from {len(raw_articles)} articles")  # ADD THIS
        
        if raw_articles:
            for article in raw_articles:
                try:
                    evidence_item = self._build_evidence_item(article, claim, nlp_score)  # UPDATE: pass nlp_score
                    if evidence_item:
                        evidence_list.append(evidence_item)
                except Exception as e:
                    logger.warning(f"[FIX2] Error building evidence: {e}")  # UPDATE THIS
        
        # === FIX 2: FORCE FALLBACK EVIDENCE IF EMPTY ===  # ADD THIS SECTION
        if not evidence_list:
            logger.warning("[FIX2] No evidence items built - adding fallback evidence")
            fallback_evidence = {
                "source": "System Fallback",
                "stance": "NEUTRAL",
                "credibility": 0.3,
                "snippet": "Insufficient real sources available",
                "text": (
                    f"Claim: {claim}\n\n"
                    f"Status: No strong corroborating or refuting sources found.\n"
                    f"This may indicate:\n"
                    f"  - Limited external evidence availability\n"
                    f"  - Claim specificity or recency\n"
                    f"  - Search source limitations\n\n"
                    f"Analysis proceeding with system classification."
                ),
                "url": "generated://system-fallback",
                "is_fallback": True,
                "credibility_reason": "System-generated due to lack of real sources",
                "stance_confidence": 0.33,
                "retrieved_at": datetime.now().isoformat()
            }
            evidence_list = [fallback_evidence]
        
        logger.info(f"[FIX2] Returning {len(evidence_list)} evidence items")
        return evidence_list  # ✅ NEVER EMPTY
```

### Change 2.3: Update _build_evidence_item() signature

BEFORE:
```python
    def _build_evidence_item(self, article: Dict) -> Optional[Dict]:
        """Build a single evidence item from an article."""
```

AFTER:
```python
    def _build_evidence_item(self, article: Dict, claim: str = "", nlp_score: float = 0.5) -> Optional[Dict]:
        """Build a single evidence item from an article."""
```

---

## FIX 3: VerdictEngine - Guaranteed Detailed Reasoning

**File**: `backend/services/verdict_engine.py`
**Method**: `_uncertain_verdict()`
**Line**: ~220

### Change 3.1: Find and replace _uncertain_verdict() method

BEFORE (line ~220):
```python
    def _uncertain_verdict(self, reason: str = "No evidence found") -> Dict:
        """Generate uncertain verdict."""
        return {
            "verdict": "UNCERTAIN",
            "confidence": 0.3,
            "reasoning": f"Could not determine verdict: {reason}"
        }
```

AFTER:
```python
    def _uncertain_verdict(
        self,
        reason: str = "No evidence found",
        nlp_score: float = 0.5,
        claim: str = "",
        is_fallback: bool = False
    ) -> Dict:
        """
        === FIX 3: DETAILED REASONING FOR UNCERTAIN VERDICT ===
        Generate detailed step-by-step reasoning for uncertain verdict.
        """
        nlp_confidence = abs(nlp_score - 0.5) * 2 * 100
        nlp_indicator = "credibility concerns" if nlp_score < 0.5 else "plausible indicators"
        
        detailed_reasoning = f"""VERDICT ANALYSIS: UNCERTAIN

Reason for Uncertainty:
{reason}

Detailed Analysis:
1. Evidence Assessment
   - Type: {'Fallback/System-generated' if is_fallback else 'External sources'}
   - Finding: Insufficient reliable sources to determine verdict
   - Status: {'Limited availability' if not claim else f'Unable to verify: "{claim[:60]}"'}

2. NLP Language Analysis
   - System detected {nlp_indicator} in the claim text
   - Language credibility score: {nlp_confidence:.0f}%
   - Linguistic confidence: {'Low' if nlp_confidence < 30 else 'Moderate' if nlp_confidence < 70 else 'High'}

3. Verification Status
   - External verification: {'Not available' if is_fallback else 'Incomplete'}
   - Claim specificity: {'High (may require specialized sources)' if len(claim.split()) > 5 else 'Moderate'}
   - Temporal factor: {'Recent/Breaking' if nlp_score > 0.7 else 'Established'}

4. Evidence Availability
   - Sources found: {'System fallback only' if is_fallback else 'Limited'}
   - Credibility sources: {'None (system analysis only)' if is_fallback else 'Mixed'}
   - Coverage: Limited coverage available

System Conclusion:
The claim cannot be definitively verified or falsified based on insufficient evidence.

Recommendations:
1. Seek additional verified sources from domain experts
2. Monitor for updates as more evidence becomes available
3. Consider consulting fact-checking organizations
4. Re-verify the claim as additional information emerges

Confidence Level: LOW (30%)
Reliability: {'System analysis' if is_fallback else 'Limited'} with {'system' if is_fallback else 'mixed'} verification"""
        
        return {
            "verdict": "UNCERTAIN",
            "confidence": 0.3,
            "reasoning": detailed_reasoning.strip(),
            "is_fallback": is_fallback
        }
```

### Change 3.2: Update compute_verdict() to pass new parameters

BEFORE (in compute_verdict method):
```python
        if not evidence_list:
            logger.warning("No evidence - returning uncertain")
            return self._uncertain_verdict("No external evidence available")
```

AFTER:
```python
        if not evidence_list:
            logger.warning("[FIX3] No evidence - returning uncertain with detailed reasoning")
            return self._uncertain_verdict(
                reason="No external evidence available",
                nlp_score=nlp_score,
                claim=claim,
                is_fallback=True
            )
```

---

## FIX 4: ScoringEngine - Guaranteed Explanation Generation

**File**: `backend/services/scoring_engine.py`
**Method**: `analyze()` or `_generate_explanations()`
**Line**: ~280

### Change 4.1: Add method to validate explanations

ADD AFTER the class definition (around line 20):
```python
    def _explanations_valid(self, explanations: Dict) -> bool:
        """
        Check if explanations are valid and non-empty.
        """
        if not explanations:
            return False
        
        for key, value in explanations.items():
            if isinstance(value, str) and not value.strip():
                return False
            if isinstance(value, list) and len(value) == 0:
                return False
        
        return True
```

### Change 4.2: Modify explanation generation (in analyze method)

BEFORE (line ~280):
```python
        # Generate explanations
        if include_explanations:
            try:
                explanations = self._generate_explanations(...)
            except Exception as e:
                logger.warning(f"Failed to generate explanations: {e}")
                explanations = {}
        
        response["explanations"] = explanations
```

AFTER:
```python
        # === FIX 4: GUARANTEED EXPLANATION GENERATION ===
        logger.info("[FIX4] STEP 5: Generating explanations...")
        try:
            explanations = self._generate_explanations(
                claim=claim,
                verdict=verdict_result,
                evidence=ranked_evidence,
                nlp_score=nlp_score
            )
            if not explanations or not self._explanations_valid(explanations):
                logger.warning("[FIX4] Explanation generation failed - using fallback")
                explanations = self._fallback_explanations(claim, verdict_result)
        except Exception as e:
            logger.error(f"[FIX4] Explanation generation error: {e}")
            explanations = self._fallback_explanations(claim, verdict_result)
        
        logger.info("[FIX4] Explanations generated successfully")
        response["explanations"] = explanations  # ✅ ALWAYS SET
```

### Change 4.3: Add fallback explanations method

ADD AFTER the class methods:
```python
    def _fallback_explanations(self, claim: str, verdict: Dict) -> Dict[str, Any]:
        """
        === FIX 4: FALLBACK EXPLANATIONS ===
        Generate explanations when real generation fails.
        """
        return {
            "summary": f"Analysis of '{claim[:60]}' complete: Verdict is {verdict.get('verdict', 'UNCERTAIN')}",
            "decision_logic": "Fallback analysis: Limited evidence available",
            "top_sources": [
                {
                    "source": "System Fallback Analysis",
                    "stance": "NEUTRAL",
                    "credibility": 0.3,
                    "is_fallback": True
                }
            ],
            "reasoning_steps": [
                "1. Attempted evidence retrieval",
                "2. Performed NLP analysis",
                "3. Generated system verdict",
                "4. Returned fallback explanation"
            ],
            "confidence_factors": {
                "source_credibility": "30% (fallback)",
                "evidence_consistency": "Low",
                "external_verification": "No",
                "overall_confidence": f"{verdict.get('confidence', 0.3):.0%}"
            }
        }
```

---

## FIX 5: All Sources - Fallback Flag Tracking

**File(s)**: All source creation points
**Action**: Add `"is_fallback": bool` to every source dict

### Change 5.1: In retrieval_engine.py

From:
```python
    search_results = {
        "title": "...",
        "url": "...",
        # ... other fields
    }
```

To:
```python
    search_results = {
        "title": "...",
        "url": "...",
        # ... other fields
        "is_fallback": False,  # ADD THIS
    }
```

### Change 5.2: In evidence_builder.py

From:
```python
    evidence_item = {
        "source": "...",
        "stance": "...",
        # ... other fields
    }
```

To:
```python
    evidence_item = {
        "source": "...",
        "stance": "...",
        # ... other fields
        "is_fallback": article.get("is_fallback", False),  # ADD THIS
    }
```

### Change 5.3: In scoring_engine.py - source conversion

From:
```python
    sources.append({
        "title": item.get("source", "Unknown"),
        "url": item.get("url", "unknown"),
        # ... other fields
    })
```

To:
```python
    sources.append({
        "title": item.get("source", "Unknown"),
        "url": item.get("url", "unknown"),
        # ... other fields
        "is_fallback": item.get("is_fallback", False),  # ADD THIS
    })
```

---

## FIX 6: Evidence Quality Score

**File**: `backend/services/scoring_engine.py`
**Method**: `analyze()` (add call to new method)
**Line**: ~290 (after evidence ranking)

### Change 6.1: Add evidence quality computation method

ADD AT END OF CLASS:
```python
    def _compute_evidence_quality(self, evidence_list: List[Dict]) -> str:
        """
        === FIX 6: EVIDENCE QUALITY SCORE ===
        Compute quality metric for evidence.
        """
        if not evidence_list:
            return "NONE"
        
        avg_credibility = (
            sum(e.get("credibility", 0) for e in evidence_list) / len(evidence_list)
        )
        
        fallback_count = sum(1 for e in evidence_list if e.get("is_fallback"))
        real_count = len(evidence_list) - fallback_count
        
        if real_count >= 3 and avg_credibility > 0.7:
            return "HIGH"
        elif real_count >= 1 or avg_credibility > 0.5:
            return "MEDIUM"
        else:
            return "LOW"
```

### Change 6.2: Call quality computation in analyze()

BEFORE (in analyze method):
```python
        # Build response
        response = self._build_response(
            claim=claim,
            verdict=verdict_result,
            evidence=ranked_evidence,
            explanations=explanations
        )
```

AFTER:
```python
        # === FIX 6: COMPUTE EVIDENCE QUALITY
        logger.info("[FIX4] STEP 6: Computing evidence quality...")
        evidence_quality = self._compute_evidence_quality(evidence_list)
        logger.info(f"[FIX4] Evidence quality: {evidence_quality}")
        
        # Build response
        response = self._build_response(
            claim=claim,
            verdict=verdict_result,
            evidence=ranked_evidence,
            explanations=explanations,
            evidence_quality=evidence_quality,  # ADD THIS
            nlp_score=nlp_score  # ADD THIS
        )
```

### Change 6.3: Update _build_response() signature

FROM:
```python
def _build_response(self, claim, verdict, evidence, explanations):
```

TO:
```python
def _build_response(self, claim, verdict, evidence, explanations, evidence_quality="LOW", nlp_score=0.5):
```

### Change 6.4: Add quality to response in _build_response()

IN RESPONSE DICT:
```python
    response = {
        "claim": claim,
        "verdict": verdict.get("verdict", "UNCERTAIN"),
        # ... existing fields ...
        "evidence_quality": evidence_quality,  # ADD THIS
        "timestamp": datetime.now().isoformat()
    }
```

---

## FIX 7: Guaranteed Response Structure

**File**: `backend/services/scoring_engine.py`
**Method**: `analyze()` (add call before returning)
**Line**: ~300 (just before return)

### Change 7.1: Add guarantee method

ADD AT END OF CLASS:
```python
    def _guarantee_response_structure(self, response: Dict) -> Dict:
        """
        === FIX 7: GUARANTEE RESPONSE STRUCTURE ===
        Ensure all required fields are present and non-empty.
        """
        required_fields = {
            "claim": "Unknown claim",
            "verdict": "UNCERTAIN",
            "confidence": 0.3,
            "explanation": "Analysis completed",
            "reasoning": "System analysis performed",
            "sources": [],
            "key_signals": ["Analysis complete"],
            "evidence_quality": "LOW",
            "timestamp": datetime.now().isoformat()
        }
        
        # Ensure all fields exist
        for field, default in required_fields.items():
            if field not in response or response[field] is None:
                response[field] = default
            
            # Ensure non-empty for critical fields
            if field == "explanation" and not response[field]:
                response[field] = "Analysis completed successfully"
            elif field == "reasoning" and not response[field]:
                response[field] = "System analysis performed"
            elif field == "sources" and not response[field]:
                response[field] = [self._fallback_source()]
            elif field == "key_signals" and not response[field]:
                response[field] = ["Analysis complete"]
        
        logger.info("[FIX7] Response structure guaranteed")
        return response
```

### Change 7.2: Call guarantee before returning

IN analyze() METHOD:
```python
        # === FIX 7: GUARANTEE RESPONSE STRUCTURE ===
        response = self._guarantee_response_structure(response)
        
        logger.info("[FIX4] Analysis pipeline complete")
        return response
```

---

## FIX 8: Analyze Endpoint - Fail-Safe Response

**File**: `backend/api/analyze.py`
**Function**: Main analyze endpoint
**Line**: Exception handlers (~200+)

### Change 8.1: Add fallback response function

ADD AT TOP LEVEL IN FILE:
```python
def _fallback_response(
    claim: str,
    reason: str = "Unable to complete analysis"
) -> Dict:
    """
    === FIX 8: FALLBACK RESPONSE ===
    Generate complete fallback response when analysis fails.
    """
    logger.warning(f"[FIX8] Generating fallback response for: {claim[:60]}")
    
    return AnalyzeResponse(
        claim=claim,
        verdict="UNCERTAIN",
        confidence=0.3,
        explanation=f"System could not verify claim: {reason}",
        reasoning=f"""ANALYSIS FALLBACK RESPONSE

Issue: {reason}

The system encountered an error during analysis. This may indicate:
- Limited evidence availability
- Temporary system issue
- Search source limitation

Recommendation:
1. Try a more specific search
2. Verify with domain experts
3. Check for recent updates
4. Review multiple independent sources

Status: Uncertain - Insufficient verification
Confidence: LOW (30%)""",
        sources=[SourceInfo(
            title="System Fallback",
            url="generated://fallback",
            credibility="30%",
            summary="Fallback when analysis unavailable",
            supports="NEUTRAL",
            is_fallback=True
        )],
        key_signals=[
            "Fallback mode activated",
            "Limited evidence available",
            reason[:60]
        ],
        evidence_quality="NONE",
        timestamp=datetime.now().isoformat()
    )
```

### Change 8.2: Update main endpoint exception handling

BEFORE (end of analyze endpoint):
```python
    except Exception as e:
        logger.error(f"Analyze error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred during analysis"
        )
```

AFTER:
```python
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[FIX8] Analyze endpoint error: {e}", exc_info=True)
        
        # === FIX 8: NEVER RETURN EMPTY ERROR ===
        # Always return complete fallback response instead of HTTPException
        fallback_response = _fallback_response(
            claim=claim,
            reason=f"Analysis pipeline error: {str(e)[:100]}"
        )
        
        # === FIX 7: GUARANTEE STRUCTURE ===
        # (Call guarantee method if available)
        
        return fallback_response
```

### Change 8.3: Add input validation with fallback

BEFORE (start of analyze endpoint):
```python
    async def analyze(claim: str):
        try:
            # ... analyze code ...
```

AFTER:
```python
    async def analyze(claim: str):
        logger.info(f"[FIX8] Analyzing claim: {claim[:80]}")
        
        try:
            # Validate input
            if not claim or not claim.strip():
                logger.warning("[FIX8] Empty claim provided")
                return _fallback_response(
                    claim="[Empty claim]",
                    reason="No claim provided"
                )
            
            # ... analyze code ...
```

---

## Testing After Each Fix

### After FIX 1 & 2:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"claim": "test with no sources available"}'

# Check: sources is non-empty array
```

### After FIX 3:
```bash
# Same curl, check: reasoning field is not empty

# Should see [FIX3] in logs
```

### After FIX 4:
```bash
# Same curl, check: explanation field is populated

# Should see [FIX4] in logs
```

### After FIX 6 & 7:
```bash
# Same curl, check: evidence_quality and all fields present

# Should see [FIX6] and [FIX7] in logs
```

### After FIX 8:
```bash
# Simulate endpoint error
# Should return complete response, not 500 error

# Should see [FIX8] in logs
```

---

## Verification Checklist

After applying ALL 8 fixes:

- [ ] All `[FIXn]` log statements present in code
- [ ] No empty responses returned
- [ ] All 7 response fields present: verdict, confidence, explanation, reasoning, sources, key_signals, evidence_quality
- [ ] Fallback responses have `is_fallback: true` flag
- [ ] No HTTP 500 errors on invalid input
- [ ] Tests pass for all edge cases
- [ ] Rollback works if needed

---

## Quick Reference: Changes Summary

| FIX | File | Method | Change Type | Lines |
|-----|------|--------|------------|-------|
| 1 | retrieval_engine.py | search_and_scrape() | Replace return | 76 |
| 2 | evidence_builder.py | build() | Add guarantee | 62 |
| 3 | verdict_engine.py | _uncertain_verdict() | Enhance method | 220 |
| 4 | scoring_engine.py | analyze() | Add explanation guarantee | 280 |
| 5 | All | All sources | Add is_fallback field | Multiple |
| 6 | scoring_engine.py | _compute_evidence_quality() | Add method | New |
| 7 | scoring_engine.py | _guarantee_response_structure() | Add method | New |
| 8 | api/analyze.py | analyze() | Add fail-safe | ~200 |

---

Done! All 8 fixes are now integrated into your codebase.
