#!/usr/bin/env python3
import sys
from services.evidence_builder import EvidenceBuilder

# Patch the function to add logging
orig_func = EvidenceBuilder._compute_semantic_similarity

def logged_similarity(self, claim, article_text):
    try:
        print(f"\n[ENTERING] claim={claim[:40]}, article_len={len(article_text)}")
        
        if not article_text or len(article_text.strip()) < 20:
            print("[EXIT] Article too short")
            return 0.0
        
        # Method 1: Keyword overlap
        claim_words = set(claim.lower().split())
        article_words = set(article_text.lower().split()[:200])
        
        stop_words = {
            "the", "a", "an", "and", "or", "is", "are", "was", "were",
            "be", "been", "being", "have", "has", "had", "do", "does", "did",
            "will", "would", "could", "should", "may", "might", "must",
            "of", "in", "on", "at", "by", "for", "with", "to", "from", "as"
        }
        
        claim_words_filtered = claim_words - stop_words
        article_words_filtered = article_words - stop_words
        
        if not claim_words_filtered or not article_words_filtered:
            print("[EXIT] No filtered words")
            return 0.0
        
        # Compute Jaccard
        intersection = len(claim_words_filtered & article_words_filtered)
        union = len(claim_words_filtered | article_words_filtered)
        jaccard_sim = intersection / union if union > 0 else 0.0
        print(f"[JACCARD] intersection={intersection}, union={union}, jaccard={jaccard_sim:.3f}")
        
        # Method 2: Named entity
        claim_entities = {w for w in claim.split() if w and w[0].isupper() and len(w) > 2}
        article_entities = {w for w in article_text.split()[:200] if w and w[0].isupper() and len(w) > 2}
        
        entity_overlap = len(claim_entities & article_entities)
        entity_similarity = entity_overlap / max(len(claim_entities), 1)
        print(f"[ENTITY] overlap={entity_overlap}, entity_sim={entity_similarity:.3f}")
        
        # Method 3: Content relevance
        important_claim_words = [w for w in claim_words_filtered if len(w) > 3]
        if important_claim_words:
            matching_count = sum(1 for w in important_claim_words if w in article_words_filtered)
            content_relevance = matching_count / len(important_claim_words)
        else:
            content_relevance = 0.5
        print(f"[CONTENT] important={len(important_claim_words)}, matching={matching_count if important_claim_words else 'N/A'}, relevance={content_relevance:.3f}")
        
        # Weighted combo
        if entity_overlap > 0:
            similarity = (jaccard_sim * 0.40) + (entity_similarity * 0.40) + (content_relevance * 0.20)
        else:
            similarity = (jaccard_sim * 0.60) + (content_relevance * 0.40)
        
        print(f"[SIMILARITY_BEFORE_BOOST] {similarity:.3f}")
        
        # Topic boost
        article_text_lower = article_text.lower()
        topic_keywords = [w for w in claim_words_filtered if len(w) > 3]
        
        if topic_keywords:
            topic_match_count = sum(1 for w in topic_keywords if w in article_text_lower)
            topic_relevance = topic_match_count / len(topic_keywords)
            print(f"[TOPIC] keywords={topic_keywords}, matches={topic_match_count}, topic_rel={topic_relevance:.3f}")
            similarity = max(similarity, topic_relevance * 0.7)
            print(f"[FINAL] {similarity:.3f}")
        
        return min(1.0, max(0.0, similarity))
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 0.0

EvidenceBuilder._compute_semantic_similarity = logged_similarity

# Now test
builder = EvidenceBuilder()

claim = "The Moon is made of cheese"
article = "The Moon is not made of cheese. NASA has confirmed through scientific research that the Moon is primarily composed of rock and dust. The popular myth originated in folklore."

similarity = builder._compute_semantic_similarity(claim, article)
print(f"\n=== RESULT: {similarity:.3f} ===")
