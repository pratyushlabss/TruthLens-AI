#!/usr/bin/env python3
import sys
from services.evidence_builder import EvidenceBuilder

builder = EvidenceBuilder()

# Test 1: Moon cheese 
claim = "The Moon is made of cheese"
article = "The Moon is not made of cheese. NASA has confirmed through scientific research that the Moon is primarily composed of rock and dust. The popular myth originated in folklore."

print("=" * 70)
print("TEST 1: Moon claim")
print("=" * 70)
print(f"Claim: {claim}")
print(f"Article length: {len(article)} chars")
print(f"Article first 100 chars: {article[:100]}")

# Manually compute similarity steps
claim_words = set(claim.lower().split())
article_words = set(article.lower().split()[:200])

print(f"\nClaim words: {claim_words}")
print(f"Article words (first 200): {article_words}")

stop_words = {
    "the", "a", "an", "and", "or", "is", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "must",
    "of", "in", "on", "at", "by", "for", "with", "to", "from", "as", "not"
}

claim_words_filtered = claim_words - stop_words
article_words_filtered = article_words - stop_words

print(f"\nFiltered claim words: {claim_words_filtered}")
print(f"Filtered article words: {article_words_filtered}")

intersection = len(claim_words_filtered & article_words_filtered)
union = len(claim_words_filtered | article_words_filtered)

print(f"\nIntersection: {intersection}")
print(f"Union: {union}")
print(f"Jaccard sim: {intersection / union if union > 0 else 0}")

similarity = builder._compute_semantic_similarity(claim, article)
print(f"\nFinal similarity: {similarity:.3f}")
