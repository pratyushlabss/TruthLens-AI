"""
TruthLens AI - Real Web Scraper Service
Purpose: Fetch and extract real content from trusted sources
No fake data. If scraping fails, raise error.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
from urllib.parse import urljoin, urlparse
import time

logger = logging.getLogger(__name__)

class ScrapingError(Exception):
    """Raised when scraping fails."""
    pass

class WebScraperService:
    """
    Real web scraper for extracting evidence from trusted sources.
    """
    
    # Trust ratings for domains
    DOMAIN_TRUST = {
        'reuters.com': 'high',
        'bbc.com': 'high',
        'bbc.co.uk': 'high',
        'wikipedia.org': 'high',
        'gov.uk': 'high',
        '.gov': 'high',
        '.edu': 'high',
        'nasa.gov': 'high',
        'cdc.gov': 'high',
        'who.int': 'high',
        'nature.com': 'high',
        'science.org': 'high',
        'thelancet.com': 'high',
        'jama.com': 'high',
        'theguardian.com': 'medium',
        'nytimes.com': 'medium',
        'washingtonpost.com': 'medium',
        'independent.co.uk': 'medium',
        'economist.com': 'medium',
    }
    
    def __init__(self, timeout=10, min_content_length=500):
        """
        Initialize scraper.
        
        Args:
            timeout: Request timeout in seconds
            min_content_length: Minimum content length in characters
        """
        self.timeout = timeout
        self.min_content_length = min_content_length
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_url(self, url: str) -> Dict:
        """
        Scrape a single URL and extract content.
        
        Returns:
            {
                'url': str,
                'title': str,
                'content': str,
                'length': int,
                'success': bool
            }
            
        Raises:
            ScrapingError if content cannot be extracted
        """
        try:
            logger.info(f"Scraping: {url}")
            
            # Validate URL format
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Fetch page
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else urlparse(url).netloc
            
            # Extract main content
            # Try <article>, <main>, or body
            content_container = (
                soup.find('article') or 
                soup.find('main') or 
                soup.find('div', class_=lambda x: x and 'content' in x.lower()) or
                soup.find('body')
            )
            
            if content_container:
                # Remove navigation elements
                for nav in content_container.find_all(['nav', 'aside']):
                    nav.decompose()
                
                # Remove common ad/tracking elements
                for ad in content_container.find_all(class_=lambda x: x and any(
                    word in x.lower() for word in ['ad', 'tracking', 'comment']
                )):
                    ad.decompose()
                
                content_text = content_container.get_text()
            else:
                content_text = soup.get_text()
            
            # Clean content
            lines = [line.strip() for line in content_text.split('\n') if line.strip()]
            content = ' '.join(lines)
            
            # Validate content length
            if len(content) < self.min_content_length:
                raise ScrapingError(
                    f"Content too short ({len(content)} chars, "
                    f"minimum {self.min_content_length} required)"
                )
            
            logger.info(f"✅ Successfully scraped {len(content)} characters from {url}")
            
            return {
                'url': url,
                'title': title_text,
                'content': content,
                'length': len(content),
                'success': True
            }
            
        except requests.RequestException as e:
            error_msg = f"Failed to fetch {url}: {str(e)}"
            logger.error(error_msg)
            raise ScrapingError(error_msg)
        except Exception as e:
            error_msg = f"Failed to parse {url}: {str(e)}"
            logger.error(error_msg)
            raise ScrapingError(error_msg)
    
    def scrape_multiple_urls(self, urls: List[str], 
                           max_results: int = 5) -> List[Dict]:
        """
        Scrape multiple URLs and return successful results.
        
        Args:
            urls: List of URLs to scrape
            max_results: Stop after this many successful scrapes
            
        Returns:
            List of scraped content dictionaries
            
        Raises:
            ScrapingError if no URLs can be scraped
        """
        results = []
        errors = []
        
        for url in urls[:max_results * 2]:  # Try more than needed
            if len(results) >= max_results:
                break
            
            try:
                result = self.scrape_url(url)
                results.append(result)
                time.sleep(0.5)  # Be respectful to servers
                
            except ScrapingError as e:
                errors.append(str(e))
                continue
        
        if not results:
            raise ScrapingError(
                f"Failed to scrape any URLs. Errors:\n" + 
                "\n".join(errors[:3])
            )
        
        logger.info(f"✅ Successfully scraped {len(results)} / {len(urls)} URLs")
        return results
    
    def get_domain_trust(self, url: str) -> str:
        """
        Get trust level for a domain.
        
        Returns: 'high' | 'medium' | 'low'
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Check exact matches
        for trusted_domain, trust_level in self.DOMAIN_TRUST.items():
            if domain == trusted_domain or domain.endswith(trusted_domain):
                return trust_level
        
        # Check TLD-based trust
        if any(domain.endswith(tld) for tld in ['.gov', '.edu', '.int', '.ac.uk']):
            return 'high'
        
        # Low trust for unknown sources
        return 'low'
    
    def validate_url(self, url: str) -> bool:
        """
        Check if URL is from a trusted source.
        """
        trust = self.get_domain_trust(url)
        return trust in ['high', 'medium']

