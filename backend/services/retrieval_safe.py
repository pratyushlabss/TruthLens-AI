"""
FIXED: Retrieval System - PRODUCTION SAFE VERSION
Features: Wikipedia API safety, Tavily integration safety, fallback handling.
"""

import logging
import requests
import time
from typing import List, Dict, Tuple, Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)


class SafeRetrievalSystem:
    """
    Retrieval system with comprehensive error handling.
    NEVER crashes - always provides fallback data or empty list.
    """
    
    def __init__(self, timeout_seconds: int = 10):
        """Initialize retrieval system with timeout."""
        self.timeout = timeout_seconds
        self.wikipedia_api_url = "https://en.wikipedia.org/w/api.php"
        self.tavily_api_url = "https://api.tavily.com/search"
        logger.info(f"[RETRIEVAL] Initialized with {timeout_seconds}s timeout")
    
    # =========================================================================
    # WIKIPEDIA API CALLS - SAFE WRAPPERS
    # =========================================================================
    
    def _safe_wikipedia_search(self, query: str) -> List[str]:
        """
        Safely search Wikipedia - NEVER crashes.
        Returns list of article titles or empty list on failure.
        """
        if not query or not query.strip():
            logger.debug("[WIKI] ❌ Empty query provided")
            return []
        
        try:
            query = query.strip()[:200]
            logger.debug(f"[WIKI] Searching: {query}")
            
            # Step 1: Search for articles
            try:
                response = requests.get(
                    self.wikipedia_api_url,
                    params={
                        "action": "query",
                        "list": "search",
                        "srsearch": query,
                        "srwhat": "text",
                        "srlimit": 5,
                        "format": "json",
                    },
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()
                
            except requests.Timeout:
                logger.warning(f"[WIKI] ⚠️ Search timeout for: {query}")
                return []
                
            except requests.RequestException as e:
                logger.warning(f"[WIKI] ⚠️ Search request failed: {e}")
                return []
                
            except Exception as e:
                logger.warning(f"[WIKI] ⚠️ Search parse error: {e}")
                return []
            
            # Step 2: Extract article titles
            try:
                search_results = data.get("query", {}).get("search", [])
                titles = [item.get("title", "") for item in search_results if item.get("title")]
                
                logger.debug(f"[WIKI] ✅ Found {len(titles)} articles")
                return titles[:5]  # Limit to 5
                
            except (KeyError, ValueError) as e:
                logger.warning(f"[WIKI] ⚠️ Failed to parse search results: {e}")
                return []
        
        except Exception as e:
            logger.error(f"[WIKI] ❌ Unexpected error in search: {e}")
            return []
    
    def _safe_wikipedia_get_text(self, title: str) -> str:
        """
        Safely fetch Wikipedia article text - NEVER crashes.
        Returns article text or empty string on failure.
        """
        if not title or not title.strip():
            return ""
        
        try:
            title = title.strip()[:200]
            logger.debug(f"[WIKI] Fetching: {title}")
            
            # Fetch article content
            try:
                response = requests.get(
                    self.wikipedia_api_url,
                    params={
                        "action": "query",
                        "titles": title,
                        "prop": "extracts|info",
                        "explaintext": True,
                        "exintro": False,
                        "exlimit": 1,
                        "format": "json",
                    },
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()
                
            except requests.Timeout:
                logger.warning(f"[WIKI] ⚠️ Fetch timeout for: {title}")
                return ""
                
            except requests.RequestException as e:
                logger.warning(f"[WIKI] ⚠️ Fetch request failed: {e}")
                return ""
                
            except Exception as e:
                logger.warning(f"[WIKI] ⚠️ Fetch parse error: {e}")
                return ""
            
            # Extract text
            try:
                pages = data.get("query", {}).get("pages", {})
                if not pages:
                    return ""
                
                page = next(iter(pages.values()), {})
                text = page.get("extract", "")
                
                if text:
                    text = text[:5000]  # Limit to 5000 chars
                    logger.debug(f"[WIKI] ✅ Fetched {len(text)} chars")
                    return text
                else:
                    logger.debug(f"[WIKI] ⚠️ No text found for: {title}")
                    return ""
                    
            except (KeyError, ValueError, StopIteration) as e:
                logger.warning(f"[WIKI] ⚠️ Failed to parse article: {e}")
                return ""
        
        except Exception as e:
            logger.error(f"[WIKI] ❌ Unexpected error in get_text: {e}")
            return ""
    
    # =========================================================================
    # TAVILY API CALLS - SAFE WRAPPERS
    # =========================================================================
    
    def _safe_tavily_search(self, query: str, api_key: Optional[str] = None) -> List[Dict]:
        """
        Safely search Tavily - NEVER crashes.
        Returns list of result dicts or empty list on failure.
        """
        if not query or not query.strip():
            logger.debug("[TAVILY] ❌ Empty query")
            return []
        
        if not api_key:
            logger.debug("[TAVILY] ❌ No API key provided")
            return []
        
        try:
            query = query.strip()[:200]
            logger.debug(f"[TAVILY] Searching: {query}")
            
            # Call Tavily API
            try:
                response = requests.post(
                    self.tavily_api_url,
                    json={
                        "api_key": api_key,
                        "query": query,
                        "max_results": 3,
                        "include_domains": [],
                        "exclude_domains": [],
                    },
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()
                
            except requests.Timeout:
                logger.warning(f"[TAVILY] ⚠️ Search timeout for: {query}")
                return []
                
            except requests.HTTPError as e:
                if e.response.status_code == 401:
                    logger.warning("[TAVILY] ⚠️ Invalid API key")
                elif e.response.status_code == 429:
                    logger.warning("[TAVILY] ⚠️ Rate limited")
                else:
                    logger.warning(f"[TAVILY] ⚠️ HTTP error: {e.response.status_code}")
                return []
                
            except requests.RequestException as e:
                logger.warning(f"[TAVILY] ⚠️ Request failed: {e}")
                return []
                
            except Exception as e:
                logger.warning(f"[TAVILY] ⚠️ Parse error: {e}")
                return []
            
            # Extract results
            try:
                results = data.get("results", [])
                
                # Validate and sanitize results
                clean_results = []
                for result in results:
                    try:
                        clean_results.append({
                            "title": str(result.get("title", "Unknown"))[:200],
                            "content": str(result.get("content", ""))[:2000],
                            "url": str(result.get("url", ""))[:500],
                            "source": str(result.get("source", "Tavily"))[:100],
                        })
                    except Exception as e:
                        logger.debug(f"[TAVILY] ⚠️ Failed to parse result: {e}")
                        continue
                
                logger.debug(f"[TAVILY] ✅ Found {len(clean_results)} results")
                return clean_results[:3]
                
            except (KeyError, ValueError) as e:
                logger.warning(f"[TAVILY] ⚠️ Failed to parse results: {e}")
                return []
        
        except Exception as e:
            logger.error(f"[TAVILY] ❌ Unexpected error: {e}")
            return []
    
    # =========================================================================
    # MAIN RETRIEVAL ORCHESTRATION - SAFE
    # =========================================================================
    
    def retrieve(self, query: str, tavily_api_key: Optional[str] = None) -> List[Dict]:
        """
        Main retrieval orchestration - NEVER crashes.
        
        Returns:
            List of evidence dicts with keys:
            - sentence (str): Extracted sentence
            - source (str): Source name
            - url (str): Source URL
            - title (str): Article/result title
        
        GUARANTEES:
            - Returns list (never None)
            - Each item has required keys (never None values)
            - Never raises exception
            - Always provides something or empty list
        """
        logger.info(f"[RETRIEVAL] Starting retrieval for: {query[:100]}")
        
        all_evidence = []
        start_time = time.time()
        
        try:
            # STEP 1: Get Wikipedia articles
            logger.debug("[RETRIEVAL] STEP 1: Wikipedia search")
            try:
                wiki_titles = self._safe_wikipedia_search(query)
                logger.debug(f"[RETRIEVAL] Found {len(wiki_titles)} Wikipedia articles")
                
                # Fetch text from each Wikipedia article
                for title in wiki_titles:
                    try:
                        text = self._safe_wikipedia_get_text(title)
                        if text:
                            # Extract sentences
                            sentences = self._extract_sentences(text)
                            for sentence in sentences[:3]:  # Limit to 3 per article
                                try:
                                    all_evidence.append({
                                        "sentence": sentence,
                                        "source": "Wikipedia",
                                        "title": title,
                                        "url": f"https://en.wikipedia.org/wiki/{quote(title)}",
                                    })
                                except Exception as e:
                                    logger.debug(f"[RETRIEVAL] ⚠️ Failed to add evidence: {e}")
                                    continue
                    
                    except Exception as e:
                        logger.debug(f"[RETRIEVAL] ⚠️ Failed to fetch Wikipedia article: {e}")
                        continue
                
                logger.debug(f"[RETRIEVAL] Added {len(all_evidence)} Wikipedia evidences")
                
            except Exception as e:
                logger.warning(f"[RETRIEVAL] ⚠️ Wikipedia retrieval error: {e}")
                # Continue to Tavily
            
            # STEP 2: Get Tavily results (if API key provided)
            logger.debug("[RETRIEVAL] STEP 2: Tavily search")
            try:
                if tavily_api_key:
                    tavily_results = self._safe_tavily_search(query, tavily_api_key)
                    logger.debug(f"[RETRIEVAL] Found {len(tavily_results)} Tavily results")
                    
                    for result in tavily_results:
                        try:
                            # Extract up to 2 sentences per result
                            content = result.get("content", "")
                            if content:
                                sentences = self._extract_sentences(content)
                                for sentence in sentences[:2]:
                                    try:
                                        all_evidence.append({
                                            "sentence": sentence,
                                            "source": result.get("source", "Tavily"),
                                            "title": result.get("title", ""),
                                            "url": result.get("url", ""),
                                        })
                                    except Exception as e:
                                        logger.debug(f"[RETRIEVAL] ⚠️ Failed to add Tavily evidence: {e}")
                                        continue
                        
                        except Exception as e:
                            logger.debug(f"[RETRIEVAL] ⚠️ Failed to process Tavily result: {e}")
                            continue
                    
                    logger.debug(f"[RETRIEVAL] Total evidences after Tavily: {len(all_evidence)}")
                else:
                    logger.debug("[RETRIEVAL] ⚠️ Tavily API key not provided, skipping")
                    
            except Exception as e:
                logger.warning(f"[RETRIEVAL] ⚠️ Tavily retrieval error: {e}")
                # Continue with what we have
            
            # STEP 3: Ensure minimum safe format
            logger.debug("[RETRIEVAL] STEP 3: Sanitizing results")
            try:
                safe_evidence = []
                for item in all_evidence:
                    try:
                        safe_item = {
                            "sentence": str(item.get("sentence", "")).strip()[:500],
                            "source": str(item.get("source", "Unknown")).strip()[:100],
                            "url": str(item.get("url", "")).strip()[:2000],
                            "title": str(item.get("title", "")).strip()[:200],
                        }
                        
                        # Ensure sentence is not empty
                        if safe_item["sentence"]:
                            safe_evidence.append(safe_item)
                    
                    except Exception as e:
                        logger.debug(f"[RETRIEVAL] ⚠️ Failed to sanitize evidence: {e}")
                        continue
                
                all_evidence = safe_evidence
                
            except Exception as e:
                logger.error(f"[RETRIEVAL] ❌ Sanitization error: {e}")
            
            duration = time.time() - start_time
            logger.info(f"[RETRIEVAL] ✅ Complete: {len(all_evidence)} evidences in {duration:.2f}s")
            
            # Return what we have (or empty list if nothing)
            return all_evidence if all_evidence else []
        
        except Exception as e:
            logger.error(f"[RETRIEVAL] ❌ CRITICAL: Retrieval failed: {e}", exc_info=True)
            # Return empty list - NEVER crash
            return []
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text - SAFE.
        Returns list of sentences or empty list.
        """
        if not text or not text.strip():
            return []
        
        try:
            # Simple sentence splitting
            sentences = []
            for paragraph in text.split("\n"):
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                
                # Split by . ! ? but keep them
                for sent in paragraph.replace("!", ".").replace("?", ".").split("."):
                    sent = sent.strip()
                    if sent and len(sent) > 10:  # Minimum 10 chars
                        sentences.append(sent + ".")
                        if len(sentences) >= 10:  # Limit to 10 sentences per text
                            break
            
            return sentences[:10]
        
        except Exception as e:
            logger.warning(f"[EXTRACTION] ⚠️ Failed to extract sentences: {e}")
            return []
