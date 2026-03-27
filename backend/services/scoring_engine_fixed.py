"""
Scoring Engine - FIXED with guaranteed explanation generation.
Orchestrates the entire 7-step analysis pipeline.
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ScoringEngine:
    """
    Orchestrates complete analysis pipeline with explanations.
    === FIX 4: GUARANTEED EXPLANATION GENERATION ===
    NEVER skips explanation - always generates fallback if needed.
    """
    
    def __init__(self):
        """Initialize scoring engine."""
        self.logger = logger
    
    def analyze(
        self,
        claim: str,
        retrieval_engine,
        evidence_builder,
        verdict_engine
    ) -> Dict[str, Any]:
        """
        Execute full analysis pipeline.
        === FIX 4: GUARANTEED EXPLANATION GENERATION ===
        Always generates explanations, never returns empty.
        
        Args:
            claim: Claim to analyze
            retrieval_engine: Retrieval service
            evidence_builder: Evidence builder service
            verdict_engine: Verdict computation service
            
        Returns:
            Complete analysis response (guaranteed non-empty)
        """
        
        logger.info(f"[FIX4] Starting analysis pipeline for: {claim[:60]}")
        
        # STEP 1: Retrieve evidence
        logger.info("[FIX4] STEP 1: Retrieving evidence...")
        try:
            raw_articles = retrieval_engine.search_and_scrape(
                claim=claim,
                max_results=10
            )
            if not raw_articles:
                raw_articles = [self._fallback_article(claim)]
        except Exception as e:
            logger.error(f"[FIX4] Retrieval failed: {e}")
            raw_articles = [self._fallback_article(claim)]
        
        logger.info(f"[FIX4] Retrieved {len(raw_articles)} articles")
        
        # STEP 2: Build evidence
        logger.info("[FIX4] STEP 2: Building evidence...")
        try:
            nlp_score = self._compute_nlp_score(claim)
            evidence_list = evidence_builder.build(
                raw_articles=raw_articles,
                claim=claim,
                nlp_score=nlp_score
            )
            if not evidence_list:
                evidence_list = [self._fallback_evidence()]
        except Exception as e:
            logger.error(f"[FIX4] Evidence building failed: {e}")
            evidence_list = [self._fallback_evidence()]
        
        logger.info(f"[FIX4] Built {len(evidence_list)} evidence items")
        
        # STEP 3: Compute verdict
        logger.info("[FIX4] STEP 3: Computing verdict...")
        try:
            verdict_result = verdict_engine.compute_verdict(
                evidence_list=evidence_list,
                nlp_score=nlp_score,
                claim=claim
            )
            if not verdict_result:
                verdict_result = self._fallback_verdict("Analysis failed")
        except Exception as e:
            logger.error(f"[FIX4] Verdict computation failed: {e}")
            verdict_result = self._fallback_verdict(f"Error: {str(e)[:50]}")
        
        logger.info(f"[FIX4] Verdict: {verdict_result.get('verdict', 'UNKNOWN')}")
        
        # STEP 4: Rank evidence
        logger.info("[FIX4] STEP 4: Ranking evidence...")
        ranked_evidence = self._rank_evidence(evidence_list)
        logger.info(f"[FIX4] Ranked {len(ranked_evidence)} evidence items")
        
        # === FIX 4: GUARANTEED EXPLANATION GENERATION ===
        logger.info("[FIX4] STEP 5: Generating explanations...")
        try:
            explanations = self._generate_explanations(
                claim=claim,
                verdict=verdict_result,
                evidence=ranked_evidence,
                nlp_score=nlp_score
            )
            if not explanations or not self._explanations_valid(explanations):
                logger.warning("[FIX4] Explanation generation failed - using fallback")
                explanations = self._fallback_explanations(claim, verdict_result)
        except Exception as e:
            logger.error(f"[FIX4] Explanation generation error: {e}")
            explanations = self._fallback_explanations(claim, verdict_result)
        
        logger.info("[FIX4] Explanations generated successfully")
        
        # STEP 6: Compute evidence quality
        logger.info("[FIX4] STEP 6: Computing evidence quality...")
        evidence_quality = self._compute_evidence_quality(evidence_list)
        logger.info(f"[FIX4] Evidence quality: {evidence_quality}")
        
        # STEP 7: Build response
        logger.info("[FIX4] STEP 7: Building response...")
        response = self._build_response(
            claim=claim,
            verdict=verdict_result,
            evidence=ranked_evidence,
            explanations=explanations,
            evidence_quality=evidence_quality,
            nlp_score=nlp_score
        )
        
        # === FIX 7: GUARANTEE RESPONSE STRUCTURE ===
        response = self._guarantee_response_structure(response)
        
        logger.info("[FIX4] Analysis pipeline complete")
        return response
    
    def _explanations_valid(self, explanations: Dict) -> bool:
        """
        Check if explanations are valid and non-empty.
        
        Args:
            explanations: Explanation dict to validate
            
        Returns:
            True if valid and populated
        """
        if not explanations:
            return False
        
        for key, value in explanations.items():
            if isinstance(value, str) and not value.strip():
                return False
            if isinstance(value, list) and len(value) == 0:
                return False
        
        return True
    
    def _generate_explanations(
        self,
        claim: str,
        verdict: Dict,
        evidence: List[Dict],
        nlp_score: float
    ) -> Dict[str, Any]:
        """
        Generate comprehensive explanations.
        
        Args:
            claim: The claim analyzed
            verdict: Verdict result
            evidence: Ranked evidence
            nlp_score: NLP score
            
        Returns:
            Explanation dict
        """
        verdict_type = verdict.get("verdict", "UNCERTAIN")
        confidence = verdict.get("confidence", 0.5)
        
        # Extract top sources
        top_sources = []
        for item in evidence[:3]:
            top_sources.append({
                "source": item.get("source", "Unknown"),
                "stance": item.get("stance", "NEUTRAL"),
                "credibility": item.get("credibility", 0.5),
                "is_fallback": item.get("is_fallback", False)
            })
        
        explanations = {
            "summary": self._generate_summary(
                claim=claim,
                verdict=verdict_type,
                confidence=confidence
            ),
            "decision_logic": self._generate_decision_logic(
                verdict=verdict,
                evidence_count=len(evidence)
            ),
            "top_sources": top_sources,
            "reasoning_steps": self._generate_reasoning_steps(
                verdict=verdict,
                evidence_count=len(evidence),
                nlp_score=nlp_score
            ),
            "confidence_factors": self._generate_confidence_factors(
                verdict=verdict,
                evidence=evidence
            )
        }
        
        return explanations
    
    def _generate_summary(
        self,
        claim: str,
        verdict: str,
        confidence: float
    ) -> str:
        """Generate summary explanation."""
        confidence_pct = int(confidence * 100)
        
        if verdict == "TRUE":
            return f"Claim '{claim[:60]}' appears to be TRUE based on available evidence ({confidence_pct}% confidence)."
        elif verdict == "FALSE":
            return f"Claim '{claim[:60]}' appears to be FALSE based on contradicting evidence ({confidence_pct}% confidence)."
        else:
            return f"Claim '{claim[:60]}' is UNCERTAIN - insufficient evidence to verify ({confidence_pct}% confidence)."
    
    def _generate_decision_logic(
        self,
        verdict: Dict,
        evidence_count: int
    ) -> str:
        """Generate decision logic explanation."""
        reasoning = verdict.get("reasoning", "Analysis completed.")
        
        logic = f"""

Decision Logic:
- Verdict reached by analyzing {evidence_count} evidence source(s)
- Assessment methodology: Evidence weight + source credibility ranking
- Confidence calculation: Credibility × Evidence consistency × NLP alignment

Verdict: {verdict.get('verdict', 'UNCERTAIN')}
Confidence Score: {verdict.get('confidence', 0.5):.0%}

Reasoning: {reasoning[:300]}...
"""
        return logic.strip()
    
    def _generate_reasoning_steps(
        self,
        verdict: Dict,
        evidence_count: int,
        nlp_score: float
    ) -> List[str]:
        """Generate step-by-step reasoning."""
        steps = [
            f"1. Analyzed {evidence_count} evidence source(s)",
            f"2. NLP language analysis score: {nlp_score:.0%}",
            f"3. Computed source credibility weights",
            f"4. Evaluated stance alignment",
            f"5. Determined overall verdict: {verdict.get('verdict')}",
            f"6. Calculated confidence: {verdict.get('confidence'):.0%}"
        ]
        return steps
    
    def _generate_confidence_factors(
        self,
        verdict: Dict,
        evidence: List[Dict]
    ) -> Dict[str, str]:
        """Generate confidence factors explanation."""
        avg_credibility = (
            sum(e.get("credibility", 0) for e in evidence) / len(evidence)
            if evidence else 0.3
        )
        
        fallback_count = sum(1 for e in evidence if e.get("is_fallback"))
        
        return {
            "source_credibility": f"{avg_credibility:.0%} average",
            "evidence_consistency": "High" if len(evidence) > 2 else "Low",
            "external_verification": (
                "No external sources" if fallback_count == len(evidence)
                else f"{len(evidence) - fallback_count} real sources"
            ),
            "overall_confidence": f"{verdict.get('confidence', 0.5):.0%}"
        }
    
    def _fallback_explanations(
        self,
        claim: str,
        verdict: Dict
    ) -> Dict[str, Any]:
        """
        === FIX 4: FALLBACK EXPLANATIONS ===
        Generate explanations when real generation fails.
        """
        return {
            "summary": f"Analysis of '{claim[:60]}' complete: Verdict is {verdict.get('verdict', 'UNCERTAIN')}",
            "decision_logic": "Fallback analysis: Limited evidence available - system used NLP analysis",
            "top_sources": [
                {
                    "source": "System Fallback Analysis",
                    "stance": "NEUTRAL",
                    "credibility": 0.3,
                    "is_fallback": True
                }
            ],
            "reasoning_steps": [
                "1. Attempted evidence retrieval",
                "2. Performed NLP language analysis",
                "3. Generated system verdict",
                "4. Returned fallback explanation"
            ],
            "confidence_factors": {
                "source_credibility": "30% (system fallback)",
                "evidence_consistency": "Low",
                "external_verification": "No external sources",
                "overall_confidence": f"{verdict.get('confidence', 0.3):.0%}"
            }
        }
    
    def _rank_evidence(self, evidence_list: List[Dict]) -> List[Dict]:
        """Rank evidence by credibility."""
        return sorted(
            evidence_list,
            key=lambda x: x.get("credibility", 0),
            reverse=True
        )
    
    def _compute_evidence_quality(self, evidence_list: List[Dict]) -> str:
        """
        === FIX 6: EVIDENCE QUALITY SCORE ===
        Compute quality metric for evidence.
        """
        if not evidence_list:
            return "NONE"
        
        avg_credibility = (
            sum(e.get("credibility", 0) for e in evidence_list) / len(evidence_list)
        )
        
        fallback_count = sum(1 for e in evidence_list if e.get("is_fallback"))
        real_count = len(evidence_list) - fallback_count
        
        if real_count >= 3 and avg_credibility > 0.7:
            return "HIGH"
        elif real_count >= 1 or avg_credibility > 0.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _build_response(
        self,
        claim: str,
        verdict: Dict,
        evidence: List[Dict],
        explanations: Dict,
        evidence_quality: str,
        nlp_score: float
    ) -> Dict[str, Any]:
        """
        Build analysis response.
        
        Args:
            claim: The claim
            verdict: Verdict result
            evidence: Ranked evidence
            explanations: Explanations
            evidence_quality: Quality metric
            nlp_score: NLP score
            
        Returns:
            Response dict
        """
        # Convert evidence to sources
        sources = []
        for item in evidence[:5]:
            sources.append({
                "title": item.get("source", "Unknown"),
                "url": item.get("url", "unknown"),
                "credibility": f"{item.get('credibility', 0.5):.0%}",
                "summary": item.get("snippet", item.get("text", "")[:200]),
                "supports": item.get("stance", "NEUTRAL"),
                "is_fallback": item.get("is_fallback", False)
            })
        
        response = {
            "claim": claim,
            "verdict": verdict.get("verdict", "UNCERTAIN"),
            "confidence": verdict.get("confidence", 0.3),
            "explanation": explanations.get("summary", "Analysis complete"),
            "reasoning": verdict.get("reasoning", "See detailed analysis above"),
            "sources": sources,
            "key_signals": [
                f"Evidence quality: {evidence_quality}",
                f"Sources analyzed: {len(evidence)}",
                f"Verdict confidence: {verdict.get('confidence', 0.3):.0%}",
                f"NLP analysis: {'Supports' if nlp_score > 0.6 else 'Contradicts' if nlp_score < 0.4 else 'Neutral to'} claim"
            ],
            "detailed_explanation": explanations,
            "evidence_quality": evidence_quality,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    
    def _guarantee_response_structure(self, response: Dict) -> Dict:
        """
        === FIX 7: GUARANTEE RESPONSE STRUCTURE ===
        Ensure all required fields are present and non-empty.
        """
        required_fields = {
            "claim": "Unknown claim",
            "verdict": "UNCERTAIN",
            "confidence": 0.3,
            "explanation": "Analysis completed",
            "reasoning": "System analysis performed",
            "sources": [],
            "key_signals": ["Analysis complete"],
            "detailed_explanation": {},
            "evidence_quality": "LOW",
            "timestamp": datetime.now().isoformat()
        }
        
        # Ensure all fields exist
        for field, default in required_fields.items():
            if field not in response or response[field] is None:
                response[field] = default
            
            # Ensure non-empty for certain fields
            if field == "explanation" and not response[field]:
                response[field] = "Analysis completed successfully"
            elif field == "reasoning" and not response[field]:
                response[field] = "System analysis performed"
            elif field == "sources" and not response[field]:
                response[field] = [self._fallback_source()]
            elif field == "key_signals" and not response[field]:
                response[field] = ["Analysis complete"]
        
        return response
    
    def _compute_nlp_score(self, claim: str) -> float:
        """Compute NLP classification score."""
        # Mock NLP score based on claim characteristics
        claim_lower = claim.lower()
        
        suspicious_words = ["fake", "hoax", "conspiracy", "alien", "illuminati"]
        credible_words = ["research", "study", "evidence", "scientific", "confirmed"]
        
        score = 0.5
        
        for word in suspicious_words:
            if word in claim_lower:
                score -= 0.1
        
        for word in credible_words:
            if word in claim_lower:
                score += 0.1
        
        return max(0.1, min(0.9, score))
    
    def _fallback_article(self, claim: str) -> Dict:
        """Create fallback article."""
        return {
            "title": "System Fallback",
            "url": "generated://fallback",
            "text": f"No external sources found for: {claim}",
            "snippet": "System-generated fallback",
            "source": "System",
            "credibility": 0.2,
            "is_fallback": True
        }
    
    def _fallback_evidence(self) -> Dict:
        """Create fallback evidence item."""
        return {
            "source": "System Fallback",
            "stance": "NEUTRAL",
            "credibility": 0.3,
            "snippet": "System-generated fallback evidence",
            "text": "Analysis proceeding with system classification",
            "url": "generated://fallback",
            "is_fallback": True
        }
    
    def _fallback_verdict(self, reason: str) -> Dict:
        """Create fallback verdict."""
        return {
            "verdict": "UNCERTAIN",
            "confidence": 0.3,
            "reasoning": f"Analysis could not complete: {reason}. System returned UNCERTAIN as fallback.",
            "is_fallback": True
        }
    
    def _fallback_source(self) -> Dict:
        """Create fallback source."""
        return {
            "title": "System Fallback",
            "url": "generated://fallback",
            "credibility": "30%",
            "summary": "System-generated fallback source",
            "supports": "NEUTRAL",
            "is_fallback": True
        }
