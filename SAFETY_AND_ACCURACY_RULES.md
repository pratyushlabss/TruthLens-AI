# TruthLens AI - Safety & Accuracy Rules

**Quick Reference Checklist**  
**Purpose**: Prevent hallucinations, false confidence, and incorrect claims  
**Audience**: All developers working on fact-checking pipeline

---

## 🛡️ CORE SAFETY RULES (DO NOT VIOLATE)

### **Rule 1: Never Hallucinate Sources** ✅ CRITICAL

❌ **WRONG**:
```python
{
  "evidence": [
    {
      "source": "Scientific study shows X is true",
      # ❌ NO ACTUAL SOURCE, NO URL
      "summary": "Research demonstrates..."
    }
  ]
}
```

✅ **RIGHT**:
```python
{
  "evidence": [
    {
      "source": "Nature Climate Change: Mann et al. (2024)",
      "url": "https://doi.org/10.1038/s41558-024-xxxxx",
      "authors": ["M.E. Mann", "S. Rahmstorf", "R. Arndt"],
      "publication_date": "2024-01-15",
      "tier": 1,  # Peer-reviewed
      "summary": "Comprehensive analysis confirms 97% scientific consensus..."
    }
  ]
}
```

**Implementation Rule**:
```python
# Every evidence source MUST have:
required_fields = {
    'source': str,          # Name + type (BBC, NIST, etc.)
    'url': str,            # Actual link to source
    'tier': int,           # 1, 2, or 3
    'publication_date': str  # Date published
}

# Reject if any missing:
if not all(e.get(field) for field in required_fields):
    raise ValueError("Cannot include evidence without full attribution")
```

---

### **Rule 2: Never Assume Facts Without Evidence** ✅ CRITICAL

❌ **WRONG**:
```python
classification = 'TRUE'  # Because "I think it's probably true"
confidence = 0.9        # Without checking sources
# ❌ No evidence reviewed, just assumption
```

✅ **RIGHT**:
```python
# First check: Do we have evidence?
if len(evidence) < 2:
    classification = 'UNKNOWN'  # Default to uncertain
    confidence = 0.2
    return {
        'classification': classification,
        'credibility': 0,
        'reason': 'Insufficient independent sources'
    }

# Only assign confidence after reviewing evidence
if all_sources_agree and all_tier1:
    confidence = 0.95  # Only if justified
else if sources_partially_agree:
    confidence = 0.6   # Lower for mixed evidence
```

**Implementation Checklist**:
```python
def can_classify_as_true(evidence_list):
    """Only classify as TRUE if criteria are met."""
    
    # Check 1: Minimum sources
    if len(evidence_list) < 2:
        return False  # NOT ENOUGH DATA
    
    # Check 2: Source quality
    tier1_sources = [e for e in evidence_list if e.get('tier') == 1]
    if not tier1_sources:
        return False  # NO HIGH-QUALITY SOURCES
    
    # Check 3: Agreement
    stances = [e.get('stance') for e in evidence_list]
    if stances.count('support') < len(stances) * 0.8:
        return False  # NOT UNANIMOUS ENOUGH
    
    return True  # ✅ NOW we can classify
```

---

### **Rule 3: Prefer UNKNOWN Over Guessing** ✅ CRITICAL

❌ **WRONG**:
```python
# Evidence is weak, but let's make a guess
if weak_evidence_found:
    classification = 'TRUE'  # ❌ Guessing
    confidence = 0.6         # ❌ Undeserved confidence
```

✅ **RIGHT**:
```python
# When in doubt, UNKNOWN is correct answer
if evidence_quality_is_weak or sources_conflict:
    classification = 'UNKNOWN'  # ✅ Honest answer
    confidence = 0.3            # ✅ Low confidence
    warnings.append('Insufficient reliable evidence')
```

**Decision Tree**:
```
Do we have 2+ independent Tier 1/2 sources?
├─ NO → UNKNOWN (return immediately)
└─ YES
    ├─ Do they unanimously agree? (80%+)
    │  ├─ YES → TRUE or FALSE (with high confidence)
    │  └─ NO → DISPUTED or UNKNOWN (with caveats)
    └─ Check: Can strong minority position change conclusion?
       ├─ YES → Mark DISPUTED
       └─ NO → Assign classification with caveats
```

---

### **Rule 4: Be Skeptical By Default** ✅ CRITICAL

❌ **WRONG**:
```python
# Accept evidence at face value
def evaluate_evidence(source):
    # Just trust whatever the source says
    return source['content_is_true']  # ❌ No verification
```

✅ **RIGHT**:
```python
# Verify evidence passes strict checks
def evaluate_evidence(source):
    """Only trust sources that pass 5+ checks."""
    
    checks = {
        'is_tier1_or_2': source.get('tier') in [1, 2],
        'has_methodology': 'method' in source or 'study' in source,
        'is_recent': check_date_recency(source['date']),
        'has_citations': source.get('citation_count', 0) > 0,
        'not_retracted': not source.get('is_retracted', False)
    }
    
    score = sum(checks.values()) / len(checks)
    
    if score < 0.8:  # Require 4/5 checks
        return False  # Reject this source
    
    return True  # ✅ Source passes
```

---

### **Rule 5: Ignore Low-Trust Sources** ✅ CRITICAL

❌ **WRONG**:
```python
# Include blogs in analysis
sources = [
    'https://random-blog.com/blog-post-123',  # ❌ Blog
    'https://facebook.com/uncle-joe-shares',   # ❌ Social media
    'conspiracy_theory_website.com',            # ❌ Conspiracy
    'credible-research.org'                     # ✅ Only one valid
]

# Use all sources
average_credibility = sum(s.credibility for s in sources) / len(sources)
# ❌ Contaminated by low-quality sources
```

✅ **RIGHT**:
```python
# Filter sources FIRST
def filter_sources(raw_sources):
    """Only keep Tier 1/2 sources."""
    
    rejected = []
    accepted = []
    
    for source in raw_sources:
        if source['url'].includes(['blog', 'reddit', 'twitter', 'facebook']):
            rejected.append(source)  # ❌ Social media
            continue
        
        if source['domain'] not in TRUSTED_DOMAINS:
            rejected.append(source)  # ❌ Unknown site
            continue
        
        if not source.get('publish_date'):
            rejected.append(source)  # ❌ No publication info
            continue
        
        accepted.append(source)  # ✅ Passed checks
    
    return accepted, rejected

# Only analyze accepted sources
sources = filter_sources(raw_sources)[0]

if len(sources) < 2:
    return {
        'classification': 'UNKNOWN',
        'confidence': 0.0,
        'reason': 'Insufficient trusted sources'
    }
```

---

## 🚫 HALLUCINATION PREVENTION

### **Check #1: Source Verification**

```python
def verify_source_exists(source_dict):
    """Ensure source was actually retrieved, not fabricated."""
    
    required = ['source', 'url', 'publication_date', 'summary']
    
    if not all(source_dict.get(k) for k in required):
        raise ValueError(f"Source missing fields: {source_dict}")
    
    # Verify URL is accessible (optional but good practice)
    try:
        response = requests.head(source_dict['url'], timeout=5)
        if response.status_code >= 400:
            raise ValueError(f"URL not accessible: {source_dict['url']}")
    except:
        # If can't verify, mark with warning
        source_dict['WARNING'] = 'URL could not be verified'
    
    return True
```

### **Check #2: Confidence Bounds**

```python
# Confidence can NEVER exceed evidence quality
max_confidence = {
    'UNKNOWN': 0.5,      # Never >50% when uncertain
    'DISPUTED': 0.6,     # Never >60% when conflicting
    'TRUE': 1.0,         # Can be high if unanimous
    'FALSE': 1.0         # Can be high if unanimous
}

for result in results:
    classification = result['classification']
    confidence = result['confidence']
    
    if confidence > max_confidence.get(classification, 0.5):
        raise ValueError(
            f"Confidence {confidence} exceeds limit for {classification}"
        )
```

### **Check #3: Evidence Count Verification**

```python
def verify_evidence_count(classification, evidence_list):
    """Ensure evidence count matches classification."""
    
    required_evidence = {
        'TRUE': 2,      # Min 2 Tier 1/2 sources
        'FALSE': 2,     # Min 2 sources with clear contradiction
        'DISPUTED': 2,  # Min 2 with disagreement
        'UNKNOWN': 0    # Can have zero or weak evidence
    }
    
    needed = required_evidence.get(classification, 2)
    actual = len([e for e in evidence_list if e.get('tier') in [1, 2]])
    
    if actual < needed:
        raise ValueError(
            f"{classification} requires {needed} sources, "
            f"but only {actual} tier 1/2 sources found"
        )
```

---

## ⚠️ WARNING FLAGS (Must Be Added)

### **When to add warnings**:

```python
warnings = []

# Flag 1: Insufficient sources
if len(evidence) < 3:
    warnings.append(
        f"Limited sources ({len(evidence)} found). "
        "Confidence may be lower than ideal."
    )

# Flag 2: Conflicting evidence
if (support_count > 0 and contradict_count > 0):
    warnings.append(
        f"Conflicting sources ({support_count} support, "
        f"{contradict_count} contradict). Marked as DISPUTED."
    )

# Flag 3: Outdated information
if most_recent_date < (now - timedelta(days=365)):
    warnings.append(
        f"Evidence is over 1 year old. May not reflect current status."
    )

# Flag 4: No Tier 1 sources
if len(tier1_sources) == 0:
    warnings.append(
        "No peer-reviewed sources found. "
        "Relying on journalism only."
    )

# Flag 5: Single source (never acceptable)
if len(evidence) == 1:
    warnings.append(
        "⚠️ CRITICAL: Only 1 source found. "
        "This cannot support any classification except UNKNOWN."
    )
    classification = 'UNKNOWN'
    confidence = 0.0

result['warnings'] = warnings
```

---

## 📊 CLASSIFICATION MATRIX (Quick Reference)

| Situation | Classification | Min Confidence | Warnings |
|-----------|---|---|---|
| 2+ sources, unanimous agreement, all Tier 1 | TRUE | 0.80 | None |
| 2+ sources, unanimous disagreement, Tier 1 | FALSE | 0.80 | None |
| Conflicting credible sources | DISPUTED | 0.40 | "Credible disagreement" |
| 0-1 sources | UNKNOWN | 0.0 | "Insufficient evidence" |
| Weak sources only | UNKNOWN | <0.5 | "No trusted sources found" |
| Mixed Tier 2 + Tier 3 | Consider UNKNOWN | <0.6 | "Limited source quality" |
| Future prediction | DISPUTED or UNKNOWN | <0.6 | "Speculative claim" |
| Non-falsifiable | UNKNOWN | 0.0 | "Cannot be verified" |

---

## 🔍 AUDIT CHECKLIST (Before Returning Result)

```python
def validate_result_before_return(result):
    """Final check before sending to user."""
    
    checks = {
        'has_claim': bool(result.get('claim')),
        'has_classification': result.get('classification') in 
                              ['TRUE', 'FALSE', 'DISPUTED', 'UNKNOWN'],
        'credibility_in_range': 0 <= result.get('credibility', 0) <= 100,
        'confidence_in_range': 0 <= result.get('confidence', 0) <= 1,
        'confidence_matches_classification': 
            validate_confidence_bounds(result),
        'has_evidence_if_not_unknown': 
            len(result.get('evidence', [])) > 0 or 
            result['classification'] == 'UNKNOWN',
        'no_hallucinated_sources': 
            all(verify_source(e) for e in result.get('evidence', [])),
        'warnings_present': isinstance(result.get('warnings', []), list),
    }
    
    if not all(checks.values()):
        failed = [k for k, v in checks.items() if not v]
        raise ValueError(f"Result validation failed: {failed}")
    
    return True  # ✅ Safe to return
```

---

## 💡 EXAMPLES OF CORRECT DECISIONS

### **Example 1: Conservative With Insufficient Data**
```python
{
    'claim': 'There are living organisms on Mars',
    'classification': 'UNKNOWN',
    'credibility': 15,  # Low because mostly speculative
    'confidence': 0.25,  # Very low
    'evidence': [
        {
            'source': 'NASA: Mars Rovers',
            'summary': 'No life detected yet, but search is ongoing'
        }
    ],
    'warnings': [
        'No confirmed evidence of life',
        'Ongoing research field',
        'Cannot yet prove absence'
    ]
}
```

### **Example 2: Clear But Multiple-Source-Based**
```python
{
    'claim': 'The earth orbits the sun',
    'classification': 'TRUE',
    'credibility': 99,
    'confidence': 0.99,
    'evidence': [
        {'source': 'NASA', 'tier': 1, 'stance': 'supporting'},
        {'source': 'ESA', 'tier': 1, 'stance': 'supporting'},
        {'source': 'JAXA', 'tier': 1, 'stance': 'supporting'}
    ],
    'warnings': []  # No warnings: strong consensus
}
```

### **Example 3: Disputed With Both Sides Shown**
```python
{
    'claim': 'Artificial intelligence will surpass human intelligence',
    'classification': 'DISPUTED',
    'credibility': 50,
    'confidence': 0.4,
    'evidence': [
        {'source': 'AI researchers projection', 'stance': 'supporting'},
        {'source': 'Skeptical computer scientists', 'stance': 'contradicting'}
    ],
    'warnings': [
        'Future prediction with inherent uncertainty',
        'Expert opinion differs',
        'Different definitions of intelligence'
    ]
}
```

---

## ✅ FINAL VALIDATION BEFORE COMMIT

Before merging code that affects verification:

- [ ] All sources have URLs
- [ ] All sources have dates
- [ ] No blogs/social media in Tier 1/2
- [ ] Confidence ≤ evidence quality
- [ ] UNKNOWN used when appropriate
- [ ] Warnings added for weak evidence
- [ ] Test case coverage >90%
- [ ] No hallucinated examples
- [ ] Peer-reviewed by another engineer

---

**Remember**: Accuracy = Trust = User Value

One hallucinated source = Loss of all credibility.

