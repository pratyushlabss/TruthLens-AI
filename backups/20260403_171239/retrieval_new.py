"""Wikipedia retrieval and query expansion for RAG pipeline."""
import logging
import os
from typing import List, Dict, Any, Optional
import re
from urllib.parse import quote
import time

import requests

try:
    import wikipedia as wiki
    HAS_WIKIPEDIA = True
except ImportError:
    HAS_WIKIPEDIA = False
    wiki = None
    logging.warning("wikipedia library not installed; using Wikipedia API fallback")

logger = logging.getLogger(__name__)

# Global cache for Tavily and Wikipedia results
_RETRIEVAL_CACHE = {}

class RetrievalError(Exception):
    """Raised when retrieval fails."""

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_REST_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"
DEFAULT_USER_AGENT = "TruthLensAI/1.0 (retrieval_new.py)"
TAVILY_API_URL = "https://api.tavily.com/search"


class QueryExpander:
    """Expands a user query into multiple search variants."""

    def __init__(self, expansion_count: int = 3):
        self.expansion_count = expansion_count
    
    def expand_query(self, query: str, num_variants: int = 3) -> List[str]:
        """Generate query variants for better coverage."""
        if not query:
            raise RetrievalError("Empty query")
        
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
    
    def expand_query_by_intent(self, query: str, entity: str, intent: str) -> List[str]:
        """
        QUERY EXPANSION BY INTENT: Generate intent-specific search queries.
        
        Args:
            query: Original claim/query
            entity: Main entity/subject
            intent: Claim intent ('life_status', 'historical', 'general')
        
        Returns:
            List of 4-6 intent-specific queries
        """
        queries = set()  # Use set to avoid duplicates
        
        if intent == "life_status":
            # Life status queries focus on current status and death news
            queries.add(f"Is {entity} alive")
            queries.add(f"{entity} death news")
            queries.add(f"{entity} alive 2024 current status")
            queries.add(f"{entity} recent news alive")
            queries.add(f"{entity} still living")
            queries.add(query)  # Original query
            
        elif intent == "historical":
            # Historical queries focus on timeline and events
            queries.add(f"{entity} history timeline")
            queries.add(f"{entity} when first established")
            queries.add(f"{entity} founding date event")
            queries.add(f"{entity} biography facts")
            queries.add(query)
            
        else:  # general
            # General queries for broad coverage
            queries.add(f"{entity}")
            queries.add(f"{entity} facts information")
            queries.add(f"{entity} what is")
            queries.add(f"{entity} biography")
            queries.add(query)
        
        # Remove duplicates and limit to 5
        result = [q.strip() for q in queries if q.strip()]
        return result[:5]


class WikipediaRetriever:
    """Retrieves articles from Wikipedia API."""
    
    def __init__(self):
        """Initialize retriever."""
        self.language = "en"
        self.timeout = int(os.getenv("WIKIPEDIA_TIMEOUT", "5"))
        self._page_cache = {}
        self._page_cache_order = []
        self._search_cache = {}
        self._search_cache_order = []
        self._cache_max = 200
        if not HAS_WIKIPEDIA:
            logger.warning("Wikipedia library not available; using API fallback")

    def _cache_get(self, cache: dict, key: str):
        return cache.get(key)

    def _cache_set(self, cache: dict, order: List[str], key: str, value: Dict[str, Any]):
        if key in cache:
            return
        cache[key] = value
        order.append(key)
        if len(order) > self._cache_max:
            oldest = order.pop(0)
            cache.pop(oldest, None)

    def _api_search(self, query: str, max_results: int) -> List[str]:
        """Search Wikipedia using the public API and return titles."""
        cache_key = f"{query}::{max_results}"
        cached = self._cache_get(self._search_cache, cache_key)
        if cached is not None:
            return cached
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": max_results,
            "format": "json",
        }
        response = requests.get(
            WIKIPEDIA_API_URL,
            params=params,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        titles = [item.get("title", "") for item in data.get("query", {}).get("search", []) if item.get("title")]
        self._cache_set(self._search_cache, self._search_cache_order, cache_key, titles)
        return titles

    def _api_fetch_page(self, title: str) -> Dict[str, Any]:
        """Fetch page extract and summary using the Wikipedia API."""
        cached = self._cache_get(self._page_cache, title)
        if cached is not None:
            return cached
        summary = ""
        page_url = f"https://en.wikipedia.org/wiki/{quote(title)}"

        try:
            summary_resp = requests.get(
                f"{WIKIPEDIA_REST_SUMMARY_URL}{quote(title)}",
                headers={"User-Agent": DEFAULT_USER_AGENT},
                timeout=self.timeout,
            )
            if summary_resp.ok:
                summary_data = summary_resp.json()
                summary = summary_data.get("extract", "") or ""
                page_url = (
                    summary_data.get("content_urls", {})
                    .get("desktop", {})
                    .get("page", page_url)
                )
        except Exception as e:
            logger.debug(f"Wikipedia summary fetch failed for {title}: {e}")

        extract_params = {
            "action": "query",
            "prop": "extracts",
            "explaintext": 1,
            "exlimit": 1,
            "titles": title,
            "format": "json",
        }
        extract_resp = requests.get(
            WIKIPEDIA_API_URL,
            params=extract_params,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            timeout=self.timeout,
        )
        extract_resp.raise_for_status()
        extract_data = extract_resp.json()
        pages = extract_data.get("query", {}).get("pages", {})
        page_data = next(iter(pages.values()), {})
        content = page_data.get("extract", "") or ""

        page_data = {
            "title": page_data.get("title", title),
            "url": page_url,
            "content": content[:5000],
            "summary": summary[:1000],
            "source": "Wikipedia",
        }
        self._cache_set(self._page_cache, self._page_cache_order, title, page_data)
        return page_data

    def title_relevance(self, title: str, entity_tokens: List[str]) -> float:
        """Score title relevance to entity tokens."""
        if not title or not entity_tokens:
            return 0.0
        title_tokens = re.findall(r"[a-z0-9]+", title.lower())
        if not title_tokens:
            return 0.0
        hits = sum(1 for token in entity_tokens if token.lower() in title_tokens)
        return hits / max(len(entity_tokens), 1)
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search Wikipedia and return articles."""
        if not query:
            return []
        
        try:
            if HAS_WIKIPEDIA and wiki is not None:
                results = wiki.search(query, results=max_results)
                articles = []
                
                for title in results[:max_results]:
                    try:
                        page = wiki.page(title, auto_suggest=True, redirect=True)
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
                        logger.debug(f"Error fetching page {title}: {e}")
                        continue
                
                return articles

            titles = self._api_search(query, max_results)
            articles = []
            for title in titles[:max_results]:
                try:
                    articles.append(self._api_fetch_page(title))
                except Exception as e:
                    logger.debug(f"Error fetching page {title}: {e}")
                    continue

            return articles
        
        except Exception as e:
            logger.error(f"Wikipedia search error for '{query}': {e}")
            return []


class RetrievalPipeline:
    """Orchestrates retrieval with query expansion and deduplication."""
    
    def __init__(self):
        """Initialize retrieval pipeline."""
        self.query_expander = QueryExpander()
        self.wikipedia_retriever = WikipediaRetriever()
        self.tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
        self.fallback_retriever = self.wikipedia_retriever
        self.expander = self.query_expander
        self.retriever = self.wikipedia_retriever
        logger.info("RetrievalPipeline initialized (Wikipedia + Tavily fallback)")
    
    def tavily_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search using Tavily API as fallback/supplement."""
        if not self.tavily_key:
            logger.debug("Tavily API key not set, skipping")
            return []
        
        cache_key = f"tavily::{query}::{max_results}"
        if cache_key in _RETRIEVAL_CACHE:
            logger.debug(f"Tavily cache hit for: {query}")
            return _RETRIEVAL_CACHE[cache_key]
        
        try:
            payload = {
                "api_key": self.tavily_key,
                "query": query,
                "search_depth": "basic",
                "max_results": max_results
            }
            response = requests.post(
                TAVILY_API_URL,
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for r in data.get("results", []):
                results.append({
                    "title": r.get("title", ""),
                    "content": r.get("content", ""),
                    "url": r.get("url", ""),
                    "source": "Tavily"
                })
            
            _RETRIEVAL_CACHE[cache_key] = results
            logger.info(f"Tavily search found {len(results)} results for: {query}")
            return results
        except Exception as e:
            logger.warning(f"Tavily search failed for '{query}': {e}")
            return []
    
    def retrieve(
        self,
        query: str,
        max_articles: int = 10,
        entity_tokens: Optional[List[str]] = None,
        min_title_relevance: float = 0.4,
        expand_queries: bool = True
    ) -> List[Dict[str, Any]]:
        """Retrieve articles using hybrid strategy (Wikipedia + Tavily)."""
        if not query:
            return []

        if expand_queries:
            queries = self.expander.expand_query(query, num_variants=2)  # Reduced from 3
        else:
            queries = [query]
        
        articles = []
        seen_urls = set()
        
        # Step 1: Try Wikipedia (faster, curated)
        for q in queries:
            if len(articles) >= max_articles:
                break
            
            try:
                results = self.retriever.search(q, max_results=3)  # Reduced from 5
                for article in results:
                    if entity_tokens:
                        title = article.get("title", "")
                        relevance = self.retriever.title_relevance(title, entity_tokens)
                        if relevance < min_title_relevance:
                            continue
                    if article.get("url") not in seen_urls:
                        articles.append(article)
                        seen_urls.add(article["url"])
                        
                    if len(articles) >= max_articles:
                        break
            except Exception as e:
                logger.warning(f"Wikipedia search failed for '{q}': {e}")
        
        # Step 2: If insufficient, fallback to Tavily
        if len(articles) < max_articles // 2:
            logger.info(f"Wikipedia returned {len(articles)} articles, trying Tavily fallback...")
            for q in queries:
                if len(articles) >= max_articles:
                    break
                
                tavily_results = self.tavily_search(q, max_results=3)
                for article in tavily_results:
                    if article.get("url") not in seen_urls:
                        articles.append(article)
                        seen_urls.add(article["url"])
                    
                    if len(articles) >= max_articles:
                        break
        
        logger.info(f"Retrieved {len(articles)} total articles for query: {query}")
        return articles
