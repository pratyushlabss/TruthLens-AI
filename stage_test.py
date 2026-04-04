#!/usr/bin/env python3
"""Detailed stage-by-stage test to debug pipeline"""
import os
import sys
sys.path.insert(0, '/Users/pratyush/ai truthlens')

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('OPENAI_API_KEY', '')
print(f"🔑 API Key: {api_key[:20] if api_key else 'NONE'}...")

# Stage 1: Test retrieval
print("\n" + "="*70)
print("STAGE 1: RETRIEVAL")
print("="*70)

from backend.services.retrieval_new import RetrievalPipeline

retrieval = RetrievalPipeline()
articles = retrieval.retrieve("Einstein won Nobel Prize", max_articles=5)
print(f"✅ Articles retrieved: {len(articles)}")
if articles:
    for i, art in enumerate(articles[:2], 1):
        print(f"   [{i}] {art.get('title')} - {len(art.get('content', ''))} chars")

# Stage 2: Test sentence extraction
print("\n" + "="*70)
print("STAGE 2: SENTENCE EXTRACTION")
print("="*70)

from backend.services.utils_new import extract_sentences

sentences = []
for article in articles:
    content = article.get("content", "")
    if content:
        extracted = extract_sentences(content, min_length=15)
        sentences.extend(extracted)
        print(f"✅ Extracted from '{article.get('title')}': {len(extracted)} sentences")

print(f"📊 Total sentences: {len(sentences)}")
if sentences:
    print(f"   Sample: {sentences[0][:80]}...")

# Stage 3: Test ranking
print("\n" + "="*70)
print("STAGE 3: RANKING")
print("="*70)

from backend.services.ranking_new import SentenceTransformerEmbedder

embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2", device="cpu")
claim = "Einstein won Nobel Prize"

if sentences:
    result = embedder.rank_by_similarity(claim, sentences, top_k=3)
    print(f"✅ Top ranked evidence: {len(result['ranked_evidence'])}")
    for i, (sent, score) in enumerate(zip(result['ranked_evidence'], result['similarity_scores']), 1):
        print(f"   [{i}] Score={score:.4f}: {sent[:70]}...")
else:
    print("❌ No sentences to rank!")

# Stage 4: Test LLM reasoner
print("\n" + "="*70)
print("STAGE 4: LLM REASONER")
print("="*70)

from backend.services.llm_reasoner import LLMReasoner

llm = LLMReasoner(openai_api_key=api_key)
if result['ranked_evidence']:
    reasoning = llm.reason_over_evidence(
        claim,
        result['ranked_evidence']
    )
    print(f"✅ Reasoning result:")
    print(f"   Label: {reasoning.get('label')}")
    print(f"   Confidence: {reasoning.get('confidence')}")
else:
    print("❌ No evidence to reason over!")
