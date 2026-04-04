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
    # All deprecated - now using OpenAI for all LLM/verification tasks
}

OPTIONAL_ENV_VARS = {
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
    
    # Connectivity validation removed - OpenAI API and database checks are done elsewhere
    pass
    
    print("="*70 + "\n")

# ============================================================================
# STEP 4: GLOBAL CONFIG CLASS
# ============================================================================

class Config:
    """Global configuration object."""
    
    # Environment variables (validated)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')
    GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID', '')
    
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
    
    # === NEW RAG PIPELINE FEATURE FLAGS ===
    USE_NEW_RAG_PIPELINE = os.getenv('USE_NEW_RAG_PIPELINE', 'false').lower() == 'true'
    NEW_RAG_EMBEDDER_MODEL = os.getenv('NEW_RAG_EMBEDDER_MODEL', 'all-MiniLM-L6-v2')
    NEW_RAG_USE_NLI = os.getenv('NEW_RAG_USE_NLI', 'true').lower() == 'true'
    NEW_RAG_TOP_K_EVIDENCE = int(os.getenv('NEW_RAG_TOP_K_EVIDENCE', '5'))
    NEW_RAG_QUERY_EXPANSION = os.getenv('NEW_RAG_QUERY_EXPANSION', 'true').lower() == 'true'
    NEW_RAG_DEVICE = os.getenv('NEW_RAG_DEVICE', 'cpu')  # 'cpu' or 'cuda'
    
    @classmethod
    def initialize(cls):
        """Initialize all configuration from environment."""
        try:
            env_vars = validate_environment()
            
            cls.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
            cls.TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')
            cls.GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID', '')
            
            print("✅ Configuration initialized successfully\n")
            return True
            
        except EnvironmentError as e:
            print(f"❌ Configuration initialization failed:\n{e}")
            # No sys.exit - allow fallback
            return False

# ============================================================================
# INITIALIZATION
# ============================================================================

# Initialize on import
if __name__ != "__main__":
    Config.initialize()

