#!/usr/bin/env python3
"""
Comprehensive Environment & Integration Validation Script
Verifies OpenAI + Tavily integration in TruthLens AI pipeline
"""

import sys
import os
import py_compile
from pathlib import Path

# Add backend to path
sys.path.insert(0, '/Users/pratyush/ai truthlens')

def validate_syntax():
    """Validate Python syntax of all modified files."""
    files_to_check = [
        "/Users/pratyush/ai truthlens/backend/main.py",
        "/Users/pratyush/ai truthlens/backend/services/llm_reasoner.py",
        "/Users/pratyush/ai truthlens/backend/services/retrieval_new.py",
        "/Users/pratyush/ai truthlens/backend/services/pipeline_new.py",
        "/Users/pratyush/ai truthlens/backend/config/env_config.py",
    ]
    
    print("\n" + "="*70)
    print("SYNTAX VALIDATION")
    print("="*70)
    
    all_ok = True
    for filepath in files_to_check:
        try:
            py_compile.compile(filepath, doraise=True)
            print(f"✅ {Path(filepath).name} - OK")
        except py_compile.PyCompileError as e:
            print(f"❌ {Path(filepath).name} - SYNTAX ERROR")
            print(f"   {e}")
            all_ok = False
    
    return all_ok


def validate_imports():
    """Validate that all imports work correctly."""
    print("\n" + "="*70)
    print("IMPORT VALIDATION")
    print("="*70)
    
    all_ok = True
    
    # Test 1: Config module
    try:
        from backend.config.env_config import EnvironmentConfig
        print("✅ EnvironmentConfig imported")
        EnvironmentConfig.log_config()
    except ImportError as e:
        print(f"❌ EnvironmentConfig import failed: {e}")
        all_ok = False
    
    # Test 2: LLMReasoner
    try:
        from backend.services.llm_reasoner import LLMReasoner
        print("✅ LLMReasoner imported")
    except Exception as e:
        print(f"❌ LLMReasoner import failed: {e}")
        all_ok = False
    
    # Test 3: Retrieval Pipeline
    try:
        from backend.services.retrieval_new import RetrievalPipeline, WikipediaRetriever, TavilyRetriever
        print("✅ RetrievalPipeline imported (with Tavily support)")
    except Exception as e:
        print(f"❌ RetrievalPipeline import failed: {e}")
        all_ok = False
    
    # Test 4: Production Pipeline
    try:
        from backend.services.pipeline_new import ProductionRAGPipeline
        print("✅ ProductionRAGPipeline imported")
    except Exception as e:
        print(f"❌ ProductionRAGPipeline import failed: {e}")
        all_ok = False
    
    return all_ok


def validate_env_loading():
    """Validate environment variables are being loaded correctly."""
    print("\n" + "="*70)
    print("ENVIRONMENT VARIABLE LOADING")
    print("="*70)
    
    from backend.config.env_config import EnvironmentConfig
    
    openai_key = EnvironmentConfig.get_openai_key()
    tavily_key = EnvironmentConfig.get_tavily_key()
    
    if openai_key:
        print(f"✅ OPENAI_API_KEY: {openai_key[:15]}...{openai_key[-10:]}")
    else:
        print(f"❌ OPENAI_API_KEY: NOT SET")
    
    if tavily_key:
        print(f"✅ TAVILY_API_KEY: {tavily_key[:15]}...{tavily_key[-10:]}")
    else:
        print(f"⚠️ TAVILY_API_KEY: NOT SET (optional)")
    
    return openai_key is not None


def validate_pipeline_initialization():
    """Validate that pipeline initializes with all components."""
    print("\n" + "="*70)
    print("PIPELINE INITIALIZATION")
    print("="*70)
    
    try:
        from backend.services.pipeline_new import ProductionRAGPipeline
        
        print("🚀 Initializing ProductionRAGPipeline...")
        pipeline = ProductionRAGPipeline(use_nli=False, device="cpu")
        
        # Check components
        checks = {
            "LLMReasoner": pipeline.llm_reasoner is not None,
            "RetrievalPipeline": pipeline.retrieval_pipeline is not None,
            "SentenceTransformerEmbedder": pipeline.embedder is not None,
        }
        
        all_ok = True
        for component, initialized in checks.items():
            status = "✅" if initialized else "⚠️"
            print(f"{status} {component}: {'initialized' if initialized else 'failed to initialize'}")
            if not initialized:
                all_ok = False
        
        # Check retrieval sources
        print("\n🔍 Retrieval Sources:")
        retrieval = pipeline.retrieval_pipeline
        if retrieval:
            has_wiki = hasattr(retrieval, 'wiki_retriever') and retrieval.wiki_retriever
            has_tavily = hasattr(retrieval, 'tavily_retriever') and retrieval.tavily_retriever and retrieval.tavily_retriever.api_key
            
            print(f"  Wikipedia: {'✅' if has_wiki else '❌'}")
            print(f"  Tavily: {'✅' if has_tavily else '⚠️'}")
        
        return all_ok
    
    except Exception as e:
        print(f"❌ Pipeline initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + "  TRUTHLENS AI - OPENAI + TAVILY INTEGRATION VALIDATION".center(68) + "║")
    print("╚" + "="*68 + "╝")
    
    results = {
        "Syntax Validation": validate_syntax(),
        "Import Validation": validate_imports(),
        "Environment Loading": validate_env_loading(),
        "Pipeline Initialization": validate_pipeline_initialization(),
    }
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL VALIDATION TESTS PASSED")
        print("Status: ✅ System ready for production use")
    else:
        print("⚠️ SOME VALIDATION TESTS FAILED")
        print("Status: ❌ Fix errors before deployment")
    print("="*70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
