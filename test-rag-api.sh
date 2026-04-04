#!/bin/bash
# RAG Pipeline API - Testing Commands

RAG_API="http://127.0.0.1:8000"

echo "🚀 TruthLens RAG Pipeline - API Testing"
echo "========================================"

# 1. Health Check
echo ""
echo "1️⃣ Health Check:"
echo "$ curl $RAG_API/health"
curl -s "$RAG_API/health" | jq .
echo ""

# 2. Analyze Simple Claim
echo ""
echo "2️⃣ Analyze: 'Paris is the capital of France'"
echo "$ curl -X POST $RAG_API/analyze -H 'Content-Type: application/json' -d '{\"claim\": \"...\"}'"
curl -s -X POST "$RAG_API/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "Paris is the capital of France",
    "top_k_evidence": 5
  }' | jq .
echo ""

# 3. Analyze False Claim
echo ""
echo "3️⃣ Analyze: 'The Earth is flat'"
echo "$ curl -X POST $RAG_API/analyze -H 'Content-Type: application/json' -d '{\"claim\": \"The Earth is flat\"}'"
curl -s -X POST "$RAG_API/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "The Earth is flat",
    "top_k_evidence": 3
  }' | jq .
echo ""

# 4. Interactive Mode
echo ""
echo "4️⃣ Interactive Mode:"
echo "Enter a claim to analyze (or 'quit' to exit):"
while true; do
  read -p "Claim: " claim
  if [ "$claim" == "quit" ]; then
    break
  fi
  
  echo "Analyzing..."
  curl -s -X POST "$RAG_API/analyze" \
    -H "Content-Type: application/json" \
    -d "{\"claim\": \"$claim\", \"top_k_evidence\": 5}" | jq .
  echo ""
done

echo ""
echo "✅ Testing completed!"
