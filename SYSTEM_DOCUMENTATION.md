# TruthLens AI - System Documentation

## 1. Project Overview
- **What it does**: Verifies textual claims using a Hybrid RAG + LLM reasoning pipeline, returning a clear label, confidence percentage, and evidence-backed explanations.
- **Problem solved**: Prevents misinformation by ranking credible evidence and ignoring weak/noisy sources rather than averaging them.
- **System type**: Hybrid Retrieval-Augmented Generation (RAG) + LLM reasoning engine.

## 2. Architecture Pipeline (Step-by-Step)
1. **Claim Input**: Accepts a user-provided claim.
2. **Claim Understanding (LLM)**: Extracts the main entity, intent, keywords, and claim type.
3. **Query Generation (LLM)**: Generates 3-5 focused Wikipedia queries.
4. **Retrieval (Wikipedia)**: Fetches relevant articles via Wikipedia API/library.
5. **Entity Resolution**: Keeps evidence tied to the same entity.
6. **Evidence Cleaning**: Extracts clean, meaningful sentences and removes noise.
7. **Similarity Scoring**: Embedding similarity between claim and evidence.
8. **Semantic Credibility (LLM)**: LLM rates evidence as factual/neutral/speculative.
9. **Evidence Ranking**: Weighted score combines similarity and semantic credibility.
10. **NLI Relationship**: LLM/NLI determines SUPPORTS/CONTRADICTS/NEUTRAL.
11. **Consistency Check**: Normalized support-vs-contradict balance.
12. **Temporal/Claim Adaptation**: Adjust scoring for temporal, numerical, and opinion claims.
13. **LLM Reasoning Layer**: LLM determines label and reasoning confidence.
14. **Confidence Calculation**: Reasoning-weighted formula + sigmoid calibration.
15. **Final Decision**: Reasoning-first label with evidence fallback.
16. **UI Output**: Structured JSON with label, confidence, key signals, details.

## 3. Each Function Explained

### backend/api/analyze_v2.py
- ` _initialize_pipeline()`
  - Purpose: Initialize and cache the global pipeline instance.
  - Input: None.
  - Output: `ProductionRAGPipeline` instance.
  - Logic: Builds pipeline with Config options and stores it globally.

- `analyze_v2_endpoint()`
  - Purpose: Main API endpoint for analysis.
  - Input: `claim`, optional `session_id`, optional `image`.
  - Output: `AnalyzeV2Response`.
  - Logic: Validates input, runs pipeline, maps results to response schema.

- `analyze_v2_streamlined()`
  - Purpose: Faster endpoint without extra LLM/NLI steps (if wired).
  - Input: `claim`, optional `session_id`.
  - Output: `AnalyzeV2Response`.
  - Logic: Runs streamlined pipeline.

- `_error_response_v2()`
  - Purpose: Construct a safe error response.
  - Input: `claim`, `error_msg`.
  - Output: `AnalyzeV2Response` with error payload.
  - Logic: Builds consistent error response for UI safety.

### backend/services/pipeline_new.py
- `ProductionRAGPipeline.__init__()`
  - Purpose: Initialize retrieval, embeddings, and LLM reasoner.
  - Input: `use_nli`, `embedder_model`, `device`, `top_k_evidence`.
  - Output: Pipeline instance.
  - Logic: Creates RetrievalPipeline, SentenceTransformerEmbedder, LLMReasoner.

- `_stage_query_expansion()`
  - Purpose: Compatibility wrapper for tests.
  - Input: `claim`, `expansion_enabled`.
  - Output: Query list.
  - Logic: Uses `_build_default_queries` when expansion is enabled.

- `_stage_extract_sentences()`
  - Purpose: Compatibility wrapper to extract sentences per article.
  - Input: Articles list.
  - Output: Sentences list + source metadata.
  - Logic: Cleans and extracts with `clean_evidence`.

- `_stage_deduplication()`
  - Purpose: Compatibility wrapper to deduplicate sentences.
  - Input: Sentences list.
  - Output: Unique sentences + indices.
  - Logic: Uses `deduplicate_evidence`.

- `_build_default_queries()`
  - Purpose: Fallback query generation.
  - Input: `claim`, `entity`, `keywords`.
  - Output: List of 3-5 queries.
  - Logic: Generates templated queries and deduplicates.

- `_entity_tokens()`
  - Purpose: Build normalized entity tokens.
  - Input: `entity`, `keywords`.
  - Output: Token list.
  - Logic: Tokenizes entity or falls back to keywords.

- `_title_contains_entity()`
  - Purpose: Title relevance filter.
  - Input: Title, entity tokens.
  - Output: Boolean.
  - Logic: Checks overlap threshold.

- `_sentence_mentions_entity()`
  - Purpose: Evidence entity filter.
  - Input: Sentence, entity tokens.
  - Output: Boolean.
  - Logic: Checks token overlap threshold.

- `_compute_consistency()`
  - Purpose: Agreement scoring.
  - Input: Evidence list.
  - Output: `(consistency, support_ratio, refute_ratio)`.
  - Logic: Uses SUPPORTS vs CONTRADICTS ratio normalized to [0,1].

- `_sigmoid()`
  - Purpose: Calibrate confidence to prevent overconfidence.
  - Input: Raw confidence score.
  - Output: Sigmoid-scaled confidence.
  - Logic: Logistic scaling centered at 0.5.

- `_is_time_sensitive()`
  - Purpose: Detect temporal claims.
  - Input: Claim, claim_category.
  - Output: Boolean.
  - Logic: Checks temporal keywords and category.

- `_extract_year()`
  - Purpose: Extract most recent year from evidence.
  - Input: Evidence sentence.
  - Output: Year or None.
  - Logic: Regex scan for 19xx/20xx.

- `_compute_source_reliability()`
  - Purpose: Source reliability weighting.
  - Input: Evidence sentence, is_lead flag.
  - Output: Float 0.1-0.95.
  - Logic: Boosts intro and references, penalizes controversy.

- `_numeric_match_score()`
  - Purpose: Numeric exact-match scoring.
  - Input: Claim, evidence sentence.
  - Output: Ratio 0-1.
  - Logic: Counts matched numbers.

- `_compute_confidence()`
  - Purpose: Final confidence formula.
  - Input: Evidence scores, consistency, reasoning confidence.
  - Output: Float 0.05-0.99.
  - Logic: Reasoning-weighted formula + boost for strong evidence.

- `_retrieve_articles()`
  - Purpose: Wikipedia retrieval and dedup.
  - Input: Queries, entity tokens, max articles.
  - Output: Article list.
  - Logic: Runs RetrievalPipeline and dedupes by URL.

- `analyze()`
  - Purpose: End-to-end pipeline orchestrator.
  - Input: Claim, top_k_evidence, query_expansion_enabled.
  - Output: Structured analysis dict.
  - Logic: Runs steps 1-15; returns label, evidence, and UI-ready payload.

- `_insufficient_response()`
  - Purpose: Safe UNCERTAIN response for low evidence.
  - Input: Claim, reason, elapsed time.
  - Output: Structured UNCERTAIN response.
  - Logic: Returns zero-confidence safe output.

- `_error_response()`
  - Purpose: Error response wrapper.
  - Input: Claim, error message, elapsed time.
  - Output: Error response dict.
  - Logic: Returns consistent error payload.

- `StreamlineRAGPipeline.__init__()`
  - Purpose: Fast pipeline configuration.
  - Input: `embedder_model`, `device`.
  - Output: Pipeline instance.
  - Logic: Disables optional NLI features.

### backend/services/llm_reasoner.py
- `LLMReasoner.__init__()`
  - Purpose: Configure LLM access and caches.
  - Input: Env vars.
  - Output: Instance with session and caches.
  - Logic: Sets API keys, models, caches.

- `analyze_claim()`
  - Purpose: Extract entity, intent, keywords, type using LLM.
  - Input: Claim string.
  - Output: Dict with fields `main_entity`, `claim_intent`, `keywords`, `claim_type`.
  - Logic: LLM call with fallback heuristics and caching.

- `generate_search_queries()`
  - Purpose: Create 3-5 focused Wikipedia queries.
  - Input: Claim, entity, keywords.
  - Output: Query list.
  - Logic: LLM call with fallback templates and caching.

- `reason_over_evidence()`
  - Purpose: LLM reasoning on evidence list.
  - Input: Claim, evidence list.
  - Output: Dict with `label`, `reasoning`, `reasoning_confidence`.
  - Logic: LLM call and fallback heuristic.

- `_call_llm()`
  - Purpose: Route to OpenAI/HF or fallback.
  - Input: Prompt.
  - Output: JSON object or None.
  - Logic: Try OpenAI then HuggingFace.

- `_call_openai()` / `_call_huggingface()`
  - Purpose: Provider-specific inference calls.
  - Input: Prompt.
  - Output: Parsed JSON or None.
  - Logic: HTTP request via shared session.

- `_parse_json()`
  - Purpose: Extract JSON block from LLM output.
  - Input: Text.
  - Output: Parsed JSON or None.
  - Logic: Regex + `json.loads`.

- `_normalize_claim_analysis()`
  - Purpose: Normalize LLM claim analysis.
  - Input: Raw dict.
  - Output: Normalized dict.
  - Logic: Sanitizes values and list types.

- `_fallback_claim_analysis()`
  - Purpose: Heuristic entity extraction.
  - Input: Claim.
  - Output: Dict.
  - Logic: Uses `extract_candidate_entity`.

- `_sanitize_queries()` / `_fallback_queries()`
  - Purpose: Clean and enforce entity-in-query.
  - Input: Queries, claim, entity, keywords.
  - Output: Clean query list.
  - Logic: Dedup + entity prefix.

- `_normalize_reasoning()` / `_fallback_reasoning()`
  - Purpose: Normalize LLM verdict or fallback.
  - Input: Raw LLM dict or evidence.
  - Output: Reasoning dict.
  - Logic: Constrains label and confidence.

- `compute_semantic_credibility()`
  - Purpose: LLM-based credibility scoring.
  - Input: Evidence sentence.
  - Output: Float 0.2-0.95.
  - Logic: LLM classifies factual/neutral/speculative.

- `detect_relationship()`
  - Purpose: NLI-like classification of evidence vs claim.
  - Input: Claim, evidence sentence.
  - Output: SUPPORTS/CONTRADICTS/NEUTRAL.
  - Logic: LLM classification.

- `classify_evidence_type()`
  - Purpose: Evidence type detection.
  - Input: Evidence sentence.
  - Output: factual/historical/opinion/speculation.
  - Logic: LLM classification.

### backend/services/retrieval_new.py
- `QueryExpander.__init__()` / `expand_query()`
  - Purpose: Expand queries with variants.
  - Input: Query, `num_variants`.
  - Output: Query list.
  - Logic: Adds context keywords.

- `WikipediaRetriever.__init__()`
  - Purpose: Setup retriever and caches.
  - Input: None.
  - Output: Instance.
  - Logic: Initializes caches and API settings.

- `WikipediaRetriever._api_search()` / `_api_fetch_page()`
  - Purpose: Wikipedia API search and page fetch.
  - Input: Query or title.
  - Output: Titles or page dict.
  - Logic: Caches results to reduce calls.

- `WikipediaRetriever.title_relevance()`
  - Purpose: Score title relevance to entity tokens.
  - Input: Title, entity tokens.
  - Output: Float 0-1.
  - Logic: Token overlap ratio.

- `WikipediaRetriever.search()`
  - Purpose: Search and fetch articles.
  - Input: Query, max results.
  - Output: Article list.
  - Logic: Wikipedia library or API fallback.

- `RetrievalPipeline.__init__()`
  - Purpose: Compose expander + retriever.
  - Input: None.
  - Output: Instance.
  - Logic: Uses WikipediaRetriever.

- `RetrievalPipeline.retrieve()`
  - Purpose: Expanded search with title filtering.
  - Input: Query, max articles, entity tokens.
  - Output: Articles list.
  - Logic: Expand query, filter by title relevance.

### backend/services/ranking_new.py
- `SentenceTransformerEmbedder.__init__()`
  - Purpose: Load embedding model and cache.
  - Input: Model name, device.
  - Output: Embedder.
  - Logic: Initializes SentenceTransformer.

- `embed_texts()`
  - Purpose: Embed texts with caching.
  - Input: Text list.
  - Output: Embedding matrix.
  - Logic: Cache hits and batch inference.

- `_normalize_scores()` / `_penalize_weak_matches()`
  - Purpose: Normalize similarity and reduce noise.
  - Input: Scores.
  - Output: Normalized scores.
  - Logic: Min-max + penalties.

- `rank_by_similarity()`
  - Purpose: Rank evidence by similarity.
  - Input: Query, sentences, top_k.
  - Output: Ranked evidence and scores.
  - Logic: Cosine similarity + penalties.

- `compute_similarity_scores()`
  - Purpose: Return normalized similarity for all sentences.
  - Input: Query, sentences.
  - Output: Score list.

- `compute_ranking_confidence()`
  - Purpose: Aggregate ranking confidence.
  - Input: Scores, strategy.
  - Output: Float.

- `rank_and_score()`
  - Purpose: Convenience method to rank and score.

- `RankingPipeline.__init__()` / `rank_evidence()`
  - Purpose: Thin wrapper around embedder ranking.

### backend/services/utils_new.py
- `extract_sentences()`
  - Purpose: Sentence segmentation.
  - Input: Text.
  - Output: Sentence list.

- `clean_text()`
  - Purpose: Strip HTML and normalize whitespace.

- `normalize_text()` / `normalize_entity()`
  - Purpose: Normalize for comparison.

- `tokenize()`
  - Purpose: Tokenize and remove stopwords.

- `extract_candidate_entity()`
  - Purpose: Heuristic entity extraction.

- `sentence_quality()`
  - Purpose: Score sentence quality.

- `deduplicate_sentences()` / `deduplicate_evidence()`
  - Purpose: Remove duplicates.

- `clean_evidence()`
  - Purpose: Extract clean evidence sentences.

- `chunk_text()`
  - Purpose: Text chunking utility.

- `format_evidence_dict()`
  - Purpose: Normalize evidence into API format.

## 4. Scoring System Details
- **Similarity**: cosine similarity, normalized to $[0,1]$.
- **Semantic credibility**: LLM classification mapped to score.
- **Source reliability**: intro/references/controversy weighting.
- **Evidence score**:

$$
\\text{credibility} = 0.7 \\cdot \\text{semantic\_credibility} + 0.3 \\cdot \\text{source\_reliability}

\\text{evidence\_score} = 0.6 \\cdot \\text{similarity} + 0.4 \\cdot \\text{credibility}
$$

- **Confidence**:

$$
\\text{raw\_confidence} = 0.4 \\cdot \\overline{e} + 0.3 \\cdot c + 0.3 \\cdot r

\\text{confidence} = \\sigma(\\text{raw\_confidence})
$$

Where:
- $\overline{e}$ = average evidence score
- $c$ = consistency score
- $r$ = reasoning confidence

- **Consistency**:

$$
\\text{consistency} = \\frac{(\\text{support} - \\text{contradict}) / \\text{total} + 1}{2}
$$

**Boost rule**: If 2+ evidence items have $\text{evidence\_score} \ge 0.75$, add $+0.10$ (capped at 0.99).

- **Percentage**:

$$
\text{confidence\_percentage} = 100 \cdot \text{confidence}
$$

## 5. Decision Logic
- **TRUE** if:
  - $\text{confidence} \ge 0.75$ and support ratio $\ge 0.6$ and refute ratio $< 0.3$.
  - Or LLM reasoning says TRUE with support ratio $\ge 0.5$.
- **MISINFORMATION** if:
  - $\text{confidence} \le 0.30$ and refute ratio $\ge 0.6$ and average evidence $\ge 0.6$.
  - Or LLM reasoning says MISINFORMATION with refute ratio $\ge 0.5$ and avg evidence $\ge 0.6$.
- **UNCERTAIN** otherwise or when evidence is weak/conflicting.

Reasoning-first rule:
- If reasoning confidence $> 0.8$, the LLM label is prioritized only when average evidence score $> 0.6$.

Thresholds:
- **TRUE**: $\ge 75\%$
- **MISINFORMATION**: $\le 30\%$
- **UNCERTAIN**: between 30-75% or mixed signals

## 6. Evidence Handling
- **Filtering**:
  - Remove if similarity < 0.5
  - Remove if credibility < 0.4
  - Remove if unrelated to entity
- **Deduplication**: uses normalized text to remove duplicates.
- **Top-K**: sorted by evidence_score, keep only top 3-5.
- **Weak evidence ignored**: filtered out before scoring and confidence.
- **Evidence type**: LLM tags evidence as factual/historical/opinion/speculation for explainability.
- **Diversity**: prefers evidence from different pages to reduce same-source bias.
- **Temporal penalties**: outdated evidence is down-weighted for time-sensitive claims.

## 7. LLM Reasoning Layer
- **Role**: Interprets evidence holistically and detects contradictions.
- **Output**: label + reasoning + reasoning confidence.
- **Impact**: reasoning confidence contributes to final confidence, and label can resolve edge cases when evidence is mixed.
- **NLI relationship**: LLM/NLI classification (SUPPORTS/CONTRADICTS/NEUTRAL) feeds consistency scoring.

## 8. Improvements Made (Old vs New)
- **Old**: Similarity-only scoring.
  - **New**: Weighted similarity + semantic credibility with strict filtering.
- **Old**: Query generation was generic.
  - **New**: LLM-driven query generation with entity-aware templates.
- **Old**: No entity resolution.
  - **New**: Entity filtering by title and sentence matching.
- **Old**: Heuristic credibility and contradiction.
  - **New**: LLM semantic credibility and NLI-style relationship detection.
- **Old**: Simple consistency logic.
  - **New**: Normalized support-vs-contradict consistency.
- **Old**: Weak evidence lowered confidence.
  - **New**: Weak evidence removed before scoring.
- **Old**: No reasoning layer.
  - **New**: LLM reasoning with confidence priority.
- **Old**: Unstructured UI output.
  - **New**: Structured JSON with key_signals and explainability details.
- **Old**: No caching.
  - **New**: Embedding cache, Wikipedia cache, LLM cache.

## 9. Debug Logging System
- Logs include:
  - Retrieved articles (raw vs filtered)
  - Raw evidence count
  - Evidence filtering summary and removal reasons
  - NLI relationship results
  - Semantic credibility classifications
  - Reasoning confidence and contribution weights
  - Temporal penalties and evidence years
  - Confidence breakdown with averages and ratios
- Debug workflow:
  - Check logs for missing evidence
  - Verify query generation and article retrieval
  - Inspect removed evidence reasons

## 10. Performance Optimization
- **Embedding cache**: avoids recomputation of repeated sentences.
- **Wikipedia cache**: reduces repeated API requests.
- **LLM cache**: reuses analysis and queries for repeated claims.
- **Batch embedding**: reduces overhead for similarity scoring.

## 11. Sample Output
```json
{
  "label": "TRUE",
  ext{credibility} = 0.7 \cdot \text{semantic\_credibility} + 0.3 \cdot \text{source\_reliability}
  ext{evidence\_score} = 0.6 \cdot \text{similarity} + 0.4 \cdot \text{credibility}
  "key_signals": [
    {
      "text": "The Earth is approximately an oblate spheroid.",
      ext{raw\_confidence} = 0.4 \cdot \overline{e} + 0.3 \cdot c + 0.3 \cdot r
      ext{confidence} = \sigma(\text{raw\_confidence})
      "score": 0.86,
      "source": "Earth"
    }
  ],
      ext{consistency} = \frac{(\text{support} - \text{contradict}) / \text{total} + 1}{2}
    "why_selected": "Top evidence selected by similarity, credibility, and entity alignment.",
    "why_removed": "similarity < 0.5",
    "consistency": "Support ratio 0.80, refute ratio 0.00.",
    "reasoning": "Evidence agrees across credible sources.",
    "why_confidence": "Confidence driven by avg evidence 0.82, consistency 0.90, reasoning 0.85.",
    "top_influence": "Top influence: The Earth is approximately an oblate spheroid.",
    "rejected_evidence": "credibility < 0.4: Some weak evidence text"
  },
  "confidence_breakdown": {
    "evidence": 0.328,
    "consistency": 0.27,
    "reasoning": 0.255
  }
}
```

## 12. Future Improvements
- Add multi-source retrieval beyond Wikipedia (news, academic, gov).
- Add explicit NLI contradiction model for stronger stance detection.
- Use a domain-specific credibility model instead of heuristics.
- Add vector DB for large-scale retrieval and caching.

## 13. How to Debug / Modify System
- **Scoring**: edit `compute_semantic_credibility()` in `backend/services/llm_reasoner.py` and `_compute_confidence()` in `backend/services/pipeline_new.py`.
- **Retrieval**: adjust query generation in `backend/services/llm_reasoner.py` and retrieval filters in `backend/services/retrieval_new.py`.
- **Thresholds**: update decision logic in `ProductionRAGPipeline.analyze()`.
- **UI output**: update response mapping in `backend/api/analyze_v2.py`.
