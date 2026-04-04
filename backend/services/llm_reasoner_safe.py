"""
FIXED: LLM Reasoner - PRODUCTION SAFE VERSION
Features: Safe entity extraction, safe LLM calls, fallback reasoning.
"""

import logging
import json
import requests
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SafeLLMReasoner:
    """
    LLM reasoner with comprehensive safety and error handling.
    NEVER returns None - always provides safe defaults.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, 
                 huggingface_api_key: Optional[str] = None,
                 cache_timeout_minutes: int = 60):
        """Initialize reasoner with API keys and caching."""
        self.openai_api_key = openai_api_key
        self.huggingface_api_key = huggingface_api_key
        self.cache_timeout = timedelta(minutes=cache_timeout_minutes)
        self.response_cache = {}
        logger.info(f"[LLM] Initialized with caching ({cache_timeout_minutes}m TTL)")
    
    # =========================================================================
    # ENTITY EXTRACTION - SAFE (NEVER RETURNS NONE)
    # =========================================================================
    
    def extract_entity(self, claim: str) -> Tuple[str, List[str]]:
        """
        Extract main entity from claim - SAFE.
        
        GUARANTEES:
        - Returns (entity, tokens) tuple
        - entity is NEVER None (returns "Unknown" if fails)
        - tokens is NEVER None (returns [] if fails)
        - entity is always a string, never empty (minimum "Unknown")
        
        Returns:
            (entity_str, token_list) where:
            - entity_str: Main entity or "Unknown"
            - token_list: Keywords or empty list
        """
        if not claim or not claim.strip():
            logger.debug("[ENTITY] ❌ Empty claim")
            return ("Unknown", [])
        
        try:
            claim = claim.strip()
            logger.debug(f"[ENTITY] Extracting from: {claim[:80]}")
            
            # STEP 1: Try LLM extraction
            try:
                entity = self._extract_entity_llm(claim)
                if entity and isinstance(entity, str) and entity.strip():
                    entity = entity.strip()
                    logger.debug(f"[ENTITY] ✅ LLM extracted: {entity}")
                    tokens = self._extract_keywords(claim)
                    return (entity, tokens)
            except Exception as e:
                logger.debug(f"[ENTITY] ⚠️ LLM extraction failed: {e}")
            
            # STEP 2: Try heuristic extraction
            try:
                entity = self._extract_entity_heuristic(claim)
                if entity and isinstance(entity, str) and entity.strip():
                    entity = entity.strip()
                    logger.debug(f"[ENTITY] ✅ Heuristic extracted: {entity}")
                    tokens = self._extract_keywords(claim)
                    return (entity, tokens)
            except Exception as e:
                logger.debug(f"[ENTITY] ⚠️ Heuristic extraction failed: {e}")
            
            # STEP 3: Extract first noun phrase as fallback
            try:
                words = claim.split()[:10]  # First 10 words max
                if words:
                    entity = " ".join(words[:3])  # First 3 words
                    entity = entity.strip(" ,;.:!?()[]{}\"'")
                    
                    if entity and len(entity) > 2:
                        logger.debug(f"[ENTITY] ✅ Fallback extracted: {entity}")
                        tokens = self._extract_keywords(claim)
                        return (entity, tokens)
            except Exception as e:
                logger.debug(f"[ENTITY] ⚠️ Fallback extraction failed: {e}")
            
            # STEP 4: Last resort - use "Unknown"
            logger.warning("[ENTITY] ❌ All extraction methods failed, using 'Unknown'")
            tokens = self._extract_keywords(claim)
            return ("Unknown", tokens)
        
        except Exception as e:
            logger.error(f"[ENTITY] ❌ CRITICAL: {e}", exc_info=True)
            # GUARANTEED SAFE RETURN
            return ("Unknown", [])
    
    def _extract_entity_llm(self, claim: str) -> Optional[str]:
        """Try to extract entity using LLM - SAFE (returns None on failure, not crash)."""
        try:
            prompt = f"""Extract the main entity (person, place, or thing) from this claim in ONE word maximum:

Claim: {claim}

Entity (one word or short phrase):"""
            
            response = self._call_llm(prompt, max_tokens=20)
            if response:
                entity = response.strip().split()[0]  # First word
                if entity and len(entity) > 1:
                    return entity
        except Exception as e:
            logger.debug(f"[ENTITY-LLM] ⚠️ Failed: {e}")
        return None
    
    def _extract_entity_heuristic(self, claim: str) -> Optional[str]:
        """Extract entity using heuristics - SAFE."""
        try:
            # Check for common patterns: "person's disease", "place's event", etc.
            patterns = [
                (" has ", 1),  # X has disease
                (" died of ", 1),  # X died of
                (" was born in ", 1),  # X was born in  
                (" is a ", 1),  # X is a
                (" claimed ", 1),  # X claimed
            ]
            
            for pattern, position in patterns:
                if pattern in claim:
                    parts = claim.split(pattern)
                    if len(parts) > position:
                        text = parts[position - 1] if position == 1 else parts[position]
                        words = text.split()
                        entity = " ".join(words[:2])  # First 2 words
                        entity = entity.strip(" ,;.:!?()[]{}\"'")
                        if entity and len(entity) > 1:
                            return entity
            
            return None
        except Exception as e:
            logger.debug(f"[ENTITY-HEURISTIC] ⚠️ Failed: {e}")
            return None
    
    def _extract_keywords(self, claim: str) -> List[str]:
        """Extract keywords - SAFE (returns empty list on failure)."""
        try:
            # Simple: split by spaces and filter short words
            words = [w.strip('"\'()[]{},.;:!?-') for w in claim.split()]
            keywords = [w for w in words if len(w) > 3 and not w.startswith("the")]
            return keywords[:10]
        except Exception as e:
            logger.debug(f"[KEYWORDS] ⚠️ Failed: {e}")
            return []
    
    # =========================================================================
    # CLAIM ANALYSIS - SAFE
    # =========================================================================
    
    def analyze_claim(self, claim: str) -> Dict[str, Any]:
        """
        Analyze claim for initial entity and keywords - SAFE.
        
        Returns:
            Dict with keys:
            - entity (str): Main entity - GUARANTEED not None
            - keywords (List[str]): Keywords - GUARANTEED not None
            - intent (str): Claim type
            - analysis_provided (bool): Whether LLM analysis succeeded
        
        GUARANTEES:
        - Always returns dict
        - 'entity' is always string (minimum "Unknown")
        - 'keywords' is always list (minimum [])
        - Never raises exception
        """
        logger.info(f"[ANALYSIS] Analyzing claim: {claim[:80]}")
        
        try:
            # STEP 1: Extract entity (GUARANTEED SAFE)
            entity, keywords = self.extract_entity(claim)
            
            # Double-check entity is not None
            if not entity or entity is None:
                entity = "Unknown"
            
            entity = str(entity).strip()
            if not entity:
                entity = "Unknown"
            
            logger.debug(f"[ANALYSIS] Entity: {entity}, Keywords: {keywords}")
            
            # STEP 2: Detect intent
            try:
                intent = self.detect_claim_intent(claim)
            except Exception as e:
                logger.debug(f"[ANALYSIS] ⚠️ Intent detection failed: {e}")
                intent = "general"
            
            # STEP 3: Try LLM analysis for richer info
            analysis_provided = False
            try:
                llm_analysis = self._analyze_claim_llm(claim, entity)
                if llm_analysis:
                    analysis_provided = True
                    if "keywords" in llm_analysis:
                        keywords = llm_analysis["keywords"]
            except Exception as e:
                logger.debug(f"[ANALYSIS] ⚠️ LLM analysis failed: {e}")
                # Continue with heuristic analysis
            
            result = {
                "entity": entity,  # GUARANTEED NOT NONE
                "keywords": keywords if isinstance(keywords, list) else [],  # GUARANTEED NOT NONE
                "intent": intent,
                "analysis_provided": analysis_provided,
            }
            
            logger.debug(f"[ANALYSIS] ✅ Complete: {result}")
            return result
        
        except Exception as e:
            logger.error(f"[ANALYSIS] ❌ CRITICAL: {e}", exc_info=True)
            # GUARANTEED SAFE RETURN
            return {
                "entity": "Unknown",
                "keywords": [],
                "intent": "general",
                "analysis_provided": False,
            }
    
    def _analyze_claim_llm(self, claim: str, entity: str) -> Optional[Dict]:
        """Try to analyze claim with LLM - SAFE (returns None on failure)."""
        try:
            prompt = f"""Analyze this claim and extract key information:

Claim: {claim}
Entity: {entity}

Respond in JSON format:
{{
  "claim_type": "life_status|historical|general",
  "keywords": ["keyword1", "keyword2"]
}}

Response:"""
            
            response = self._call_llm(prompt, max_tokens=100)
            if response:
                try:
                    data = json.loads(response)
                    if data.get("keywords") and isinstance(data["keywords"], list):
                        return data
                except json.JSONDecodeError:
                    logger.debug("[ANALYSIS-LLM] ⚠️ JSON parse failed")
        except Exception as e:
            logger.debug(f"[ANALYSIS-LLM] ⚠️ Failed: {e}")
        return None
    
    # =========================================================================
    # INTENT DETECTION - SAFE
    # =========================================================================
    
    def detect_claim_intent(self, claim: str) -> str:
        """
        Detect claim intent - SAFE.
        
        Returns: 'life_status', 'historical', or 'general'
        NEVER returns None.
        """
        try:
            claim_lower = claim.lower()
            
            # Life status indicators
            if any(word in claim_lower for word in ["died", "death", "dead", "alive", "living"]):
                return "life_status"
            
            # Historical indicators
            if any(word in claim_lower for word in ["year", "date", "happened", "occurred", "war", "event"]):
                return "historical"
            
            # Default
            return "general"
        except Exception as e:
            logger.debug(f"[INTENT] ⚠️ Fallback to 'general': {e}")
            return "general"
    
    # =========================================================================
    # LLM API CALLS - SAFE
    # =========================================================================
    
    def _call_llm(self, prompt: str, max_tokens: int = 200) -> Optional[str]:
        """
        Call LLM (OpenAI → HuggingFace fallback) - SAFE.
        Returns response string or None on failure (NEVER crashes).
        """
        try:
            # Check cache first
            cache_key = hashlib.md5(prompt.encode()).hexdigest()
            if cache_key in self.response_cache:
                cached_response, cached_time = self.response_cache[cache_key]
                if datetime.now() - cached_time < self.cache_timeout:
                    logger.debug("[LLM] ✅ Cache hit")
                    return cached_response
            
            # Try OpenAI first
            if self.openai_api_key:
                try:
                    logger.debug("[LLM-OpenAI] Calling OpenAI...")
                    response = self._call_openai(prompt, max_tokens)
                    if response:
                        self.response_cache[cache_key] = (response, datetime.now())
                        return response
                except Exception as e:
                    logger.debug(f"[LLM-OpenAI] ⚠️ Failed: {e}")
            
            # Fallback to HuggingFace
            if self.huggingface_api_key:
                try:
                    logger.debug("[LLM-HF] Calling HuggingFace...")
                    response = self._call_huggingface(prompt, max_tokens)
                    if response:
                        self.response_cache[cache_key] = (response, datetime.now())
                        return response
                except Exception as e:
                    logger.debug(f"[LLM-HF] ⚠️ Failed: {e}")
            
            logger.warning("[LLM] ⚠️ All LLM calls failed")
            return None
        
        except Exception as e:
            logger.error(f"[LLM] ❌ Unexpected error: {e}")
            return None
    
    def _call_openai(self, prompt: str, max_tokens: int = 200) -> Optional[str]:
        """Call OpenAI API - SAFE (returns None on failure)."""
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.3,
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        except requests.Timeout:
            logger.debug("[OpenAI] ⚠️ Timeout")
            return None
        except requests.HTTPError as e:
            logger.debug(f"[OpenAI] ⚠️ HTTP error: {e.response.status_code}")
            return None
        except Exception as e:
            logger.debug(f"[OpenAI] ⚠️ Error: {e}")
            return None
    
    def _call_huggingface(self, prompt: str, max_tokens: int = 200) -> Optional[str]:
        """Call HuggingFace API - SAFE (returns None on failure)."""
        try:
            response = requests.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
                headers={"Authorization": f"Bearer {self.huggingface_api_key}"},
                json={"inputs": prompt, "parameters": {"max_length": max_tokens}},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("generated_text", "")
            return ""
        
        except requests.Timeout:
            logger.debug("[HuggingFace] ⚠️ Timeout")
            return None
        except requests.HTTPError as e:
            logger.debug(f"[HuggingFace] ⚠️ HTTP error: {e.response.status_code}")
            return None
        except Exception as e:
            logger.debug(f"[HuggingFace] ⚠️ Error: {e}")
            return None
    
    # =========================================================================
    # EVIDENCE REASONING - SAFE
    # =========================================================================
    
    def reason_over_evidence(self, claim: str, evidence_list: List[Dict]) -> Dict[str, Any]:
        """
        Generate final reasoning over evidence - SAFE.
        
        Returns:
            Dict with keys:
            - summary (str): Analysis summary
            - label (str): SUPPORTS / REFUTES / UNCERTAIN
            - confidence (float): 0.0-1.0
            
        NEVER returns None, always returns safe dict.
        """
        try:
            if not evidence_list:
                logger.warning("[REASONING] ❌ No evidence provided")
                return self._safe_reasoning_response(
                    "No evidence found",
                    "UNCERTAIN",
                    0.0
                )
            
            logger.info(f"[REASONING] Analyzing {len(evidence_list)} evidence items")
            
            # Try LLM reasoning
            try:
                llm_result = self._reason_over_evidence_llm(claim, evidence_list)
                if llm_result:
                    return llm_result
            except Exception as e:
                logger.debug(f"[REASONING] ⚠️ LLM reasoning failed: {e}")
            
            # Fallback: Heuristic reasoning
            return self._reason_over_evidence_heuristic(claim, evidence_list)
        
        except Exception as e:
            logger.error(f"[REASONING] ❌ CRITICAL: {e}", exc_info=True)
            return self._safe_reasoning_response("Error in reasoning", "UNCERTAIN", 0.0)
    
    def _reason_over_evidence_llm(self, claim: str, evidence_list: List[Dict]) -> Optional[Dict]:
        """LLM-based reasoning - SAFE (returns None on failure)."""
        try:
            evidence_text = "\n".join([f"- {e.get('sentence', '')} (source: {e.get('source', '')})" 
                                      for e in evidence_list[:5]])
            
            prompt = f"""Based on this evidence, determine if the claim is supported:

Claim: {claim}

Evidence:
{evidence_text}

Respond in JSON format with your verdict:
{{
  "label": "SUPPORTS|REFUTES|UNCERTAIN",
  "confidence": 0.0-1.0,
  "summary": "explanation"
}}

Response:"""
            
            response = self._call_llm(prompt, max_tokens=200)
            if response:
                try:
                    data = json.loads(response)
                    return {
                        "label": data.get("label", "UNCERTAIN"),
                        "confidence": float(data.get("confidence", 0.5)),
                        "summary": data.get("summary", ""),
                    }
                except json.JSONDecodeError:
                    logger.debug("[REASONING-LLM] ⚠️ JSON parse failed")
        except Exception as e:
            logger.debug(f"[REASONING-LLM] ⚠️ Failed: {e}")
        return None
    
    def _reason_over_evidence_heuristic(self, claim: str, evidence_list: List[Dict]) -> Dict:
        """Heuristic-based reasoning - SAFE."""
        try:
            avg_similarity = sum(e.get("similarity_score", 0.0) for e in evidence_list) / len(evidence_list) if evidence_list else 0
            
            if avg_similarity > 0.7:
                return self._safe_reasoning_response(
                    f"Strong evidence found supporting claim",
                    "SUPPORTS",
                    min(0.95, avg_similarity)
                )
            elif avg_similarity > 0.5:
                return self._safe_reasoning_response(
                    f"Moderate evidence found",
                    "UNCERTAIN",
                    0.6
                )
            else:
                return self._safe_reasoning_response(
                    f"Limited supporting evidence",
                    "UNCERTAIN",
                    0.4
                )
        except Exception as e:
            logger.error(f"[REASONING-HEURISTIC] ⚠️ Failed: {e}")
            return self._safe_reasoning_response("Error in heuristic reasoning", "UNCERTAIN", 0.0)
    
    def _safe_reasoning_response(self, summary: str, label: str, confidence: float) -> Dict:
        """Create safe reasoning response with defaults."""
        return {
            "summary": str(summary)[:500],
            "label": str(label).strip().upper(),
            "confidence": max(0.0, min(1.0, float(confidence))),
        }
