"""
TRUTHLENS 15-MODULE SYSTEM - DEPLOYMENT & SETUP GUIDE

Complete installation and configuration for production deployment.
"""

# ============================================================================
# PREREQUISITE PACKAGES
# ============================================================================

"""
Install these packages to enable all 15 modules:

1. CORE DEPENDENCIES (Required)
   - fastapi (API framework)
   - pydantic (Data validation)
   - requests (HTTP client)
   - beautifulsoup4 (HTML parsing)
   - newspaper3k (News extraction)

2. NLI MODULE (Optional but recommended)
   - transformers[torch] (BART MNLI model)
   - torch (PyTorch for model inference)
   - If installing: pip install transformers torch

3. SCRAPING ENHANCEMENTS (Optional)
   - playwright (Browser automation for JS-heavy sites)
   - If installing: pip install playwright
   - Then run: playwright install (downloads chromium)

4. LEARNING MEMORY (Included in Python stdlib)
   - sqlite3 (built-in, no installation needed)

Installation command:
    pip install -r requirements.txt

# Or install full stack:
    pip install fastapi pydantic requests beautifulsoup4 newspaper3k transformers[torch] playwright
    playwright install
"""


# ============================================================================
# SYSTEM INITIALIZATION
# ============================================================================

"""
AUTOMATIC INITIALIZATION
When the API starts:
  1. ScrapingEngine checks for Playwright availability
  2. NLIModel attempts to load BART MNLI
  3. All other modules initialize with error handling
  4. System logs success/failure of each module
  5. Missing modules degrade gracefully

MANUAL INITIALIZATION
In code:
    from backend.services.inference_engine import InferenceEngine
    engine = InferenceEngine()  # All 15 modules initialized
    result = engine.analyze_claim("Your claim here")

If module import fails:
    - InquiryGenerator missing? Uses original claim
    - QueryExpander missing? Uses single query
    - FactExtractor missing? Uses snippets
    - NLIModel missing? Uses pattern matching
    - ReasoningEngine missing? Uses threshold logic
    - LearningMemory missing? Skips memory storage
    - ScrapingEngine missing? Uses snippet text
"""


# ============================================================================
# CONFIGURATION OPTIONS
# ============================================================================

"""
KEY SETTINGS (In inference_engine.py):

1. PIPELINE LIMITS
   - Max articles processed: 15 (line 158 in _extract_facts)
   - Max stances processed: 50 (line 218 in _detect_stances)
   - Top facts returned: 30 (line 242 in _rank_and_filter)
   - Evidence quality sources: 5 (line 296 in analyze_claim)

   To change: Modify the slice [15], [50], [30], [5] in inference_engine.py

2. SCORE THRESHOLDS
   - Verdict threshold: 1.5 (line 335 in _compute_verdict)
   - Confidence multiplier: 1.1 (line 350 in _tune_confidence)
   - Confidence reasoning boost: 1.15 (line 355 in _tune_confidence)

   To adjust: Modify threshold values in _compute_verdict, _tune_confidence

3. SOURCE CREDIBILITY (line 245-259 in _score_source)
   - BBC, Reuters, AP, etc.: 0.95
   - Forbes, Medium, Wired: 0.70
   - Reddit, Twitter, etc.: 0.40
   - Unknown domains: 0.50-0.65

   To customize: Update domain lists in _score_source()

4. RECENCY SCORING (line 261-277 in _calculate_recency)
   - ≤7 days: 1.0
   - ≤30 days: 0.90
   - ≤90 days: 0.75
   - ≤1 year: 0.60
   - >1 year: 0.40

   To adjust: Modify day thresholds in _calculate_recency()

5. LEARNING MEMORY DATABASE
   - Default location: truthlens_memory.db (current directory)
   - To change: Pass db_path to LearningMemory("path/to/db.db")

6. SCRAPING TIMEOUTS
   - Default: 8 seconds per URL
   - To change: Pass timeout parameter to scraper.scrape(url, timeout=15)

7. PLAYWRIGHT HEADLESS MODE
   - Always headless (no browser window)
   - To add visual mode (debugging): Set headless=False in scraping_engine.py line 73
"""


# ============================================================================
# ENVIRONMENT VARIABLES (OPTIONAL)
# ============================================================================

"""
Set these environment variables to customize behavior:

1. TRUTHLENS_MODE
   Default: "production"
   Options: "production", "debug", "test"
   Usage: Controls logging level and error handling

2. TRUTHLENS_MODULES
   Default: all modules enabled
   Options: Comma-separated module names
   Example: TRUTHLENS_MODULES="inquiry_generator,query_expander,reasoning_engine"
   Usage: Disable specific modules for testing

3. TRUTHLENS_MEMORY_DB
   Default: "truthlens_memory.db"
   Usage: Set custom database path for learning memory

4. TRUTHLENS_API_TIMEOUT
   Default: 30 seconds
   Usage: Maximum time for API analysis to complete

5. TRUTHLENS_LOG_LEVEL
   Default: "INFO"
   Options: "DEBUG", "INFO", "WARNING", "ERROR"
   Usage: Control verbosity of system logging

To set environment variables:
    export TRUTHLENS_MODE=production
    export TRUTHLENS_MEMORY_DB=/var/lib/truthlens/memory.db
    python main.py
"""


# ============================================================================
# PERFORMANCE TUNING
# ============================================================================

"""
FOR FASTER ANALYSIS (Sacrifice some accuracy):
1. Reduce max_articles in _extract_facts: 15 → 10
2. Reduce max_facts in fact_extractor: 20 → 10
3. Skip NLI model: Use pattern-based fallback only
4. Disable Playwright: Use BeautifulSoup only
5. Reduce top_facts returned: 30 → 15
6. Increase verdict threshold: 1.5 → 2.0 (more UNCERTAIN)

Estimated speedup: 30-50% faster, -10-20% accuracy

FOR HIGHER ACCURACY (Sacrifice speed):
1. Increase max_articles: 15 → 25
2. Increase max_facts: 20 → 50
3. Use full BART MNLI with higher timeout
4. Enable all scraping methods (Playwright + BeautifulSoup + newspaper3k)
5. Increase analysis confidence threshold: 0.7 → 0.8
6. Add semantic similarity re-ranking step

Estimated slowdown: 2× slower, +10-15% accuracy

MEMORY OPTIMIZATION:
- Batch query limiting: max 5 queries to reduce retrieval size
- Fact deduplication: Remove semantic duplicates
- Streaming: Process articles one-at-a-time instead of loading all
- Caching: Use learning memory to skip repeated analysis

SCALING:
- Worker processes: Use FastAPI with uvicorn workers
  uvicorn main:app --workers 4 --reload
- Load balancing: Deploy multiple TruthLens instances behind nginx
- Database: Move SQLite to PostgreSQL for concurrent access
- Caching layer: Add Redis for query/verdict caching
"""


# ============================================================================
# MONITORING & LOGGING
# ============================================================================

"""
LOGGING STRUCTURE:
Every analysis generates logs with tags:

[PIPELINE] - Main orchestrator (InferenceEngine)
  [PIPELINE-1] Claim understanding
  [PIPELINE-2] Inquiry generation
  [PIPELINE-3] Query expansion
  [PIPELINE-4] Article retrieval
  [PIPELINE-5-6] Scraping & fact extraction
  [PIPELINE-7] NLI stance detection
  [PIPELINE-8-9] Source ranking
  [PIPELINE-10] Standards checking
  [PIPELINE-11] Logical reasoning
  [PIPELINE-12] Verdict computation
  [PIPELINE-13] Confidence tuning
  [PIPELINE-14] Explainability
  [PIPELINE-15] Memory update

[MODULE-NAME] - Individual module operations
  [INQUIRY] - InquiryGenerator
  [QUERY-EXPANSION] - QueryExpander
  [SCRAPER] - ScrapingEngine
  [FACT-EXTRACTION] - FactExtractor
  [NLI] - NLIModel
  [REASONING] - ReasoningEngine
  [LEARNING] - LearningMemory

[ENDPOINT] - API operations
[ERROR-RESPONSE] - Error handling
[RESPONSE] - Response construction

SAMPLE LOG OUTPUT:
===================================
[PIPELINE] 🚀 Starting claim analysis: 'Barack Obama is dead'
[PIPELINE-1] Claim understood: entities=['Barack Obama']
[PIPELINE-2] Generated inquiries: 5 questions
[PIPELINE-3] Expanded to 10 queries
[PIPELINE-4] Retrieved 18 articles
[PIPELINE-5-6] Extracted 280 facts from articles
[PIPELINE-7] Stance detection: 15 non-neutral facts
[PIPELINE-8-9] Ranked 30 facts by credibility & recency
[PIPELINE-10] Standards check: met
[PIPELINE-11] Reasoning result: contradiction detected
[PIPELINE-12] Verdict: FALSE
[PIPELINE-13] Confidence: 92%
[PIPELINE-14] Explanation generated
[PIPELINE-15] Memory updated for future use
[PIPELINE] ✅ Analysis complete
===================================

TO MONITOR IN PRODUCTION:
1. Count [PIPELINE] logs to track analyses
2. Search for errors in logs to diagnose issues
3. Monitor [LEARNING] logs to verify memory operations
4. Track confidence distribution to assess model calibration
5. Count UNCERTAIN verdicts - high count may indicate data quality issues
"""


# ============================================================================
# TESTING CHECKLIST
# ============================================================================

"""
BEFORE PRODUCTION DEPLOYMENT:

Pre-Flight Checks:
  ☐ All 7 new modules present:
    ☐ nli_model.py
    ☐ reasoning_engine.py
    ☐ learning_memory.py
    ☐ scraping_engine.py
    ☐ Updated inquiry_generator.py (if recreated)
    ☐ Updated query_expander.py (if recreated)
    ☐ Updated fact_extractor.py (if recreated)
  
  ☐ InferenceEngine correctly imports all modules
  ☐ analyze_claim() executes without errors
  ☐ All 15 [PIPELINE-N] log messages appear

Module Tests:
  ☐ InquiryGenerator.understand() returns entities
  ☐ QueryExpander.expand() returns 8-10 queries
  ☐ FactExtractor.extract() returns 5+ facts
  ☐ NLIModel.detect_stance() returns stance + confidence
  ☐ ReasoningEngine.reason() returns logic_chain
  ☐ LearningMemory stores and retrieves queries
  ☐ ScrapingEngine scrapes article content

Critical Test Cases:
  ☐ "Barack Obama is dead" → FALSE (recent activity evidence)
  ☐ "The moon is made of cheese" → FALSE (scientific evidence)
  ☐ "The Earth is flat" → FALSE (orbital mechanics)
  ☐ "Claim with no evidence found" → UNCERTAIN
  ☐ "Claim with high support" → TRUE

Error Handling:
  ☐ System continues if QueryExpander fails
  ☐ System continues if NLI model unavailable
  ☐ System continues if Playwright unavailable
  ☐ System continues if memory DB inaccessible
  ☐ API returns valid response even in degraded mode

Performance:
  ☐ Single analysis completes in <30 seconds
  ☐ Memory database doesn't grow unbounded
  ☐ No memory leaks in repeated analyses
  ☐ API stays responsive with 10+ concurrent requests

Production Readiness:
  ☐ Logging configured for production
  ☐ Error responses are user-friendly
  ☐ API rate limiting in place (optional)
  ☐ Database backups scheduled
  ☐ Monitoring/alerting configured
"""


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
ISSUE: "ModuleNotFoundError: No module named 'inference_engine'"
SOLUTION:
  1. Verify file exists: backend/services/inference_engine.py
  2. Ensure sys.path includes backend directory
  3. Check __init__.py files exist in all directories

ISSUE: "Playwright not available"
SOLUTION:
  - System will silently fall back to BeautifulSoup
  - To enable: pip install playwright && playwright install
  - Not required for functionality, just improves JS site support

ISSUE: "BART MNLI model fails to load"
SOLUTION:
  - System automatically uses pattern-based fallback
  - Model is ~1GB, first load takes time
  - If memory-constrained, pattern matching will work fine

ISSUE: "Learning memory database locked"
SOLUTION:
  1. Stop duplicate API instances
  2. Delete truthlens_memory.db.lock if stuck
  3. Move to PostgreSQL for better concurrency

ISSUE: "All claims return UNCERTAIN"
SOLUTION:
  1. Check RetrievalEngine is returning articles
  2. Verify articles have sufficient text content
  3. Adjust verdict threshold in _compute_verdict (may be too high)
  4. Check source credibility scores (may be too low)

ISSUE: "Verdict changes between runs"
SOLUTION:
  - This is expected if articles are dynamic
  - Use use_cache=True to use learning memory
  - Consider caching results in memory for 24hrs

ISSUE: "Memory database grows too large"
SOLUTION:
  1. Implement retention policy (delete >1 year old)
  2. Migrate to SQLite with WAL mode for compression
  3. Archive old data to separate database
  4. Use PostgreSQL for better management
"""


# ============================================================================
# VERSION & CHANGES
# ============================================================================

"""
VERSION: 2.0 (15-Module Reasoning System)

NEW IN 2.0:
  ✅ NLIModel: BART MNLI for stance detection
  ✅ ReasoningEngine: Logical inference rules
  ✅ LearningMemory: SQLite persistent storage
  ✅ ScrapingEngine: Playwright support
  ✅ All 15 modules fully integrated
  ✅ Advanced testing suite
  ✅ Comprehensive documentation

UPGRADE FROM 1.0:
  1. New modules are optional (system still works without)
  2. No breaking API changes
  3. Existing analysis endpoint still works
  4. Learning memory is new feature (no migration needed)

BACKWARDS COMPATIBILITY:
  ✅ analyze_claim() signature unchanged
  ✅ API response format compatible
  ✅ Existing code works without modification
  ✅ Can run old and new systems side-by-side
"""

print(__doc__)
