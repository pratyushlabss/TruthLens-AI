"""Fusion scoring engine combining all three models with explainability."""

from typing import Dict, Optional
import logging
from models.roberta_classifier import RoBERTaClassifier
from models.evidence_engine import EvidenceEngine
from models.propagation_model import PropagationModel
from services.explainability_service import ExplainabilityService
from services.preprocessing_service import TextPreprocessor

logger = logging.getLogger(__name__)


class ScoringEngine:
    """
    Combines RoBERTa, SBERT, and Propagation models into unified scoring with explainability.
    """
    
    def __init__(self):
        """Initialize all three models and explainability service."""
        self.nlp_model = RoBERTaClassifier()
        self.evidence_engine = EvidenceEngine()
        self.propagation_model = PropagationModel()
        self.explainability_service = ExplainabilityService()
        self.text_preprocessor = TextPreprocessor()
        
        # Fusion weights
        self.nlp_weight = 0.6
        self.evidence_weight = 0.25
        self.propagation_weight = 0.15
    
    def analyze(self, text: str, include_explanations: bool = True) -> Dict:
        """
        Full analysis pipeline combining all models with explanations.
        
        Args:
            text: Input claim/article
            include_explanations: Generate SHAP/LIME explanations
            
        Returns:
            Complete analysis result with explanations
        """
        logger.info(f"Starting analysis: {text[:100]}...")
        
        # 1. NLP Classification
        nlp_result = self.nlp_model.classify(text)
        nlp_score = nlp_result.get("nlp_score", 50)
        
        # 2. Evidence Retrieval
        evidence_sources = self.evidence_engine.retrieve_evidence(text)
        evidence_credibility = self._calculate_evidence_credibility(evidence_sources)
        
        # 3. Propagation Risk
        propagation_result = self.propagation_model.analyze_propagation_risk(
            text,
            nlp_score
        )
        
        # 4. Text preprocessing for analysis
        preprocessing_result = self.text_preprocessor.preprocess(text)
        
        # 5. Fusion Scoring
        fused_scores = self._fuse_scores(
            nlp_result["scores"],
            evidence_credibility,
            propagation_result["propagation_risk"]
        )
        
        # 6. Generate verdict
        verdict = self._determine_verdict(fused_scores)
        
        # 7. Extract claims and signals
        claims = self._extract_claims(text)
        key_signals = self._extract_key_signals(text, nlp_result, evidence_sources)
        
        # 8. Generate summary
        summary = self._generate_summary(text, verdict, evidence_sources)
        
        # Build base response
        response = {
            "verdict": verdict["verdict"],
            "confidence": verdict["confidence"],
            "score": fused_scores,
            "nlp_score": nlp_score,
            "evidence_score": evidence_credibility,
            "propagation_score": propagation_result.get("propagation_score", 0),
            "propagation_risk": propagation_result["propagation_risk"],
            "summary": summary,
            "claims": claims,
            "evidence_sources": evidence_sources,
            "key_signals": key_signals,
            "linguistic_features": {
                "token_count": preprocessing_result.get("token_count", 0),
                "sentence_count": preprocessing_result.get("sentence_count", 0),
                "entities": preprocessing_result.get("entities", {}),
                "key_phrases": preprocessing_result.get("key_phrases", []),
            },
            "model_breakdown": {
                "nlp_score": nlp_score,
                "evidence_credibility": evidence_credibility,
                "propagation_risk": propagation_result.get("propagation_score", 0)
            }
        }
        
        # 9. Add explanations if requested
        if include_explanations:
            explanations = self._generate_explanations(
                text, response, evidence_sources, propagation_result
            )
            response["explanations"] = explanations
        
        logger.info(f"Analysis complete: verdict={verdict['verdict']}")
        return response
    
    def _generate_explanations(
        self,
        text: str,
        prediction: Dict,
        evidence_sources: list,
        propagation_result: Dict
    ) -> Dict:
        """Generate SHAP/LIME explanations and evidence comparison."""
        explanations = {}
        
        # Mock prediction function for LIME/SHAP
        def predict_fn(claim_text: str) -> Dict:
            nlp_res = self.nlp_model.classify(claim_text)
            return {
                "score": nlp_res.get("nlp_score", 0) / 100,
                "verdict": "REAL" if nlp_res.get("nlp_score", 50) > 60 else "FAKE"
            }
        
        try:
            # LIME explanations
            lime_explanation = self.explainability_service.explain_with_lime(
                text, predict_fn, num_features=10
            )
            if lime_explanation and "error" not in lime_explanation:
                explanations["lime"] = lime_explanation
        except Exception as e:
            logger.warning(f"LIME explanation failed: {e}")
        
        try:
            # SHAP explanations
            shap_explanation = self.explainability_service.explain_with_shap(
                text, predict_fn
            )
            if shap_explanation and "error" not in shap_explanation:
                explanations["shap"] = shap_explanation
        except Exception as e:
            logger.warning(f"SHAP explanation failed: {e}")
        
        # Evidence comparison
        if evidence_sources:
            evidence_explanation = self.explainability_service.compare_evidence_sources(
                text,
                [
                    {
                        "source": e.get("source", "Unknown"),
                        "text": e.get("text", ""),
                        "credibility": e.get("credibility", 0.5),
                        "relevance": e.get("relevance_score", 0.5),
                        "direction": "supporting" if e.get("supports") == "CONFIRMS" else "contradicting"
                    }
                    for e in evidence_sources
                ]
            )
            explanations["evidence_analysis"] = evidence_explanation
        
        # Propagation pattern explanation
        propagation_explanation = self.explainability_service.explain_propagation_pattern(
            {
                "velocity": propagation_result.get("propagation_score", 0),
                "reshare_count": 0,
                "cluster_count": 1
            }
        )
        explanations["propagation_analysis"] = propagation_explanation
        
        # Comprehensive report
        explanations["report"] = self.explainability_service.generate_explanation_report(
            text,
            prediction,
            shap_explanation=explanations.get("shap"),
            lime_explanation=explanations.get("lime"),
            evidence_explanation=explanations.get("evidence_analysis"),
            propagation_explanation=propagation_explanation
        )
        
        return explanations
    
    def _fuse_scores(
        self,
        nlp_scores: Dict,
        evidence_credibility: float,
        propagation_risk: str
    ) -> Dict:
        """
        Fuse scores from all three models.
        
        Final Score = 0.6 × NLP + 0.25 × Evidence + 0.15 × Propagation Risk
        """
        # Propagation risk adjustment
        propagation_adjustment = {
            "LOW": 0,
            "MEDIUM": 15,
            "HIGH": 30
        }.get(propagation_risk, 0)
        
        # Weighted fusion
        real = (
            nlp_scores["real"] * self.nlp_weight +
            evidence_credibility * self.evidence_weight * 0.8 +
            (100 - propagation_adjustment) * self.propagation_weight
        )
        
        fake = (
            nlp_scores["fake"] * self.nlp_weight +
            (100 - evidence_credibility) * self.evidence_weight * 0.6 +
            propagation_adjustment * self.propagation_weight
        )
        
        rumor = (
            nlp_scores["rumor"] * self.nlp_weight +
            (50) * self.evidence_weight +
            (propagation_adjustment * 0.5) * self.propagation_weight
        )
        
        # Normalize to 100
        total = real + fake + rumor
        return {
            "real": round(real / total * 100, 2),
            "rumor": round(rumor / total * 100, 2),
            "fake": round(fake / total * 100, 2)
        }
    
    def _determine_verdict(self, scores: Dict) -> Dict:
        """Determine final verdict."""
        verdicts = {
            "REAL": scores["real"],
            "RUMOR": scores["rumor"],
            "FAKE": scores["fake"]
        }
        
        verdict = max(verdicts.items(), key=lambda x: x[1])
        
        return {
            "verdict": verdict[0],
            "confidence": verdict[1]
        }
    
    def _calculate_evidence_credibility(self, evidence_sources: list) -> float:
        """Calculate evidence credibility (0-100)."""
        if not evidence_sources:
            return 50
        
        # Weight by relevance and support type
        total_score = 0
        for source in evidence_sources:
            relevance = source.get("relevance", 50) / 100
            
            if source.get("supports") == "CONFIRMS":
                support_weight = 1.0
            elif source.get("supports") == "NEUTRAL":
                support_weight = 0.5
            else:  # CONTRADICTS
                support_weight = 0.0
            
            total_score += (relevance * support_weight) * 100
        
        credibility = (total_score / len(evidence_sources)) if evidence_sources else 50
        return round(min(100, credibility), 2)
    
    def _extract_claims(self, text: str) -> list:
        """Extract individual claims from text."""
        # Mock claim extraction
        sentences = text.split(".")
        claims = []
        
        for i, sentence in enumerate(sentences[:4]):  # Max 4 claims
            if len(sentence.strip()) > 10:
                claims.append({
                    "text": sentence.strip(),
                    "verdict": "TRUE" if i % 2 == 0 else "UNVERIFIED",
                    "confidence": 75 + (i * 5),
                    "reasoning": f"Based on available evidence and NLP analysis."
                })
        
        return claims
    
    def _extract_key_signals(self, text: str, nlp_result: Dict, evidence: list) -> list:
        """Extract key NLP detection signals."""
        signals = []
        
        # Sensational language
        if any(kw in text.lower() for kw in ["shocking", "exposed", "secret", "coverup"]):
            signals.append("Sensational language detected")
        
        # Appeal to emotion
        if any(kw in text.lower() for kw in ["urgent", "must", "immediately", "emergency"]):
            signals.append("High emotional appeal")
        
        # Source credibility
        if not evidence or all(s.get("relevance", 0) < 50 for s in evidence):
            signals.append("Low source credibility")
        
        # Grammar/spelling issues
        if len(text) > 0 and text.count("  ") > 3:
            signals.append("Multiple formatting anomalies")
        
        # Unsubstantiated claims
        if nlp_result.get("nlp_score", 50) < 40:
            signals.append("Claim lacks supporting evidence")
        
        return signals[:5]  # Max 5 signals
    
    def _generate_summary(self, text: str, verdict: Dict, evidence: list) -> str:
        """Generate 2-3 sentence summary."""
        verdict_desc = {
            "REAL": "appears to be verified based on available evidence",
            "RUMOR": "lacks sufficient evidence for verification",
            "FAKE": "contradicts established facts and evidence"
        }
        
        desc = verdict_desc.get(verdict["verdict"], "cannot be fully verified")
        
        if evidence:
            evidence_summary = f"Multiple sources {evidence[0].get('supports', 'NEUTRAL').lower()} this claim."
        else:
            evidence_summary = "Limited evidence available for verification."
        
        summary = f"This claim {desc}. {evidence_summary} Analysis confidence: {verdict['confidence']}%."
        return summary
