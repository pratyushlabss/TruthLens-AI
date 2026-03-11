"""Web scraping service for trusted news sources."""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio
from newspaper import Article
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class TrustedSourceScraper:
    """Scrapes and processes articles from trusted news sources."""

    # Trusted source domains
    TRUSTED_SOURCES = {
        "reuters.com": {"credibility": 0.98, "category": "news_agency"},
        "apnews.com": {"credibility": 0.97, "category": "news_agency"},
        "bbc.com": {"credibility": 0.96, "category": "news_agency"},
        "bbc.co.uk": {"credibility": 0.96, "category": "news_agency"},
        "theguardian.com": {"credibility": 0.93, "category": "newspaper"},
        "nytimes.com": {"credibility": 0.92, "category": "newspaper"},
        "washingtonpost.com": {"credibility": 0.91, "category": "newspaper"},
        "ft.com": {"credibility": 0.90, "category": "newspaper"},
        "telegraph.co.uk": {"credibility": 0.89, "category": "newspaper"},
        "bloomberg.com": {"credibility": 0.88, "category": "news_agency"},
        "aljazeera.com": {"credibility": 0.87, "category": "news_agency"},
        "snopes.com": {"credibility": 0.94, "category": "fact_checker"},
        "factcheck.org": {"credibility": 0.95, "category": "fact_checker"},
        "politifact.com": {"credibility": 0.92, "category": "fact_checker"},
    }

    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """
        Initialize scraper.

        Args:
            timeout: Request timeout in seconds
            max_retries: Number of retries for failed requests
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def is_trusted_source(self, url: str) -> bool:
        """
        Check if URL is from a trusted source.

        Args:
            url: URL to check

        Returns:
            True if from trusted source
        """
        try:
            domain = urlparse(url).netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain in self.TRUSTED_SOURCES
        except Exception as e:
            logger.error(f"Error checking trusted source: {e}")
            return False

    def get_source_credibility(self, url: str) -> float:
        """
        Get credibility score of source.

        Args:
            url: Source URL

        Returns:
            Credibility score (0-1)
        """
        domain = urlparse(url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        source_info = self.TRUSTED_SOURCES.get(domain, {})
        return source_info.get("credibility", 0.5)

    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape article from URL using newspaper library.

        Args:
            url: Article URL

        Returns:
            Dictionary with article data or None on failure
        """
        if not self.is_trusted_source(url):
            logger.warning(f"URL not from trusted source: {url}")
            return None

        retries = 0
        while retries < self.max_retries:
            try:
                article = Article(url, timeout=self.timeout)
                article.download()
                article.parse()

                # Extract data
                article_data = {
                    "url": url,
                    "title": article.title,
                    "text": article.text,
                    "authors": article.authors,
                    "publish_date": article.publish_date.isoformat()
                    if article.publish_date
                    else None,
                    "summary": article.summary,
                    "keywords": article.keywords,
                    "source_credibility": self.get_source_credibility(url),
                    "domain": urlparse(url).netloc,
                    "scraped_at": datetime.utcnow().isoformat(),
                    "word_count": len(article.text.split()),
                }

                logger.info(f"Successfully scraped: {article_data['title'][:50]}...")
                return article_data

            except Exception as e:
                retries += 1
                logger.warning(
                    f"Scrape attempt {retries} failed for {url}: {e}"
                )
                if retries >= self.max_retries:
                    logger.error(f"Failed to scrape {url} after {self.max_retries} retries")
                    return None
                asyncio.run(asyncio.sleep(1))

        return None

    def scrape_articles_batch(self, urls: List[str]) -> List[Dict]:
        """
        Scrape multiple articles.

        Args:
            urls: List of URLs to scrape

        Returns:
            List of article data dictionaries
        """
        articles = []
        for url in urls:
            article = self.scrape_article(url)
            if article:
                articles.append(article)

        logger.info(f"Successfully scraped {len(articles)}/{len(urls)} articles")
        return articles

    def extract_claims_from_article(self, article_data: Dict) -> List[str]:
        """
        Extract potential claims from article text.

        Args:
            article_data: Article data dictionary

        Returns:
            List of extracted claims
        """
        text = article_data.get("text", "")

        # Split into sentences
        sentences = text.split(".")

        # Filter for claim-like sentences (longer, factual)
        claims = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence.split()) >= 5:  # At least 5 words
                claims.append(sentence)

        logger.info(f"Extracted {len(claims)} potential claims from article")
        return claims[:10]  # Return top 10 claims

    def search_for_topic(
        self, topic: str, num_results: int = 10
    ) -> List[str]:
        """
        Search for articles about a specific topic from trusted sources.

        Args:
            topic: Topic to search for
            num_results: Number of results to return

        Returns:
            List of article URLs
        """
        urls = []

        # Search each trusted source
        for domain, info in list(self.TRUSTED_SOURCES.items())[:5]:  # Top 5 sources
            search_url = f"https://{domain}/search?q={topic}"

            try:
                response = self.session.get(search_url, timeout=self.timeout)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")
                links = soup.find_all("a", limit=num_results // 5)

                for link in links:
                    href = link.get("href")
                    if href and href.startswith("http"):
                        urls.append(href)

            except Exception as e:
                logger.error(f"Error searching {domain}: {e}")

        logger.info(f"Found {len(urls)} articles for topic: {topic}")
        return urls[:num_results]

    def verify_claim_with_sources(
        self, claim: str, num_sources: int = 5
    ) -> Dict:
        """
        Verify a claim by searching for supporting/contradicting sources.

        Args:
            claim: Claim to verify
            num_sources: Number of sources to search

        Returns:
            Dictionary with verification results
        """
        logger.info(f"Verifying claim: {claim[:100]}...")

        urls = self.search_for_topic(claim, num_results=num_sources)
        articles = self.scrape_articles_batch(urls)

        # Calculate aggregate credibility
        total_credibility = 0
        for article in articles:
            total_credibility += article["source_credibility"]

        avg_credibility = (
            total_credibility / len(articles) if articles else 0
        )

        return {
            "claim": claim,
            "sources_found": len(articles),
            "articles": articles,
            "average_source_credibility": avg_credibility,
            "verified_at": datetime.utcnow().isoformat(),
        }

    def get_trending_topics(self) -> Dict[str, int]:
        """
        Get trending topics from trusted news sources.

        Returns:
            Dictionary of trending topics with mention counts
        """
        topics = {}

        # In production, this would connect to RSS feeds or news APIs
        # For now, return mock data
        logger.info("Fetching trending topics")

        return {
            "climate_change": 145,
            "election": 89,
            "technology": 76,
            "health": 134,
            "economy": 98,
        }

    def cleanup_old_articles(self, days: int = 30) -> int:
        """
        Remove cached articles older than specified days.

        Args:
            days: Days to keep articles

        Returns:
            Number of articles removed
        """
        # In production, this would clean database
        logger.info(f"Cleaning articles older than {days} days")
        return 0

    def load_trusted_sources_config(self) -> Dict:
        """
        Load trusted sources configuration from JSON file.

        Returns:
            Trusted sources configuration
        """
        try:
            config_path = Path(__file__).parent.parent / "config" / "trusted_sources.json"
            with open(config_path, "r") as f:
                config = json.load(f)
            logger.info("Loaded trusted sources configuration")
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
