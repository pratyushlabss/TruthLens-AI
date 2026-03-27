"""Multimodal vision service using BLIP for image captioning."""

import logging
from typing import Optional, Dict
import torch
from io import BytesIO
import base64
import logging

logger = logging.getLogger(__name__)


class MultimodalVisionService:
    """
    Handles multimodal analysis including image captioning using BLIP.
    Converts images to text for claim analysis.
    """
    
    def __init__(self):
        """Initialize multimodal vision service with lazy loading."""
        self.device = self._get_optimal_device()
        self.model = None
        self.processor = None
        self._initialized = False
        logger.info("✓ Multimodal Vision Service initialized (lazy-loaded)")
    
    def _get_optimal_device(self) -> torch.device:
        """Get optimal device for vision model inference."""
        try:
            if torch.backends.mps.is_available() and torch.backends.mps.is_built():
                device = torch.device("mps")
                logger.info("✓ Using Metal Performance Shaders (MPS) for BLIP")
                return device
        except Exception:
            pass
        
        if torch.cuda.is_available():
            device = torch.device(f"cuda:{torch.cuda.current_device()}")
            logger.info(f"✓ Using CUDA GPU for BLIP: {torch.cuda.get_device_name(0)}")
            return device
        
        device = torch.device("cpu")
        logger.info("✓ Using CPU for BLIP vision model")
        return device
    
    def _initialize(self):
        """Lazy initialize BLIP model on first use."""
        if self._initialized:
            return
        
        logger.info("Loading BLIP image captioning model...")
        
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            from PIL import Image
            
            # Download and cache model
            model_name = "Salesforce/blip-image-captioning-base"
            self.processor = BlipProcessor.from_pretrained(model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device.type in ["cuda", "mps"] else torch.float32
            )
            
            # Move to optimal device
            self.model = self.model.to(self.device)
            self.model.eval()
            
            self._initialized = True
            logger.info(f"✓ BLIP model loaded on {self.device.type.upper()}")
        except Exception as e:
            logger.error(f"Failed to load BLIP model: {e}")
            raise
    
    def extract_image_caption(self, image_input) -> Optional[str]:
        """
        Extract text caption from image using BLIP.
        
        Supports multiple input formats:
        - File path (str)
        - Base64-encoded image string
        - PIL Image object
        - Bytes
        
        Args:
            image_input: Image in various formats
        
        Returns:
            Generated caption string or None on error
        """
        self._initialize()
        
        try:
            from PIL import Image
            import requests
            from io import BytesIO
            
            # Convert input to PIL Image
            if isinstance(image_input, str):
                # Try file path first
                try:
                    image = Image.open(image_input)
                except:
                    # Try as base64
                    if image_input.startswith("data:image"):
                        # Remove data URL prefix
                        image_data = image_input.split(",")[1]
                    else:
                        image_data = image_input
                    
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_bytes))
            elif isinstance(image_input, bytes):
                image = Image.open(BytesIO(image_input))
            else:
                # Assume PIL Image
                image = image_input
            
            # Convert RGBA to RGB if needed
            if image.mode in ("RGBA", "P"):
                rgb_image = Image.new("RGB", image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
                image = rgb_image
            
            # Generate caption
            with torch.no_grad():
                inputs = self.processor(image, return_tensors="pt").to(self.device)
                out = self.model.generate(**inputs, max_new_tokens=50)
                caption = self.processor.decode(out[0], skip_special_tokens=True)
            
            logger.info(f"✓ Image caption extracted: {caption[:100]}")
            return caption
        
        except Exception as e:
            logger.error(f"Image caption extraction failed: {e}")
            return None
    
    def analyze_image_for_claim(
        self,
        image_input,
        claim_text: str
    ) -> Dict:
        """
        Analyze image in context of a claim.
        
        Example:
            Claim: "Trump wins election"
            Image: Screenshot of fake newspaper
            Analysis: Detects incongruence between claim and image context
        
        Args:
            image_input: Image data
            claim_text: Related claim to analyze
        
        Returns:
            Dictionary with image analysis and claim mismatch score
        """
        caption = self.extract_image_caption(image_input)
        
        if not caption:
            return {
                "caption": None,
                "analysis": "Could not extract image caption",
                "mismatch_score": 0.0
            }
        
        # Calculate semantic similarity between caption and claim
        mismatch_score = self._calculate_caption_claim_mismatch(caption, claim_text)
        
        return {
            "caption": caption,
            "analysis": f"Image shows: {caption}. Claim context: {claim_text[:100]}...",
            "mismatch_score": mismatch_score,
            "is_suspicious": mismatch_score > 0.6  # High mismatch suggests fake/modified image
        }
    
    def _calculate_caption_claim_mismatch(self, caption: str, claim: str) -> float:
        """
        Calculate how much image caption contradicts the claim (0-1 scale).
        
        High score = strong mismatch (suggests manipulated/irrelevant image)
        Low score = caption aligns with claim
        
        Args:
            caption: Image caption from BLIP
            claim: Claim text
        
        Returns:
            Mismatch score (0-1)
        """
        try:
            from sentence_transformers import SentenceTransformer, util
            
            # Use same SBERT model for consistency
            sbert = SentenceTransformer("all-MiniLM-L6-v2")
            
            caption_emb = sbert.encode(caption, convert_to_numpy=True)
            claim_emb = sbert.encode(claim, convert_to_numpy=True)
            
            # Similarity score (0-1)
            similarity = util.cos_sim(caption_emb, claim_emb)[0][0].item()
            
            # Invert: high similarity = low mismatch
            mismatch = 1.0 - similarity
            
            return min(1.0, max(0.0, mismatch))
        
        except Exception as e:
            logger.warning(f"Mismatch calculation failed: {e}")
            return 0.5  # Neutral score on error
