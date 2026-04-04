"""
Environment Configuration Module
Centralizes access to all API credentials with debug logging.
"""

import os
import logging
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file (FIRST - before anything else)
env_path = Path(__file__).parent.parent.parent / ".env"  # Go up to root
if env_path.exists():
    load_dotenv(env_path)
    logger.debug(f"✅ Loaded .env from {env_path}")
else:
    logger.warning(f"⚠️ .env file not found at {env_path}")

# Also try loading from current directory
load_dotenv()


class EnvironmentConfig:
    """Centralized access to all API credentials and configuration."""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Tavily Configuration
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()
    
    # Other APIs (optional)
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "").strip()
    SERPER_API_KEY = os.getenv("SERPER_API_KEY", "").strip()
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend/truthlens.db")
    
    # System
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def verify_required_keys(cls) -> bool:
        """
        Verify that required API keys are configured.
        
        Returns:
            True if all required keys present, False otherwise
        """
        required = {
            "OPENAI_API_KEY": cls.OPENAI_API_KEY,
        }
        
        optional = {
            "TAVILY_API_KEY": cls.TAVILY_API_KEY,
        }
        
        missing_required = []
        missing_optional = []
        
        for key, value in required.items():
            if not value:
                missing_required.append(key)
            else:
                # Log with masking
                masked = f"{value[:10]}...{value[-8:]}" if len(value) > 20 else "***"
                logger.info(f"✅ {key} loaded: {masked}")
        
        for key, value in optional.items():
            if not value:
                logger.warning(f"⚠️ {key} NOT set - feature will be disabled")
                missing_optional.append(key)
            else:
                masked = f"{value[:10]}...{value[-8:]}" if len(value) > 20 else "***"
                logger.info(f"✅ {key} loaded: {masked}")
        
        if missing_required:
            logger.error(f"❌ CRITICAL: Missing required keys: {', '.join(missing_required)}")
            return False
        
        return True
    
    @classmethod
    def get_openai_key(cls) -> Optional[str]:
        """Get OpenAI API key with validation."""
        if not cls.OPENAI_API_KEY:
            logger.error("❌ OPENAI_API_KEY not configured")
            return None
        return cls.OPENAI_API_KEY
    
    @classmethod
    def get_tavily_key(cls) -> Optional[str]:
        """Get Tavily API key (returns None if not configured)."""
        if not cls.TAVILY_API_KEY:
            logger.debug("⚠️ TAVILY_API_KEY not configured - Tavily search disabled")
            return None
        return cls.TAVILY_API_KEY
    
    @classmethod
    def log_config(cls):
        """Log all configuration for debugging."""
        logger.info("="*70)
        logger.info("ENVIRONMENT CONFIGURATION")
        logger.info("="*70)
        
        configs = {
            "OpenAI Model": cls.OPENAI_MODEL,
            "OpenAI Key": "✅ SET" if cls.OPENAI_API_KEY else "❌ NOT SET",
            "Tavily Key": "✅ SET" if cls.TAVILY_API_KEY else "⚠️ NOT SET",
            "Debug Mode": cls.DEBUG_MODE,
            "Log Level": cls.LOG_LEVEL,
            "Database": cls.DATABASE_URL[:50] + "...",
        }
        
        for key, value in configs.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("="*70)


# Verify configuration on module load
if not EnvironmentConfig.verify_required_keys():
    logger.error("❌ Environment configuration INCOMPLETE - Some features may not work")
else:
    logger.info("✅ Environment configuration VERIFIED")


class EnvironmentConfig:
    """Centralized access to all API credentials and configuration."""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Tavily Configuration
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()
    
    # Other APIs (optional)
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "").strip()
    SERPER_API_KEY = os.getenv("SERPER_API_KEY", "").strip()
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend/truthlens.db")
    
    # System
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def verify_required_keys(cls) -> bool:
        """
        Verify that required API keys are configured.
        
        Returns:
            True if all required keys present, False otherwise
        """
        required = {
            "OPENAI_API_KEY": cls.OPENAI_API_KEY,
        }
        
        optional = {
            "TAVILY_API_KEY": cls.TAVILY_API_KEY,
        }
        
        missing_required = []
        missing_optional = []
        
        for key, value in required.items():
            if not value:
                missing_required.append(key)
            else:
                # Log with masking
                masked = f"{value[:8]}...{value[-8:]}"
                logger.info(f"✅ {key} loaded: {masked}")
        
        for key, value in optional.items():
            if not value:
                logger.warning(f"⚠️ {key} NOT set - feature will be disabled")
                missing_optional.append(key)
            else:
                masked = f"{value[:8]}...{value[-8:]}"
                logger.info(f"✅ {key} loaded: {masked}")
        
        if missing_required:
            logger.error(f"❌ CRITICAL: Missing required keys: {', '.join(missing_required)}")
            return False
        
        return True
    
    @classmethod
    def get_openai_key(cls) -> Optional[str]:
        """Get OpenAI API key with validation."""
        if not cls.OPENAI_API_KEY:
            logger.error("❌ OPENAI_API_KEY not configured")
            return None
        return cls.OPENAI_API_KEY
    
    @classmethod
    def get_tavily_key(cls) -> Optional[str]:
        """Get Tavily API key (returns None if not configured)."""
        if not cls.TAVILY_API_KEY:
            logger.debug("⚠️ TAVILY_API_KEY not configured - Tavily search disabled")
            return None
        return cls.TAVILY_API_KEY
    
    @classmethod
    def log_config(cls):
        """Log all configuration for debugging."""
        logger.info("="*70)
        logger.info("ENVIRONMENT CONFIGURATION")
        logger.info("="*70)
        
        configs = {
            "OpenAI Model": cls.OPENAI_MODEL,
            "OpenAI Key": "✅ SET" if cls.OPENAI_API_KEY else "❌ NOT SET",
            "Tavily Key": "✅ SET" if cls.TAVILY_API_KEY else "⚠️ NOT SET",
            "Debug Mode": cls.DEBUG_MODE,
            "Log Level": cls.LOG_LEVEL,
            "Database": cls.DATABASE_URL[:50] + "...",
        }
        
        for key, value in configs.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("="*70)


# Verify configuration on module load
if not EnvironmentConfig.verify_required_keys():
    logger.error("❌ Environment configuration INCOMPLETE")
else:
    logger.info("✅ Environment configuration VERIFIED")
