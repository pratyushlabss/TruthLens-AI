"""
TruthLens AI - HuggingFace NLI (Natural Language Inference) Integration
Purpose: Real fact-checking using facebook/bart-large-mnli model
No fake inferences. Real model predictions only.
"""

import logging
from typing import Dict, List, Tuple
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

logger = logging.getLogger(__name__)

class NLIError(Exception):
    """Raised when NLI inference fails."""
    pass

class HuggingFaceNLI:
    """
    Real Natural Language Inference using BART-large-MNLI.
    
    ENTAILMENT (support):     Claim is supported by evidence
    CONTRADICTION (contradict): Claim is contradicted by evidence
    NEUTRAL:                  Evidence is neutral / doesn't speak to claim
    """
    
    # Model configuration
    MODEL_NAME = "facebook/bart-large-mnli"
    LABEL_MAPPING = {
        "entailment": "support",
        "contradiction": "contradict",
        "neutral": "neutral",
    }
    
    def __init__(self, api_key: str = None, device: str = 'cpu'):
        """
        Initialize HuggingFace NLI pipeline.
        
        Args:
            api_key: Optional HuggingFace API key (from environment)
            device: Device to run on ('cpu' or 'cuda')
        """
        self.api_key = api_key
        self.device = 0 if device == 'cuda' and torch.cuda.is_available() else -1
        
        logger.info(f"Loading NLI model: {self.MODEL_NAME}")

        try:
            # Load model and tokenizer. We use facebook/bart-large-mnli as a
            # proper Natural Language Inference model (entailment /
            # contradiction / neutral), not as a generic zero-shot classifier.
            self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.MODEL_NAME
            )

            # Create an NLI pipeline that returns scores for all three labels
            # for a given (premise, hypothesis) pair encoded as:
            #   "premise </s></s> hypothesis"
            self.pipeline = pipeline(
                "text-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                device=self.device,
                return_all_scores=True,
            )

            logger.info(f"✅ NLI model loaded successfully on device {device}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load NLI model: {e}")
            raise NLIError(f"Model initialization failed: {e}")
    
    def infer_single(self, claim: str, evidence: str) -> Dict:
        """
        Compare a single claim against evidence.
        
        Args:
            claim: The claim to verify
            evidence: The evidence text
            
        Returns:
            {
                'claim': str,
                'evidence': str,
                'stance': 'support' | 'contradict' | 'neutral',
                'confidence': float (0-1),
                'raw_labels': dict,
            }
        """
        try:
            # Truncate if too long (model has max token limit)
            max_length = 512
            claim_trunc = claim[:max_length]
            evidence_trunc = evidence[:max_length]

            # Encode NLI pair: evidence (premise) and claim (hypothesis).
            sequence = f"{evidence_trunc} </s></s> {claim_trunc}"

            # Run inference via text-classification pipeline, which returns a
            # list of {"label": ..., "score": ...} entries.
            outputs = self.pipeline(sequence)[0]

            # Normalise label names and collect scores for the three NLI
            # classes.
            label_scores = {}
            for item in outputs:
                label = str(item.get("label", "")).lower()
                score = float(item.get("score", 0.0))
                if "entail" in label:
                    label_scores["entailment"] = score
                elif "contradict" in label:
                    label_scores["contradiction"] = score
                elif "neutral" in label:
                    label_scores["neutral"] = score

            # Ensure all keys exist
            for key in ("entailment", "contradiction", "neutral"):
                label_scores.setdefault(key, 0.0)

            # Top label and stance
            top_label = max(label_scores, key=label_scores.get)
            top_score = label_scores[top_label]

            stance = self.LABEL_MAPPING.get(top_label, "neutral")
            
            logger.info(
                f"NLI: '{claim[:50]}...' vs evidence "
                f"→ {stance} ({top_score:.2%})"
            )
            
            return {
                'claim': claim,
                'evidence': evidence[:200],  # Include excerpt
                'stance': stance,
                'confidence': float(top_score),
                'raw_labels': {
                    'entailment': label_scores['entailment'],
                    'contradiction': label_scores['contradiction'],
                    'neutral': label_scores['neutral'],
                }
            }
            
        except Exception as e:
            logger.error(f"❌ NLI inference failed: {e}")
            raise NLIError(f"Inference failed for claim: {e}")
    
    def infer_batch(self, claim: str, evidence_list: List[str]) -> List[Dict]:
        """
        Compare claim against multiple evidence texts.
        
        Args:
            claim: The claim to verify
            evidence_list: List of evidence texts
            
        Returns:
            List of inference results
        """
        try:
            results = []
            
            logger.info(f"Running batch inference: 1 claim vs {len(evidence_list)} evidence")
            
            for i, evidence in enumerate(evidence_list):
                try:
                    result = self.infer_single(claim, evidence)
                    results.append(result)
                except Exception as e:
                    logger.warning(f"Failed to infer evidence {i}: {e}")
                    continue
            
            if not results:
                raise NLIError("All batch inferences failed")
            
            logger.info(f"✅ Completed batch inference: {len(results)} successful")
            return results
            
        except Exception as e:
            logger.error(f"❌ Batch inference failed: {e}")
            raise NLIError(f"Batch inference error: {e}")
    
    def compute_verdict(self, claim: str, inferences: List[Dict]) -> Dict:
        """
        Compute final verdict based on multiple inferences.
        STRICT mode: requires clear majority.
        
        Args:
            claim: The original claim
            inferences: List of inference results
            
        Returns:
            {
                'claim': str,
                'verdict': 'TRUE' | 'FALSE' | 'CONFLICTED',
                'confidence': int (0-100),
                'support_count': int,
                'contradict_count': int,
                'neutral_count': int,
                'evidence_quality': float (0-1),
            }
        """
        try:
            if not inferences:
                raise NLIError("No inferences provided for verdict computation")
            
            # Count stances
            support_count = sum(1 for i in inferences if i['stance'] == 'support')
            contradict_count = sum(1 for i in inferences if i['stance'] == 'contradict')
            neutral_count = sum(1 for i in inferences if i['stance'] == 'neutral')
            
            total = len(inferences)
            
            # Compute verdict (STRICT MODE)
            # Need clear majority
            if contradict_count > support_count:
                verdict = 'FALSE'
                # Confidence: how many contradict vs total
                confidence = int((contradict_count / total) * 100)
            elif support_count > contradict_count:
                verdict = 'TRUE'
                # Confidence: how many support vs total
                confidence = int((support_count / total) * 100)
            else:
                # Equal split or mostly neutral
                verdict = 'CONFLICTED'
                confidence = 50
            
            # Ensure confidence is in bounds
            confidence = max(40, min(100, confidence))
            
            # Compute average confidence of inferences
            avg_evidence_confidence = sum(i['confidence'] for i in inferences) / total
            
            logger.info(
                f"Verdict computed: {verdict} ({confidence}%) based on "
                f"{support_count} support, {contradict_count} contradict, "
                f"{neutral_count} neutral"
            )
            
            return {
                'claim': claim,
                'verdict': verdict,
                'confidence': confidence,
                'support_count': support_count,
                'contradict_count': contradict_count,
                'neutral_count': neutral_count,
                'evidence_quality': avg_evidence_confidence,
                'total_evidence': total,
            }
            
        except Exception as e:
            logger.error(f"❌ Verdict computation failed: {e}")
            raise NLIError(f"Verdict computation error: {e}")

