"""Explainability service for interpretable AI predictions."""

import logging
from typing import Dict, List, Any, Callable
import numpy as np
import shap
from lime.lime_text import LimeTextExplainer
import json

logger = logging.getLogger(__name__)


class ExplainabilityService:
    """Provides SHAP and LIME explanations for model predictions."""

    def __init__(self):
        """Initialize explainability service."""
        self.lime_explainer = LimeTextExplainer(class_names=["Not Misinformation", "Misinformation"])
        logger.info("Initialized explainability service")

    def explain_with_shap(
        self,
        text: str,
        predict_fn: Callable,
        background_data: List[str] = None,
        num_samples: int = 100,
    ) -> Dict:
        """
        Generate SHAP explanations for a prediction.

        Args:
            text: Input text to explain
            predict_fn: Model prediction function
            background_data: Background samples for baseline
            num_samples: Number of samples for SHAP

        Returns:
            Dictionary with SHAP explanation
        """
        logger.info(f"Generating SHAP explanation for: {text[:100]}...")

        try:
            # Create a simple wrapper that returns probabilities
            def wrapped_predict(texts):
                predictions = []
                for t in texts:
                    try:
                        pred = predict_fn(t)
                        if isinstance(pred, dict):
                            # Extract probability for positive class
                            prob = pred.get("score", 0.5)
                        else:
                            prob = pred
                        predictions.append([1 - prob, prob])
                    except Exception as e:
                        logger.warning(f"Error in prediction: {e}")
                        predictions.append([0.5, 0.5])
                return np.array(predictions)

            # Use background data or create default
            if background_data is None:
                background_data = [
                    "this is a factual statement",
                    "this is likely misinformation",
                ]

            # Create explainer
            masker = shap.maskers.Text(wrapped_predict, background_data[0])
            explainer = shap.Explainer(wrapped_predict, masker=masker)

            # Generate explanation
            shap_values = explainer([text])

            # Extract feature importance
            feature_importance = {}
            if hasattr(shap_values, "values"):
                # Get SHAP values for positive class
                shap_vals = shap_values.values[0, :, 1]
                base_value = shap_values.base_values[0, 1]

                # Get the text tokens/words
                tokens = text.split()
                for i, token in enumerate(tokens):
                    if i < len(shap_vals):
                        feature_importance[token] = float(shap_vals[i])

            # Sort by absolute impact
            sorted_features = sorted(
                feature_importance.items(),
                key=lambda x: abs(x[1]),
                reverse=True,
            )

            return {
                "method": "SHAP",
                "top_features": sorted_features[:10],
                "feature_importance": feature_importance,
                "base_value": float(base_value) if "base_value" in locals() else 0.5,
                "model_output": float(wrapped_predict([text])[0, 1]),
            }

        except Exception as e:
            logger.error(f"SHAP explanation failed: {e}")
            return {"method": "SHAP", "error": str(e), "top_features": []}

    def explain_with_lime(
        self,
        text: str,
        predict_fn: Callable,
        num_features: int = 10,
        num_samples: int = 1000,
    ) -> Dict:
        """
        Generate LIME explanations for a prediction.

        Args:
            text: Input text to explain
            predict_fn: Model prediction function that returns [prob_class0, prob_class1]
            num_features: Number of features to explain
            num_samples: Number of perturbed samples

        Returns:
            Dictionary with LIME explanation
        """
        logger.info(f"Generating LIME explanation for: {text[:100]}...")

        try:
            # Wrapper function for LIME
            def predict_proba(texts):
                predictions = []
                for t in texts:
                    try:
                        pred = predict_fn(t)
                        if isinstance(pred, dict):
                            # Extract probability for positive class
                            prob = pred.get("score", 0.5)
                        else:
                            prob = pred
                        predictions.append([1 - prob, prob])
                    except Exception as e:
                        logger.warning(f"Error in prediction: {e}")
                        predictions.append([0.5, 0.5])
                return np.array(predictions)

            # Generate explanation
            explanation = self.lime_explainer.explain_instance(
                text,
                predict_proba,
                num_features=num_features,
                num_samples=num_samples,
            )

            # Extract feature importance
            feature_importance = dict(explanation.as_list())

            return {
                "method": "LIME",
                "prediction": explanation.predict_proba[1],  # Probability of class 1
                "top_features": explanation.as_list()[:10],
                "feature_importance": feature_importance,
                "predicted_class": int(round(explanation.predict_proba[1])),
                "confidence": float(max(explanation.predict_proba)),
            }

        except Exception as e:
            logger.error(f"LIME explanation failed: {e}")
            return {"method": "LIME", "error": str(e), "top_features": []}

    def compare_evidence_sources(self, claim: str, evidence: List[Dict]) -> Dict:
        """
        Compare and explain prediction based on evidence sources.

        Args:
            claim: The claim being analyzed
            evidence: List of evidence dictionary with source, text, credibility

        Returns:
            Dictionary with source comparison
        """
        logger.info(f"Comparing {len(evidence)} evidence sources")

        supporting = []
        contradicting = []
        neutral = []

        for item in evidence:
            credibility = item.get("credibility", 0.5)
            relevance = item.get("relevance", 0.5)
            direction = item.get("direction", "neutral")  # supporting/contradicting/neutral

            weighted_score = credibility * relevance

            if direction == "supporting":
                supporting.append((item.get("source"), weighted_score))
            elif direction == "contradicting":
                contradicting.append((item.get("source"), weighted_score))
            else:
                neutral.append((item.get("source"), weighted_score))

        # Calculate aggregate scores
        supporting_strength = sum(s[1] for s in supporting) / len(supporting) if supporting else 0
        contradicting_strength = (
            sum(c[1] for c in contradicting) / len(contradicting)
            if contradicting
            else 0
        )
        neutral_strength = sum(n[1] for n in neutral) / len(neutral) if neutral else 0

        return {
            "claim": claim,
            "supporting_evidence": supporting,
            "supporting_strength": float(supporting_strength),
            "contradicting_evidence": contradicting,
            "contradicting_strength": float(contradicting_strength),
            "neutral_evidence": neutral,
            "neutral_strength": float(neutral_strength),
            "net_support": float(supporting_strength - contradicting_strength),
            "total_sources": len(evidence),
        }

    def explain_propagation_pattern(
        self, propagation_data: Dict
    ) -> Dict:
        """
        Explain propagation analysis results.

        Args:
            propagation_data: Propagation metrics

        Returns:
            Dictionary with explanation
        """
        logger.info("Explaining propagation pattern")

        velocity = propagation_data.get("velocity", 0)
        reshare_count = propagation_data.get("reshare_count", 0)
        cluster_count = propagation_data.get("cluster_count", 1)

        # Risk assessment
        if velocity > 1000:
            velocity_risk = "VERY HIGH - Extremely rapid spread"
        elif velocity > 500:
            velocity_risk = "HIGH - Rapid viral spread detected"
        elif velocity > 100:
            velocity_risk = "MEDIUM - Moderate spread rate"
        else:
            velocity_risk = "LOW - Slow organic spread"

        if reshare_count > 10000:
            reshare_risk = "CRITICAL - Massive engagement"
        elif reshare_count > 1000:
            reshare_risk = "HIGH - Significant engagement"
        else:
            reshare_risk = "MODERATE - Normal engagement"

        if cluster_count > 5:
            clustering_risk = "HIGH - Multiple isolated clusters (echo chambers)"
        else:
            clustering_risk = "MODERATE - Limited clustering"

        return {
            "velocity_score": float(velocity),
            "velocity_interpretation": velocity_risk,
            "reshare_count": int(reshare_count),
            "reshare_interpretation": reshare_risk,
            "cluster_count": int(cluster_count),
            "clustering_interpretation": clustering_risk,
            "propagation_risk_level": "HIGH"
            if "HIGH" in velocity_risk or "CRITICAL" in reshare_risk
            else "MODERATE"
            if "MEDIUM" in velocity_risk or "HIGH" in clustering_risk
            else "LOW",
            "key_findings": [
                f"Content spread at velocity of {velocity:.1f} shares per hour",
                f"{reshare_count} total reshares detected",
                f"{cluster_count} distinct social clusters identified",
            ],
        }

    def generate_explanation_report(
        self,
        claim: str,
        prediction: Dict,
        shap_explanation: Dict = None,
        lime_explanation: Dict = None,
        evidence_explanation: Dict = None,
        propagation_explanation: Dict = None,
    ) -> Dict:
        """
        Generate comprehensive explanation report.

        Args:
            claim: The claim being analyzed
            prediction: Model prediction results
            shap_explanation: SHAP explanation
            lime_explanation: LIME explanation
            evidence_explanation: Evidence comparison
            propagation_explanation: Propagation pattern

        Returns:
            Comprehensive explanation report
        """
        logger.info("Generating comprehensive explanation report")

        # Build executive summary
        verdict = prediction.get("verdict", "UNVERIFIED")
        confidence = prediction.get("confidence", 0)

        if confidence > 0.8:
            confidence_text = "Very High Confidence"
        elif confidence > 0.6:
            confidence_text = "High Confidence"
        elif confidence > 0.4:
            confidence_text = "Moderate Confidence"
        else:
            confidence_text = "Low Confidence"

        report = {
            "claim": claim,
            "verdict": verdict,
            "confidence": float(confidence),
            "confidence_description": confidence_text,
            "executive_summary": f"This claim is assessed as {verdict} with {confidence_text} ({confidence:.1%})",
            "prediction_scores": {
                "nlp_score": float(prediction.get("nlp_score", 0)),
                "evidence_score": float(prediction.get("evidence_score", 0)),
                "propagation_score": float(prediction.get("propagation_score", 0)),
                "final_score": float(prediction.get("score", 0)),
            },
            "explanations": {},
        }

        # Add SHAP explanation
        if shap_explanation:
            report["explanations"]["shap"] = {
                "top_influential_words": [
                    {"word": w, "influence": float(v)}
                    for w, v in shap_explanation.get("top_features", [])
                ],
                "overall_model_output": float(shap_explanation.get("model_output", 0)),
            }

        # Add LIME explanation
        if lime_explanation:
            report["explanations"]["lime"] = {
                "top_features": lime_explanation.get("top_features", []),
                "prediction_probability": float(
                    lime_explanation.get("prediction", 0)
                ),
            }

        # Add evidence explanation
        if evidence_explanation:
            report["explanations"]["evidence"] = {
                "supporting_sources": [
                    s[0] for s in evidence_explanation.get("supporting_evidence", [])
                ],
                "contradicting_sources": [
                    c[0] for c in evidence_explanation.get("contradicting_evidence", [])
                ],
                "net_support_score": float(evidence_explanation.get("net_support", 0)),
            }

        # Add propagation explanation
        if propagation_explanation:
            report["explanations"]["propagation"] = {
                "velocity": float(propagation_explanation.get("velocity_score", 0)),
                "risk_level": propagation_explanation.get("propagation_risk_level"),
                "key_findings": propagation_explanation.get("key_findings", []),
            }

        return report

    def create_visualization_data(self, explanation_report: Dict) -> Dict:
        """
        Create data for visualization of explanations.

        Args:
            explanation_report: Explanation report

        Returns:
            Data formatted for visualization
        """
        return {
            "scores": {
                "nlp": explanation_report["prediction_scores"]["nlp_score"],
                "evidence": explanation_report["prediction_scores"]["evidence_score"],
                "propagation": explanation_report["prediction_scores"][
                    "propagation_score"
                ],
            },
            "confidence": explanation_report["confidence"],
            "top_influential_words": [
                item["word"]
                for item in explanation_report["explanations"]
                .get("shap", {})
                .get("top_influential_words", [])[:5]
            ],
            "sources": {
                "supporting": len(
                    explanation_report["explanations"]
                    .get("evidence", {})
                    .get("supporting_sources", [])
                ),
                "contradicting": len(
                    explanation_report["explanations"]
                    .get("evidence", {})
                    .get("contradicting_sources", [])
                ),
            },
        }
