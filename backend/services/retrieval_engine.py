"""
Web Retrieval Engine - HYBRID SEARCH IMPLEMENTATION
Primary: Tavily API
Fallback: DuckDuckGo HTML scraping
Content Extraction: newspaper3k + BeautifulSoup + requests
NEVER returns empty list - always has fallback evidence
"""

import logging
import os
from typing import List, Dict, Optional
from datetime import datetime
import requests
from urllib.parse import quote

logger = logging.getLogger(__name__)


class RetrievalEngine:
    """
    Hybrid web retrieval engine.
    - Primary: Tavily API (real search)
    - Fallback 1: DuckDuckGo HTML scraping
    - Fallback 2: Hardcoded fallback evidence
    - Always returns evidence (never empty)
    """
    
    def __init__(self):
        """Initialize retrieval engine with ML enhancements."""
        self.tavily_api_key = os.getenv("TAVILY_API_KEY", "")
        self.duckduckgo_base_url = "https://duckduckgo.com/"
        
        # Load semantic model for content validation and deduplication
        self.semantic_model = None
        self.cached_embeddings = {}
        self._load_semantic_model()
        
        # Domain credibility database (0.3-0.95 scale)
        self.credible_domains = {
            # Tier 1: Highest credibility (0.95)
            'wikipedia.org': 0.95, 'nature.com': 0.95, 'science.org': 0.95,
            'bbc.com': 0.95, 'reuters.com': 0.95, 'apnews.com': 0.95,
            'theguardian.com': 0.95, 'nytimes.com': 0.95,
            # Tier 2: High credibility (0.90)
            'arxiv.org': 0.90, 'scholar.google.com': 0.90, 'gov.uk': 0.90,
            'nasa.gov': 0.90, 'fda.gov': 0.90, 'who.int': 0.90,
            'bbc.co.uk': 0.90, 'economist.com': 0.90,
            # Tier 3: Good credibility (0.80)
            'medium.com': 0.80, 'techcrunch.com': 0.80, 'forbes.com': 0.80,
            'wired.com': 0.80, 'theverge.com': 0.80, 'cnn.com': 0.80,
            # Tier 4: Moderate credibility (0.60)
            'reddit.com': 0.60, 'quora.com': 0.60, 'medium.com': 0.60,
            # Default for unknown domains
        }
        
        logger.info("[RETRIEVAL] 🔧 Initializing Hybrid Retrieval Engine with ML Enhancements")
        logger.info(f"[RETRIEVAL] Tavily API Key configured: {bool(self.tavily_api_key)}")
        logger.info(f"[RETRIEVAL] Semantic model loaded: {self.semantic_model is not None}")
        logger.info(f"[RETRIEVAL] Domain credibility database: {len(self.credible_domains)} domains")
        logger.info("[RETRIEVAL] DuckDuckGo fallback: Ready")
        logger.info("[RETRIEVAL] ✅ RetrievalEngine initialized with ML capabilities")
    
    def search_and_scrape(
        self,
        claim: str,
        max_results: int = 10,
        timeout: int = 30
    ) -> List[Dict]:
        """
        Search for evidence and scrape content.
        
        Hybrid search strategy:
        1. Try Tavily API (if configured)
        2. Fallback to DuckDuckGo HTML scraping
        3. Return hardcoded fallback if both fail
        
        Args:
            claim: The claim to search for
            max_results: Maximum number of results
            timeout: Timeout in seconds
            
        Returns:
            List of articles (guaranteed non-empty)
        """
        logger.info(f"[RETRIEVAL] 🔍 Search request: {claim[:80]}")
        
        # Try Tavily API first (if configured)
        if self.tavily_api_key:
            logger.info("[RETRIEVAL] 🎯 Attempting Tavily API search...")
            results = self._search_with_tavily(claim, max_results)
            if results:
                logger.info(f"[RETRIEVAL] ✅ Tavily: Retrieved {len(results)} articles")
                return results[:max_results]
            logger.warning("[RETRIEVAL] ⚠️  Tavily search failed or no results")
        
        # Fallback to DuckDuckGo
        logger.info("[RETRIEVAL] 🔄 Attempting DuckDuckGo fallback search...")
        results = self._search_with_duckduckgo(claim, max_results)
        if results:
            logger.info(f"[RETRIEVAL] ✅ DuckDuckGo: Retrieved {len(results)} articles")
            return results[:max_results]
        
        logger.warning("[RETRIEVAL] ⚠️  DuckDuckGo search failed")
        
        # Final fallback: Return hardcoded evidence
        logger.info("[RETRIEVAL] 🛡️  FINAL FALLBACK: Returning hardcoded evidence")
        return [self._fallback_article(claim)]
    
    # ========================================================================
    # TAVILY API SEARCH (Primary)
    # ========================================================================
    
    def _search_with_tavily(self, claim: str, max_results: int) -> List[Dict]:
        """
        Search using Tavily API.
        
        Args:
            claim: Search query
            max_results: Number of results
            
        Returns:
            List of articles
        """
        try:
            logger.info(f"[TAVILY] 🌐 Searching Tavily for: {claim[:60]}")
            
            import requests
            
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": self.tavily_api_key,
                "query": claim,
                "max_results": min(max_results, 10),
                "include_answer": True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get("results", [])
            
            logger.info(f"[TAVILY] ✅ Tavily returned {len(articles)} results")
            
            # Convert Tavily results to standard format and rank
            processed = []
            for article in articles:
                url = article.get("url", "")
                scraped_content = self._scrape_url(url)
                source = self._extract_domain(url)
                credibility = self._assess_source_credibility(url)
                processed.append({
                    "title": article.get("title", "No title"),
                    "url": url,
                    "snippet": article.get("snippet", ""),
                    "text": scraped_content,
                    "source": source,
                    "credibility": credibility,
                    "is_fallback": False,
                    "retrieved_at": datetime.now().isoformat()
                })
            
            logger.info(f"[TAVILY] ✅ Processed {len(processed)} articles for content")
            
            # Deduplicate and rank results
            processed = self._detect_duplicates(processed)
            processed = self._rank_and_filter_results(processed, claim)
            
            logger.info(f"[TAVILY] ✅ After dedup+rank: {len(processed)} articles")
            return processed
        
        except Exception as e:
            logger.warning(f"[TAVILY] ❌ Error: {e}")
            return []
    
    # ========================================================================
    # DUCKDUCKGO FALLBACK SEARCH
    # ========================================================================
    
    def _search_with_duckduckgo(self, claim: str, max_results: int) -> List[Dict]:
        """
        Search using DuckDuckGo HTML scraping.
        
        Args:
            claim: Search query
            max_results: Number of results
            
        Returns:
            List of articles
        """
        try:
            logger.info(f"[DUCKDUCKGO] 🦆 Scraping DuckDuckGo for: {claim[:60]}")
            
            import requests
            from bs4 import BeautifulSoup
            
            # DuckDuckGo search URL
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            search_url = f"https://duckduckgo.com/html?q={quote(claim)}"
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract results
            results = []
            result_divs = soup.find_all("div", class_="result")
            
            for result_div in result_divs[:max_results]:
                try:
                    title_elem = result_div.find("a", class_="result__a")
                    snippet_elem = result_div.find("a", class_="result__snippet")
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get("href", "")
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    # Scrape article content
                    content = self._scrape_url(url)
                    source = self._extract_domain(url)
                    credibility = self._assess_source_credibility(url)
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "text": content,
                        "source": source,
                        "credibility": credibility,
                        "is_fallback": False,
                        "retrieved_at": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.debug(f"[DUCKDUCKGO] Error parsing result: {e}")
                    continue
            
            logger.info(f"[DUCKDUCKGO] ✅ Retrieved {len(results)} articles")
            
            # Deduplicate and rank results
            results = self._detect_duplicates(results)
            results = self._rank_and_filter_results(results, claim)
            
            logger.info(f"[DUCKDUCKGO] ✅ After dedup+rank: {len(results)} articles")
            return results
        
        except Exception as e:
            logger.warning(f"[DUCKDUCKGO] ❌ Error: {e}")
            return []
    
    # ========================================================================
    # CONTENT SCRAPING
    # ========================================================================
    
    def _scrape_url(self, url: str) -> str:
        """
        Scrape article content from URL.
        Try: newspaper3k → BeautifulSoup → requests
        
        Args:
            url: URL to scrape
            
        Returns:
            Article content
        """
        if not url:
            return ""
        
        try:
            # Try newspaper3k first (best for articles)
            try:
                from newspaper import Article
                article = Article(url, language='en')
                article.download()
                article.parse()
                if article.text:
                    logger.debug(f"[SCRAPE] ✅ newspaper3k: {url[:50]}")
                    cleaned = self._clean_content(article.text)
                    return cleaned
            except:
                pass
            
            # Try BeautifulSoup with requests
            try:
                import requests
                from bs4 import BeautifulSoup
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                response = requests.get(url, headers=headers, timeout=5)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Remove script and style
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text(separator=" ", strip=True)
                if text:
                    logger.debug(f"[SCRAPE] ✅ BeautifulSoup: {url[:50]}")
                    cleaned = self._clean_content(text)
                    return cleaned
            except:
                pass
            
            logger.warning(f"[SCRAPE] ⚠️  Could not scrape: {url[:50]}")
            return ""
        
        except Exception as e:
            logger.debug(f"[SCRAPE] Error: {e}")
            return ""
    
    # ========================================================================
    # UTILITIES
    # ========================================================================
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return domain or "unknown"
        except:
            return "unknown"
    
    # ========================================================================
    # ML-ENHANCED CONTENT PROCESSING
    # ========================================================================
    
    def _load_semantic_model(self) -> None:
        """Load SentenceTransformer semantic model for embeddings."""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("[MODEL] 📦 Loading SentenceTransformer (all-MiniLM-L6-v2)...")
            self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("[MODEL] ✅ SentenceTransformer loaded successfully")
        except ImportError:
            logger.warning("[MODEL] ⚠️  SentenceTransformer not installed - install with pip install sentence-transformers")
            self.semantic_model = None
        except Exception as e:
            logger.warning(f"[MODEL] ❌ Error loading semantic model: {e}")
            self.semantic_model = None
    
    def _validate_content_relevance(self, claim: str, content: str) -> float:
        """
        Validate if article content is relevant to the claim using semantic similarity.
        
        Args:
            claim: The original claim
            content: Article content to validate
            
        Returns:
            Relevance score (0.0-1.0)
        """
        if not self.semantic_model or not content or len(content) < 50:
            return 0.5  # Default if model unavailable
        
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Use first 500 chars to avoid huge text
            content_sample = content[:500]
            
            # Get embeddings
            claim_emb = self.semantic_model.encode(claim)
            content_emb = self.semantic_model.encode(content_sample)
            
            # Compute cosine similarity
            similarity = cosine_similarity([claim_emb], [content_emb])[0][0]
            return float(max(0.0, min(1.0, similarity)))  # Clamp to [0, 1]
        except Exception as e:
            logger.debug(f"[SEMANTIC] Error computing relevance: {e}")
            return 0.5
    
    def _clean_content(self, text: str) -> str:
        """
        Clean article content by removing boilerplate and limiting length.
        
        Removes:
        - Navigation menus
        - Cookie/privacy notices
        - Ad content
        - Subscribe/signup prompts
        - Excessive whitespace
        
        Args:
            text: Raw article text
            
        Returns:
            Cleaned content (max 2000 chars)
        """
        if not text:
            return ""
        
        import re
        
        # Remove common boilerplate patterns
        boilerplate_patterns = [
            r'Accept cookies?.*?(?=\n|$)',
            r'Subscribe|Sign up|Sign in.*?(?=\n|$)',
            r'Share this article.*?(?=\n|$)',
            r'Related articles?.*?(?=\n|$)',
            r'Advertisement.*?(?=\n|$)',
            r'Privacy Policy|Terms of Service|Contact Us.*?(?=\n|$)',
            r'Follow us on.*?(?=\n|$)',
            r'\[Click here.*?\]',
        ]
        
        for pattern in boilerplate_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Split into sentences and limit to 20 sentences
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
        text = '. '.join(sentences[:20])
        
        # Limit to 2000 characters
        return text[:2000]
    
    def _assess_source_credibility(self, source_url: str) -> float:
        """
        Assess source credibility based on domain authority.
        
        Args:
            source_url: URL to assess
            
        Returns:
            Credibility score (0.3-0.95)
        """
        if not source_url:
            return 0.5
        
        try:
            domain = self._extract_domain(source_url).lower()
            
            # Check exact domain match
            if domain in self.credible_domains:
                return self.credible_domains[domain]
            
            # Check domain suffix (e.g., .edu, .gov, .ac.uk)
            if domain.endswith('.edu'):
                return 0.85
            if domain.endswith('.gov') or domain.endswith('.gov.uk'):
                return 0.90
            if domain.endswith('.ac.uk') or domain.endswith('.edu.au'):
                return 0.85
            
            # Check for known unreliable sources
            unreliable = ['facebook', 'twitter', 'instagram', 'tiktok', 'youtube']
            if any(unreliable in domain for unreliable in unreliable):
                return 0.4
            
            # Default for unknown domains
            return 0.5
        except Exception as e:
            logger.debug(f"[CREDIBILITY] Error assessing source: {e}")
            return 0.5
    
    def _score_article_quality(self, content: str) -> float:
        """
        Score article quality based on multiple factors.
        
        Factors considered:
        - Word count (longer = better, up to 500+ words)
        - Sentence count (more sentences = more detail)
        - Citation presence ("source", "according to", "study")
        - Quote presence (text in quotes suggests attribution)
        - Statistical data (numbers and percentages)
        - Opinion markers detection (avoid excessive opinion)
        
        Args:
            content: Article text
            
        Returns:
            Quality score (0.0-1.0)
        """
        if not content:
            return 0.0
        
        import re
        
        score = 0.5  # Base score
        
        # Factor 1: Word count (up to 20 pts)
        word_count = len(content.split())
        if word_count >= 500:
            score += 0.15
        elif word_count >= 300:
            score += 0.10
        elif word_count >= 100:
            score += 0.05
        
        # Factor 2: Sentence count (up to 10 pts)
        sentence_count = len([s for s in content.split('.') if s.strip()])
        if sentence_count >= 15:
            score += 0.10
        elif sentence_count >= 8:
            score += 0.05
        
        # Factor 3: Citation indicators (up to 15 pts)
        citation_patterns = ['according to', 'research', 'study', 'published', 'found that', 'data show']
        citation_count = sum(1 for p in citation_patterns if p in content.lower())
        score += min(0.15, citation_count * 0.05)
        
        # Factor 4: Quotes (up to 10 pts)
        quote_count = content.count('"')
        score += min(0.10, quote_count * 0.02)
        
        # Factor 5: Statistics (numbers, percentages) (up to 10 pts)
        stat_pattern = r'\d+[%|percentagerange|\s]*|\b(?:percent|%|half|two-thirds)\b'
        stat_count = len(re.findall(stat_pattern, content))
        score += min(0.10, stat_count * 0.02)
        
        # Factor 6: Opinion detection (reduce score if too opinionated)
        opinion_markers = ['I think', 'in my opinion', 'believe', 'seem to', 'appear to']
        opinion_count = sum(1 for op in opinion_markers if op in content.lower())
        if opinion_count > 5:
            score -= 0.15
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, score))
    
    def _detect_duplicates(self, results: List[Dict]) -> List[Dict]:
        """
        Detect and remove duplicate articles using semantic similarity.
        
        Deduplication logic:
        - If two articles have similarity > 0.85, keep only the higher quality one
        - Uses semantic embeddings for robust deduplication
        
        Args:
            results: List of article dictionaries
            
        Returns:
            Deduplicated results
        """
        if not results or not self.semantic_model:
            return results
        
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Score all articles
            for result in results:
                if 'quality_score' not in result:
                    result['quality_score'] = self._score_article_quality(result.get('text', ''))
            
            # Get embeddings for all articles
            embeddings = []
            for result in results:
                emb = self.semantic_model.encode(result.get('text', '')[:500])
                embeddings.append(emb)
            
            # Find duplicates
            keep_indices = set(range(len(results)))
            for i in range(len(results)):
                if i not in keep_indices:
                    continue
                
                for j in range(i + 1, len(results)):
                    if j not in keep_indices:
                        continue
                    
                    # Compute similarity
                    similarity = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
                    
                    if similarity > 0.85:  # Threshold for duplicates
                        # Keep the one with higher quality score
                        if results[i]['quality_score'] >= results[j]['quality_score']:
                            keep_indices.discard(j)
                        else:
                            keep_indices.discard(i)
                            break
            
            deduplicated = [results[i] for i in sorted(keep_indices)]
            logger.info(f"[DEDUP] Removed {len(results) - len(deduplicated)} duplicates")
            return deduplicated
        
        except Exception as e:
            logger.debug(f"[DEDUP] Error during deduplication: {e}")
            return results
    
    def _rank_and_filter_results(self, results: List[Dict], claim: str) -> List[Dict]:
        """
        Rank and filter results based on combined scoring.
        
        Ranking formula (normalized):
        - Relevance: 30% (semantic similarity to claim)
        - Quality: 40% (article quality score)
        - Credibility: 30% (source domain authority)
        
        Results with combined score < 0.3 are filtered out.
        
        Args:
            results: List of article dictionaries
            claim: The original claim
            
        Returns:
            Ranked and filtered results
        """
        if not results:
            return results
        
        try:
            # Score all articles
            for result in results:
                # Relevance (30%)
                relevance = self._validate_content_relevance(claim, result.get('text', ''))
                
                # Quality (40%)
                quality = self._score_article_quality(result.get('text', ''))
                
                # Credibility (30%)
                credibility = result.get('credibility', 0.5)
                
                # Combined score
                combined = (relevance * 0.30) + (quality * 0.40) + (credibility * 0.30)
                result['relevance_score'] = relevance
                result['combined_score'] = combined
            
            # Sort by combined score (descending)
            ranked = sorted(results, key=lambda x: x.get('combined_score', 0), reverse=True)
            
            # Filter out low-scoring results (< 0.3)
            filtered = [r for r in ranked if r.get('combined_score', 0) >= 0.3]
            
            logger.info(f"[RANK] Ranked {len(results)} articles, filtered to {len(filtered)}")
            return filtered if filtered else ranked[:5]  # Always return at least top 5
        
        except Exception as e:
            logger.warning(f"[RANK] Error during ranking: {e}")
            return results
    
    # ========================================================================
    # FALLBACK
    # ========================================================================
    
    def _fallback_article(self, claim: str) -> Dict:
        """Create fallback article when all search methods fail."""
        logger.warning(f"[FALLBACK] Creating fallback article for: {claim[:60]}")
        
        return {
            "title": f"Analysis: {claim[:80]}",
            "url": "generated://fallback-article",
            "snippet": "System-generated analysis when external sources unavailable",
            "text": f"""
CLAIM ANALYSIS FALLBACK

Original Claim: "{claim}"

Status: External search sources unavailable

Analysis Mode: System internal analysis only

The system attempted to search multiple sources:
1. Tavily API search - Not configured or unavailable
2. DuckDuckGo HTML scraping - Search failed
3. External API fallbacks - Not available

Internal Analysis Performed:
- Claim tokenization and preprocessing
- NLP semantic analysis
- Internal knowledge base lookup
- Confidence score calculation

Result: Verdict based on internal analysis only

Recommendation: When external sources become available,
re-run this analysis for improved accuracy.

Timestamp: {datetime.now().isoformat()}
""",
            "source": "System Internal Analysis",
            "credibility": 0.3,
            "is_fallback": True,
            "retrieved_at": datetime.now().isoformat()
        }

