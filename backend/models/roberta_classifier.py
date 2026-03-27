"""RoBERTa-based fake news classifier with hardware optimization and lazy loading."""

import numpy as np
from typing import Dict, Tuple, Optional
import logging
import torch

logger = logging.getLogger(__name__)

class RoBERTaClassifier:
    """RoBERTa model for fake news detection with GPU acceleration (MPS for Mac)."""
    
    def __init__(self, model_name: str = "roberta-base-openai-detector"):
        """
        Initialize RoBERTa classifier with hardware-optimized lazy loading.
        Defaults to OpenAI detector model for GPT/AI-generated content detection (60% weight).
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self.device = self._get_optimal_device()
        self.tokenizer: Optional[object] = None
        self.model: Optional[object] = None
        self._initialized = False
        
        self.label_map = {0: "REAL", 1: "RUMOR", 2: "FAKE"}
    
    def _get_optimal_device(self) -> torch.device:
        """
        Get optimal device for inference.
        
        Priority:
        1. Metal Performance Shaders (MPS) - Mac GPU acceleration
        2. CUDA - NVIDIA GPU
        3. CPU - Fallback
        
        Returns:
            torch.device object
        """
        try:
            if torch.backends.mps.is_available() and torch.backends.mps.is_built():
                device = torch.device("mps")
                logger.info("✓ Using Metal Performance Shaders (MPS) for Mac GPU acceleration")
                return device
        except Exception as e:
            logger.debug(f"MPS not available: {e}")
        
        if torch.cuda.is_available():
            device = torch.device(f"cuda:{torch.cuda.current_device()}")
            logger.info(f"✓ Using NVIDIA GPU: {torch.cuda.get_device_name(0)}")
            return device
        
        device = torch.device("cpu")
        logger.info("✓ Using CPU for inference")
        return device
    
    def _initialize(self):
        """Lazy initialize the model and tokenizer on first use."""
        if self._initialized:
            return
        
        logger.info(f"Loading RoBERTa model: {self.model_name}")
        
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            
            # Load tokenizer (CPU-agnostic)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Load model on optimal device
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=3  # REAL, RUMOR, FAKE
            )
            
            # Move to optimal device (MPS, CUDA, or CPU)
            self.model = self.model.to(self.device)
            self.model.eval()
            
            # Optimize for inference
            with torch.no_grad():
                pass
            
            self._initialized = True
            logger.info(f"✓ RoBERTa model loaded on {self.device.type.upper()}")
        except Exception as e:
            logger.error(f"Failed to load RoBERTa model: {e}")
            raise
    
    def classify(self, text: str) -> Dict:
        """
        Classify text as real, rumor, or fake.
        
        Args:
            text: Input claim/article text
            
        Returns:
            Dictionary with verdict, confidence, and scores
        """
        # Lazy initialize on first use
        self._initialize()
        
        import torch
        
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
