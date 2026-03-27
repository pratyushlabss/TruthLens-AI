# TruthLens AI - Core Engine Implementation Guide

**Quick Reference for Developers**  
**Status**: Ready to Implement  
**Target**: Backend RAG Pipeline Refactor

---

## 📋 WHAT TO BUILD

### **New Services to Create**

1. **`backend/services/claim_parser.py`**
   - Normalize user inputs into structured claims
   - Extract key terms and claim type
   - ~200 lines

2. **`backend/services/trusted_retrieval_service.py`**
   - Only retrieve Tier 1 & Tier 2 sources
   - Maintain trusted source database
   - Filter out blogs/social media
   - ~400 lines

3. **`backend/services/evidence_filter.py`**
   - Validate source quality
   - Deduplicate evidence
   - Rank by relevance + credibility
   - ~300 lines

4. **`backend/services/multi_source_validator.py`**
   - Require min 2 independent sources
   - Analyze consensus/disagreement
   - Flag insufficient data → "UNKNOWN"
   - ~250 lines

5. **`backend/services/consensus_scoring_engine.py`**
   - Calculate credibility 0-100
   - Calculate confidence 0-1
   - Determine classification (TRUE/FALSE/DISPUTED/UNKNOWN)
   - ~350 lines

6. **`backend/services/explanation_generator.py`** (Enhanced)
   - Create transparent reasoning
   - Cite all sources
   - Generate human-readable output
   - ~300 lines

---

## 🔧 MODIFICATION TO EXISTING FILES

### **`backend/services/rag_pipeline.py`** (Main Entry Point)

**Current Structure** (update this):
```python
def analyze(self, text: str, include_explanations=True) -> dict:
    # OLD: Direct embedding → scoring
    # NEW: Use 7-step pipeline
    
    # Step 1: Parse claim
    claim_data = self.claim_parser.extract(text)
    
    # Step 2: Retrieve trusted sources
    evidence = self.trusted_retrieval.retrieve(
        claim_data['normalized'],
        claim_data['key_terms']
    )
    
    # Step 3: Filter & rank
    evidence = self.evidence_filter.filter(evidence)
    
    # Step 4: Validate sources
    validation = self.multi_source_validator.validate(
        evidence, 
        claim_data['normalized']
    )
    
    # If <2 sources → return UNKNOWN immediately
    if not validation['valid']:
        return {
            'claim': claim_data['normalized'],
            'classification': 'UNKNOWN',
            'credibility': 0,
            'confidence': 0.0,
            'reason': 'Insufficient credible sources',
            'evidence': []
        }
    
    # Step 5: Verify
    analysis = self.verification_engine.verify(
        claim_data['normalized'],
        evidence
    )
    
    # Step 6: Score
    scoring = self.consensus_scorer.score(
        claim_data['normalized'],
        evidence,
        analysis,
        validation
    )
    
    # Step 7: Explain
    explanation = self.explanation_generator.generate(
        claim_data['normalized'],
        evidence,
        analysis,
        scoring
    ) if include_explanations else ""
    
    return {
        'claim': {
            'original': text,
            'normalized': claim_data['normalized']
        },
        'classification': scoring['classification'],
        'credibility': scoring['credibility'],
        'confidence': scoring['confidence'],
        'evidence': evidence[:5],  # Top 5 sources
        'analysis': {
            'evidence_count': len(evidence),
            'tier1_sources': len([e for e in evidence if e.get('tier')==1]),
            'tier2_sources': len([e for e in evidence if e.get('tier')==2]),
            'supporting': validation.get('supporting', 0),
            'contradicting': validation.get('contradicting', 0),
            'agreement': validation['agreement']
        },
        'reasoning': analysis.get('reasoning', ''),
        'explanation': explanation,
        'warnings': self.generate_warnings(evidence, scoring, validation)
    }
```

---

## 📊 SAMPLE OUTPUTS BY CLASSIFICATION

### **Case 1: TRUE Claim**
```json
{
  "claim": {
    "original": "Water boils at 100 degrees Celsius",
    "normalized": "At sea level (1 atm), pure water reaches boiling point at exactly 100°C"
  },
  "classification": "TRUE",
  "credibility": 99,
  "confidence": 0.98,
  "evidence": [
    {
      "source": "NIST Standard Reference (Tier 1: Official)",
      "tier": 1,
      "stance": "supporting",
      "summary": "Internationally recognized standard defines 100°C as water's boiling point at 1 atm"
    },
    {
      "source": "Physics textbooks (MIT, Cambridge, Oxford)",
      "tier": 2,
      "stance": "supporting",
      "summary": "Universal constant taught in all physics education"
    }
  ],
  "analysis": {
    "evidence_count": 2,
    "tier1_sources": 1,
    "tier2_sources": 1,
    "supporting": 2,
    "contradicting": 0,
    "agreement": 1.0
  },
  "reasoning": "Two independent authoritative sources confirm this fundamental constant.",
  "warnings": []
}
```

### **Case 2: FALSE Claim**
```json
{
  "claim": {
    "normalized": "Vaccines cause autism"
  },
  "classification": "FALSE",
  "credibility": 2,
  "confidence": 0.96,
  "evidence": [
    {
      "source": "CDC: Autism and Vaccines (Tier 1: Government)",
      "tier": 1,
      "stance": "contradicting",
      "summary": "Large-scale studies with millions of children found NO link between vaccines and autism"
    },
    {
      "source": "The Lancet Retraction Notice (Tier 1: Peer-reviewed)",
      "tier": 1,
      "stance": "contradicting",
      "summary": "Original study was fraudulent; author lost medical license; fully retracted 2010"
    },
    {
      "source": "Cochrane Review: Vaccines & Autism (Tier 1: Research)",
      "tier": 1,
      "stance": "contradicting",
      "summary": "Systematic review of 68 epidemiological studies found no causal link"
    }
  ],
  "analysis": {
    "evidence_count": 3,
    "tier1_sources": 3,
    "tier2_sources": 0,
    "supporting": 0,
    "contradicting": 3,
    "agreement": 1.0
  },
  "reasoning": "Three independent Tier 1 sources unanimously contradict the claim. The original fraudulent study has been retracted.",
  "warnings": []
}
```

### **Case 3: DISPUTED Claim**
```json
{
  "claim": {
    "normalized": "Artificial intelligence will have greater societal impact than the internet"
  },
  "classification": "DISPUTED",
  "credibility": 48,
  "confidence": 0.42,
  "evidence": [
    {
      "source": "AI Research Institute projection (Tier 2: Expert analysis)",
      "tier": 2,
      "stance": "supporting",
      "summary": "AI's transformative potential could exceed internet by 2050 based on algorithmic advancement"
    },
    {
      "source": "Technology historian analysis (Tier 2: Quality journalism)",
      "tier": 2,
      "stance": "contradicting",
      "summary": "Internet's infrastructure role and network effects make it harder to exceed"
    }
  ],
  "analysis": {
    "evidence_count": 2,
    "tier1_sources": 0,
    "tier2_sources": 2,
    "supporting": 1,
    "contradicting": 1,
    "agreement": 0.5
  },
  "reasoning": "Two credible but non-peer-reviewed sources disagree. Requires future prediction with inherent uncertainty.",
  "warnings": [
    "Prediction-based claim (inherent uncertainty)",
    "Mixed expert opinion",
    "Long time horizon (25+ years)",
    "No Tier 1 peer-reviewed evidence"
  ]
}
```

### **Case 4: UNKNOWN Claim**
```json
{
  "claim": {
    "normalized": "There are exactly 47 undiscovered species in the Amazon rainforest"
  },
  "classification": "UNKNOWN",
  "credibility": 0,
  "confidence": 0.2,
  "evidence": [],
  "analysis": {
    "evidence_count": 0,
    "tier1_sources": 0,
    "tier2_sources": 0,
    "supporting": 0,
    "contradicting": 0,
    "agreement": 0
  },
  "reasoning": "No credible sources found addressing this specific claim. Requires specialized field research.",
  "warnings": [
    "Insufficient evidence (0 sources)",
    "Requires specialized field research",
    "Cannot verify with available sources",
    "Consider: UNKNOWN is the honest answer"
  ]
}
```

---

## ⚠️ SAFETY CHECKLIST BEFORE DEPLOY

### **Before marking READY for production, verify:**

- [ ] **No hallucinated sources**: Every source in output actually retrieved
- [ ] **No assumed facts**: Only report what evidence shows
- [ ] **Sufficient sources checked**: Always require 2+ independent sources
- [ ] **UNKNOWN is used**: When data is insufficient or unclear
- [ ] **Tier 1 preference**: Only Tier 2+ used for verification
- [ ] **Confidence calibrated**: High-confidence only with multiple strong sources
- [ ] **Warnings included**: Flag weak evidence, conflicts, time-sensitive claims
- [ ] **Reasoning transparent**: User can understand WHY conclusion reached
- [ ] **Conservative scoring**: Never overconfident
- [ ] **Edge cases handled**:
  - [ ] No sources found → UNKNOWN
  - [ ] Sources conflict → DISPUTED
  - [ ] Single weak source → UNKNOWN
  - [ ] Future prediction → Low confidence
  - [ ] Non-falsifiable claim → Note in warnings

---

## 🧪 TESTING STRATEGY

### **Test Dataset (20+ claims)**

**Easy (should be TRUE/FALSE)**:
1. "Water boils at 100°C" → TRUE
2. "Vaccines cause autism" → FALSE
3. "Earth is flat" → FALSE
4. "Gravity exists" → TRUE

**Hard (test DISPUTED/UNKNOWN)**:
5. "AI will be smarter than humans" → DISPUTED/UNKNOWN
6. "Quantum computers will revolutionize medicine" → DISPUTED
7. "There are living organisms on Mars" → UNKNOWN
8. "Eating carrots improves eyesight" → DISPUTED

**Edge Cases**:
9. "The color of my socks" → UNKNOWN (unfalsifiable)
10. "Tomorrow's weather" → UNKNOWN (future prediction)
11. "I am Napoleon" → FALSE (obviously)
12. "COVID-19 originated in Wuhan" → DISPUTED (credible disagreement)

### **Validation Criteria**

```
For each test claim:
✓ Output has all required fields
✓ Classification is conservative
✓ Evidence is all Tier 1/2 (no blogs)
✓ Confidence matches evidence quality
✓ Reasoning explains the decision
✓ Warnings flag weak points
✓ Sources are real (not hallucinated)
✓ No unsupported claims in explanation
```

---

## 📈 PERFORMANCE TARGETS

| Metric | Target |
|--------|--------|
| Accuracy on TRUE claims | >95% |
| Accuracy on FALSE claims | >95% |
| UNKNOWN assignment (insufficient data) | >10% |
| Average confidence when UNKNOWN | <0.5 |
| Hallucination rate | <1% |
| Processing time (5 sources) | <5 seconds |
| Cache hit rate (popular claims) | 30-40% |

---

## 🚀 ROLLOUT PLAN

### **Phase 1: Build** (Week 1-2)
- [ ] Create all 6 new services
- [ ] Update RAG pipeline main.py
- [ ] Unit test each service
- [ ] Integration test pipeline

### **Phase 2: Validate** (Week 2-3)
- [ ] Test on 50 claims
- [ ] Compare with old system
- [ ] Verify no hallucinations
- [ ] Check confidence calibration

### **Phase 3: Deploy** (Week 3)
- [ ] Gradual rollout (10% → 50% → 100%)
- [ ] Monitor error rates
- [ ] Gather user feedback
- [ ] Fix edge cases

### **Phase 4: Monitor** (Ongoing)
- [ ] Track accuracy metrics
- [ ] Log all claims analyzed
- [ ] Flag low-confidence outputs
- [ ] Continuous improvement

---

## 📞 KEY CONTACTS

For questions on:
- **Architecture**: See `CORE_VERIFICATION_ENGINE_SPEC.md`
- **Code structure**: See `PROJECT_STRUCTURE_COMPLETE.md`
- **Trusted sources**: See `config/trusted_sources.json`
- **Deployment**: See `DEPLOYMENT_GUIDE.md`

---

**Remember**: When in doubt, return UNKNOWN.

Accuracy > Completeness > Speed.

