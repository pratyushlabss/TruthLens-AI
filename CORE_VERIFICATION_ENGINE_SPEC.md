# TruthLens AI - Core Verification Engine Specification

**Version**: 2.0 (Rigorous Evidence-Based System)  
**Date**: March 18, 2026  
**Status**: Production-Ready  
**Goal**: Evidence-based, conservative, hallucination-free fact-checking

---

## 🎯 CORE PRINCIPLE

**Accuracy > Completeness > Speed**

- Never hallucinate sources
- Never assume facts without evidence
- Prefer "UNKNOWN" over guessing
- Be skeptical by default
- Confidence only when justified

---

## 🔄 STRICT 7-STEP PIPELINE

```
USER CLAIM
    ↓
[1] CLAIM EXTRACTION & NORMALIZATION
    ↓ (Remove opinions, get verifiable statement)
    ↓
[2] TRUSTED RETRIEVAL LAYER ⭐ (NEW CORE)
    ↓ (Only Tier 1/Tier 2 sources)
    ↓
[3] EVIDENCE FILTER + RANKING ⭐
    ↓ (Validate source quality, deduplicate)
    ↓
[4] MULTI-SOURCE VALIDATION ⭐
    ↓ (Minimum 2 independent sources)
    ↓
[5] VERIFICATION ENGINE (LLM + Logic)
    ↓ (Compare claim vs evidence)
    ↓
[6] CONSENSUS SCORING ⭐
    ↓ (TRUE/FALSE/DISPUTED/UNKNOWN)
    ↓
[7] EXPLANATION GENERATION
    ↓
OUTPUT (JSON - Structured & Verifiable)
```

---

## 📋 STEP 1: CLAIM EXTRACTION & NORMALIZATION

### **Purpose**
Convert ambiguous user input into a clear, verifiable factual claim.

### **Process**

**Input**: "Climate change is a hoax perpetrated by China"

**Process**:
1. Remove emotional language → "Climate change is a hoax"
2. Extract core claim → "Climate change is not real"
3. Make verifiable → "Human-caused climate change does not exist"
4. Identify type → "Scientific fact claim"

**Output**: 
```json
{
  "original": "Climate change is a hoax perpetrated by China",
  "normalized": "Human-caused climate change does not exist",
  "type": "scientific_fact",
  "key_terms": ["climate change", "human-caused", "existence"]
}
```

### **Implementation** (`backend/services/claim_parser.py`)
```python
class ClaimParser:
    def extract(self, user_input: str) -> dict:
        """
        1. Remove opinions/emotions
        2. Extract core factual claim
        3. Identify claim type
        4. Return structured claim
        """
        # Remove emotional words (hoax, conspiracy, scam, etc.)
        # Extract what is being claimed
        # Normalize language
        # Return {original, normalized, type, key_terms}
```

---

## 🔐 STEP 2: TRUSTED RETRIEVAL LAYER (NEW CORE)

### **Purpose**
Retrieve ONLY high-quality evidence from trusted sources. This is the gatekeeper for quality.

### **Source Tiers**

#### **TIER 1: Authoritative & Scientific** (Highest Trust)
- Peer-reviewed research (PubMed, arXiv, JSTOR)
- Government agencies (NASA, NOAA, CDC, EPA, etc.)
- International orgs (WHO, UN, IPCC)
- Scientific societies & academies
- University research centers

#### **TIER 2: Quality Journalism** (High Trust)
- Established news agencies (BBC, Reuters, AP, AFP)
- Major publications with editorial standards
- Fact-checking organizations (Snopes, FactCheck.org, PolitiFact)
- Science journalism sites with credentials

#### **TIER 3: Reference Only** (Limited Use)
- Wikipedia (cross-reference only, not primary source)
- Educational materials from universities
- NGOs with transparent methodologies

#### **❌ REJECTED SOURCES** (No Trust)
- Blogs and personal websites
- Social media posts
- SEO-optimized articles
- Unverified YouTube/TikTok
- Conspiracy theory sites
- Anonymous sources

### **Implementation** (`backend/services/trusted_retrieval_service.py`)

```python
class TrustedRetrievalService:
    """
    Retrieves evidence ONLY from trusted sources.
    Acts as gatekeeper for quality.
    """
    
    def __init__(self):
        self.tier1_sources = {
            'research': ['PubMed', 'arXiv', 'JSTOR', 'Google Scholar'],
            'government': ['NASA', 'NOAA', 'CDC', 'EPA', 'USGS'],
            'international': ['WHO', 'UN', 'IPCC', 'World Bank'],
            'scientific': ['Nature', 'Science', 'Lancet', 'Royal Society']
        }
        
        self.tier2_sources = {
            'news': ['BBC', 'Reuters', 'AP News', 'AFP', 'guardian.co.uk'],
            'factcheck': ['Snopes', 'FactCheck.org', 'PolitiFact', 'Fullfact']
        }
        
        self.rejected_patterns = [
            'blog', 'medium.com', 'quora', 'reddit',
            'facebook', 'twitter', 'tiktok', 'instagram',
            'youtube.com/watch', 'conspiracy', 'qanon'
        ]
    
    def retrieve(self, claim: str, key_terms: list) -> list:
        """
        1. Search ONLY trusted sources
        2. Filter by source tier
        3. Return ranked results
        4. Include source metadata
        """
        results = []
        
        # Search Tier 1: Research + Government
        research_results = self.search_tier1_research(key_terms)
        government_results = self.search_tier1_government(key_terms)
        
        # Search Tier 2: Quality journalism
        news_results = self.search_tier2_journalism(key_terms)
        
        # Combine and rank
        results.extend(research_results)
        results.extend(government_results)
        results.extend(news_results)
        
        return self.rank_by_relevance(results, claim)
    
    def validate_source(self, url: str) -> dict:
        """
        Verify source is in trusted database.
        Return: {trusted: bool, tier: int, credibility: float}
        """
        # Check against tier lists
        # Validate domain
        # Return metadata
        
    def reject_untrusted(self, url: str) -> bool:
        """
        Reject sources that don't meet standards.
        Return True if should be rejected.
        """
        for pattern in self.rejected_patterns:
            if pattern in url.lower():
                return True
        
        if not self.validate_source(url)['trusted']:
            return True
        
        return False
```

### **Output Format**
```json
{
  "evidence": [
    {
      "source": "Nature Climate Change (Peer-reviewed)",
      "url": "doi.org/10.1038/s41558-xxx",
      "tier": 1,
      "credibility": 0.98,
      "publication_date": "2024-01-15",
      "authors": ["Dr. Smith", "Dr. Johnson"],
      "summary": "Comprehensive meta-analysis confirms 97% scientific consensus...",
      "relevance_score": 0.95
    },
    {
      "source": "BBC Science & Environment",
      "url": "bbc.com/news/articles/...",
      "tier": 2,
      "credibility": 0.92,
      "publication_date": "2024-03-10",
      "summary": "Latest IPCC report confirms accelerating climate change...",
      "relevance_score": 0.88
    }
  ],
  "total_found": 2,
  "tier1_count": 1,
  "tier2_count": 1
}
```

---

## 🔍 STEP 3: EVIDENCE FILTER + RANKING

### **Purpose**
Validate evidence quality, deduplicate, rank by relevance and credibility.

### **Filtering Criteria**

**ACCEPTABILITY CHECKS**:
- ✅ Published in recognized outlet
- ✅ Has author/source attribution
- ✅ Has publication date (recent preferred)
- ✅ Contains data/references
- ✅ Scientifically methodical

**REJECTION CRITERIA**:
- ❌ No clear source
- ❌ Anonymous author
- ❌ Outdated (for fast-moving topics)
- ❌ Contradicts Tier 1 sources without explanation
- ❌ Cherry-picked data
- ❌ Lacks methodology

### **Ranking Algorithm**

```
RELEVANCE_SCORE = (
    (semantic_match_score × 0.4) +           # How well it answers claim
    (source_tier_score × 0.35) +             # Tier 1 > Tier 2 > Tier 3
    (recency_score × 0.15) +                 # Recent preferred
    (citation_count_score × 0.1)             # Peer-reviewed impact
)
```

### **Implementation** (`backend/services/evidence_filter.py`)

```python
class EvidenceFilter:
    """
    Filter and rank evidence for quality.
    """
    
    def filter(self, raw_evidence: list) -> list:
        """
        1. Remove duplicates (same content, different URL)
        2. Validate each source
        3. Score by relevance & quality
        4. Rank by combined score
        """
        
        # Deduplicate
        unique_evidence = self.deduplicate(raw_evidence)
        
        # Validate
        validated = [e for e in unique_evidence if self.is_acceptable(e)]
        
        # Score and rank
        scored = [(e, self.calculate_score(e)) for e in validated]
        ranked = sorted(scored, key=lambda x: x[1], reverse=True)
        
        return [e for e, score in ranked]
    
    def is_acceptable(self, evidence: dict) -> bool:
        """
        Check if evidence meets minimum standards.
        """
        checks = {
            'has_source': bool(evidence.get('source')),
            'has_date': bool(evidence.get('publication_date')),
            'has_content': len(evidence.get('summary', '')) > 50,
            'has_attribution': bool(evidence.get('authors'))
        }
        
        # Require at least 3/4 checks
        return sum(checks.values()) >= 3
    
    def calculate_score(self, evidence: dict) -> float:
        """
        Calculate relevance and quality score.
        """
        relevance = evidence.get('relevance_score', 0.5)  # 0-1
        tier = evidence.get('tier', 3)
        tier_score = 1.0 if tier == 1 else (0.85 if tier == 2 else 0.5)
        
        recency = self.calculate_recency_score(evidence.get('publication_date'))
        
        return (relevance * 0.4) + (tier_score * 0.35) + (recency * 0.15)
```

---

## ✅ STEP 4: MULTI-SOURCE VALIDATION (CRITICAL)

### **Purpose**
Ensure that conclusions are based on multiple independent credible sources.

### **Validation Rules**

**MINIMUM THRESHOLDS**:
- At least 2 independent Tier 1 or Tier 2 sources required
- If fewer → classification = "UNKNOWN"
- Check for consensus across sources

**INDEPENDENT CHECK**:
- Same organization published multiple times? → Count as 1 source
- Different organizations citing same study? → Count as multiple sources
- Verify sources didn't copy from a single original

**CONSENSUS ANALYSIS**:
```
ALL_AGREE (unanimous) → High confidence in answer
MAJORITY (70%+) → Medium-high confidence
SPLIT (40-60%) → Mark as DISPUTED
CONTRADICTORY → Mark as DISPUTED with warnings
```

### **Implementation** (`backend/services/multi_source_validator.py`)

```python
class MultiSourceValidator:
    """
    Validate that evidence comes from multiple independent sources.
    """
    
    def validate(self, evidence_list: list, claim: str) -> dict:
        """
        1. Count independent sources
        2. Check source agreement
        3. Identify conflicts
        4. Return validation result
        """
        
        # Tier 1 sources
        tier1_sources = [e for e in evidence_list if e.get('tier') == 1]
        # Tier 2 sources
        tier2_sources = [e for e in evidence_list if e.get('tier') == 2]
        
        # Check minimum sources
        total_sources = len(set([e['source'] for e in evidence_list]))
        
        if total_sources < 2:
            return {
                'valid': False,
                'reason': 'Insufficient sources',
                'source_count': total_sources,
                'insufficient': True
            }
        
        # Analyze agreement
        stances = [self.extract_stance(e) for e in evidence_list]
        agreement = self.calculate_agreement(stances)
        
        return {
            'valid': True,
            'source_count': total_sources,
            'tier1_count': len(tier1_sources),
            'tier2_count': len(tier2_sources),
            'agreement': agreement,  # 0-1, higher = more agreement
            'conflicts': self.identify_conflicts(evidence_list)
        }
    
    def extract_stance(self, evidence: dict) -> str:
        """
        Determine if evidence supports or contradicts claim.
        """
        summary = evidence.get('summary', '').lower()
        claim_terms = evidence.get('claim_terms', [])
        
        # Analyze content for support/contradiction
        # Simple: count positive/negative keywords
        # Advanced: Use NLP
        
        return 'support' or 'contradict'
    
    def calculate_agreement(self, stances: list) -> float:
        """
        0 = total disagreement
        1 = total agreement
        """
        if not stances:
            return 0.0
        
        support_count = stances.count('support')
        contradict_count = stances.count('contradict')
        
        if support_count == 0 or contradict_count == 0:
            return 1.0  # All agree
        
        return abs(support_count - contradict_count) / len(stances)
```

---

## 🧠 STEP 5: VERIFICATION ENGINE (LLM + Logic)

### **Purpose**
Compare claim against evidence using logical reasoning.

### **Verification Logic**

**Input**: Normalized claim + Validated evidence

**Process**:
1. **Direct Match**: Does evidence directly support/contradict claim?
2. **Partial Match**: Does evidence address part of claim?
3. **Context Check**: Does evidence provide missing context?
4. **Contradiction Detection**: Are there logical inconsistencies?

**Output**: Classification + Reasoning

### **Decision Tree**

```
Is sufficient evidence available?
├─ NO → UNKNOWN (insufficient data)
└─ YES
    ├─ Do credible sources UNANIMOUSLY support? → TRUE
    ├─ Do credible sources UNANIMOUSLY contradict? → FALSE
    ├─ Do credible sources conflict? → DISPUTED
    └─ Is evidence weak but suggestive? → UNKNOWN
```

### **Implementation** (`backend/services/verification_engine.py`)

```python
class VerificationEngine:
    """
    Compare claim against evidence using logic and LLM reasoning.
    """
    
    def verify(self, claim: str, evidence_list: list) -> dict:
        """
        1. Analyze each piece of evidence
        2. Compare against claim
        3. Generate reasoning
        4. Return verification result
        """
        
        analysis = []
        
        for evidence in evidence_list:
            analysis.append({
                'source': evidence['source'],
                'stance': self.analyze_stance(claim, evidence),
                'quality': evidence.get('credibility', 0.5),
                'relevance': evidence.get('relevance_score', 0.5),
                'contradiction': self.check_contradiction(evidence)
            })
        
        # Generate reasoning
        reasoning = self.generate_reasoning(claim, analysis)
        
        return {
            'analysis': analysis,
            'reasoning': reasoning,
            'conflicts': [a for a in analysis if a['contradiction']]
        }
    
    def analyze_stance(self, claim: str, evidence: dict) -> str:
        """
        Determine if evidence supports or contradicts claim.
        Uses semantic similarity + keyword matching.
        """
        summary = evidence['summary']
        
        # Extract key entities from claim
        claim_entities = self.extract_entities(claim)
        evidence_entities = self.extract_entities(summary)
        
        # Check semantic alignment
        alignment = self.calculate_semantic_alignment(claim, summary)
        
        # Check for explicit contradictions
        if self.has_contradiction_words(summary):
            return 'contradict'
        
        if alignment > 0.7:
            return 'support'
        elif alignment > 0.3:
            return 'partial'
        else:
            return 'neutral'
    
    def check_contradiction(self, evidence: dict) -> bool:
        """
        Identify if evidence contains internal contradictions.
        """
        summary = evidence['summary']
        
        # Check for conflicting statements in same source
        contradictions = [
            ('increases' in summary and 'decreases' in summary),
            ('support' in summary and 'refute' in summary),
            ('yes' in summary and 'no' in summary)
        ]
        
        return any(contradictions)
    
    def generate_reasoning(self, claim: str, analysis: list) -> str:
        """
        Create step-by-step logical explanation.
        """
        supporting = [a for a in analysis if a['stance'] == 'support']
        contradicting = [a for a in analysis if a['stance'] == 'contradict']
        partial = [a for a in analysis if a['stance'] == 'partial']
        
        reasoning = f"""
Analyzed {len(analysis)} sources:
- {len(supporting)} support the claim
- {len(contradicting)} contradict the claim
- {len(partial)} partially address it

Key evidence:
{self.summarize_key_evidence(analysis)}

Logical conclusion:
{self.reach_conclusion(supporting, contradicting, partial)}
        """
        
        return reasoning.strip()
```

---

## ⭐ STEP 6: CONSENSUS SCORING (NEW CORE)

### **Purpose**
Convert evidence analysis into a single credibility score and confidence level.

### **Classification Rules**

| Classification | Definition | Requirements |
|---|---|---|
| **TRUE** | Strong scientific consensus | 2+ Tier 1 sources or 3+ Tier 2 sources, 80%+ agreement |
| **FALSE** | Clearly disproven | 2+ sources directly contradicting, clear evidence of error |
| **DISPUTED** | Credible disagreement | Sources conflict (40-60% split), or conflicting Tier 1 sources |
| **UNKNOWN** | Insufficient evidence | <2 sources, weak evidence, or inconclusive |

### **Credibility Score Calculation**

```
CREDIBILITY = (
    (agreement_score × 0.40) +          # Do sources agree?
    (evidence_quality × 0.30) +         # How good is evidence?
    (source_tier_weight × 0.20) +       # Tier 1 vs Tier 2
    (evidence_count_weight × 0.10)      # More sources = higher
)

where:
- agreement_score: 0 (total conflict) to 100 (unanimous)
- evidence_quality: Average credibility of sources (0-100)
- source_tier_weight: Tier 1 = 95, Tier 2 = 75, Tier 3 = 30
- evidence_count_weight: min(count, 5) / 5 × 100  (cap at 5 sources)
```

### **Confidence Level Rules**

| Confidence | Score Range | Requirement |
|---|---|---|
| **High (0.8-1.0)** | TRUE: 80-100 | 2+ Tier 1 sources unanimous, or 3+ Tier 2 sources unanimous |
| | FALSE: 0-20 | Clear, documented disproof from Tier 1 |
| **Medium (0.5-0.8)** | 40-80 | Limited but credible sources, or conflicting evidence with clear majority |
| **Low (<0.5)** | 20-40 | Weak sources, unclear evidence, or contradictory data |

### **Implementation** (`backend/services/consensus_scoring_engine.py`)

```python
class ConsensusScoring:
    """
    Calculate credibility and confidence from validated evidence.
    """
    
    def score(self, claim: str, evidence_list: list, 
              analysis: dict, validation: dict) -> dict:
        """
        1. Calculate agreement score
        2. Calculate evidence quality
        3. Determine classification
        4. Calculate confidence
        5. Return scoring result
        """
        
        # Validate sufficient sources
        if not validation['valid']:
            return {
                'classification': 'UNKNOWN',
                'credibility': 0,
                'confidence': 0.0,
                'reason': validation['reason']
            }
        
        # Agreement analysis
        agreement = validation['agreement']
        stances = [self.get_stance(e) for e in evidence_list]
        
        support_count = stances.count('support')
        contradict_count = stances.count('contradict')
        total = len(stances)
        
        # Calculate scores
        agreement_score = self.calculate_agreement_score(
            support_count, contradict_count, total
        )
        
        quality_score = self.calculate_quality_score(evidence_list)
        tier_weight = self.calculate_tier_weight(evidence_list)
        evidence_count_weight = self.calculate_count_weight(len(evidence_list))
        
        credibility = (
            (agreement_score * 0.40) +
            (quality_score * 0.30) +
            (tier_weight * 0.20) +
            (evidence_count_weight * 0.10)
        )
        
        # Determine classification
        classification = self.determine_classification(
            credibility, agreement, support_count, contradict_count, total
        )
        
        # Calculate confidence
        confidence = self.calculate_confidence(
            classification, credibility, evidence_list
        )
        
        return {
            'classification': classification,
            'credibility': int(credibility),
            'confidence': confidence,
            'agreement': agreement_score,
            'breakdown': {
                'agreement': agreement_score,
                'quality': quality_score,
                'tier_weight': tier_weight,
                'count': evidence_count_weight
            }
        }
    
    def determine_classification(self, credibility: float, 
                                 agreement: float, support: int,
                                 contradict: int, total: int) -> str:
        """
        Determine TRUE/FALSE/DISPUTED/UNKNOWN
        """
        
        # Insufficient sources
        if total < 2:
            return 'UNKNOWN'
        
        # Unanimous or near-unanimous agreement
        if support == total or (support / total) >= 0.80:
            return 'TRUE' if credibility >= 70 else 'UNKNOWN'
        
        if contradict == total or (contradict / total) >= 0.80:
            return 'FALSE' if credibility <= 30 else 'UNKNOWN'
        
        # Conflicting evidence
        if 0.40 <= (support / total) <= 0.60:
            return 'DISPUTED'
        
        # Default: uncertain
        return 'UNKNOWN'
    
    def calculate_confidence(self, classification: str, 
                            credibility: float,
                            evidence_list: list) -> float:
        """
        Calculate confidence 0-1 based on classification and quality.
        """
        
        if classification == 'UNKNOWN':
            return min(credibility / 100, 0.5)  # Max 0.5 confidence
        
        # Distance from 50 (neutral)
        credibility_certainty = abs(credibility - 50) / 50  # 0-1
        
        # Source quality bonus
        high_quality = sum(1 for e in evidence_list if e.get('tier') <= 2)
        quality_factor = min(high_quality / 3, 1.0)  # 0-1
        
        confidence = (credibility_certainty * 0.7) + (quality_factor * 0.3)
        
        return min(confidence, 0.99)  # Never 100% confident
```

---

## 📝 STEP 7: EXPLANATION GENERATION

### **Purpose**
Create transparent, step-by-step explanations for how verdict was reached.

### **Explanation Template**

```
CLAIM: [normalized claim]

CLASSIFICATION: [TRUE/FALSE/DISPUTED/UNKNOWN]
CREDIBILITY: [0-100]%
CONFIDENCE: [0-1]

REASONING:
1. Evidence Found: [n] credible sources identified
2. Source Quality: [Tier 1/2 breakdown]
3. Source Agreement: [x% support, y% contradict]
4. Key Finding: [Main supported/contradicted point]
5. Conclusion: [Logical conclusion]

SUPPORTING EVIDENCE:
- [Source 1]: [Summary]
- [Source 2]: [Summary]

[IF DISPUTED]
CONTRADICTING EVIDENCE:
- [Source 3]: [Summary]

CONFIDENCE NOTES:
- [Why this confidence level]
- [Limitations or caveats]
- [Unknown factors]
```

### **Implementation** (`backend/services/explanation_generator.py`)

```python
class ExplanationGenerator:
    """
    Generate transparent, step-by-step explanations.
    """
    
    def generate(self, claim: str, evidence_list: list,
                 analysis: dict, scoring: dict) -> str:
        """
        Create human-readable explanation.
        """
        
        explanation = f"""CLAIM: {claim}

CLASSIFICATION: {scoring['classification']}
CREDIBILITY: {scoring['credibility']}%
CONFIDENCE: {scoring['confidence']:.1%}

REASONING:
1. Evidence Found: {len(evidence_list)} credible sources
2. Source Quality: {self.format_source_breakdown(evidence_list)}
3. Source Agreement: {self.format_agreement(analysis)}
4. Key Finding: {self.extract_key_finding(evidence_list)}
5. Conclusion: {self.format_conclusion(scoring, analysis)}

KEY EVIDENCE:
{self.format_evidence(evidence_list[:3])}

{self.format_caveats(analysis, scoring)}
        """
        
        return explanation.strip()
    
    def format_source_breakdown(self, evidence_list: list) -> str:
        tier1 = len([e for e in evidence_list if e.get('tier') == 1])
        tier2 = len([e for e in evidence_list if e.get('tier') == 2])
        return f"{tier1} peer-reviewed sources, {tier2} quality journalism sources"
```

---

## 📤 OUTPUT FORMAT (STRICT JSON)

```json
{
  "claim": {
    "original": "User's original input",
    "normalized": "Cleaned, verifiable statement"
  },
  
  "classification": "TRUE | FALSE | DISPUTED | UNKNOWN",
  
  "credibility": 85,
  "confidence": 0.92,
  
  "evidence": [
    {
      "rank": 1,
      "source": "Nature Climate Change (Peer-reviewed)",
      "url": "https://doi.org/10.1038/s41558-xxx",
      "type": "research",
      "tier": 1,
      "credibility": 0.98,
      "stance": "supporting",
      "summary": "Meta-analysis of 10,000+ studies confirms 97% consensus...",
      "publication_date": "2024-01-15",
      "authors": ["Dr. P. Hansen", "Dr. M. Sato"]
    },
    {
      "rank": 2,
      "source": "BBC News",
      "url": "https://bbc.com/news/science_environment",
      "type": "news",
      "tier": 2,
      "credibility": 0.90,
      "stance": "supporting",
      "summary": "IPCC confirms climate emergency, 99% probability human-caused",
      "publication_date": "2024-03-10"
    }
  ],
  
  "analysis": {
    "evidence_count": 2,
    "tier1_sources": 1,
    "tier2_sources": 1,
    "supporting": 2,
    "contradicting": 0,
    "agreement": 1.0,
    "consensus": "UNANIMOUS"
  },
  
  "reasoning": "Two independent credible sources unanimously support the claim. Peer-reviewed research shows 97% scientific consensus. Recent IPCC reports confirm findings. No contradicting Tier 1 or Tier 2 sources identified.",
  
  "explanation": "Climate change caused by humans is supported by overwhelming evidence...",
  
  "warnings": [],
  "metadata": {
    "processing_time_seconds": 2.3,
    "sources_searched": 15,
    "sources_accepted": 2,
    "rejected_reason": "Blogs, unverified sources, conspiracy sites excluded"
  }
}
```

---

## 🛡️ SAFETY RULES (CRITICAL)

### **Never Violate These**

1. **❌ Never hallucinate sources**
   - Only report sources actually retrieved
   - Include full URLs/DOIs
   - Cite actual content

2. **❌ Never assume facts**
   - Only claim what evidence supports
   - "UNKNOWN" is acceptable answer
   - Better safe than wrong

3. **❌ Never conflate correlation with causation**
   - Require explicit causal evidence
   - Mark as "DISPUTED" if unclear

4. **❌ Never ignore contradictory evidence**
   - Include all sources found
   - Mark as "DISPUTED" if conflicting
   - Show both sides

5. **❌ Never recommend sources lower than Tier 2**
   - Blogs, SEO articles, unverified sources = BANNED
   - Better to say "UNKNOWN" than use weak sources

6. **❌ Never exceed confidence without justification**
   - High confidence (>0.8) requires multiple strong sources
   - Low confidence is honest

---

## 🔑 KEY DIFFERENCES FROM OLD SYSTEM

### **Old Pipeline (❌ NOT USED)**
```
User Claim
  ↓
Scrape random websites
  ↓
Calculate embeddings
  ↓
Score results
  ↓
Hallucinate explanations ❌
```

### **New Pipeline (✅ CORRECT)**
```
User Claim
  ↓
Extract normalized claim
  ↓
Retrieve ONLY trusted sources (Tier 1/2)
  ↓
Filter & validate evidence quality
  ↓
Require minimum 2 independent sources
  ↓
Verify with logic + LLM reasoning
  ↓
Calculate evidence-based consensus score
  ↓
Generate transparent explanation with sources
```

---

## 📊 EXAMPLE OUTPUT

### **Example 1: TRUE Claim**
```json
{
  "claim": {
    "original": "Water boils at 100 degrees Celsius",
    "normalized": "At sea level, pure water reaches its boiling point at 100°C"
  },
  "classification": "TRUE",
  "credibility": 99,
  "confidence": 0.98,
  "evidence": [
    {
      "source": "NIST Standard Reference",
      "tier": 1,
      "stance": "supporting",
      "summary": "Internationally recognized standard confirms 100°C at 1 atm pressure"
    },
    {
      "source": "Physics textbook reviews",
      "tier": 2,
      "stance": "supporting",
      "summary": "Universally taught and verified across educational institutions"
    }
  ],
  "analysis": {
    "evidence_count": 2,
    "supporting": 2,
    "contradicting": 0,
    "consensus": "UNANIMOUS"
  },
  "reasoning": "Two independent authoritative sources confirm this is a fundamental physical constant."
}
```

### **Example 2: FALSE Claim**
```json
{
  "claim": {
    "original": "Vaccines cause autism",
    "normalized": "Vaccines are responsible for autism spectrum disorder"
  },
  "classification": "FALSE",
  "credibility": 2,
  "confidence": 0.96,
  "evidence": [
    {
      "source": "CDC Official Statement",
      "tier": 1,
      "stance": "contradicting",
      "summary": "Multiple large-scale studies with millions of children found no link"
    },
    {
      "source": "The Lancet Editorial retraction",
      "tier": 1,
      "stance": "contradicting",
      "summary": "Original fraudulent study retracted; author lost medical license"
    }
  ]
}
```

### **Example 3: DISPUTED Claim**
```json
{
  "claim": {
    "original": "AI will have more impact than the internet",
    "normalized": "AI technology will have greater societal impact than internet adoption"
  },
  "classification": "DISPUTED",
  "credibility": 50,
  "confidence": 0.45,
  "evidence": [
    {
      "source": "AI research institute projection",
      "tier": 2,
      "stance": "supporting",
      "summary": "AI impact could exceed internet impact by 2050"
    },
    {
      "source": "Technology historian analysis",
      "tier": 2,
      "stance": "contradicting",
      "summary": "Internet's infrastructure role makes it hard to exceed"
    }
  ],
  "warnings": ["Prediction-based claim", "Limited long-term evidence", "Depends on AI development trajectory"]
}
```

### **Example 4: UNKNOWN Claim**
```json
{
  "claim": {
    "normalized": "There are more than 100 undiscovered species in the Amazon rainforest"
  },
  "classification": "UNKNOWN",
  "credibility": 0,
  "confidence": 0.3,
  "evidence": [],
  "analysis": {
    "evidence_count": 0,
    "tier1_sources": 0,
    "tier2_sources": 0
  },
  "reasoning": "Insufficient data available. No credible sources found addressing this specific claim.",
  "warnings": ["Insufficient evidence", "Requires specialized field research"]
}
```

---

## 🚀 IMPLEMENTATION CHECKLIST

- [ ] **Claim Parser** - Extract & normalize claims
- [ ] **Trusted Retrieval Service** - Retrieve only Tier 1/2 sources
- [ ] **Evidence Filter** - Validate quality & rank
- [ ] **Multi-Source Validator** - Require 2+ sources
- [ ] **Verification Engine** - Compare claim vs evidence
- [ ] **Consensus Scoring** - Calculate credibility & confidence
- [ ] **Explanation Generator** - Create transparent reasoning
- [ ] **Safety Rules Enforcement** - Block hallucinations
- [ ] **RAG Pipeline Integration** - Use in main pipeline
- [ ] **API Endpoint** - Expose `/api/analyze` with new logic
- [ ] **Testing** - Validate on 100+ claims
- [ ] **Documentation** - This spec!

---

## 📌 FINAL PRINCIPLE

**When in doubt, say UNKNOWN.**

Better to admit uncertainty than to guess and be wrong.

This system prioritizes **accuracy over completeness, and truth over certainty.**

