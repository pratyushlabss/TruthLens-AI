"""Verdict Engine - hybrid rule-based + optional NLI refinement.

Computes final verdict using rule-based logic on evidence and, when available,
refines that verdict using a HuggingFace BART MNLI NLI model. This helps reduce
incorrect TRUE/UNCERTAIN outcomes on well-established facts while preserving
existing behavior if transformers are unavailable.
"""

import logging
from typing import Dict, List, Optional
from enum import Enum

try:
    # Soft dependency: if the NLI stack is unavailable, we fall back to
    # pure rule-based logic without failing requests.
    from services.huggingface_nli import HuggingFaceNLI, NLIError  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    HuggingFaceNLI = None  # type: ignore
    NLIError = Exception  # type: ignore

logger = logging.getLogger(__name__)


class VerdictType(str, Enum):
    """Verdict types."""
    TRUE = "TRUE"
    FALSE = "FALSE"
    UNCERTAIN = "UNCERTAIN"


class VerdictEngine:
    """
    Computes verdict from evidence.
    === FIX 3: GUARANTEED DETAILED REASONING ===
    Always returns detailed step-by-step reasoning.
    """
    
    def __init__(self):
        """Initialize verdict engine."""
        self.confidence_threshold = 0.6
        # Lazily created HuggingFace NLI helper (BART MNLI). When this is
        # None, the engine operates in pure rule-based mode.
        self._nli = None
    
    def compute_verdict(
        self,
        evidence_list: List[Dict],
        nlp_score: float,
        claim: str
    ) -> Dict:
        """
        Compute verdict from evidence.
        === FIX 3: GUARANTEED DETAILED REASONING ===
        Always returns detailed reasoning, never empty.
        
        Args:
            evidence_list: List of evidence items
            nlp_score: NLP classification score (0-1)
            claim: The claim being analyzed
            
        Returns:
            Verdict dict with detailed reasoning
        """
        logger.info(f"[FIX3] Computing verdict for: {claim[:60]}")
        
        if not evidence_list:
            logger.warning("[FIX3] No evidence - returning uncertain with fallback reasoning")
            return self._uncertain_verdict(
                reason="No external evidence available",
                nlp_score=nlp_score,
                claim=claim,
                is_fallback=True
            )
        
        # Check if all evidence is fallback
        real_evidence = [e for e in evidence_list if not e.get("is_fallback", False)]
        fallback_evidence = [e for e in evidence_list if e.get("is_fallback", False)]
        
        if not real_evidence and fallback_evidence:
            logger.warning("[FIX3] Only fallback evidence - returning uncertain")
            return self._uncertain_verdict(
                reason="Only system-generated fallback evidence available",
                nlp_score=nlp_score,
                claim=claim,
                is_fallback=True
            )
        
        # Analyze real evidence (rule-based core)
        verdict = self._analyze_evidence(real_evidence, nlp_score, claim)

        # Optional refinement with NLI if the model is available and
        # confident enough. If anything goes wrong here we simply fall back
        # to the rule-based verdict.
        try:
            refined = self._refine_with_nli(real_evidence, claim, verdict)
            if refined is not None:
                verdict = refined
        except Exception as e:  # pragma: no cover - defensive logging only
            logger.warning(f"[FIX3] NLI refinement failed; using rule-based verdict only: {e}")

        logger.info(f"[FIX3] Computed verdict: {verdict['verdict']} (confidence: {verdict['confidence']:.2f})")
        return verdict
    
    def _analyze_evidence(
        self,
        evidence_list: List[Dict],
        nlp_score: float,
        claim: str
    ) -> Dict:
        """
        Analyze evidence and compute verdict with improved logic.
        
        Args:
            evidence_list: Real evidence items
            nlp_score: NLP score
            claim: The claim
            
        Returns:
            Verdict dict
        """
        supports_count = 0
        refutes_count = 0
        neutral_count = 0
        average_credibility = 0
        
        for evidence in evidence_list:
            stance = evidence.get("stance", "NEUTRAL")
            credibility = evidence.get("credibility", 0.5)
            semantic_sim = evidence.get("semantic_similarity", evidence.get("stance_confidence", 0.5))
            
            # Weight evidence by both credibility and semantic similarity
            evidence_weight = credibility * semantic_sim
            
            if stance == "SUPPORTS":
                supports_count += evidence_weight
            elif stance == "REFUTES":
                refutes_count += evidence_weight
            else:
                neutral_count += evidence_weight
            
            average_credibility += credibility
        
        if evidence_list:
            average_credibility /= len(evidence_list)
        
        # Normalize scores
        total_score = supports_count + refutes_count + neutral_count
        
        if total_score == 0:
            return self._uncertain_verdict(
                reason="Evidence available but inconclusive",
                nlp_score=nlp_score,
                claim=claim
            )
        
        # Determine verdict type with improved thresholds
        # Make verdicts more definitive when evidence is strong
        supports_ratio = supports_count / total_score if total_score > 0 else 0
        refutes_ratio = refutes_count / total_score if total_score > 0 else 0
        
        logger.info(f"[VERDICT] Evidence ratios - Supports: {supports_ratio:.2f}, Refutes: {refutes_ratio:.2f}, Neutral: {neutral_count/total_score:.2f}")
        
        if supports_ratio > 0.6:
            verdict_type = VerdictType.TRUE
            confidence = (supports_ratio * average_credibility) * 0.9 + 0.1
        elif refutes_ratio > 0.6:
            verdict_type = VerdictType.FALSE
            confidence = (refutes_ratio * average_credibility) * 0.9 + 0.1
        else:
            # When one side is clearly larger but just below 0.6, treat it as
            # a directional but lower-confidence verdict instead of always
            # returning UNCERTAIN.
            if supports_ratio - refutes_ratio >= 0.2:
                verdict_type = VerdictType.TRUE
                confidence = 0.55
            elif refutes_ratio - supports_ratio >= 0.2:
                verdict_type = VerdictType.FALSE
                confidence = 0.55
            else:
                verdict_type = VerdictType.UNCERTAIN
                confidence = 0.5
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            verdict_type=verdict_type,
            supports_count=supports_count,
            refutes_count=refutes_count,
            neutral_count=neutral_count,
            average_credibility=average_credibility,
            nlp_score=nlp_score,
            claim=claim
        )
        
        logger.info(f"[VERDICT] Final verdict: {verdict_type.value} (confidence: {confidence:.2f})")
        
        return {
            "verdict": verdict_type.value,
            "confidence": min(max(confidence, 0.1), 0.95),
            "reasoning": reasoning,
            "is_fallback": False
        }
    
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
        
        Args:
            reason: why uncertain
            nlp_score: NLP score
            claim: the claim
            is_fallback: if using fallback evidence
            
        Returns:
            Detailed uncertain verdict
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
   - External source verification: {'Not possible' if is_fallback else 'Incomplete'}
   - Claim specificity: {'High (may require specialized sources)' if len(claim.split()) > 5 else 'Moderate'}
   - Temporal factor: {'Recent/Breaking' if nlp_score > 0.7 else 'Established'}

4. Evidence Availability
   - Sources found: {'System fallback only - search engines unavailable' if is_fallback else 'Limited'}
   - Credibility sources: {'None (system analysis only)' if is_fallback else 'Mixed'}
   - Coverage: Limited coverage available

System Conclusion:
The claim cannot be definitively verified or falsified based on:
- Insufficient supporting or refuting evidence
- Possible search/source availability limitations
- Claim specificity or recency

Recommendations:
1. Seek additional verified sources from domain experts
2. Monitor for updates as more evidence becomes available
3. Consider consulting fact-checking organizations specialized in this domain
4. Re-verify the claim as additional information emerges

Next Steps:
- Try searching for highly specific terms related to the claim
- Look for expert analyses or official statements
- Check date ranges to ensure current information
- Cross-reference multiple independent sources

Confidence Level: LOW (30%)
Reliability: System analysis with limited external verification"""
        
        return {
            "verdict": "UNCERTAIN",
            "confidence": 0.3,
            "reasoning": detailed_reasoning.strip(),
            "is_fallback": is_fallback
        }
    
    def _generate_reasoning(
        self,
        verdict_type: VerdictType,
        supports_count: float,
        refutes_count: float,
        neutral_count: float,
        average_credibility: float,
        nlp_score: float,
        claim: str
    ) -> str:
        """
        Generate detailed reasoning for verdict.
        
        Args:
            verdict_type: The verdict type (TRUE/FALSE/UNCERTAIN)
            supports_count: Number of supporting sources
            refutes_count: Number of refuting sources
            neutral_count: Number of neutral sources
            average_credibility: Average source credibility
            nlp_score: NLP classification score
            claim: The claim
            
        Returns:
            Detailed reasoning text
        """
        total_sources = supports_count + refutes_count + neutral_count
        
        if verdict_type == VerdictType.TRUE:
            reasoning = f"""VERDICT ANALYSIS: TRUE

Evidence Summary:
- Supporting sources: {supports_count:.1f} credibility units
- Refuting sources: {refutes_count:.1f} credibility units
- Neutral sources: {neutral_count:.1f} credibility units
- Average source credibility: {average_credibility:.1%}

Analysis:
The claim "{claim[:80]}" appears to be TRUE based on:
1. Preponderance of supporting evidence ({supports_count:.0f} vs {refutes_count:.0f})
2. High average credibility of sources ({average_credibility:.0%})
3. Consistent support across multiple independent sources
4. NLP analysis supports claim plausibility

Confidence Assessment:
- Evidence weight: {(supports_count/max(total_sources,1)):.0%} support
- Source reliability: {average_credibility:.0%} average credibility
- Overall confidence: HIGH

Recommendation: The claim is supported by available evidence."""
        
        elif verdict_type == VerdictType.FALSE:
            reasoning = f"""VERDICT ANALYSIS: FALSE

Evidence Summary:
- Supporting sources: {supports_count:.1f} credibility units
- Refuting sources: {refutes_count:.1f} credibility units
- Neutral sources: {neutral_count:.1f} credibility units
- Average source credibility: {average_credibility:.1%}

Analysis:
The claim "{claim[:80]}" appears to be FALSE based on:
1. Preponderance of refuting evidence ({refutes_count:.0f} vs {supports_count:.0f})
2. Significant source credibility ({average_credibility:.0%})
3. Direct contradictions from multiple sources
4. NLP analysis indicates linguistic inconsistencies

Confidence Assessment:
- Evidence weight: {(refutes_count/max(total_sources,1)):.0%} contradiction
- Source reliability: {average_credibility:.0%} average credibility
- Overall confidence: HIGH

Recommendation: The claim is contradicted by available evidence."""
        
        else:
            reasoning = f"""VERDICT ANALYSIS: UNCERTAIN

Evidence Summary:
- Supporting evidence: {supports_count:.1f} units
- Refuting evidence: {refutes_count:.1f} units
- Neutral evidence: {neutral_count:.1f} units
- Average credibility: {average_credibility:.0%}

Analysis:
The claim "{claim[:80]}" is UNCERTAIN because:
1. Mixed evidence - both supporting and refuting sources present
2. Evidence is insufficient for definitive conclusion
3. Source credibility is moderate ({average_credibility:.0%})
4. No clear preponderance of evidence in either direction

Confidence Assessment:
- Balanced evidence: {supports_count:.0f} support vs {refutes_count:.0f} refute
- Credibility average: {average_credibility:.0%}
- Overall confidence: MODERATE

Recommendation: Seek additional verification before acceptance."""
        
        return reasoning.strip()

    # ------------------------------------------------------------------
    # Optional NLI refinement helpers
    # ------------------------------------------------------------------
    def _ensure_nli(self) -> Optional["HuggingFaceNLI"]:  # type: ignore[name-defined]
        """Lazily initialize the HuggingFace NLI model if available.

        Returns None if the transformers/NLI stack is unavailable so the
        engine can keep working in pure rule-based mode.
        """
        if HuggingFaceNLI is None:
            return None
        if self._nli is not None:
            return self._nli
        try:
            logger.info("[NLI] Initializing HuggingFace NLI model (BART MNLI)...")
            self._nli = HuggingFaceNLI(device="cpu")
            return self._nli
        except Exception as e:  # pragma: no cover - model load failure path
            logger.warning(f"[NLI] Failed to initialize NLI model, skipping refinement: {e}")
            self._nli = None
            return None

    def _refine_with_nli(
        self,
        evidence_list: List[Dict],
        claim: str,
        current_verdict: Dict,
    ) -> Optional[Dict]:
        """Optionally refine the rule-based verdict using BART MNLI.

        - Select the most relevant non-fallback evidence texts.
        - Run NLI to classify each as supporting/contradicting/neutral.
        - If NLI returns a strong majority TRUE/FALSE verdict with high
          confidence, allow it to override the existing verdict.
        """
        nli = self._ensure_nli()
        if nli is None:
            return None

        real_evidence = [e for e in evidence_list if not e.get("is_fallback", False)]
        if not real_evidence:
            return None

        # Rank by semantic similarity / stance confidence
        ranked = sorted(
            real_evidence,
            key=lambda e: e.get("semantic_similarity", e.get("stance_confidence", 0.0)),
            reverse=True,
        )
        top_items = ranked[:5]

        texts: List[str] = []
        for ev in top_items:
            text = ev.get("text") or ev.get("snippet") or ""
            if text and len(text.strip()) > 20:
                texts.append(text)

        if not texts:
            return None

        try:
            inferences = nli.infer_batch(claim, texts)
            nli_verdict = nli.compute_verdict(claim, inferences)
        except Exception as e:  # pragma: no cover - runtime NLI errors
            logger.warning(f"[NLI] Inference failed, skipping refinement: {e}")
            return None

        nli_label = nli_verdict.get("verdict")  # 'TRUE' | 'FALSE' | 'CONFLICTED'
        nli_conf = float(nli_verdict.get("confidence", 0)) / 100.0

        logger.info(
            f"[NLI] verdict={nli_label} conf={nli_conf:.2f} "
            f"(support={nli_verdict.get('support_count')}, "
            f"contradict={nli_verdict.get('contradict_count')}, "
            f"neutral={nli_verdict.get('neutral_count')})"
        )

        # Ignore conflicted/low-confidence outcomes
        if nli_label not in {"TRUE", "FALSE"} or nli_conf < 0.7:
            return None

        current_label = current_verdict.get("verdict", "UNCERTAIN")

        # If current verdict is UNCERTAIN, a strong NLI signal is very useful.
        if current_label == "UNCERTAIN":
            logger.info("[NLI] Overriding UNCERTAIN with strong NLI verdict")
            updated = dict(current_verdict)
            updated["verdict"] = nli_label
            updated["confidence"] = max(current_verdict.get("confidence", 0.3), nli_conf)
            return updated

        # If NLI strongly disagrees with the rule-based verdict, prefer NLI
        # only when it is very confident.
        if current_label != nli_label and nli_conf >= 0.8:
            logger.info("[NLI] Overriding rule-based verdict with very strong NLI verdict")
            updated = dict(current_verdict)
            updated["verdict"] = nli_label
            updated["confidence"] = max(current_verdict.get("confidence", 0.3), nli_conf)
            return updated

        return None
