#!/usr/bin/env python3
# Test if the issue is substring vs word matching

article_text = "The Moon is not made of cheese. NASA has confirmed through scientific research that the Moon is primarily composed of rock and dust. The popular myth originated in folklore."
article_text_lower = article_text.lower()
topic_keywords = ['cheese', 'made', 'moon']

print("Testing substring matching:")
for w in topic_keywords:
    found = w in article_text_lower
    print(f"  '{w}' in article_text_lower: {found}")

# Now test word matching
article_words_lower = set(article_text_lower.split())
print("\nTesting word set matching:")
for w in topic_keywords:
    found = w in article_words_lower
    print(f"  '{w}' in article_words_lower: {found}")
    if not found:
        print(f"    Article words: {[ww for ww in article_words_lower if 'cheese' in ww or 'moon' in ww]}")
