"""
TRUTHLENS 15-MODULE REASONING SYSTEM - QUICK REFERENCE

A comprehensive guide to the production-grade fact-checking system.
"""

# ============================================================================
# QUICK START - HOW TO USE
# ============================================================================

from backend.services.inference_engine import InferenceEngine

# Initialize engine (creates all 15 modules)
engine = InferenceEngine()

# Analyze a claim (complete 15-step pipeline)
result = engine.analyze_claim("Barack Obama is dead")

# Result contains:
# {
#     'verdict': 'TRUE' or 'FALSE' or 'UNCERTAIN',
#     'confidence': 0.0-1.0 (confidence score),
#     'support_score': float (cumulative support evidence weight),
#     'refute_score': float (cumulative refutation evidence weight),
#     'verdict_facts': {
#         'supporting': int (count of supporting facts),
#         'refuting': int (count of refuting facts)
#     },
#     'reasoning_applied': List[str] (reasoning chain if applicable),
#     'explanation': str (human-readable explanation)
# }


# ============================================================================
# 15-MODULE PIPELINE BREAKDOWN
# ============================================================================

"""
STEP [1-2] CLAIM UNDERSTANDING & INQUIRY GENERATION
Module: InquiryGenerator
Purpose: Convert claim into structured questions for verification
Input: "Barack Obama is dead"
Output:
  - Entities: ['Barack Obama', 'Obama', 'Barack Hussein Obama']
  - Domain: 'person'
  - Inquiries: [
      'Is Barack Obama alive?',
      'When did Barack Obama die?',
      'Is Obama still alive?',
      'Recent news about Obama',
      'Obama alive or dead?'
    ]

STEP [3] ADAPTIVE QUERY EXPANSION
Module: QueryExpander
Purpose: Generate search query variations
Input: Claim + Inquiries
Output: ['Barack Obama dead', 'Obama is alive', 'Obama latest news', ...]
Count: 8-10 queries covering: fact-check, news, research, scientific angles

STEP [4] HYBRID RETRIEVAL
Module: RetrievalEngine (existing)
Purpose: Search web via Tavily API + DuckDuckGo fallback
Input: Expanded queries
Output: 15-20 article objects with: title, url, snippet, text, source

STEP [5-6] SCRAPING & FACT EXTRACTION
Modules: ScrapingEngine (NEW) + FactExtractor
Purpose: Extract meaningful facts from articles
Process:
  1. ScrapingEngine attempts: Playwright → BeautifulSoup → newspaper3k → snippet
  2. FactExtractor splits into sentences, filters fluff (ads, navigation)
  3. Returns: 10-20 meaningful facts per article
Output: List of facts with metadata

STEP [7] NLI STANCE DETECTION
Module: NLIModel (NEW)
Purpose: Classify if each fact supports, refutes, or is neutral to claim
Method: BART MNLI (NLI entailment/contradiction classification)
Fallback: Pattern matching (negation words, positive confirmation words)
Output: Each fact tagged with stance: SUPPORTS | REFUTES | NEUTRAL
Confidence: 0.0-1.0 for each stance

STEP [8-9] SOURCE RANKING & TIME AWARENESS
Module: InferenceEngine._rank_and_filter()
Purpose: Score facts by credibility and recency
Scoring:
  - Source credibility: 0.3-0.95 (BBC=0.95, Reddit=0.40, Unknown=0.50)
  - Recency: 1.0 (≤7 days) → 0.40 (>1 year)
  - Combined: 60% credibility + 40% recency
Output: Top 30 facts ranked by combined score

STEP [10] STANDARD RULES
Module: InferenceEngine._check_standards()
Purpose: Apply threshold rules
Rules:
  - Minimum 2 sources required
  - Minimum evidence score threshold
  - Credibility must exceed 70%
Output: Standards met? True/False

STEP [11] LOGICAL REASONING
Module: ReasoningEngine (NEW)
Purpose: Apply inference rules to detect indirect contradictions
Rules:
  - If claim "X is dead" + recent activity evidence → FALSE
  - If claim "X has disease" + recovery evidence → FALSE
  - If future prediction contradicted by past events → FALSE
  - Check for internal conflicts (one source says yes, another says no)
Output: {
  'inference': str (reasoning explanation),
  'logic_chain': List[str] (step-by-step reasoning),
  'verdict_override': 'TRUE'|'FALSE'|None (if reasoning applies),
  'confidence_adjustment': -0.3 to +0.3 (confidence boost/penalty)
}

STEP [12] VERDICT ENGINE
Module: InferenceEngine._compute_verdict()
Purpose: Produce final verdict (TRUE/FALSE/UNCERTAIN)
Logic:
  1. Calculate support_score = Σ(credibility × stance_confidence) for supporting facts
  2. Calculate refute_score = Σ(credibility × stance_confidence) for refuting facts
  3. If reasoning override exists, use it
  4. Else if refute_score ≥ 1.5 AND refute_score > support_score × 1.2 → FALSE
  5. Else if support_score ≥ 1.5 AND support_score > refute_score × 1.2 → TRUE
  6. Else → UNCERTAIN
Output: Verdict + scores + fact counts

STEP [13] CONFIDENCE TUNING
Module: InferenceEngine._tune_confidence()
Purpose: Calibrate confidence score
Calculation:
  - Base: min(1.0, score_diff / 3.0)
  - Boost if high agreement: × 1.1
  - Further boost if reasoning applied: × 1.15
  - Clamp to [0.0, 1.0]
Output: Confidence 0.0-1.0

STEP [14] EXPLAINABILITY
Module: InferenceEngine._explain_verdict()
Purpose: Generate human-readable explanation
Output includes:
  - Verdict + confidence
  - Fact counts (supporting/refuting)
  - Reasoning chain (if logic applied)
  - Top 3 supporting facts with sources
  - Top 3 refuting facts with sources

STEP [15] LEARNING MEMORY
Module: LearningMemory (NEW)
Purpose: Store for adaptive improvement
Stores:
  - Query pattern + verdict → retrieve for similar future claims
  - Source quality tracking → learn which sources are reliable
  - Verdict history with hash → avoid re-analyzing identical claims
Output: Information stored in SQLite for future use
"""


# ============================================================================
# MODULE DETAILS & ERROR HANDLING
# ============================================================================

"""
MODULE 1: InquiryGenerator
File: services/inquiry_generator.py
Key Methods:
  - understand(claim) → {'entities': [...], 'domain': str, 'patterns': [...]}
  - generate_inquiries(claim, analysis) → List[str] of 3-5 questions
Pattern Detection: mortality, health, political, scientific, biographical
Entity Extraction: Regex-based proper noun detection
Error Handling: Returns empty lists if analysis fails, system continues

MODULE 2: QueryExpander
File: services/query_expander.py
Key Methods:
  - expand(claim, inquiries) → List[str] of 8-10 queries
Variants Generated:
  1. Claim as-is
  2. "{claim} fact check"
  3. "{claim} true or false"
  4. "{entity} latest news"
  5. "{claim} research"
  ... (8-10 total)
Deduplication: Removes case-insensitive duplicates
Error Handling: Returns original claim if expansion fails

MODULE 3: FactExtractor
File: services/fact_extractor.py
Key Methods:
  - extract(text, max_facts=20) → List[str] of meaningful sentences
Filtering Rules:
  - Skip < 30  200
)
  - Remove fluff (click, subscribe, trending)
  - Exclude ads/navigation
  - Remove sentences > 1000 chars
  - Return top 20
Sentence Splitting: Regex-based with proper noun boundary handling
Error Handling: Returns empty list if parsing fails

MODULE 4: NLIModel
File: services/nli_model.py
Key Methods:
  - detect_stance(fact, claim) → {'stance': SUPPORTS|REFUTES|NEUTRAL, 'confidence': float}
Primary Method: BART MNLI (transformers.zero_shot_classification)
Fallback Method: Pattern matching
  - Refutation patterns: "not", "deny", "false", "contradiction"
  - Support patterns: "confirm", "verified", "true", "evidence"
  - semantic overlap analysis
Error Handling: Model loading failure → pattern matching, always returns response

MODULE 5: ReasoningEngine
File: services/reasoning_engine.py
Key Methods:
  - reason(facts, claim, stances) → Complete inference result
Rule Detection:
  1. Direct contradiction (70%+ refuting) → verdict_override='FALSE'
  2. Indirect contradiction → activity evidence vs death claim
  3. Temporal logic → future prediction vs past events
  4. Internal conflict → sources contradict each other
Output Confidence Adjustment: -0.15 to +0.25
Error Handling: Returns fallback reasoning if logic fails

MODULE 6: LearningMemory
File: services/learning_memory.py
Key Methods:
  - store_query(claim, queries, verdict, confidence) → stores in DB
  - retrieve_similar_queries(claim) → finds past analysis
  - update_source_quality(domain, reliable) → updates source scores
  - get_trusted_domains(threshold=0.7) → domains with >70% reliability
Database: SQLite with 3 tables (query_memory, source_quality, verdict_history)
Error Handling: DB errors logged, system continues, memory optional

MODULE 7: ScrapingEngine
File: services/scraping_engine.py
Key Methods:
  - scrape(url) → str (article text)
  - batch_scrape(urls) → dict (URL → text mapping)
Fallback Chain:
  1. Playwright (JS rendering, async) - handles SPAs
  2. BeautifulSoup (HTML parsing) - fast
  3. newspaper3k (news extraction) - optimized
  4. Return empty (graceful failure)
Error Handling: Each method wrapped in try-catch, falls through to next

MODULE 8-15: InferenceEngine (Orchestrator)
File: services/inference_engine.py
Key Method:
  - analyze_claim(claim, use_cache=True) → Complete analysis dict
Full Pipeline Execution:
  - Initialize all 7 modules (graceful if any fail)
  - Execute 15 steps sequentially
  - Log each step with [PIPELINE-N] tags
  - Return complete result with confidence and reasoning
Error Handling: Every module call wrapped in try-catch, falls back to defaults
"""


# ============================================================================
# EXAMPLE ANALYSIS FLOW
# ============================================================================

"""
INPUT: "Barack Obama is dead"

[PIPELINE-1] Claim Understanding
  → Entities: ['Barack Obama', 'Obama']
  → Domain: 'person'
  → Patterns: ['deceased_claim']

[PIPELINE-2] Inquiry Generation
  → 'Is Barack Obama alive?'
  → 'When did Obama die?'
  → 'Obama latest news'
  → 'Recent Obama activity'
  → 'Obama 2024'

[PIPELINE-3] Query Expansion
  → 'Barack Obama dead fact check'
  → 'Is Obama still alive'
  → 'Obama latest news 2024'
  → 'Barack Obama alive'
  → ... (10 queries total)

[PIPELINE-4] Hybrid Retrieval
  → Retrieved 15 articles from Tavily API
  → Plus 5 from DuckDuckGo fallback
  → Total: 20 articles

[PIPELINE-5-6] Scraping & Fact Extraction
  → Scraped 18/20 articles successfully
  → Extracted 280 facts total
  → Example facts:
    * "Obama spoke at the UN in December 2023"
    * "Barack Obama appeared on podcast in January 2024"
    * "Obama released new political book in 2024"

[PIPELINE-7] NLI Stance Detection
  → "Obama spoke at UN" + "Obama is dead" = REFUTES (confidence: 0.95)
  → "Obama has passed away" + "Obama is dead" = SUPPORTS (confidence: 0.85)
  → ... (280 facts classified)

[PIPELINE-8-9] Source Ranking
  → Scored by credibility (BBC=0.95, CNN=0.90, etc.)
  → Scored by recency (recent articles = 1.0, older = 0.60)
  → Combined scores: top 30 facts selected

[PIPELINE-10] Standard Rules
  → Check: ✅ 18+ sources (need 2)
  → Check: ✅ High credibility scores
  → Check: ✅ Standards met

[PIPELINE-11] Logical Reasoning
  → Detected indirect contradiction:
  → Claim: "Obama is dead"
  → Evidence: "Obama spoke at UN in Dec 2023, appeared on podcast Jan 2024"
  → Inference: "Claims death contradicted by recent documented activity"
  → verdict_override = 'FALSE'
  → confidence_adjustment = +0.2

[PIPELINE-12] Verdict Engine
  → support_score: 4.5 (multiple recent activity documenting he's alive)
  → refute_score: 0.1 (no credible sources say he's dead)
  → Reasoning override detected → VERDICT: FALSE

[PIPELINE-13] Confidence Tuning
  → Base: min(1.0, (4.5-0.1)/3.0) = 0.73
  → Agreement boost: high consensus → ×1.1 = 0.80
  → Reasoning boost: logic applied → ×1.15 = 0.92
  → Final: 0.92

[PIPELINE-14] Explainability
  → VERDICT: FALSE (Confidence: 92%)
  → Supporting Facts: 18
  → Refuting Facts: 0
  → Reasoning Chain:
      → "Strong refutation signal detected (100% articles contradict claim)"
      → "Claims person is dead, but recent activity evidence suggests alive"
  → Top Evidence:
      * "Obama spoke at UN in December 2023" (from BBC)
      * "Obama appeared on podcast January 2024" (from CNN)
      * "Obama released new book in 2024" (from NYT)

[PIPELINE-15] Learning Memory
  → Stored: claim="Barack Obama is dead"
  → Verdict: FALSE (confidence: 0.92)
  → Queries used: [list of 10 queries]
  → For future similar claims, system can fast-track analysis

FINAL OUTPUT:
{
  'verdict': 'FALSE',
  'confidence': 0.92,
  'support_score': 4.5,
  'refute_score': 0.1,
  'verdict_facts': {'supporting': 18, 'refuting': 0},
  'reasoning_applied': ['Strong refutation signal...', 'Claims death contradicted...'],
  'explanation': '... (full human-readable text) ...'
}
"""


# ============================================================================
# KEY METRICS & THRESHOLDS
# ============================================================================

"""
THRESHOLDS:
- Verdict threshold: 1.5 (score must be ≥1.5 to trigger TRUE/FALSE, else UNCERTAIN)
- Confidence boost threshold: 20% (if >80% agreement, boost ×1.1)
- High reliability threshold: 0.7 (for trusted domain selection)
- Minimum sources: 2 (standard compliance)
- Score differential: 1.2× (refute must be 1.2× higher than support for FALSE)

SCORING:
- Source credibility: 0.3-0.95
  * High-authority (BBC, Reuters, AP, Guardian, Nature): 0.95
  * Medium (Medium, Forbes, Wired): 0.70
  * Low (Reddit, Twitter, Facebook): 0.40
  * Unknown: 0.50-0.65
- Recency scoring:
  * ≤7 days: 1.0
  * ≤30 days: 0.90
  * ≤90 days: 0.75
  * ≤1 year: 0.60
  * >1 year: 0.40
- Combined score: 60% credibility + 40% recency

CONFIDENCE CALCULATION:
- Base: min(1.0, (|support_score - refute_score|) / 3.0)
- Agreement boost: ×1.1 if >80% agreement
- Reasoning boost: ×1.15 if logic applied
- Final: clamp to [0.0, 1.0]
"""


# ============================================================================
# FAILURE MODES & RECOVERY
# ============================================================================

"""
SCENARIO: InquiryGenerator unavailable
  Fallback: System uses original claim as single query
  Impact: Fewer search variations, broader results
  Recovery: ✅ Analysis continues

SCENARIO: All articles scraped successfully but no content
  Fallback: Use article snippets instead
  Impact: Fewer facts extracted, lower confidence
  Recovery: ✅ Analysis continues with available data

SCENARIO: NLI model download fails (>1GB)
  Fallback: Pattern-based stance detection
  Impact: Lower accuracy but maintains function
  Recovery: ✅ System uses keyword patterns (negation, confirmation)

SCENARIO: Reasoning engine fails
  Fallback: Threshold-based verdict only
  Impact: No indirect contradiction detection
  Recovery: ✅ Still produces verdict from evidence scores

SCENARIO: Learning memory database error
  Fallback: Memory system disabled, analysis continues
  Impact: No learning from past analysis
  Recovery: ✅ Each analysis is independent

SCENARIO: All modules fail (catastrophic)
  Fallback: Return UNCERTAIN verdict with 30% confidence
  Impact: Minimal analysis performed
  Recovery: ✅ API still returns valid response
"""

print(__doc__)
