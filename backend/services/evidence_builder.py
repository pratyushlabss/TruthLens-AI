"""
Evidence Builder - converts raw articles into structured evidence.
Semantic similarity uses sentence-transformers when available, with a
keyword-based Jaccard fallback.  Stance detection uses a lightweight
cross-encoder NLI model (cross-encoder/nli-MiniLM2-L6-H768) when
available, falling back to keyword heuristics.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level lazy-loaded models (shared across all EvidenceBuilder instances)
# ---------------------------------------------------------------------------
_semantic_model = None   # SentenceTransformer for embedding similarity
_nli_pipeline = None     # cross-encoder for stance detection
_nli_attempted = False   # avoid retrying a failed load


def _get_semantic_model():
    """Return a shared SentenceTransformer, loading it once."""
    global _semantic_model
    if _semantic_model is not None:
        return _semantic_model
    try:
        from sentence_transformers import SentenceTransformer
        _semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("[EVIDENCE] ✅ Loaded SentenceTransformer for semantic similarity")
    except Exception as e:
        logger.warning(f"[EVIDENCE] SentenceTransformer unavailable: {e}")
        _semantic_model = None
    return _semantic_model


def _get_nli_pipeline():
    """Return a shared cross-encoder NLI pipeline, loading it once."""
    global _nli_pipeline, _nli_attempted
    if _nli_attempted:
        return _nli_pipeline
    _nli_attempted = True
    try:
        from transformers import pipeline as hf_pipeline
        # Small, fast NLI model (~85 MB) — free from HuggingFace
        _nli_pipeline = hf_pipeline(
            "text-classification",
            model="cross-encoder/nli-MiniLM2-L6-H768",
            device=-1,           # CPU
            top_k=None,          # return scores for all labels
        )
        logger.info("[EVIDENCE] ✅ Loaded cross-encoder NLI for stance detection")
    except Exception as e:
        logger.warning(f"[EVIDENCE] Cross-encoder NLI unavailable: {e}")
        _nli_pipeline = None
    return _nli_pipeline


class EvidenceBuilder:
    """
    Builds structured evidence from raw articles.
    === FIX 2: GUARANTEED NON-EMPTY EVIDENCE ===
    Always returns evidence, never empty.
    """
    
    def __init__(self):
        """Initialize evidence builder."""
        self.stance_labels = ["SUPPORTS", "REFUTES", "NEUTRAL"]
    
    def build(
        self,
        raw_articles: List[Dict],
        claim: str,
        nlp_score: float = 0.5,
        roberta_classifier = None
    ) -> List[Dict]:
        """
        Build structured evidence from raw articles with semantic analysis.
        === FIX 2: GUARANTEED NON-EMPTY EVIDENCE ===
        Always returns at least one evidence item.
        
        Args:
            raw_articles: Raw scraped articles
            claim: The claim being analyzed
            nlp_score: NLP classification score (0-1)
            roberta_classifier: NLP classifier for semantic analysis
            
        Returns:
            Structured evidence list (guaranteed non-empty)
        """
        evidence_list = []
        self.roberta_classifier = roberta_classifier
        
        logger.info(f"[BUILDING] Evidence from {len(raw_articles)} articles")
        
        # Process each article
        if raw_articles:
            for article in raw_articles:
                try:
                    evidence_item = self._build_evidence_item(article, claim)
                    if evidence_item:
                        evidence_list.append(evidence_item)
                except Exception as e:
                    logger.warning(f"[FIX2] Error building evidence item: {e}")
                    continue
        
        # === FIX 2: FORCE FALLBACK EVIDENCE IF EMPTY ===
        if not evidence_list:
            logger.warning(
                "[FIX2] No evidence items built - adding fallback evidence"
            )
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
        return evidence_list
    
    def _build_evidence_item(self, article: Dict, claim: str) -> Optional[Dict]:
        """Build a single evidence item from an article with semantic analysis."""
        try:
            article_text = article.get("text", "") or article.get("snippet", "")
            norm_claim = self._normalize_claim(claim)
            semantic_similarity = self._compute_semantic_similarity(norm_claim, article_text)
            stance = self._determine_stance(claim, article_text, semantic_similarity)

            logger.info(
                f"[EVIDENCE] {article.get('source', 'Unknown')[:30]} → "
                f"{stance} (sim:{semantic_similarity:.2f})"
            )

            credibility = article.get("credibility", 0.5)
            is_fallback = article.get("is_fallback", False)

            return {
                "source": article.get("source", "Unknown Source"),
                "stance": stance,
                "credibility": credibility,
                "credibility_reason": (
                    "From external source" if not is_fallback
                    else "System-generated fallback"
                ),
                "snippet": article.get("snippet", article.get("title", "No text")),
                "text": article_text,
                "url": article.get("url", "unknown"),
                "is_fallback": is_fallback,
                "stance_confidence": semantic_similarity,
                "semantic_similarity": semantic_similarity,
                "retrieved_at": article.get("retrieved_at", datetime.now().isoformat()),
            }

        except Exception as e:
            logger.warning(f"[EVIDENCE] Error building item: {e}")
            return None

    @staticmethod
    def _normalize_claim(claim: str) -> str:
        """
        Normalise claim text before NLI/embedding processing.
        ALL-CAPS input degrades model quality — convert to sentence case.
        """
        if claim == claim.upper() and len(claim) > 3:
            return claim.capitalize()
        return claim

    def _select_nli_context(self, article_text: str, norm_claim: str) -> str:
        """
        Pick the most claim-relevant sentences from the article for NLI.

        Using article[:512] is fragile — for e.g. an assassination-attempt
        article the first sentences describe the shooting, not the survival.
        Selecting semantically-closest sentences gives the NLI model the
        most on-topic snippet.
        """
        import re
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", article_text) if len(s.strip()) > 20]
        if len(sentences) <= 3:
            return article_text[:512]

        model = _get_semantic_model()
        if model is None:
            return article_text[:512]

        try:
            from sklearn.metrics.pairwise import cosine_similarity
            import re as _re
            claim_emb = model.encode(norm_claim).reshape(1, -1)
            candidates = sentences[:40]  # cap to avoid large batches

            # Pre-process candidates: if a sentence opens with a quoted phrase
            # that restates the claim (common in debunking/definition articles),
            # strip the quote so NLI sees the editorial assertion, not the claim.
            # e.g. (curly-quote)”The Moon is made of green cheese”(curly-quote)
            #      is a statement referring to a fanciful belief...
            #   -> is a statement referring to a fanciful belief...
            # Use code-point sets to avoid literal Unicode chars in source.
            _OPEN_CP = {0x22, 0x27, 0x60, 0x201C, 0x201E, 0x2018}
            _CLOSE_CP = {0x22, 0x27, 0x60, 0x201D, 0x201F, 0x2019}
            cleaned = []
            for sent in candidates:
                if sent and ord(sent[0]) in _OPEN_CP:
                    end = next(
                        (i for i, ch in enumerate(sent[1:], 1) if ord(ch) in _CLOSE_CP),
                        -1,
                    )
                    stripped = sent[end + 1:].strip() if end > 0 else sent
                    cleaned.append(stripped if len(stripped) > 20 else sent)
                else:
                    cleaned.append(sent)

            sent_embs = model.encode(cleaned)
            sims = cosine_similarity(claim_emb, sent_embs)[0]
            # Use the single highest-similarity sentence.
            # Multi-sentence context causes NLI errors when secondary sentences
            # contain contradictory framing (e.g. "was shot" alongside "survived").
            best_idx = int(sims.argmax())
            return cleaned[best_idx][:512]
        except Exception:
            return article_text[:512]

    def _determine_stance(
        self, claim: str, article_text: str, semantic_similarity: float
    ) -> str:
        """
        Determine stance of an article toward the claim.

        Priority:
        1. Cross-encoder NLI model — correct text_pair API call
        2. Keyword-only fallback (very conservative, high threshold)
        3. Default NEUTRAL when uncertain
        """
        # Low similarity → article is off-topic, skip NLI entirely
        if not article_text or semantic_similarity < 0.60:
            return "NEUTRAL"

        norm_claim = self._normalize_claim(claim)

        # ── Method 1: NLI cross-encoder ──────────────────────────────────────
        # Correct call: nli(premise, text_pair=hypothesis)
        # NOT: nli("premise [SEP] hypothesis") — that scrambles scores
        nli = _get_nli_pipeline()
        if nli is not None:
            try:
                # Select most relevant sentences — avoids NLI being misled by
                # article introductions that describe context rather than resolution
                premise = self._select_nli_context(article_text, norm_claim)
                premise_lower = premise.lower()

                # Pre-NLI check: definitional/debunking sentences cannot reliably
                # indicate an article's stance. Examples:
                #   '"The Moon is made of green cheese" is a statement referring
                #    to a fanciful belief...'
                #   'Flat Earth is an archaic and scientifically disproven conception'
                # NLI will latch on to the claim words and give wrong SUPPORTS/REFUTES.
                # Return NEUTRAL immediately so these don't pollute the verdict.
                debunking_context = any(w in premise_lower for w in [
                    "fanciful belief", "popular myth", "is a myth", "is a legend",
                    "is a statement referring", "is an idiom", "is a saying",
                    "is a proverb", "folk belief", "misconception that",
                    "disproven conception", "archaic", "pseudoscience",
                    "conspiracy theory", "false belief", "unproven claim",
                ])
                if debunking_context:
                    logger.info("[STANCE/NLI] Definitional/debunking sentence → NEUTRAL")
                    return "NEUTRAL"

                # Safety override: if the premise explicitly says the subject
                # "survived" or is "currently" active, NLI often misclassifies
                # complex biographical sentences. Check for life-confirmation
                # keywords and correct a spurious REFUTES before scoring.
                life_confirmed = any(kw in premise_lower for kw in [
                    "survived", "is alive", "is currently", "is serving",
                    "currently serving", "is the president", "47th president",
                    "returned to", "is well", "is in good health",
                ])

                # Use keyword arg 'text_pair' so the tokenizer receives a proper pair
                outputs = nli(premise, text_pair=norm_claim)
                # outputs is a list-of-dicts or list-of-lists depending on top_k
                items = outputs[0] if isinstance(outputs[0], list) else outputs
                scores = {}
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    lbl = item.get("label", "").lower()
                    sc = float(item.get("score", 0))
                    if "entail" in lbl:
                        scores["entailment"] = sc
                    elif "contradict" in lbl:
                        scores["contradiction"] = sc
                    elif "neutral" in lbl:
                        scores["neutral"] = sc

                entail = scores.get("entailment", 0)
                contra = scores.get("contradiction", 0)
                neutral = scores.get("neutral", 0)

                logger.debug(
                    f"[STANCE/NLI] entail={entail:.3f} contra={contra:.3f} "
                    f"neutral={neutral:.3f} | '{norm_claim[:50]}'"
                )

                # Only act on a confident result (≥ 0.60) to avoid false positives
                best = max(entail, contra, neutral)
                if best >= 0.60:
                    if entail == best:
                        logger.info(f"[STANCE/NLI] SUPPORTS ({entail:.3f})")
                        return "SUPPORTS"
                    if contra == best:
                        # Sanity-check before trusting REFUTES.
                        # The 68M NLI model frequently gives spurious REFUTES on:
                        #   - Sentences that describe the claim's topic without negating it
                        #     e.g. "Spherical Earth = approximation of sphere" vs "Earth is round"
                        #   - Debunking articles ("Flat Earth is disproven") where the article
                        #     SUPPORTS the claim by disproving the opposite
                        #   - Sentences with survival/life-context words (assassination attempts)
                        #
                        # We only trust REFUTES when the premise EXPLICITLY negates
                        # one of the claim's key terms ("not round", "no evidence that").
                        premise_lower = premise.lower()
                        claim_words = [
                            w for w in norm_claim.lower().split()
                            if len(w) > 3 and w not in {
                                "this", "that", "with", "from", "have", "will",
                                "been", "were", "they", "their", "some",
                            }
                        ]
                        has_explicit_negation = any(
                            f"not {w}" in premise_lower
                            or f"no {w}" in premise_lower
                            or f"isn't {w}" in premise_lower
                            or f"aren't {w}" in premise_lower
                            for w in claim_words
                        )
                        has_debunking_lang = any(w in premise_lower for w in [
                            "disproven", "discredited", "pseudoscience",
                            "misconception", "archaic", "conspiracy",
                            "false belief", "myth", "unproven",
                        ])
                        if life_confirmed or has_debunking_lang or not has_explicit_negation:
                            logger.info(
                                f"[STANCE/NLI] REFUTES overridden → NEUTRAL "
                                f"(life_confirmed={life_confirmed}, "
                                f"debunking={has_debunking_lang}, "
                                f"explicit_neg={has_explicit_negation})"
                            )
                            return "NEUTRAL"
                        logger.info(f"[STANCE/NLI] REFUTES confirmed ({contra:.3f})")
                        return "REFUTES"

                # NLI uncertain → NEUTRAL (do NOT fall through to keyword heuristics)
                logger.debug(f"[STANCE/NLI] Uncertain (best={best:.3f}) → NEUTRAL")
                return "NEUTRAL"

            except Exception as e:
                logger.debug(f"[STANCE/NLI] NLI inference failed: {e}")

        # ── Method 2: Conservative keyword heuristics (no NLI available) ─────
        # Only trigger on strong, unambiguous misinformation-specific phrases.
        # Generic negations like "is not" appear in every normal article and
        # must NOT be used as refutation signals.
        article_lower = article_text.lower()
        strong_refute = [
            "debunked", "debunks", "is a hoax", "is false", "is untrue",
            "misinformation", "disinformation", "fabricated", "fact check: false",
            "this claim is false", "no evidence that", "has been disproved",
        ]
        strong_support = [
            "confirmed by", "verified by", "fact check: true",
            "this claim is true", "evidence confirms", "is indeed alive",
            "is currently", "is still alive",
        ]

        refute_hits = sum(1 for p in strong_refute if p in article_lower)
        support_hits = sum(1 for p in strong_support if p in article_lower)

        if refute_hits >= 1 and refute_hits > support_hits:
            return "REFUTES"
        if support_hits >= 1 and support_hits > refute_hits:
            return "SUPPORTS"
        return "NEUTRAL"
    
    def _compute_semantic_similarity(self, claim: str, article_text: str) -> float:
        """
        Compute semantic similarity between claim and article text.

        Uses sentence-transformers embeddings when available (cosine similarity),
        with a keyword-overlap fallback.
        """
        if not article_text or len(article_text.strip()) < 20:
            return 0.0

        # ── Method 1: Sentence-transformer cosine similarity ─────────────────
        model = _get_semantic_model()
        if model is not None:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                claim_emb = model.encode(claim).reshape(1, -1)
                text_emb = model.encode(article_text[:1000]).reshape(1, -1)
                sim = float(cosine_similarity(claim_emb, text_emb)[0][0])
                # Cosine similarity is in [-1, 1]; map to [0, 1]
                sim = (sim + 1.0) / 2.0
                logger.debug(f"[SEM] Embedding similarity: {sim:.3f}")
                return float(max(0.0, min(1.0, sim)))
            except Exception as e:
                logger.debug(f"[SEM] Embedding similarity failed: {e}")

        # ── Method 2: Keyword + entity overlap (fast fallback) ───────────────
        stop_words = {
            "the", "a", "an", "and", "or", "is", "are", "was", "were",
            "be", "been", "have", "has", "had", "do", "does", "did",
            "will", "would", "could", "should", "of", "in", "on", "at",
            "by", "for", "with", "to", "from", "as", "it", "its",
        }
        claim_words = {w for w in claim.lower().split() if w not in stop_words and len(w) > 2}
        article_words = {w for w in article_text.lower().split()[:300] if w not in stop_words and len(w) > 2}

        if not claim_words or not article_words:
            return 0.0

        intersection = len(claim_words & article_words)
        union = len(claim_words | article_words)
        jaccard = intersection / union if union > 0 else 0.0

        # Boost for keyword coverage (fraction of claim words found in article)
        coverage = intersection / len(claim_words) if claim_words else 0.0
        similarity = (jaccard * 0.5) + (coverage * 0.5)

        logger.debug(f"[SEM] Keyword similarity: {similarity:.3f} (jaccard={jaccard:.3f}, coverage={coverage:.3f})")
        return float(max(0.0, min(1.0, similarity)))
    
    def deduplicate_evidence(self, evidence_list: List[Dict]) -> List[Dict]:
        """
        Remove duplicate evidence items.
        Preserves fallback evidence.
        
        Args:
            evidence_list: Raw evidence list
            
        Returns:
            Deduplicated evidence (guaranteed non-empty)
        """
        if not evidence_list:
            return self._fallback_single_evidence()
        
        seen_sources = set()
        deduplicated = []
        fallback_items = []
        
        for item in evidence_list:
            source_key = (
                item.get("source", ""),
                item.get("snippet", "")[:50]
            )
            
            if source_key not in seen_sources:
                if item.get("is_fallback", False):
                    fallback_items.append(item)
                else:
                    deduplicated.append(item)
                seen_sources.add(source_key)
        
        # Always include fallback items at end if dedup is empty
        result = deduplicated if deduplicated else fallback_items
        
        if not result:
            result = self._fallback_single_evidence()
        
        logger.info(f"[FIX2] Deduplicated to {len(result)} items")
        return result
    
    def _fallback_single_evidence(self) -> List[Dict]:
        """Return single fallback evidence item."""
        return [
            {
                "source": "System Fallback",
                "stance": "NEUTRAL",
                "credibility": 0.3,
                "credibility_reason": "System-generated due to lack of sources",
                "snippet": "No external sources available",
                "text": "Analysis proceeding with system classification only.",
                "url": "generated://system",
                "is_fallback": True,
                "stance_confidence": 0.33,
                "retrieved_at": datetime.now().isoformat()
            }
        ]
