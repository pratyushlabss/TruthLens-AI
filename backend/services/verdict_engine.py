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
        nlp_score: float,  # kept for API compatibility
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
        
        explanation, reasoning = self._generate_explanations(
            verdict_type=verdict_type,
            evidence_list=evidence_list,
            supports_count=supports_count,
            refutes_count=refutes_count,
            neutral_count=neutral_count,
            average_credibility=average_credibility,
            claim=claim,
        )

        logger.info(f"[VERDICT] Final verdict: {verdict_type.value} (confidence: {confidence:.2f})")

        return {
            "verdict": verdict_type.value,
            "confidence": min(max(confidence, 0.1), 0.95),
            "explanation": explanation,
            "reasoning": reasoning,
            "signals": self._build_signals(verdict_type, evidence_list, supports_count, refutes_count),
            "is_fallback": False,
        }
    
    def _uncertain_verdict(
        self,
        reason: str = "No evidence found",
        claim: str = "",
        is_fallback: bool = False
    ) -> Dict:
        """Generate a concise uncertain verdict with explanation and signals.
        
        Args:
            reason: why uncertain
            nlp_score: NLP score
            claim: the claim
            is_fallback: if using fallback evidence
            
        Returns:
            Detailed uncertain verdict
        """
        claim_short = claim[:80] + ("…" if len(claim) > 80 else "")
        explanation = (
            f"The claim could not be definitively verified or falsified. "
            f"{'Only system-generated evidence was available.' if is_fallback else reason}"
        )
        reasoning = (
            f"Insufficient reliable evidence was found for \"{claim_short}\". "
            f"{'Search engines were unavailable; only internal analysis was performed.' if is_fallback else reason + ' Consider consulting additional authoritative sources.'}"
        )
        signals = [
            "⚠️ Verdict: UNCERTAIN",
            f"⚠️ {'No external sources available' if is_fallback else 'Insufficient evidence'}",
            "💡 Recommend cross-checking with authoritative sources",
        ]

        return {
            "verdict": "UNCERTAIN",
            "confidence": 0.3,
            "explanation": explanation,
            "reasoning": reasoning,
            "signals": signals,
            "is_fallback": is_fallback,
        }
    
    # ------------------------------------------------------------------
    # Explanation + signal generation
    # ------------------------------------------------------------------

    def _source_names(self, evidence_list: List[Dict], stance_filter: str = None) -> List[str]:
        """Return unique, human-readable source names from evidence."""
        seen, names = set(), []
        for ev in evidence_list:
            if ev.get("is_fallback"):
                continue
            if stance_filter and ev.get("stance") != stance_filter:
                continue
            src = ev.get("source", "")
            if src and src not in seen:
                seen.add(src)
                names.append(src)
        return names[:4]

    def _generate_explanations(
        self,
        verdict_type: VerdictType,
        evidence_list: List[Dict],
        supports_count: float,
        refutes_count: float,
        neutral_count: float,
        average_credibility: float,
        claim: str,
    ):
        """Return (explanation, reasoning) as a concise sentence + short paragraph."""
        total = supports_count + refutes_count + neutral_count or 1.0
        real = [e for e in evidence_list if not e.get("is_fallback")]
        real_count = len(real)
        cred_pct = int(average_credibility * 100)
        claim_short = claim[:80] + ("…" if len(claim) > 80 else "")

        if verdict_type == VerdictType.TRUE:
            support_src = self._source_names(evidence_list, "SUPPORTS")
            src_str = (", ".join(support_src[:3]) + " and others") if support_src else "multiple sources"
            explanation = (
                f"The claim appears to be supported by available evidence. "
                f"{int(supports_count / total * 100)}% of sources support it, "
                f"with an average credibility of {cred_pct}%."
            )
            reasoning = (
                f"Analysis of {real_count} source(s) found that {src_str} support "
                f"the claim \"{claim_short}\". "
                f"Supporting evidence outweighs refuting evidence "
                f"({supports_count:.1f} vs {refutes_count:.1f} credibility-weighted units). "
                f"Sources averaged {cred_pct}% credibility."
            )

        elif verdict_type == VerdictType.FALSE:
            refute_src = self._source_names(evidence_list, "REFUTES")
            src_str = (", ".join(refute_src[:3]) + " and others") if refute_src else "multiple sources"
            explanation = (
                f"The claim appears to be false or misleading. "
                f"{int(refutes_count / total * 100)}% of sources contradict it, "
                f"with an average credibility of {cred_pct}%."
            )
            reasoning = (
                f"Analysis of {real_count} source(s) found that {src_str} contradict "
                f"the claim \"{claim_short}\". "
                f"Refuting evidence outweighs supporting evidence "
                f"({refutes_count:.1f} vs {supports_count:.1f} credibility-weighted units). "
                f"Sources averaged {cred_pct}% credibility."
            )

        else:
            explanation = (
                f"The evidence is mixed or insufficient to reach a definitive verdict. "
                f"Supporting and refuting sources are roughly balanced."
            )
            reasoning = (
                f"Analysis of {real_count} source(s) for the claim \"{claim_short}\" "
                f"found no clear consensus: {supports_count:.1f} credibility units support it, "
                f"{refutes_count:.1f} contradict it, and {neutral_count:.1f} are neutral. "
                f"Seek additional authoritative sources before accepting or rejecting this claim."
            )

        return explanation, reasoning

    def _build_signals(
        self,
        verdict_type: VerdictType,
        evidence_list: List[Dict],
        supports_count: float,
        refutes_count: float,
    ) -> List[str]:
        """Build a short list of key signals shown in the UI."""
        signals = []
        real = [e for e in evidence_list if not e.get("is_fallback")]

        if verdict_type == VerdictType.TRUE:
            signals.append(f"✅ {len(real)} source(s) analyzed")
            signals.append(f"✅ Supporting evidence weight: {supports_count:.1f}")
            if refutes_count > 0:
                signals.append(f"⚠️ Some refuting evidence present: {refutes_count:.1f}")
        elif verdict_type == VerdictType.FALSE:
            signals.append(f"🔍 {len(real)} source(s) analyzed")
            signals.append(f"❌ Refuting evidence weight: {refutes_count:.1f}")
            if supports_count > 0:
                signals.append(f"⚠️ Some supporting evidence present: {supports_count:.1f}")
        else:
            signals.append(f"🔍 {len(real)} source(s) analyzed")
            signals.append("⚠️ Mixed or insufficient evidence")

        # Add top-credibility source names
        for ev in sorted(real, key=lambda e: e.get("credibility", 0), reverse=True)[:2]:
            src = ev.get("source", "")
            stance = ev.get("stance", "NEUTRAL")
            icon = "✅" if stance == "SUPPORTS" else ("❌" if stance == "REFUTES" else "➖")
            if src:
                signals.append(f"{icon} {src} — {stance.lower()}")

        return signals

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
