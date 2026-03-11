"""RoBERTa-based fake news classifier."""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from typing import Dict, Tuple

class RoBERTaClassifier:
    """RoBERTa model for fake news detection."""
    
    def __init__(self, model_name: str = "roberta-base"):
        """
        Initialize RoBERTa classifier.
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=3  # REAL, RUMOR, FAKE
        ).to(self.device)
        self.model.eval()
        
        self.label_map = {0: "REAL", 1: "RUMOR", 2: "FAKE"}
    
    def classify(self, text: str) -> Dict:
        """
        Classify text as real, rumor, or fake.
        
        Args:
            text: Input claim/article text
            
        Returns:
            Dictionary with verdict, confidence, and scores
        """
        # Tokenize
        inputs = self.tokenizer(
            text,
            max_length=512,
            truncation=True,
            return_tensors="pt"
        ).to(self.device)
        
        # Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
        
        # Convert to probabilities
        probs = torch.softmax(logits, dim=1)[0].cpu().numpy()
        pred_idx = np.argmax(probs)
        
        # Normalize to 0-100 scale
        scores = (probs * 100).round(2)
        
        return {
            "verdict": self.label_map[pred_idx],
            "confidence": float(scores[pred_idx]),
            "scores": {
                "real": float(scores[0]),
                "rumor": float(scores[1]),
                "fake": float(scores[2])
            },
            "nlp_score": float(scores[pred_idx])  # Core NLP confidence
        }
    
    def load_finetuned_model(self, model_path: str):
        """Load a fine-tuned model checkpoint."""
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_path
        ).to(self.device)
        self.model.eval()
