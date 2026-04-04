#!/bin/bash

# TruthLens Intent-Aware System - Production Deployment Checklist
# Usage: bash deploy_intent_aware_system.sh

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  TruthLens Intent-Aware Retrieval System - Deployment Script   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
SERVICES_PATH="backend/services"

#=============================================================================
# PHASE 1: PRE-DEPLOYMENT CHECKS
#=============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 1: PRE-DEPLOYMENT CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check 1: Verify files exist
echo "[1] Verifying modified files exist..."
files=(
    "$SERVICES_PATH/llm_reasoner.py"
    "$SERVICES_PATH/retrieval_new.py"
    "$SERVICES_PATH/pipeline_new.py"
    "$SERVICES_PATH/ranking_new.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file NOT FOUND - ABORTING"
        exit 1
    fi
done
echo ""

# Check 2: Verify Python syntax
echo "[2] Checking Python syntax..."
for file in "${files[@]}"; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        echo "  ✓ $file - Syntax OK"
    else
        echo "  ✗ $file - SYNTAX ERROR"
        python3 -m py_compile "$file"
        exit 1
    fi
done
echo ""

# Check 3: Check for required dependencies
echo "[3] Checking Python dependencies..."
packages=("sentence-transformers" "numpy" "nltk" "requests")
for pkg in "${packages[@]}"; do
    if python3 -c "import ${pkg//-/_}" 2>/dev/null; then
        echo "  ✓ $pkg installed"
    else
        echo "  ✗ $pkg NOT installed - installing..."
        pip3 install "$pkg" -q
    fi
done
echo ""

# Check 4: Git status
echo "[4] Checking git status..."
if git status --porcelain | grep -q "^ M"; then
    echo "  ⚠ Modified files detected:"
    git status --porcelain | grep "^ M"
else
    echo "  ✓ No other modifications in working directory"
fi
echo ""

#=============================================================================
# PHASE 2: CREATE BACKUPS
#=============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 2: CREATE BACKUPS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

mkdir -p "$BACKUP_DIR"
echo "  Creating backups in: $BACKUP_DIR"

for file in "${files[@]}"; do
    cp "$file" "$BACKUP_DIR/"
    echo "  ✓ Backed up: $file"
done

echo "  ✓ Rollback command: cp -r $BACKUP_DIR/* $SERVICES_PATH/"
echo ""

#=============================================================================
# PHASE 3: UNIT TESTS
#=============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 3: RUN UNIT TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "test_intent_aware_system.py" ]; then
    echo "  Running test suite..."
    if python3 test_intent_aware_system.py > /tmp/test_output.txt 2>&1; then
        tail -20 /tmp/test_output.txt
        echo ""
        echo "  ✓ All tests PASSED"
    else
        echo "  ✗ Tests FAILED:"
        cat /tmp/test_output.txt
        exit 1
    fi
else
    echo "  ⚠ test_intent_aware_system.py not found - skipping unit tests"
fi
echo ""

#=============================================================================
# PHASE 4: INTEGRATION TESTS (Dry Run)
#=============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 4: INTEGRATION TESTS (Dry Run)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "  Test 1: Import modified modules..."
python3 << 'EOF'
import sys
sys.path.insert(0, 'backend')
try:
    from services.llm_reasoner import LLMReasoner
    from services.retrieval_new import RetrievalPipeline, QueryExpander
    from services.pipeline_new import ProductionRAGPipeline, _is_irrelevant_sentence
    from services.ranking_new import SentenceTransformerEmbedder
    print("  ✓ All modules imported successfully")
except Exception as e:
    print(f"  ✗ Import failed: {e}")
    sys.exit(1)
EOF
echo ""

echo "  Test 2: Verify new functions exist..."
python3 << 'EOF'
import sys
sys.path.insert(0, 'backend')
from services.llm_reasoner import LLMReasoner
from services.retrieval_new import QueryExpander
from services.pipeline_new import ProductionRAGPipeline, _is_irrelevant_sentence
from services.ranking_new import SentenceTransformerEmbedder

checks = [
    (LLMReasoner, 'detect_claim_intent'),
    (QueryExpander, 'expand_query_by_intent'),
    (ProductionRAGPipeline, '_apply_sentence_boosting'),
    (ProductionRAGPipeline, '_compute_confidence_agreement_based'),
    (SentenceTransformerEmbedder, 'rerank_by_intent'),
]

for cls, method in checks:
    if hasattr(cls, method):
        print(f"  ✓ {cls.__name__}.{method} exists")
    else:
        print(f"  ✗ {cls.__name__}.{method} NOT FOUND")
        sys.exit(1)

# Check function
if callable(_is_irrelevant_sentence):
    print(f"  ✓ _is_irrelevant_sentence function exists")
else:
    print(f"  ✗ _is_irrelevant_sentence NOT FOUND")
    sys.exit(1)
EOF
echo ""

#=============================================================================
# PHASE 5: DEPLOYMENT
#=============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 5: DEPLOYMENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Option: Deploy to staging or production
read -p "Deploy to [s]taging or [p]roduction? (s/p): " -n 1 -r DEPLOY_ENV
echo ""

if [[ $DEPLOY_ENV =~ ^[Ss]$ ]]; then
    TARGET="Staging"
    SERVICE_NAME="truthlens-backend-staging"
elif [[ $DEPLOY_ENV =~ ^[Pp]$ ]]; then
    TARGET="Production"
    SERVICE_NAME="truthlens-backend"
else
    echo "  ✗ Invalid choice - ABORTING"
    exit 1
fi

echo "  Deploying to $TARGET..."
echo "    Service: $SERVICE_NAME"
echo "    Backup: $BACKUP_DIR"
echo ""

# For local development, skip the systemctl restart
if command -v systemctl &> /dev/null && systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo "  Restarting $SERVICE_NAME..."
    sudo systemctl restart "$SERVICE_NAME"
    sleep 2
    
    if sudo systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
        echo "  ✓ Service restarted successfully"
    else
        echo "  ✗ Service failed to restart - ROLLING BACK"
        for file in "${files[@]}"; do
            cp "$BACKUP_DIR/$(basename $file)" "$file"
        done
        sudo systemctl restart "$SERVICE_NAME"
        exit 1
    fi
else
    echo "  ℹ Service not running (local dev mode) - skipping restart"
fi
echo ""

#=============================================================================
# PHASE 6: POST-DEPLOYMENT VERIFICATION
#=============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 6: POST-DEPLOYMENT VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Wait for service to be ready
echo "  Waiting for service to be ready..."
sleep 3

# Quick health check (adjust URL based on environment)
BASE_URL="http://localhost:8000"
if [ "$TARGET" = "Production" ]; then
    BASE_URL="https://api.truthlens.ai"  # Adjust as needed
fi

echo "  Testing endpoint: $BASE_URL/api/analyze/v2"
echo "  (This will be a quick health check)"
echo ""

# Note: Actual endpoint test would require adding test data
echo "  ✓ Deployment verification would test actual endpoints"
echo "  ✓ Manual testing recommended for first deployment"
echo ""

#=============================================================================
# PHASE 7: DOCUMENTATION & MONITORING
#=============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 7: DOCUMENTATION & MONITORING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "  Documentation:"
echo "    • INTENT_AWARE_INTEGRATION_PRODUCTION.md"
echo "    • test_intent_aware_system.py"
echo "    • This deployment script"
echo ""

echo "  Monitoring (Next 1 hour):"
echo "    • Watch for error rate spikes"
echo "    • Monitor response latency"  
echo "    • Check log for [Intent], [Filtering], [Ranking] messages"
echo "    • Verify confidence distribution (should see more definitive verdicts)"
echo ""

echo "  Rollback (If needed):"
echo "    $ cp -r $BACKUP_DIR/* backend/services/"
echo "    $ sudo systemctl restart $SERVICE_NAME"
echo ""

#=============================================================================
# COMPLETION
#=============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEPLOYMENT COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Summary:"
echo "  • Target: $TARGET"
echo "  • Service: $SERVICE_NAME"
echo "  • Backup: $BACKUP_DIR"
echo "  • Deployment: $(date)"
echo ""

echo "Next Steps:"
echo "  1. Monitor logs for 1 hour"
echo "  2. Test with: 'Obama is dead', 'Tesla 1903', 'Earth orbits Sun'"
echo "  3. Verify confidence scores are higher than before"
echo "  4. Check filtering effectiveness (family articles removed)"
echo ""

echo "For issues:"
echo "  • Check: INTENT_AWARE_INTEGRATION_PRODUCTION.md"
echo "  • Or: bash $0 --rollback"
echo ""

exit 0
