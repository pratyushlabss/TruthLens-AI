"""
Web Scraping Service - Extract content from URLs
Uses WebScraping.ai API for reliable content extraction
"""

import os
import requests
from typing import Optional

SCRAPER_KEY = os.getenv('SCRAPER_KEY', 'eb66d83d-416a-4f5e-8c7c-d5c2b6f89541')
SCRAPER_API_URL = 'https://api.webscraping.ai/v1'

def scrape_url(url: str, timeout: int = 30) -> str:
    """
    Scrape article text from URL using WebScraping.ai
    Returns: extracted text content
    """
    if not SCRAPER_KEY:
        raise ValueError('SCRAPER_KEY not configured')
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        params = {
            'api_key': SCRAPER_KEY,
            'url': url,
            'timeout': timeout
        }
        
        response = requests.get(
            SCRAPER_API_URL,
            params=params,
            timeout=timeout + 10
        )
        
        if not response.ok:
            raise ValueError(f'Scraper API error: {response.status_code} - {response.text}')
        
        data = response.json()
        
        # Extract text from response
        if isinstance(data, dict):
            text = data.get('text') or data.get('content') or data.get('body', '')
            if text:
                return text.strip()
        
        return ''
        
    except Exception as e:
        print(f'Web scraping error: {str(e)}')
        raise ValueError(f'Web scraping failed: {str(e)}')
