"""Text preprocessing service for NLP pipeline."""

import logging
from typing import List, Dict, Set
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer
import re
import string

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet")


class TextPreprocessor:
    """Comprehensive text preprocessing for claim analysis."""

    def __init__(self, model_name: str = "en_core_web_md"):
        """
        Initialize text preprocessor.

        Args:
            model_name: spaCy model to use
        """
        try:
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
        except Exception:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("Loaded spaCy fallback model: en_core_web_sm")
            except Exception as e:
                logger.error(f"Error loading spaCy model: {e}")
                self.nlp = None

        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words("english"))

    def lowercase(self, text: str) -> str:
        """Convert text to lowercase."""
        return text.lower()

    def remove_urls(self, text: str) -> str:
        """Remove URLs from text."""
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        return re.sub(url_pattern, "", text)

    def remove_emails(self, text: str) -> str:
        """Remove email addresses from text."""
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        return re.sub(email_pattern, "", text)

    def remove_html_tags(self, text: str) -> str:
        """Remove HTML tags from text."""
        html_pattern = r"<.*?>"
        return re.sub(html_pattern, "", text)

    def remove_punctuation(self, text: str) -> str:
        """Remove punctuation from text."""
        return text.translate(str.maketrans("", "", string.punctuation))

    def remove_extra_whitespace(self, text: str) -> str:
        """Remove extra whitespace from text."""
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def remove_special_characters(self, text: str) -> str:
        """Remove special characters but keep alphanumeric and spaces."""
        return re.sub(r"[^a-zA-Z0-9\s]", "", text)

    def expand_contractions(self, text: str) -> str:
        """Expand English contractions."""
        contractions_dict = {
            "ain't": "am not",
            "aren't": "are not",
            "can't": "cannot",
            "can't've": "cannot have",
            "could've": "could have",
            "couldn't": "could not",
            "didn't": "did not",
            "doesn't": "does not",
            "don't": "do not",
            "hadn't": "had not",
            "hasn't": "has not",
            "haven't": "have not",
            "he'd": "he would",
            "he'll": "he will",
            "he's": "he is",
            "how'd": "how did",
            "how'll": "how will",
            "how's": "how is",
            "i'd": "i would",
            "i'll": "i will",
            "i'm": "i am",
            "i've": "i have",
            "isn't": "is not",
            "it'd": "it would",
            "it'll": "it will",
            "it's": "it is",
            "let's": "let us",
            "shouldn't": "should not",
            "that's": "that is",
            "there's": "there is",
            "they'd": "they would",
            "they'll": "they will",
            "they're": "they are",
            "they've": "they have",
            "wasn't": "was not",
            "we'd": "we would",
            "we'll": "we will",
            "we're": "we are",
            "we've": "we have",
            "weren't": "were not",
            "what's": "what is",
            "where's": "where is",
            "who'd": "who would",
            "who'll": "who will",
            "who're": "who are",
            "who's": "who is",
            "won't": "will not",
            "wouldn't": "would not",
            "you'd": "you would",
            "you'll": "you will",
            "you're": "you are",
            "you've": "you have",
        }

        pattern = re.compile(r"\b({})\b".format("|".join(contractions_dict.keys())))
        return pattern.sub(lambda x: contractions_dict[x.group()], text)

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        return word_tokenize(text)

    def tokenize_sentences(self, text: str) -> List[str]:
        """Tokenize text into sentences."""
        return sent_tokenize(text)

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords from token list."""
        return [token for token in tokens if token.lower() not in self.stop_words]

    def lemmatize(self, tokens: List[str]) -> List[str]:
        """Lemmatize tokens."""
        return [self.lemmatizer.lemmatize(token) for token in tokens]

    def stem(self, tokens: List[str]) -> List[str]:
        """Stem tokens."""
        return [self.stemmer.stem(token) for token in tokens]

    def get_pos_tags(self, tokens: List[str]) -> List[tuple]:
        """Get part-of-speech tags for tokens."""
        if not self.nlp:
            logger.warning("spaCy model not available")
            return []

        doc = self.nlp(" ".join(tokens))
        return [(token.text, token.pos_) for token in doc]

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        if not self.nlp:
            logger.warning("spaCy model not available")
            return {}

        doc = self.nlp(text)
        entities = {}

        for ent in doc.ents:
            ent_type = ent.label_
            if ent_type not in entities:
                entities[ent_type] = []
            entities[ent_type].append(ent.text)

        logger.info(f"Extracted {len(doc.ents)} entities")
        return entities

    def extract_key_phrases(self, text: str, top_n: int = 10) -> List[str]:
        """Extract key phrases using noun chunks."""
        if not self.nlp:
            logger.warning("spaCy model not available")
            return []

        doc = self.nlp(text)
        chunks = [chunk.text for chunk in doc.noun_chunks]

        # Remove duplicates and return top N
        unique_chunks = list(dict.fromkeys(chunks))
        return unique_chunks[:top_n]

    def preprocess(
        self,
        text: str,
        lowercase: bool = True,
        remove_urls: bool = True,
        remove_emails: bool = True,
        remove_html: bool = True,
        remove_punct: bool = True,
        remove_special: bool = False,
        expand_contractions: bool = True,
        tokenize: bool = True,
        remove_stopwords: bool = True,
        lemmatize: bool = True,
    ) -> Dict:
        """
        Complete preprocessing pipeline.

        Args:
            text: Input text
            lowercase: Convert to lowercase
            remove_urls: Remove URLs
            remove_emails: Remove emails
            remove_html: Remove HTML tags
            remove_punct: Remove punctuation
            remove_special: Remove special characters
            expand_contractions: Expand contractions
            tokenize: Tokenize text
            remove_stopwords: Remove stopwords
            lemmatize: Lemmatize tokens

        Returns:
            Dictionary with preprocessing results
        """
        logger.info(f"Preprocessing text ({len(text)} characters)")

        # Store original text
        result = {"original": text, "tokens": []}

        # Apply preprocessing steps
        processed = text

        if lowercase:
            processed = self.lowercase(processed)

        if remove_urls:
            processed = self.remove_urls(processed)

        if remove_emails:
            processed = self.remove_emails(processed)

        if remove_html:
            processed = self.remove_html_tags(processed)

        if expand_contractions:
            processed = self.expand_contractions(processed)

        if remove_punct:
            processed = self.remove_punctuation(processed)

        if remove_special:
            processed = self.remove_special_characters(processed)

        processed = self.remove_extra_whitespace(processed)
        result["cleaned_text"] = processed

        # Tokenization
        if tokenize:
            tokens = self.tokenize(processed)

            if remove_stopwords:
                tokens = self.remove_stopwords(tokens)

            if lemmatize:
                tokens = self.lemmatize(tokens)

            result["tokens"] = tokens
            result["token_count"] = len(tokens)

        # Extract linguistic features
        result["sentences"] = self.tokenize_sentences(text)
        result["sentence_count"] = len(result["sentences"])
        result["entities"] = self.extract_entities(text)
        result["key_phrases"] = self.extract_key_phrases(text)

        logger.info(
            f"Preprocessing complete: {len(result['tokens'])} tokens, "
            f"{len(result['sentences'])} sentences"
        )

        return result

    def get_vocabulary_stats(self, text: str) -> Dict:
        """Get vocabulary statistics."""
        tokens = self.tokenize(text.lower())
        unique_tokens = set(tokens)

        return {
            "total_words": len(tokens),
            "unique_words": len(unique_tokens),
            "vocabulary_richness": len(unique_tokens) / len(tokens) if tokens else 0,
            "avg_word_length": sum(len(t) for t in tokens) / len(tokens)
            if tokens
            else 0,
        }
