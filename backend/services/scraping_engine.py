"""
[4-5] SCRAPING ENGINE - Playwright + BeautifulSoup + newspaper3k with fallback chain
"""

import logging
from typing import Optional
import asyncio
import time

logger = logging.getLogger(__name__)


class ScrapingEngine:
    """
    Multi-layer scraping with robust fallback chain:
    1. Playwright (JS rendering, heavy sites)
    2. BeautifulSoup (HTML scraping, fast)
    3. newspaper3k (news article extraction)
    4. Direct snippet use (fallback)
    """
    
    def __init__(self):
        """Initialize scraping engine."""
        self.playwright_available = False
        self.browser = None
        self._init_playwright()
    
    def _init_playwright(self):
        """Try to initialize Playwright."""
        try:
            from playwright.async_api import async_playwright
            logger.info("[SCRAPER] ✅ Playwright available for JS-heavy sites")
            self.playwright_available = True
        except Exception as e:
            logger.warning(f"[SCRAPER] ⚠️ Playwright not available: {e}")
            logger.info("[SCRAPER] Will use BeautifulSoup + newspaper3k fallback")
            self.playwright_available = False
    
    def scrape(self, url: str, timeout: int = 8) -> str:
        """
        Scrape URL with automatic fallback chain.
        
        Args:
            url: URL to scrape
            timeout: Timeout in seconds
            
        Returns:
            Article text content (or empty if all methods fail)
        """
        
        if not url or not isinstance(url, str):
            logger.debug("[SCRAPER] Invalid URL")
            return ""
        
        logger.debug(f"[SCRAPER] Scraping: {url[:60]}")
        
        # Try Playwright first (JS rendering)
        if self.playwright_available:
            content = self._scrape_playwright(url, timeout)
            if content:
                logger.debug("[SCRAPER] ✅ Playwright successful")
                return content
        
        # Fallback 1: BeautifulSoup
        content = self._scrape_beautifulsoup(url, timeout)
        if content:
            logger.debug("[SCRAPER] ✅ BeautifulSoup successful")
            return content
        
        # Fallback 2: newspaper3k
        content = self._scrape_newspaper(url, timeout)
        if content:
            logger.debug("[SCRAPER] ✅ newspaper3k successful")
            return content
        
        # Fallback 3: Return empty
        logger.warning(f"[SCRAPER] ⚠️ All scraping methods failed for: {url[:50]}")
        return ""
    
    def _scrape_playwright(self, url: str, timeout: int) -> Optional[str]:
        """Scrape using Playwright (handles JS)."""
        try:
            from playwright.async_api import async_playwright
            
            # Run async operation
            return asyncio.run(self._scrape_playwright_async(url, timeout))
        
        except Exception as e:
            logger.debug(f"[SCRAPER] Playwright error: {e}")
            return None
    
    async def _scrape_playwright_async(self, url: str, timeout: int) -> Optional[str]:
        """Async Playwright scraping."""
        try:
            async_playwright_obj = __import__("playwright.async_api", fromlist=["async_playwright"])
            async with async_playwright_obj.async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                try:
                    await page.goto(url, wait_until="networkidle", timeout=timeout * 1000)
                    content = await page.content()
                    
                    # Extract text from HTML
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Remove script and style
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    text = soup.get_text()
                    text = "\n".join(line.strip() for line in text.split("\n") if line.strip())
                    
                    await browser.close()
                    return text[:10000] if text else None
                
                except Exception as e:
                    logger.debug(f"[SCRAPER] Playwright page load error: {e}")
                    await browser.close()
                    return None
        
        except Exception as e:
            logger.debug(f"[SCRAPER] Playwright async error: {e}")
            return None
    
    def _scrape_beautifulsoup(self, url: str, timeout: int) -> Optional[str]:
        """Scrape using BeautifulSoup (plain HTML)."""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            text = "\n".join(line.strip() for line in text.split("\n") if line.strip())
            
            return text[:20000] if text else None
        
        except Exception as e:
            logger.debug(f"[SCRAPER] BeautifulSoup error: {e}")
            return None
    
    def _scrape_newspaper(self, url: str, timeout: int) -> Optional[str]:
        """Scrape using newspaper3k (optimized for news articles)."""
        try:
            from newspaper import Article
            
            article = Article(url, timeout=timeout)
            article.download()
            article.parse()
            
            if article.text:
                return article.text[:20000]
            
            return None
        
        except Exception as e:
            logger.debug(f"[SCRAPER] newspaper3k error: {e}")
            return None
    
    def batch_scrape(self, urls: list, timeout: int = 8) -> dict:
        """
        Scrape multiple URLs with timing.
        
        Args:
            urls: List of URLs
            timeout: Timeout per URL
            
        Returns:
            Dict mapping URL → content
        """
        results = {}
        for url in urls[:10]:  # Limit to 10 to avoid long runtime
            try:
                content = self.scrape(url, timeout)
                results[url] = content
            except Exception as e:
                logger.debug(f"[SCRAPER] Batch error for {url[:50]}: {e}")
                results[url] = ""
        
        return results
