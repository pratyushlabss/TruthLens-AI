"""
TruthLens AI - Core Environment Configuration & Validation
CRITICAL: This runs FIRST before any other code
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ============================================================================
# STEP 1: LOAD ENVIRONMENT VARIABLES
# ============================================================================

# Load from root .env (project root directory)
# Path(__file__) = /backend/config/environment.py
# .parent = /backend/config/
# .parent.parent = /backend/
# .parent.parent.parent = / (project root)
root_env = Path(__file__).parent.parent.parent / ".env"
if root_env.exists():
    load_dotenv(root_env)
    print(f"✅ Loaded .env from {root_env}")
else:
    print(f"⚠️  .env not found at {root_env}")

# Load from backend .env if exists (for backend-specific overrides)
backend_env = Path(__file__).parent.parent / ".env"
if backend_env.exists():
    load_dotenv(backend_env)
    print(f"✅ Loaded .env from {backend_env}")

# ============================================================================
# STEP 2: VALIDATE REQUIRED ENVIRONMENT VARIABLES
# ============================================================================

REQUIRED_ENV_VARS = {
    'HUGGINGFACE_API_KEY': 'HuggingFace API key (for NLI model)',
    'PINECONE_API_KEY': 'Pinecone API key (for vector DB)',
    'PINECONE_ENV': 'Pinecone environment (e.g., us-west4-gcp)',
    'SUPABASE_URL': 'Supabase database URL',
    'SUPABASE_KEY': 'Supabase API key',
}

OPTIONAL_ENV_VARS = {
    'RAPID_API_KEY': 'RapidAPI key (for web scraping)',
    'BING_SEARCH_KEY': 'Bing Search API key',
    'GOOGLE_API_KEY': 'Google Custom Search API key',
    'GOOGLE_SEARCH_ENGINE_ID': 'Google Custom Search Engine ID',
}

class EnvironmentError(Exception):
    """Raised when environment validation fails."""
    pass

def validate_environment():
    """
    Validate that all required environment variables are set.
    Raise EnvironmentError if any are missing.
    """
    missing = []
    provided = {}
    
    print("\n" + "="*70)
    print("ENVIRONMENT VALIDATION")
    print("="*70)
    
    # Check required variables
    for var_name, description in REQUIRED_ENV_VARS.items():
        value = os.getenv(var_name)
        if value:
            # Mask sensitive values
            masked = value[:10] + "***" if len(value) > 10 else value
            print(f"✅ {var_name:<25} = {masked}")
            provided[var_name] = value
        else:
            print(f"❌ {var_name:<25} = MISSING")
            missing.append(var_name)
    
    print()
    
    # Check optional variables
    for var_name, description in OPTIONAL_ENV_VARS.items():
        value = os.getenv(var_name)
        if value:
            masked = value[:10] + "***" if len(value) > 10 else value
            print(f"⚠️  {var_name:<25} = {masked} (optional)")
            provided[var_name] = value
        else:
            print(f"⏭️  {var_name:<25} = not set (optional)")
    
    print("\n" + "="*70)
    
    # Raise error if required variables missing
    if missing:
        error_msg = f"""
🚨 CRITICAL: Missing required environment variables:
{chr(10).join(f'  - {var}' for var in missing)}

Please set these in your .env file:
{chr(10).join(f'  {var}=your_value' for var in missing)}

Cannot proceed without these configurations.
        """
        print(error_msg)
        raise EnvironmentError(error_msg)
    
    print("✅ ALL REQUIRED ENVIRONMENT VARIABLES SET")
    print("="*70 + "\n")
    
    return provided

# ============================================================================
# STEP 3: VALIDATE CONNECTIVITY
# ============================================================================

def validate_connectivity():
    """
    Test that external services are reachable.
    """
    import requests
    
    print("\n" + "="*70)
    print("CONNECTIVITY VALIDATION")
    print("="*70)
    
    services = {
        'HuggingFace': 'https://huggingface.co/api/models',
        'Pinecone': 'https://api.pinecone.io/indexes',
        'Supabase': os.getenv('SUPABASE_URL', '').split('/')[2] if os.getenv('SUPABASE_URL') else 'N/A'
    }
    
    for service_name, endpoint in services.items():
        try:
            if service_name == 'HuggingFace':
                headers = {'Authorization': f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
                response = requests.head(endpoint, headers=headers, timeout=5)
            elif service_name == 'Pinecone':
                headers = {'Api-Key': os.getenv('PINECONE_API_KEY')}
                response = requests.head(endpoint, headers=headers, timeout=5)
            else:
                response = requests.head(f'https://{endpoint}', timeout=5)
            
            if response.status_code < 500:
                print(f"✅ {service_name:<20} reachable")
            else:
                print(f"⚠️  {service_name:<20} returned {response.status_code}")
        except Exception as e:
            print(f"❌ {service_name:<20} error: {str(e)[:50]}")
    
    print("="*70 + "\n")

# ============================================================================
# STEP 4: GLOBAL CONFIG CLASS
# ============================================================================

class Config:
    """Global configuration object."""
    
    # Environment variables (validated)
    HUGGINGFACE_API_KEY = None
    PINECONE_API_KEY = None
    PINECONE_ENV = None
    SUPABASE_URL = None
    SUPABASE_KEY = None
    RAPID_API_KEY = None
    BING_SEARCH_KEY = None
    GOOGLE_API_KEY = None
    GOOGLE_SEARCH_ENGINE_ID = None
    
    # Pipeline configuration
    SCRAPING_TIMEOUT = 10  # seconds
    SCRAPING_MIN_LENGTH = 500  # characters
    PINECONE_TOP_K = 5
    HF_MODEL_NAME = "facebook/bart-large-mnli"
    HF_BATCH_SIZE = 32
    
    # Trusted domains for scraping
    TRUSTED_DOMAINS = {
        'reuters.com': 'high',
        'bbc.com': 'high',
        'wikipedia.org': 'high',
        'government.gov': 'high',
        'nasa.gov': 'high',
        'cdc.gov': 'high',
        'who.int': 'high',
        'sciencedirect.com': 'high',
        'jstor.org': 'high',
        'pubmed.ncbi.nlm.nih.gov': 'high',
        'arxiv.org': 'high',
        'theguardian.com': 'medium',
        'nytimes.com': 'medium',
        'washingtonpost.com': 'medium',
        'politico.com': 'medium',
        'vox.com': 'medium',
    }
    
    # Verdict confidence thresholds
    CONFIDENCE_HIGH = 85  # 85-100% confident
    CONFIDENCE_MEDIUM = 60  # 60-84% confident
    CONFIDENCE_LOW = 40  # 40-59% confident
    
    @classmethod
    def initialize(cls):
        """Initialize all configuration from environment."""
        try:
            env_vars = validate_environment()
            
            cls.HUGGINGFACE_API_KEY = env_vars.get('HUGGINGFACE_API_KEY')
            cls.PINECONE_API_KEY = env_vars.get('PINECONE_API_KEY')
            cls.PINECONE_ENV = env_vars.get('PINECONE_ENV')
            cls.SUPABASE_URL = env_vars.get('SUPABASE_URL')
            cls.SUPABASE_KEY = env_vars.get('SUPABASE_KEY')
            cls.RAPID_API_KEY = env_vars.get('RAPID_API_KEY')
            cls.BING_SEARCH_KEY = env_vars.get('BING_SEARCH_KEY')
            cls.GOOGLE_API_KEY = env_vars.get('GOOGLE_API_KEY')
            cls.GOOGLE_SEARCH_ENGINE_ID = env_vars.get('GOOGLE_SEARCH_ENGINE_ID')
            
            print("✅ Configuration initialized successfully\n")
            return True
            
        except EnvironmentError as e:
            print(f"❌ Configuration initialization failed:\n{e}")
            sys.exit(1)

# ============================================================================
# INITIALIZATION
# ============================================================================

# Initialize on import
if __name__ != "__main__":
    Config.initialize()

