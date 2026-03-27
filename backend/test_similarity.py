#!/usr/bin/env python3
import sys
from services.evidence_builder import EvidenceBuilder

builder = EvidenceBuilder()

# Test 1: Moon cheese 
claim = "The Moon is made of cheese"
article = "The Moon is not made of cheese. NASA has confirmed through scientific research that the Moon is primarily composed of rock and dust. The popular myth originated in folklore."

similarity = builder._compute_semantic_similarity(claim, article)
print(f"Moon claim vs NASA article:")
print(f"  Similarity: {similarity:.3f}")
print(f"  Status: {'Would trigger SUPPORTS/REFUTES' if similarity > 0.6 else 'Would be NEUTRAL (too low)'}")
print()

# Test 2: Simple overlapping claim
claim2 = "Obama was born in Kenya"
article2 = "Barack Obama was born in Hawaii in 1961. His birth certificate confirms he was born in Honolulu. He was not born in Kenya."

similarity2 = builder._compute_semantic_similarity(claim2, article2)
print(f"Obama claim vs birth article:")
print(f"  Similarity: {similarity2:.3f}")
print(f"  Status: {'Would trigger SUPPORTS/REFUTES' if similarity2 > 0.6 else 'Would be NEUTRAL (too low)'}")
