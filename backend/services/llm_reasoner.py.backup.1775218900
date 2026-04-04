"""LLM-backed claim understanding, query generation, and reasoning."""

import json
import logging
import os
import re
from typing import Dict, List, Optional

import requests

from .utils_new import extract_candidate_entity

logger = logging.getLogger(__name__)


class LLMReasoningError(Exception):
    """Raised when LLM reasoning fails."""


class LLMReasoner:
    """Lightweight LLM helper for claim understanding and reasoning."""

    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY", "").strip() or os.getenv("HF_TOKEN", "").strip()
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.hf_model = os.getenv("HF_LLM_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
        self.timeout = int(os.getenv("LLM_TIMEOUT", "20"))
        self._analysis_cache = {}
        self._query_cache = {}
        self._credibility_cache = {}
        self._relationship_cache = {}
        self._type_cache = {}
        self._cache_order = []
        self._cache_max = 200
        self._session = requests.Session()

    def _cache_get(self, cache: Dict[str, object], key: str) -> Optional[object]:
        return cache.get(key)

    def _cache_set(self, cache: Dict[str, object], key: str, value: object) -> None:
        if key in cache:
            return
        cache[key] = value
        self._cache_order.append(key)
        if len(self._cache_order) > self._cache_max:
            oldest = self._cache_order.pop(0)
            self._analysis_cache.pop(oldest, None)
            self._query_cache.pop(oldest, None)
            self._credibility_cache.pop(oldest, None)
            self._relationship_cache.pop(oldest, None)
            self._type_cache.pop(oldest, None)

    def detect_claim_intent(self, claim: str) -> str:
        """
        INTENT DETECTION: Classify claim into: 'life_status', 'historical', 'general'.
        
        Returns:
            'life_status' - For claims about whether someone is dead/alive/living
            'historical' - For claims about past events (founded, invented, won, elected)
            'general' - Default for other claims
        
        This enables intent-aware query expansion and filtering.
        """
        cache_key = f"intent::{claim.strip().lower()}"
        
        claim_lower = claim.lower()
        
        # Life status keywords
        life_status_keywords = {
            'dead', 'died', 'death', 'alive', 'living', 'passed away',
            'deceased', 'is dead', 'is alive', 'still alive', 'still living',
            'still dead', 'passed', 'perished', 'assassinated', 'murdered',
            'suicide', 'crashed', 'drowned'
        }
        
        # Historical keywords
        historical_keywords = {
            'founded', 'invented', 'discovered', 'won', 'elected', 'created',
            'first', 'established', 'formed', 'started', 'building', 'built',
            'wrote', 'written', 'published', 'premiered', 'released', 'landed',
            'developed', 'designed', 'constructed'
        }
        
        # Check for life_status keywords
        if any(kw in claim_lower for kw in life_status_keywords):
            logger.debug(f"[Intent] Detected 'life_status' intention in: {claim[:50]}")
            return "life_status"
        
        # Check for historical keywords
        if any(kw in claim_lower for kw in historical_keywords):
            logger.debug(f"[Intent] Detected 'historical' intention in: {claim[:50]}")
            return "historical"
        
        # Default
        logger.debug(f"[Intent] Defaulting to 'general' for: {claim[:50]}")
        return "general"

    def analyze_claim(self, claim: str) -> Dict[str, object]:
        """Extract structured claim understanding using the LLM."""
        cache_key = f"analysis::{claim.strip().lower()}"
        cached = self._cache_get(self._analysis_cache, cache_key)
        if isinstance(cached, dict):
            return cached
        prompt = (
            "You are a fact-checking analyst. Extract structured claim understanding. "
            "Return ONLY JSON with keys: main_entity, claim_intent, keywords, claim_type, claim_category. "
            "claim_intent must be one of: fact, rumor, status, event. "
            "claim_type must be one of: person, event, place, organization, object, other. "
            "claim_category must be one of: numerical, temporal, opinion, general.\n\n"
            f"Claim: {claim}\n"
        )
        data = self._call_llm(prompt)
        if data:
            result = self._normalize_claim_analysis(data)
            self._cache_set(self._analysis_cache, cache_key, result)
            return result
        result = self._fallback_claim_analysis(claim)
        self._cache_set(self._analysis_cache, cache_key, result)
        return result

    def generate_search_queries(self, claim: str, entity: str, keywords: List[str]) -> List[str]:
        """Generate 3-5 optimized search queries using the LLM."""
        cache_key = f"queries::{claim.strip().lower()}::{entity.strip().lower()}"
        cached = self._cache_get(self._query_cache, cache_key)
        if isinstance(cached, list):
            return cached
        prompt = (
            "Generate 3-5 concise search queries to verify the claim. "
            "Each query must be specific, include the main entity, and be context-aware. "
            "Return ONLY a JSON list of strings.\n\n"
            f"Claim: {claim}\n"
            f"Main entity: {entity}\n"
            f"Keywords: {', '.join(keywords)}\n"
        )
        data = self._call_llm(prompt)
        if isinstance(data, list):
            queries = [q for q in data if isinstance(q, str)]
            result = self._sanitize_queries(queries, claim, entity, keywords)
            self._cache_set(self._query_cache, cache_key, result)
            return result
        result = self._fallback_queries(claim, entity, keywords)
        self._cache_set(self._query_cache, cache_key, result)
        return result

    def reason_over_evidence(self, claim: str, evidence: List[Dict[str, object]]) -> Dict[str, object]:
        """Run LLM reasoning over evidence list."""
        evidence_lines = []
        for idx, item in enumerate(evidence, 1):
            evidence_lines.append(
                f"{idx}. {item.get('source', 'Unknown')} | sim={item.get('similarity', 0):.2f} | "
                f"cred={item.get('credibility_score', 0):.2f} | score={item.get('evidence_score', 0):.2f}\n"
                f"   {item.get('sentence', '')}"
            )
        evidence_text = "\n".join(evidence_lines) if evidence_lines else "No evidence provided."

        prompt = (
            "You are a fact-checking reasoner. Based ONLY on the evidence, decide whether the claim is "
            "TRUE, MISINFORMATION, or UNCERTAIN. Return ONLY JSON with keys: label, reasoning, "
            "reasoning_confidence (0-1), summary, contradictions.\n\n"
            f"Claim: {claim}\n\nEvidence:\n{evidence_text}\n"
        )
        data = self._call_llm(prompt)
        if isinstance(data, dict):
            return self._normalize_reasoning(data)
        return self._fallback_reasoning(claim, evidence)

    def compute_semantic_credibility_heuristic(self, evidence: str, source: str = "Wikipedia") -> float:
        """Use heuristic credibility scoring instead of LLM (FAST)."""
        # Heuristic: Wikipedia sources are highly credible
        if source.lower() == "wikipedia":
            return 0.85
        elif source.lower() in {"news", "newsapi"}:
            return 0.75
        elif source.lower() in {"snopes", "factcheck"}:
            return 0.90
        elif source.lower() == "tavily":
            return 0.70
        # Generic heuristic based on text content
        lowered = evidence.lower()
        speculative_terms = ["supposedly", "allegedly", "rumor", "unverified", "unclear"]
        if any(term in lowered for term in speculative_terms):
            return 0.4
        opinion_terms = ["opinion", "believe", "think", "feel"]
        if any(term in lowered for term in opinion_terms):
            return 0.5
        return 0.65  # Default neutral

    def detect_relationship_heuristic(self, claim: str, evidence: str, similarity: float = 0.0) -> str:
        """Use similarity + rule-based logic instead of LLM (FAST)."""
        # Rule-based logic: Use similarity score directly
        if similarity > 0.75:
            return "SUPPORTS"
        elif similarity < 0.40:
            return "CONTRADICTS"
        
        # Check for negation
        claim_lower = claim.lower()
        evidence_lower = evidence.lower()
        negation_words = ["not ", "no ", "never ", "neither", "nor"]
        
        claim_has_negation = any(word in claim_lower for word in negation_words)
        evidence_has_negation = any(word in evidence_lower for word in negation_words)
        
        if claim_has_negation != evidence_has_negation:
            return "CONTRADICTS"
        
        return "NEUTRAL"

    def classify_evidence_type_heuristic(self, evidence: str) -> str:
        """Use regex-based classification instead of LLM (FAST)."""
        lowered = evidence.lower()
        
        # Check for temporal/historical marker
        temporal_terms = ["year", "century", "decade", "ago", "until", "since", "founded", "established"]
        if any(term in lowered for term in temporal_terms):
            return "historical"
        
        # Check for opinion
        opinion_terms = ["opinion", "believe", "think", "feel", "argue", "claim", "suggest"]
        if any(term in lowered for term in opinion_terms):
            return "opinion"
        
        # Check for speculation
        spec_terms = ["apparently", "seemingly", "possibly", "maybe", "might", "could"]
        if any(term in lowered for term in spec_terms):
            return "speculation"
        
        # Check for factual markers
        factual_terms = ["fact", "proven", "evidence", "research", "study", "data", "official", "confirmed"]
        if any(term in lowered for term in factual_terms):
            return "factual"
        
        return "factual"  # Default

    def _call_llm(self, prompt: str) -> Optional[object]:
        """Call configured LLM provider and parse JSON output."""
        if self.openai_api_key:
            result = self._call_openai(prompt)
            if result is not None:
                return result
        if self.hf_api_key:
            result = self._call_huggingface(prompt)
            if result is not None:
                return result
        logger.warning("LLM provider not configured; using fallback reasoning")
        return None

    def _call_openai(self, prompt: str) -> Optional[object]:
        try:
            response = self._session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.openai_model,
                    "temperature": 0.2,
                    "max_tokens": 500,
                    "messages": [
                        {"role": "system", "content": "Return only valid JSON."},
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return self._parse_json(content)
        except Exception as exc:
            logger.warning(f"OpenAI LLM call failed: {exc}")
            return None

    def _call_huggingface(self, prompt: str) -> Optional[object]:
        try:
            response = self._session.post(
                f"https://api-inference.huggingface.co/models/{self.hf_model}",
                headers={
                    "Authorization": f"Bearer {self.hf_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "inputs": prompt,
                    "parameters": {"max_new_tokens": 400, "temperature": 0.2},
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and data:
                text = data[0].get("generated_text", "")
                return self._parse_json(text)
            return None
        except Exception as exc:
            logger.warning(f"HuggingFace LLM call failed: {exc}")
            return None

    def _parse_json(self, text: str) -> Optional[object]:
        try:
            match = re.search(r"\{.*\}|\[.*\]", text, re.DOTALL)
            if not match:
                return None
            return json.loads(match.group())
        except Exception:
            return None

    def _normalize_claim_analysis(self, data: Dict[str, object]) -> Dict[str, object]:
        entity = str(data.get("main_entity", "")).strip()
        claim_intent = str(data.get("claim_intent", "fact")).strip().lower()
        claim_type = str(data.get("claim_type", "other")).strip().lower()
        keywords = data.get("keywords", [])
        if not isinstance(keywords, list):
            keywords = []
        keywords = [str(k).strip() for k in keywords if str(k).strip()]
        claim_category = str(data.get("claim_category", "general")).strip().lower()
        if claim_category not in {"numerical", "temporal", "opinion", "general"}:
            claim_category = "general"
        return {
            "main_entity": entity,
            "claim_intent": claim_intent,
            "keywords": keywords,
            "claim_type": claim_type,
            "claim_category": claim_category,
        }

    def _fallback_claim_analysis(self, claim: str) -> Dict[str, object]:
        entity, tokens = extract_candidate_entity(claim)
        keywords = tokens[:6]
        claim_category = self._infer_claim_category(claim)
        return {
            "main_entity": entity,
            "claim_intent": "fact",
            "keywords": keywords,
            "claim_type": "other",
            "claim_category": claim_category,
        }

    def _infer_claim_category(self, claim: str) -> str:
        lowered = claim.lower()
        if re.search(r"\d", claim):
            return "numerical"
        temporal_terms = ["currently", "as of", "today", "now", "this year", "currently", "is president", "is prime minister"]
        if any(term in lowered for term in temporal_terms):
            return "temporal"
        opinion_terms = ["opinion", "believe", "think", "should", "best", "worst"]
        if any(term in lowered for term in opinion_terms):
            return "opinion"
        return "general"

    def _sanitize_queries(
        self,
        queries: List[str],
        claim: str,
        entity: str,
        keywords: List[str],
    ) -> List[str]:
        cleaned = []
        seen = set()
        for query in queries:
            q = " ".join(query.split()).strip()
            if not q:
                continue
            if entity and entity.lower() not in q.lower():
                q = f"{entity} {q}".strip()
            key = q.lower()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(q)
        if len(cleaned) < 3:
            cleaned.extend(self._fallback_queries(claim, entity, keywords))
        return cleaned[:5]

    def _fallback_queries(self, claim: str, entity: str, keywords: List[str]) -> List[str]:
        base = entity or " ".join(keywords[:3]) or claim
        queries = [
            f"{base} official facts",
            f"{base} biography truth",
            f"{base} verification claim",
            f"{base} controversy explained",
            f"{base} fact check",
        ]
        return self._sanitize_queries(queries, claim, entity, keywords)

    def _normalize_reasoning(self, data: Dict[str, object]) -> Dict[str, object]:
        label = str(data.get("label", "UNCERTAIN")).strip().upper()
        if label not in {"TRUE", "MISINFORMATION", "UNCERTAIN"}:
            label = "UNCERTAIN"
        reasoning_confidence = float(data.get("reasoning_confidence", 0.5))
        reasoning_confidence = min(max(reasoning_confidence, 0.0), 1.0)
        return {
            "label": label,
            "reasoning": str(data.get("reasoning", "")),
            "reasoning_confidence": reasoning_confidence,
            "summary": str(data.get("summary", "")),
            "contradictions": data.get("contradictions", ""),
        }

    def _normalize_credibility(self, data: Optional[object]) -> float:
        if not isinstance(data, dict):
            return 0.55
        label = str(data.get("label", "neutral")).strip().lower()
        if label == "factual":
            return 0.85
        if label in {"speculative", "misleading"}:
            return 0.3
        return 0.6

    def _normalize_relationship(self, data: Optional[object]) -> str:
        if not isinstance(data, dict):
            return "NEUTRAL"
        label = str(data.get("label", "NEUTRAL")).strip().upper()
        if label not in {"SUPPORTS", "CONTRADICTS", "NEUTRAL"}:
            return "NEUTRAL"
        return label

    def _normalize_evidence_type(self, data: Optional[object]) -> str:
        if not isinstance(data, dict):
            return "factual"
        label = str(data.get("label", "factual")).strip().lower()
        if label not in {"factual", "historical", "opinion", "speculation"}:
            return "factual"
        return label

    def _fallback_reasoning(self, claim: str, evidence: List[Dict[str, object]]) -> Dict[str, object]:
        if not evidence:
            return {
                "label": "UNCERTAIN",
                "reasoning": "No evidence available to assess the claim.",
                "reasoning_confidence": 0.2,
                "summary": "Insufficient evidence.",
                "contradictions": "",
            }
        contradiction_count = sum(1 for item in evidence if item.get("contradiction"))
        support_count = len(evidence) - contradiction_count
        if contradiction_count >= 2:
            label = "MISINFORMATION"
        elif support_count >= 2:
            label = "TRUE"
        else:
            label = "UNCERTAIN"
        return {
            "label": label,
            "reasoning": "Heuristic reasoning used due to missing LLM provider.",
            "reasoning_confidence": 0.5,
            "summary": "Heuristic reasoning applied.",
            "contradictions": "" if contradiction_count == 0 else "Potential contradictions detected.",
        }
