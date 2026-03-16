"""
Image Processing Service - Convert images to text and analyze
Uses Hugging Face BLIP model for image captioning
"""

import os
import requests
from typing import Optional
from werkzeug.datastructures import FileStorage

HF_TOKEN = os.getenv('HF_TOKEN')
HF_API_URL = 'https://api-inference.huggingface.co/models'

def process_image(image_file: FileStorage) -> str:
    """
    Process image file and generate caption
    Uses Salesforce/blip-image-captioning-base
    Returns: image caption text
    """
    if not HF_TOKEN:
        raise ValueError('HF_TOKEN not configured')
    
    try:
        # Read image file
        image_data = image_file.read()
        
        # Send to Hugging Face API
        response = requests.post(
            f'{HF_API_URL}/Salesforce/blip-image-captioning-base',
            headers={'Authorization': f'Bearer {HF_TOKEN}'},
            data=image_data,
            timeout=30
        )
        
        if not response.ok:
            raise ValueError(f'HF API error: {response.status_code} - {response.text}')
        
        result = response.json()
        
        # Handle response format
        if isinstance(result, list) and len(result) > 0:
            caption_obj = result[0]
            if isinstance(caption_obj, dict):
                return caption_obj.get('generated_text', 'Unable to generate image caption')
        
        return 'Unable to generate image caption'
        
    except Exception as e:
        print(f'Image processing error: {str(e)}')
        raise ValueError(f'Image processing failed: {str(e)}')

def encode_image_to_base64(image_file: FileStorage) -> str:
    """
    Encode image file to base64 string
    """
    import base64
    
    image_data = image_file.read()
    return base64.b64encode(image_data).decode('utf-8')
