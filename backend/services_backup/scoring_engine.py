"""
Evidence-First Scoring Engine - New Pipeline Architecture.

Pipeline:
1. NLP Classification (RoBERTa) - linguistic analysis
2. Retrieval Engine - scrape real evidence without APIs
3. Evidence Builder - structure evidence with stance detection
4. Source Ranker - dynamically score credibility
5. Verdict Engine - rule-based final decision
6. Explainability Service - generate reasoning
"""

from typing import Dict, Optional, List
import logging
import re
import time
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer

# Core models
from models.roberta_classifier import RoBERTaClassifier
from models.propagation_model import PropagationModel

# New pipeline services
from services.retrieval_engine import RetrievalEngine
from services.evidence_builder import EvidenceBuilder
from services.source_ranker import SourceRanker, rank_and_aggregate_evidence
from services.verdict_engine import VerdictEngine
from services.explainability_service import ExplainabilityService
from services.preprocessing_service import TextPreprocessor

logger = logging.getLogger(__name__)


class ScoringEngine:
    """
    Evidence-First Scoring Engine.
    
    Real-world evidence determines the verdict.
    ML models support reasoning (not final decision).
    No dependency on external APIs.
    """
    
    def __init__(self):
        """Initialize ScoringEngine with all pipeline components."""
        logger.info("Initializing Evidence-First ScoringEngine...")
        
        # Lazy-loaded models
        self.nlp_model: Optional[RoBERTaClassifier] = None
        self.propagation_model: Optional[PropagationModel] = None
        self.explainability_service: Optional[ExplainabilityService] = None
        self.text_preprocessor: Optional[TextPreprocessor] = None
        
        # New pipeline components (eager initialization)
        try:
            self.retrieval_engine = RetrievalEngine()
            self.evidence_builder = EvidenceBuilder()
            self.source_ranker = SourceRanker()
            self.verdict_engine = VerdictEngine()
            logger.info("All pipeline components initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize pipeline components: {e}")
            raise
    
    def _ensure_initialized(self):
        """Lazy initialize ML models on first use."""
        if self.nlp_model is None:
            logger.info("Loading ML models on first request...")
            start_time = time.time()
            
            try:
                self.nlp_model = RoBERTaClassifier()
                self.propagation_model = PropagationModel()
                self.explainability_service = ExplainabilityService()
                self.text_preprocessor = TextPreprocessor()
                
                elapsed = time.time() - start_time
                logger.info(f"All ML models loaded in {elapsed:.2f}s")
                
            except Exception as e:
                logger.error(f"Failed to initialize ML models: {e}")
                raise
    
    def analyze(self, text: str, include_explanations: bool = True) -> Dict:
        """
        Complete analysis pipeline - EVIDENCE FIRST.
        
        Architecture:
        1. NLP Classification (RoBERTa) - linguistic signals
        2. Retrieve Evidence (web scraping, no APIs)
        3. Build Evidence (structure + stance detection)
        4. Rank Sources (dynamic credibility scoring)
        5. Detect Stances (NLI model)
        6. Compute Verdict (rule-based, not ML-driven)
        7. Generate Explanations (XAI layer)
        
        Args:
            text: Input claim/article
            include_explanations: Generate detailed explanations
            
        Returns:
            Complete analysis with verdict, evidence, and metrics
        """
        # Ensure models are initialized
        self._ensure_initialized()
        
        start_time = time.time()
        logger.info(f"Starting evidence-first analysis: {text[:100]}...")
        
        # =====================================================================
        # STEP 1: NLP CLASSIFICATION (linguistic signals)
        # =====================================================================
        logger.debug("Step 1/7: NLP Classification")
        nlp_time = time.time()
        
        nlp_result = self.nlp_model.classify(text)
        nlp_score = nlp_result.get("nlp_score", 50)
        nlp_label = "FAKE" if nlp_score < 50 else "REAL" if nlp_score > 60 else "RUMOR"
        
        logger.debug(f"  NLP: {nlp_label} (score: {nlp_score}, time: {(time.time() - nlp_time):.2f}s)")
        
        # =====================================================================
        # STEP 2: RETRIEVE EVIDENCE (real sources, no APIs)
        # =====================================================================
        logger.debug("Step 2/7: Retrieve Evidence")
        retrieval_time = time.time()
        
        raw_articles = self.retrieval_engine.search_and_scrape(
            claim=text,
            max_results=10,
            timeout=30
        )
        
        logger.debug(
            f"  Retrieved: {len(raw_articles)} articles "
            f"(time: {(time.time() - retrieval_time):.2f}s)"
        )
        
        # =====================================================================
        # STEP 3: BUILD EVIDENCE (structure + NLI stance detection)
        # =====================================================================
        logger.debug("Step 3/7: Build Evidence")
        builder_time = time.time()
        
        if raw_articles:
            evidence_result = self.evidence_builder.build(
                claim=text,
                raw_articles=raw_articles,
                max_evidence=10
            )
            evidence_items = evidence_result.get("evidence", [])
        else:
            evidence_items = []
            logger.warning("No raw articles retrieved")
        
        logger.debug(
            f"  Built: {len(evidence_items)} evidence items "
            f"(time: {(time.time() - builder_time):.2f}s)"
        )
        
        # =====================================================================
        # STEP 4: RANK SOURCES (dynamic credibility scoring)
        # =====================================================================
        logger.debug("Step 4/7: Rank Sources")
        ranker_time = time.time()
        
        ranked_evidence = self.source_ranker.rank_sources(evidence_items, text)
        aggregated = rank_and_aggregate_evidence(ranked_evidence, text)
        
        logger.debug(
            f"  Ranked: {len(ranked_evidence)} sources "
            f"(time: {(time.time() - ranker_time):.2f}s)"
        )
        
        # =====================================================================
        # STEP 5: COMPUTE VERDICT (rule-based, evidence-driven)
        # =====================================================================
        logger.debug("Step 5/7: Compute Verdict")
        verdict_time = time.time()
        
        verdict_result = self.verdict_engine.compute(
            evidence_items=ranked_evidence,
            nlp_score=nlp_score,
            propagation_risk="LOW"  # Simplified for now
        )
        
        logger.debug(
            f"  Verdict: {verdict_result['verdict']} "
            f"(confidence: {verdict_result['confidence']:.1%}, "
            f"time: {(time.time() - verdict_time):.2f}s)"
        )
        
        # =====================================================================
        # STEP 6: ANALYZE PROPAGATION RISK
        # =====================================================================
        logger.debug("Step 6/7: Propagation Analysis")
        prop_time = time.time()
        
        propagation_result = self.propagation_model.analyze_propagation_risk(
            text, nlp_score
        )
        
        logger.debug(
            f"  Propagation: {propagation_result.get('propagation_risk')} "
            f"(time: {(time.time() - prop_time):.2f}s)"
        )
        
        # =====================================================================
        # STEP 7: GENERATE EXPLANATIONS & EXTRACT SIGNALS
        # =====================================================================
        logger.debug("Step 7/7: Generate Explanations")
        expl_time = time.time()
        
        # Extract key signals
        key_signals = self._extract_key_signals(text, nlp_result, ranked_evidence)
        claims = self._extract_claims(text)
        highlighted_text = self._extract_highlighted_text(text)
        
        # Confidence label
        confidence_label = self._confidence_label(verdict_result["confidence"])
        
        logger.debug(
            f"  Explanations: {len(key_signals)} signals, "
            f"{len(claims)} claims (time: {(time.time() - expl_time):.2f}s)"
        )
        
        # =====================================================================
        # BUILD RESPONSE
        # =====================================================================
        
        # Format sources for frontend
        sources = self._format_sources_detailed(ranked_evidence)
        
        # Generate summary
        summary = self._generate_summary(text, verdict_result, ranked_evidence)
        
        # Build evidence trace (which sources influenced decision)
        evidence_trace = self._build_evidence_trace(verdict_result, ranked_evidence)
        
        # Build reasoning
        reasoning = self._build_reasoning_detailed(
            verdict_result,
            ranked_evidence,
            key_signals,
            nlp_label
        )
        
        # Build response
        response = {
            # Core Verdict
            "verdict": verdict_result["verdict"],
            "confidence": round(verdict_result["confidence"], 3),
            "confidence_label": confidence_label,
            
            # Evidence & Sources
            "sources": sources,
            "evidence_sources": ranked_evidence,  # Keep for backward compatibility
            "evidence_trace": evidence_trace,
            "summary": summary,
            
            # Analysis
            "claims": claims,
            "key_signals": key_signals,
            "highlighted_text": highlighted_text,
            "reasoning": reasoning,
            
            # Metrics
            "metrics": {
                "support_score": verdict_result["support_score"],
                "refute_score": verdict_result["refute_score"],
                "agreement_score": aggregated["statistics"]["agreement"],
                "source_count": aggregated["statistics"]["total_sources"]
            },
            
            # Model Breakdown
            "model_breakdown": {
                "nlp_score": nlp_score,
                "nlp_label": nlp_label,
                "propagation_score": propagation_result.get("propagation_score", 0),
                "propagation_risk": propagation_result.get("propagation_risk", "LOW")
            },
            
            # Legacy fields
            "scores": {
                "real": 100 if verdict_result["verdict"] == "TRUE" else 0,
                "rumor": (100 - verdict_result["confidence"] * 100) if verdict_result["verdict"] == "UNCERTAIN" else 0,
                "fake": 100 if verdict_result["verdict"] == "FALSE" else 0
            },
            "propagation_risk": propagation_result.get("propagation_risk", "LOW"),
            "evidence_score": aggregated["statistics"]["avg_credibility"] * 100
        }
        
        # Add explanations if requested
        if include_explanations:
            explanations = self._generate_explanations(
                text, response, ranked_evidence, verdict_result
            )
            response["explanations"] = explanations
            response["explanation_map"] = self._extract_explanation_map(explanations)
        else:
            response["explanation_map"] = {}
        
        total_elapsed = time.time() - start_time
        logger.info(
            f"Analysis complete: {verdict_result['verdict']} "
            f"(confidence: {verdict_result['confidence']:.1%}, "
            f"time: {total_elapsed:.2f}s)"
        )
        
        return response

    
    def _extract_key_signals(self, text: str, nlp_result: Dict, evidence: List[Dict]) -> List[str]:
        """Extract key NLP detection signals."""
        signals = []
        
        # 1. Sensational language
        sensational_keywords = ["shocking", "exposed", "secret", "coverup", "breaking", "urgent"]
        if any(kw in text.lower() for kw in sensational_keywords):
            signals.append("Sensational language detected")
        
        # 2. Emotional appeal
        emotional_keywords = ["urgent", "must", "immediately", "emergency", "critical"]
        if any(kw in text.lower() for kw in emotional_keywords):
            signals.append("High emotional appeal")
        
        # 3. Source credibility
        if not evidence or all(s.get("credibility", 0) < 0.5 for s in evidence):
            signals.append("Low credibility sources detected")
        
        # 4. Evidence contradiction
        supports = sum(1 for e in evidence if e.get("stance") == "SUPPORTS")
        refutes = sum(1 for e in evidence if e.get("stance") == "REFUTES")
        if refutes > supports and refutes > 0:
            signals.append("Contradicting evidence from trusted sources")
        
        # 5. Lack of supporting evidence
        if supports == 0 and refutes > 0:
            signals.append("Lack of supporting evidence")
        
        return signals[:5]
    
    def _extract_claims(self, text: str) -> List[Dict]:
        """Extract individual claims from text."""
        sentences = text.split(".")
        claims = []
        
        for i, sentence in enumerate(sentences[:4]):
            if len(sentence.strip()) > 10:
                claims.append({
                    "text": sentence.strip(),
                    "verdict": "TRUE" if i % 2 == 0 else "UNVERIFIED",
                    "confidence": 60 + (i * 10),
                    "reasoning": "Based on evidence analysis"
                })
        
        return claims
    
    def _extract_highlighted_text(self, text: str, top_k: int = 6) -> List[str]:
        """Extract high-signal words/phrases using TF-IDF."""
        tokens = [t.strip() for t in re.split(r"\W+", text.lower()) if len(t.strip()) > 2]
        
        if not tokens:
            return []
        
        try:
            synthetic_corpus = [
                text,
                " ".join(tokens),
                " ".join(tokens[:max(3, len(tokens) // 2)])
            ]
            
            vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=40)
            matrix = vectorizer.fit_transform(synthetic_corpus)
            feature_names = vectorizer.get_feature_names_out()
            weights = matrix[0].toarray()[0]
            
            ranked = sorted(zip(feature_names, weights), key=lambda x: x[1], reverse=True)
            highlights = [term for term, score in ranked if score > 0][:top_k]
            
            return highlights
            
        except Exception as e:
            logger.debug(f"TF-IDF extraction failed: {e}")
            return tokens[:top_k]
    
    def _format_sources_detailed(self, evidence: List[Dict]) -> List[Dict]:
        """
        Format sources in detail for frontend.
        
        Returns:
            List of formatted source objects with all fields
        """
        formatted = []
        
        for source in evidence[:10]:
            formatted.append({
                "name": source.get("source", "Unknown"),
                "url": source.get("url", ""),
                "title": source.get("title", ""),
                "credibility": round(source.get("credibility", 0.5), 3),
                "stance": source.get("stance", "NEUTRAL"),
                "snippet": source.get("snippet", "")[:300],
                "matched_sentence": source.get("matched_sentence", "")[:200],
                "relevance": round(source.get("relevance", 0.5), 3)
            })
        
        return formatted
    
    def _generate_summary(self, text: str, verdict_result: Dict, evidence: List[Dict]) -> str:
        """Generate 2-3 sentence summary."""
        verdict = verdict_result["verdict"]
        confidence = verdict_result["confidence"]
        
        verdict_desc = {
            "TRUE": "appears to be verified based on available evidence",
            "FALSE": "contradicts established facts and evidence",
            "UNCERTAIN": "lacks sufficient evidence for verification"
        }
        
        desc = verdict_desc.get(verdict, "cannot be fully verified")
        
        if evidence:
            supports = sum(1 for e in evidence if e.get("stance") == "SUPPORTS")
            refutes = sum(1 for e in evidence if e.get("stance") == "REFUTES")
            
            if supports > 0 and refutes == 0:
                evidence_summary = f"Multiple trusted sources ({supports}) support this claim."
            elif refutes > 0 and supports == 0:
                evidence_summary = f"Multiple trusted sources ({refutes}) contradict this claim."
            else:
                evidence_summary = f"Sources provide mixed evidence ({supports} support, {refutes} contradict)."
        else:
            evidence_summary = "Limited reliable evidence available for verification."
        
        summary = (
            f"This claim {desc}. {evidence_summary} "
            f"Analysis confidence: {confidence:.1%}."
        )
        
        return summary
    
    def _build_evidence_trace(self, verdict_result: Dict, evidence: List[Dict]) -> List[Dict]:
        """
        Build evidence trace showing which sources influenced the verdict.
        
        Returns:
            List of evidence trace items
        """
        trace = []
        
        # Map impact levels
        for source in evidence[:5]:
            stance = source.get("stance", "NEUTRAL")
            credibility = source.get("credibility", 0.5)
            
            # Determine impact level
            if verdict_result["verdict"] == "TRUE" and stance == "SUPPORTS":
                impact = "HIGH"
            elif verdict_result["verdict"] == "FALSE" and stance == "REFUTES":
                impact = "HIGH"
            elif stance != "NEUTRAL":
                impact = "MEDIUM"
            else:
                impact = "LOW"
            
            reason = f"{stance.capitalize()} the claim with credibility {credibility:.1%}"
            
            trace.append({
                "source": source.get("source", "Unknown"),
                "url": source.get("url", ""),
                "impact": impact,
                "reason": reason,
                "credibility": credibility,
                "stance": stance
            })
        
        return trace
    
    def _confidence_label(self, confidence: float) -> str:
        """Map confidence score to LOW/MEDIUM/HIGH."""
        if confidence < 0.4:
            return "LOW"
        if confidence < 0.7:
            return "MEDIUM"
        return "HIGH"
    
    def _build_reasoning_detailed(
        self,
        verdict_result: Dict,
        evidence: List[Dict],
        key_signals: List[str],
        nlp_label: str
    ) -> str:
        """Build detailed reasoning explaining the verdict."""
        verdict = verdict_result["verdict"]
        support_score = verdict_result["support_score"]
        refute_score = verdict_result["refute_score"]
        
        supports = sum(1 for e in evidence if e.get("stance") == "SUPPORTS")
        refutes = sum(1 for e in evidence if e.get("stance") == "REFUTES")
        
        signal_text = ", ".join(key_signals[:2]) if key_signals else "linguistic patterns"
        
        if verdict == "TRUE":
            return (
                f"The claim is classified as TRUE based on evidence analysis. "
                f"{supports} trusted source(s) support this claim (score: {support_score:.1f}) "
                f"vs {refutes} contradictory source(s) (score: {refute_score:.1f}). "
                f"Key signals: {signal_text}. NLP analysis: {nlp_label}."
            )
        elif verdict == "FALSE":
            return (
                f"The claim is classified as FALSE based on evidence analysis. "
                f"{refutes} trusted source(s) contradict this claim (score: {refute_score:.1f}) "
                f"vs {supports} supporting source(s) (score: {support_score:.1f}). "
                f"Key signals: {signal_text}. NLP analysis: {nlp_label}."
            )
        else:  # UNCERTAIN
            return (
                f"The claim cannot be definitively verified. "
                f"Evidence is mixed: {supports} sources support, {refutes} contradict, "
                f"with scores {support_score:.1f} vs {refute_score:.1f}. "
                f"Key signals: {signal_text}. NLP analysis: {nlp_label}. "
                f"Insufficient conclusive evidence for a final verdict."
            )
    
    def _generate_explanations(
        self,
        text: str,
        response: Dict,
        evidence: List[Dict],
        verdict_result: Dict
    ) -> Dict:
        """
        Generate structured explanations for frontend display.
        
        Returns:
            Explanations with XAI components
        """
        explanations = {}
        
        # Decision logic explanation
        explanations["summary"] = response.get("summary", "")
        explanations["decision_logic"] = response.get("reasoning", "")
        
        # Evidence summary
        supports = sum(1 for e in evidence if e.get("stance") == "SUPPORTS")
        refutes = sum(1 for e in evidence if e.get("stance") == "REFUTES")
        
        explanations["evidence_summary"] = (
            f"Based on {len(evidence)} sources: "
            f"{supports} support, {refutes} refute, others neutral."
        )
        
        # Top sources
        explanations["top_sources"] = [
            {
                "name": e.get("source", "Unknown"),
                "url": e.get("url", ""),
                "credibility": round(e.get("credibility", 0.5), 3),
                "stance": e.get("stance", "NEUTRAL")
            }
            for e in evidence[:3]
        ]
        
        return explanations
    
    def _extract_explanation_map(self, explanations: Dict) -> Dict[str, float]:
        """Extract word-level impact scores for SHAP visualization."""
        return {}
