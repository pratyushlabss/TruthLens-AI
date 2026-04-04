"""Wikipedia retrieval and query expansion for RAG pipeline."""
import logging
from typing import List, Dict, Any
import re
import os
import requests
import json

try:
    import wikipedia as wiki
    HAS_WIKIPEDIA = True
except ImportError:
    HAS_WIKIPEDIA = False
    logging.warning("wikipedia library not installed")

logger = logging.getLogger(__name__)


class QueryExpander:
    """Expands a user query into multiple search variants."""
    
    def expand_query(self, query: str, num_variants: int = 5) -> List[str]:
        """Generate query variants for better coverage."""
        if not query:
            return [query]
        
        variants = [query.strip()]
        
        # Remove question marks
        statement = query.rstrip("?").strip()
        if statement and statement != query:
            variants.append(statement)
        
        # Add contextual keywords
        if len(variants) < num_variants:
            keywords = ["facts", "evidence", "research", "information", "what is"]
            for kw in keywords:
                if len(variants) < num_variants:
                    new_variant = f"{statement} {kw}" if statement else query
                    if new_variant not in variants:
                        variants.append(new_variant)
        
        return variants[:num_variants]


class WikipediaRetriever:
    """Retrieves articles from Wikipedia API."""
    
    def __init__(self):
        """Initialize retriever."""
        if not HAS_WIKIPEDIA:
            logger.warning("Wikipedia library not available")
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search Wikipedia and return articles."""
        if not query or not HAS_WIKIPEDIA:
            return []
        
        try:
            results = wiki.search(query, results=max_results)
            articles = []
            
            for title in results[:max_results]:
                try:
                    # BUG FIX 5: Add retry logic with backoff
                    page = None
                    retries = 2
                    for attempt in range(retries + 1):
                        try:
                            page = wiki.page(title, auto_suggest=True, redirect=True)
                            break
                        except Exception as retry_err:
                            if attempt < retries:
                                import time
                                time.sleep(1)  # 1 second backoff
                                continue
                            else:
                                raise retry_err
                    
                    if page:
                        articles.append({
                            "title": page.title,
                            "url": page.url,
                            "content": page.content[:5000],
                            "summary": page.summary[:1000],
                            "source": "Wikipedia"
                        })
                except wiki.exceptions.DisambiguationError:
                    continue
                except wiki.exceptions.PageError:
                    continue
                except Exception as e:
                    # BUG FIX 5: Change debug to error for failures
                    logger.error(f"Error fetching page {title} (retries exhausted): {e}")
                    # Return None on failure instead of partial data
                    continue
            
            return articles
        
        except Exception as e:
            logger.error(f"Wikipedia search error for '{query}': {e}")
            return []


class TavilyRetriever:
    """Retrieves web search results from Tavily API."""
    
    def __init__(self, tavily_api_key: str = None):
        """Initialize Tavily retriever with API key."""
        # Get API key from parameter or environment
        self.api_key = tavily_api_key or os.getenv("TAVILY_API_KEY", "").strip()
        self.base_url = "https://api.tavily.com/search"
        
        if self.api_key:
            logger.info("✅ [Tavily] Initialized with API key")
        else:
            logger.warning("⚠️ [Tavily] API key not found - Tavily search disabled")
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search using Tavily API and return results.
        
        Args:
            query: Search query
            max_results: Max results to return (default 5)
        
        Returns:
            List of article dicts with title, url, content, source
        """
        if not query or not self.api_key:
            return []
        
        try:
            logger.debug(f"[Tavily] Searching: {query[:100]}")
            
            payload = {
                "api_key": self.api_key,
                "query": query,
                "max_results": min(max_results, 5),  # Tavily limit is often 5
                "include_answer": True,
                "include_raw_content": True,
                "search_depth": "basic"
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            # Parse Tavily response
            if "results" in data:
                for i, result in enumerate(data["results"][:max_results]):
                    try:
                        article = {
                            "title": result.get("title", f"Result {i+1}"),
                            "url": result.get("url", ""),
                            "content": result.get("content", "")[:5000],  # Limit to 5000 chars
                            "summary": result.get("content", "")[:1000] if result.get("content") else "",
                            "source": "Tavily"
                        }
                        if article.get("content"):  # Only add if has content
                            articles.append(article)
                    except Exception as e:
                        logger.debug(f"[Tavily] Error parsing result {i}: {e}")
                        continue
            
            logger.debug(f"[Tavily] ✅ Retrieved {len(articles)} results")
            return articles
        
        except requests.Timeout:
            logger.warning(f"[Tavily] ⚠️ Request timeout (10s)")
            return []
        except requests.HTTPError as e:
            logger.warning(f"[Tavily] ⚠️ HTTP error: {e.response.status_code}")
            return []
        except json.JSONDecodeError:
            logger.warning(f"[Tavily] ⚠️ Invalid JSON response")
            return []
        except Exception as e:
            logger.error(f"[Tavily] ❌ Error: {e}")
            return []


class RetrievalPipeline:
    """Orchestrates retrieval with query expansion and multiple sources."""
    
    def __init__(self, tavily_api_key: str = None):
        """
        Initialize retrieval pipeline with Wikipedia and Tavily.
        
        Args:
            tavily_api_key: Optional Tavily API key (uses env var if not provided)
        """
        self.expander = QueryExpander()
        self.wiki_retriever = WikipediaRetriever()
        self.tavily_retriever = TavilyRetriever(tavily_api_key)
        
        has_tavily = bool(self.tavily_retriever.api_key)
        logger.info(f"✅ RetrievalPipeline initialized [Wikipedia: ✅, Tavily: {'✅' if has_tavily else '⚠️ disabled'}]")
    
    def retrieve(self, query: str, max_articles: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve articles from Wikipedia and Tavily.
        
        Strategy:
        1. Always fetch from Wikipedia
        2. Also fetch from Tavily if authorized
        3. Merge results, avoiding duplicates
        4. Return up to max_articles
        """
        if not query:
            logger.warning("[Retrieval] Empty query")
            return []
        
        logger.info(f"[Retrieval] Searching: {query[:100]}")
        
        queries = self.expander.expand_query(query, num_variants=5)
        all_results = []
        seen_urls = set()
        
        # PHASE 1: Wikipedia (always)
        logger.debug(f"[Retrieval-Phase1] Searching Wikipedia with {len(queries)} query variants")
        for q in queries:
            if len(all_results) >= max_articles:
                break
            
            try:
                wiki_results = self.wiki_retriever.search(q, max_results=5)
                for article in wiki_results:
                    if article.get("url") not in seen_urls and len(all_results) < max_articles:
                        all_results.append(article)
                        seen_urls.add(article["url"])
            except Exception as e:
                logger.warning(f"[Retrieval] Wikipedia query '{q}' failed: {e}")
        
        logger.info(f"[Retrieval] Wikipedia yielded {len(all_results)} unique articles")
        
        # PHASE 2: Tavily (if configured and we need more results)
        if self.tavily_retriever.api_key and len(all_results) < max_articles:
            remaining = max_articles - len(all_results)
            logger.debug(f"[Retrieval-Phase2] Searching Tavily for {remaining} more articles")
            
            try:
                tavily_results = self.tavily_retriever.search(query, max_results=min(5, remaining))
                added = 0
                for article in tavily_results:
                    if article.get("url") not in seen_urls and len(all_results) < max_articles:
                        all_results.append(article)
                        seen_urls.add(article["url"])
                        added += 1
                
                logger.info(f"[Retrieval] Tavily added {added} articles")
            except Exception as e:
                logger.warning(f"[Retrieval] Tavily search failed (non-fatal): {e}")
        else:
            logger.debug("[Retrieval] Tavily skipped (no API key or max articles reached)")
        
        logger.info(f"[Retrieval] ✅ Final result: {len(all_results)} articles from Wikipedia + Tavily")
        return all_results
