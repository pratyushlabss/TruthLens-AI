"""RAG Pipeline for fact-checking with real evidence retrieval."""

import os
import logging
from typing import List, Dict, Optional, Any
import requests
import json
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class RagPipeline:
    """RAG (Retrieval-Augmented Generation) pipeline for fact-checking."""
    
    def __init__(self):
        """Initialize RAG pipeline with configured API keys."""
        # Load API Keys from environment
        # DEPRECATED: HuggingFace and Pinecone removed - using OpenAI instead
        self.scraper_key = os.getenv("SCRAPER_KEY", "").strip()
        
        # Web search fallback keys (if available)
        self.google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY", "").strip()
        self.google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "").strip()
        self.serper_api_key = os.getenv("SERPER_API_KEY", "").strip()
        self.llm_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        
        # Check API key availability and log status
        logger.info("=== RAG Pipeline API Configuration ===")
        logger.info(f"OpenAI API: {'✓ CONFIGURED' if self.llm_api_key else '✗ MISSING'}")
        logger.info(f"Web Scraper API: {'✓ CONFIGURED' if self.scraper_key else '✗ MISSING'}")
        logger.info(f"Serper Search: {'✓ CONFIGURED' if self.serper_api_key else '✗ MISSING'}")
        logger.info(f"Google Search: {'✓ CONFIGURED' if (self.google_api_key and self.google_search_engine_id) else '✗ MISSING'}")
        logger.info(f"OpenAI LLM: {'✓ CONFIGURED' if self.llm_api_key else '✗ MISSING'}")
        logger.info("=" * 40)
        
        # Use Serper as fallback for web search (free tier available)
        self.use_serper = bool(self.serper_api_key)
        self.use_google = bool(self.google_api_key and self.google_search_engine_id)
        
        # Initialize Pinecone if available
        self.pinecone_index = None
        if self.pinecone_key:
            try:
                from pinecone import Pinecone, ServerlessSpec
                pinecone_client = Pinecone(api_key=self.pinecone_key)
                index_name = os.getenv("PINECONE_INDEX_NAME", "truthlens-index")
                logger.info(f"Pinecone API called: Initializing index '{index_name}'")
                # Try to get index, don't fail if it doesn't exist
                try:
                    self.pinecone_index = pinecone_client.Index(index_name)
                    logger.info(f"Pinecone query success: Connected to index '{index_name}'")
                except Exception as e:
                    logger.warning(f"Pinecone index '{index_name}' not found: {e}")
            except Exception as e:
                logger.error(f"Pinecone initialization failed: {e}")
        else:
            logger.warning("Pinecone API key not configured - vector search disabled")
        
        # Model configuration
        self.model_name = os.getenv("LLM_MODEL", "mixtral-8x7b-instruct")
        
        logger.info("RAG Pipeline ready for analysis")
    
    async def analyze_with_rag(
        self,
        claim: str,
        num_sources: int = 5
    ) -> Dict[str, Any]:
        """
        Analyze a claim using RAG pipeline.
        
        Steps:
        1. Generate search queries from the claim
        2. Search for evidence
        3. Scrape and clean content
        4. Use LLM to reason about evidence
        5. Generate TRUE/FALSE verdict
        
        Args:
            claim: The claim to fact-check
            num_sources: Number of sources to retrieve
            
        Returns:
            Dictionary with verdict, confidence, sources, and reasoning
        """
        try:
            # Step 1: Generate search queries
            search_queries = self._generate_search_queries(claim)
            logger.info(f"Generated {len(search_queries)} search queries")
            
            # Step 2: Search for evidence
            search_results = []
            for query in search_queries[:3]:  # Limit to 3 main queries
                results = await self._search_evidence(query, num_sources=3)
                search_results.extend(results)
            
            # Remove duplicates and keep top results
            unique_results = self._deduplicate_results(search_results)[:num_sources]
            
            if not unique_results:
                logger.warning(f"No search results found for claim: {claim[:100]}")
                return {
                    "verdict": "FALSE",  # Default to FALSE if no evidence found
                    "confidence": 25.0,
                    "explanation": "Insufficient credible evidence found to verify claim.",
                    "sources": [],
                    "signals": ["Unable to find credible sources supporting this claim"],
                    "reasoning": "Web search returned no relevant results. Claim cannot be verified."
                }
            
            # Step 3: Scrape content from top sources
            sources_with_content = []
            for result in unique_results[:3]:  # Process top 3 sources
                content = await self._scrape_content(result["url"])
                if content:
                    result["summary"] = content[:500]  # First 500 chars as summary
                    result["credibility"] = self._assess_credibility(result.get("source", ""))
                    sources_with_content.append(result)
            
            if not sources_with_content:
                logger.warning("Could not scrape content from sources")
                return {
                    "verdict": "FALSE",
                    "confidence": 35.0,
                    "explanation": "Found sources but unable to verify content.",
                    "sources": unique_results,
                    "signals": ["Sources found but content not accessible"],
                    "reasoning": "Unable to scrape and verify source content."
                }
            
            # Step 4: LLM reasoning
            verdict_result = await self._reason_with_llm(
                claim,
                sources_with_content
            )
            
            return {
                "verdict": verdict_result["verdict"],  # TRUE or FALSE only
                "confidence": verdict_result["confidence"],
                "explanation": verdict_result["explanation"],
                "sources": sources_with_content,
                "signals": verdict_result["signals"],
                "reasoning": verdict_result["reasoning"]
            }
            
        except Exception as e:
            logger.error(f"RAG pipeline error: {e}")
            return {
                "verdict": "FALSE",
                "confidence": 20.0,
                "explanation": "Error during fact-checking process.",
                "sources": [],
                "signals": ["System error occurred during analysis"],
                "reasoning": str(e)
            }
    
    def _generate_search_queries(self, claim: str) -> List[str]:
        """Generate optimal search queries from the claim."""
        queries = [
            claim,  # Original claim
            claim.split()[0:5],  # First 5 words
            f"fact check {claim}",  # With fact check prefix
        ]
        
        # Clean and filter
        search_queries = []
        for q in queries:
            if isinstance(q, list):
                q = " ".join(q)
            q = q.strip()
            if q and len(q) > 3:
                search_queries.append(q)
        
        return search_queries[:5]
    
    async def _search_evidence(
        self,
        query: str,
        num_sources: int = 5
    ) -> List[Dict]:
        """
        Search for evidence using available APIs.
        
        Priority:
        1. Serper.dev (free tier available)
        2. Google Custom Search (requires setup)
        3. DuckDuckGo (fallback)
        """
        if self.use_serper:
            return await self._search_serper(query, num_sources)
        elif self.use_google:
            return await self._search_google(query, num_sources)
        else:
            # Fallback: Use simple heuristic sources
            return self._get_fallback_sources(query)
    
    async def _search_serper(
        self,
        query: str,
        num_sources: int = 5
    ) -> List[Dict]:
        """Search using Serper.dev API."""
        try:
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "num": num_sources
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data.get("organic", [])[:num_sources]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": urlparse(item.get("link", "")).netloc,
                    "position": item.get("position", 0)
                })
            
            logger.info(f"Serper search returned {len(results)} results for '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Serper search error: {e}")
            return []
    
    async def _search_google(
        self,
        query: str,
        num_sources: int = 5
    ) -> List[Dict]:
        """Search using Google Custom Search API."""
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "q": query,
                "key": self.google_api_key,
                "cx": self.google_search_engine_id,
                "num": num_sources
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data.get("items", [])[:num_sources]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": item.get("displayLink", ""),
                    "position": item.get("position", 0) if hasattr(item, "position") else 0
                })
            
            logger.info(f"Google search returned {len(results)} results for '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return []
    
    def _get_fallback_sources(self, query: str) -> List[Dict]:
        """
        Fallback: Return Wikipedia and reliable news sources.
        This ensures demo/fallback mode still works without API keys.
        """
        fallback_sources = [
            {
                "title": f"Wikipedia article on {query.split()[0] if query else 'Topic'}",
                "url": f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
                "snippet": "Fallback source - requires API key for real results",
                "source": "en.wikipedia.org",
                "position": 1
            },
            {
                "title": f"BBC Fact Check: {query[:50]}",
                "url": "https://www.bbc.com/news/science_and_environment",
                "snippet": "Fallback source - requires API key for real results",
                "source": "bbc.com",
                "position": 2
            }
        ]
        
        logger.warning("Using fallback sources - configure API keys for real results")
        return fallback_sources
    
    async def _scrape_content(self, url: str) -> Optional[str]:
        """
        Scrape content from URL.
        
        Priority:
        1. Use WebScraping.ai API if SCRAPER_KEY is available
        2. Fallback to basic requests with BeautifulSoup
        """
        # PRIMARY: Use WebScraping.ai API if key is configured
        if self.scraper_key:
            return await self._scrape_with_webscraping_ai(url)
        
        # FALLBACK: Use basic scraping
        return await self._scrape_with_requests(url)
    
    async def _scrape_with_webscraping_ai(self, url: str) -> Optional[str]:
        """
        Scrape content using WebScraping.ai API.
        
        This API provides:
        - JavaScript rendering
        - Proxy rotation
        - Header management
        - Automatic retry logic
        """
        try:
            scraper_url = "https://api.webscraping.ai/v1"
            
            params = {
                "url": url,
                "api_key": self.scraper_key,
                "timeout": 30000,
                "proxy": "residential"  # Use residential proxies for better success
            }
            
            logger.info(f"Web scraping API called: Scraping {url}")
            
            response = requests.get(scraper_url, params=params, timeout=15)
            response.raise_for_status()
            
            # Extract HTML content
            html_content = response.text
            
            # Simple content extraction from HTML
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Remove script and style elements
                for tag in soup(["script", "style"]):
                    tag.decompose()
                
                # Get text
                text = soup.get_text()
                
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                content = text[:1500]  # Return first 1500 chars
                
                logger.info(f"Web scraping API called: Successfully scraped {len(content)} chars from {url}")
                return content
                
            except ImportError:
                # If BeautifulSoup not available, use simple text extraction
                logger.warning("BeautifulSoup not available, using basic text extraction")
                return html_content[:1500]
            
        except requests.exceptions.Timeout:
            logger.warning(f"Web scraping API called: Timeout scraping {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.warning(f"Web scraping API called: HTTP error {e.response.status_code} scraping {url}")
            return None
        except Exception as e:
            logger.warning(f"Web scraping API called: Error scraping {url}: {e}")
            return None
    
    async def _scrape_with_requests(self, url: str) -> Optional[str]:
        """
        Scrape content using basic requests.
        
        Fallback method when WebScraping.ai is not available.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Simple content extraction
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove unwanted tags
                for tag in soup(["script", "style"]):
                    tag.decompose()
                
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                content = ' '.join(chunk for chunk in chunks if chunk)
                content = content[:1500]
                
                logger.debug(f"Scraped {len(content)} chars from {url} (basic method)")
                return content
                
            except ImportError:
                # If BeautifulSoup not available, return raw text
                logger.debug(f"Scraped content from {url} (raw extraction)")
                return response.text[:1500]
            
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
            return None
    
    def _assess_credibility(self, source_domain: str) -> str:
        """
        Assess source credibility based on domain.
        
        Trusted sources: Wikipedia, BBC, Reuters, AP, NPR, government domains, etc.
        Medium: Reputable news sites, academic institutions
        Low: Unknown sources, social media, blogs without verification
        """
        trusted_domains = [
            "wikipedia.org",
            "bbc.com",
            "reuters.com",
            "apnews.com",
            "npr.org",
            "nature.com",
            "sciencedaily.com",
            "nasa.gov",
            ".edu",
            ".gov",
            "nature.com",
            "sciencetimes.com"
        ]
        
        # Check if domain is in trusted list
        source_lower = source_domain.lower()
        for trusted in trusted_domains:
            if trusted in source_lower:
                return "High"
        
        # Medium credibility for most news/content sites
        if any(keyword in source_lower for keyword in ["news", "times", "post", "tribune", "observer"]):
            return "Medium"
        
        # Default: Low credibility
        return "Low"
    
    async def _reason_with_llm(
        self,
        claim: str,
        sources: List[Dict]
    ) -> Dict[str, Any]:
        """
        Use LLM to reason about evidence and generate verdict.
        
        Priority:
        1. Use HuggingFace API if HF_TOKEN is available
        2. Fall back to OpenAI API if OPENAI_API_KEY is available
        3. Use heuristic reasoning as final fallback
        
        Returns: {verdict: "TRUE" | "FALSE", confidence: 0-100, explanation, signals, reasoning}
        """
        try:
            # PRIMARY: Use HuggingFace API if token is configured
            if self.hf_token:
                logger.info("HuggingFace API called: Starting inference for fact-checking")
                hf_result = await self._reason_with_huggingface(claim, sources)
                if hf_result:
                    logger.info("HuggingFace API called: Inference completed successfully")
                    return hf_result
            
            # SECONDARY: Use OpenAI API if key is configured
            if self.llm_api_key:
                logger.info("OpenAI API called: Starting reasoning with GPT")
                openai_result = await self._reason_with_openai(claim, sources)
                if openai_result:
                    logger.info("OpenAI API called: Reasoning completed successfully")
                    return openai_result
            
            # FALLBACK: Use heuristic reasoning
            logger.warning("No LLM API configured - using heuristic reasoning")
            return self._heuristic_reasoning(claim, sources)
            
        except Exception as e:
            logger.error(f"LLM reasoning error: {e}")
            # Fall back to heuristic on any error
            return self._heuristic_reasoning(claim, sources)
    
    async def _reason_with_huggingface(self, claim: str, sources: List[Dict]) -> Optional[Dict[str, Any]]:
        """
        Use HuggingFace API for inference.
        
        This uses HF's inference API with models like Mistral, Llama, etc.
        for fact-checking and reasoning.
        """
        try:
            # Prepare prompt
            evidence_text = self._prepare_evidence_text(sources)
            
            prompt = f"""Fact-check the following claim based on the provided sources.
            
Claim: {claim}

Evidence from sources:
{evidence_text}

Based on the evidence above, determine if the claim is TRUE or FALSE.
Respond with ONLY a JSON object in this exact format:
{{"verdict": "TRUE" or "FALSE", "confidence": 0-100, "explanation": "short explanation", "signals": ["signal1", "signal2"]}}"""
            
            # Call HuggingFace Inference API
            hf_api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
            headers = {
                "Authorization": f"Bearer {self.hf_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "do_sample": True
                }
            }
            
            response = requests.post(hf_api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract generated text
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                
                # Try to parse JSON from generated text
                try:
                    import re
                    json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
                    if json_match:
                        json_obj = json.loads(json_match.group())
                        return {
                            "verdict": json_obj.get("verdict", "FALSE").upper(),
                            "confidence": float(json_obj.get("confidence", 50)),
                            "explanation": json_obj.get("explanation", "Analysis completed"),
                            "signals": json_obj.get("signals", ["AI Analysis"]),
                            "reasoning": "HuggingFace LLM inference"
                        }
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse HF response as JSON: {e}")
                    return None
            
            return None
            
        except requests.exceptions.Timeout:
            logger.warning("HuggingFace API called: Timeout - using fallback")
            return None
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HuggingFace API called: HTTP error {e.response.status_code}")
            return None
        except Exception as e:
            logger.warning(f"HuggingFace API called: Error - {e}")
            return None
    
    async def _reason_with_openai(self, claim: str, sources: List[Dict]) -> Optional[Dict[str, Any]]:
        """
        Use OpenAI API (GPT) for reasoning.
        
        Fallback when HuggingFace is not available.
        """
        try:
            evidence_text = self._prepare_evidence_text(sources)
            
            prompt = f"""Fact-check the claim: {claim}

Evidence:
{evidence_text}

Is this claim TRUE or FALSE? Respond with JSON: {{"verdict": "TRUE"/"FALSE", "confidence": 0-100, "explanation": "..."}}"""
            
            # Call OpenAI API (this would require openai library)
            import openai
            openai.api_key = self.llm_api_key
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON from response
            try:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_obj = json.loads(json_match.group())
                    return {
                        "verdict": json_obj.get("verdict", "FALSE").upper(),
                        "confidence": float(json_obj.get("confidence", 50)),
                        "explanation": json_obj.get("explanation", "Analysis completed"),
                        "signals": json_obj.get("signals", ["GPT Analysis"]),
                        "reasoning": "OpenAI GPT inference"
                    }
            except (json.JSONDecodeError, ValueError):
                return None
            
            return None
            
        except Exception as e:
            logger.warning(f"OpenAI API called: Error - {e}")
            return None
    
    def _prepare_evidence_text(self, sources: List[Dict]) -> str:
        """Prepare formatted evidence text for LLM reasoning."""
        if not sources:
            return "No evidence sources found."
        
        evidence = []
        for i, source in enumerate(sources, 1):
            credibility = source.get("credibility", "Unknown")
            title = source.get("title", "Unknown")
            summary = source.get("summary", source.get("snippet", ""))[:300]
            
            evidence.append(f"{i}. [{credibility}] {title}\n   {summary}")
        
        return "\n".join(evidence)

    
    def _heuristic_reasoning(
        self,
        claim: str,
        sources: List[Dict]
    ) -> Dict[str, Any]:
        """
        Simple heuristic reasoning when LLM is not available.
        
        Analyzes source snippets and credibility to determine verdict.
        """
        if not sources:
            return {
                "verdict": "FALSE",
                "confidence": 20.0,
                "explanation": "No credible sources found to support this claim.",
                "signals": ["No evidence found"],
                "reasoning": "Insufficient evidence in search results."
            }
        
        # Count supporting vs contradicting sources
        claim_words = set(claim.lower().split())
        supporting_score = 0
        contradicting_score = 0
        
        for source in sources:
            snippet = source.get("snippet", "").lower()
            
            # Simple heuristic: count matching words
            matching_words = len(claim_words & set(snippet.split()))
            
            # Check for contradiction keywords
            contradiction_keywords = ["not", "false", "debunked", "hoax", "incorrect", "wrong"]
            if any(keyword in snippet for keyword in contradiction_keywords):
                contradicting_score += source.get("credibility") == "High" and 2 or 1
            else:
                supporting_score += matching_words / max(len(claim_words), 1)
        
        # Determine verdict
        if contradicting_score > supporting_score:
            verdict = "FALSE"
            confidence = min(95, 50 + (contradicting_score - supporting_score) * 10)
        elif supporting_score > 0:
            verdict = "TRUE"
            confidence = min(95, 50 + supporting_score * 10)
        else:
            verdict = "FALSE"
            confidence = 30.0
        
        # Generate signals
        signals = []
        if contradicting_score > 0:
            signals.append("Contradicted by credible sources")
        if supporting_score > 0:
            signals.append("Supported by evidence")
        if not sources:
            signals.append("No verifiable evidence found")
        
        return {
            "verdict": verdict,
            "confidence": float(confidence),
            "explanation": f"Analysis based on {len(sources)} sources.",
            "signals": signals if signals else ["Inconclusive evidence"],
            "reasoning": f"Supporting score: {supporting_score:.1f}, Contradicting score: {contradicting_score:.1f}"
        }
    
    def _summarize_evidence(
        self,
        claim: str,
        sources: List[Dict]
    ) -> str:
        """Create a summary of evidence for LLM reasoning."""
        summary = f"Claim: {claim}\n\nEvidence from {len(sources)} sources:\n"
        
        for i, source in enumerate(sources, 1):
            summary += f"\n{i}. {source.get('title', 'Unknown')}\n"
            summary += f"   Source: {source.get('source', 'Unknown')}\n"
            summary += f"   Credibility: {source.get('credibility', 'Unknown')}\n"
            summary += f"   Summary: {source.get('summary', source.get('snippet', 'N/A'))[:200]}\n"
        
        return summary
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results by URL."""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get("url", "")
            if url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
