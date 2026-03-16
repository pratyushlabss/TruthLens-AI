"""
TruthLens AI Backend - Multimodal Misinformation Detection API
Flask-based REST API for analyzing text, URLs, and images
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import time
from datetime import datetime
from werkzeug.utils import secure_filename
import io
import base64
from typing import Dict, List, Any, Tuple

# Load environment variables
load_dotenv()

# Validate required environment variables
required_env_vars = ["HF_TOKEN", "PINECONE_KEY", "SCRAPER_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    import warnings
    warnings.warn(
        f"WARNING: Missing required environment variables: {', '.join(missing_vars)}. "
        f"Some features may not work correctly. Please set these variables in your .env file.",
        RuntimeWarning
    )

# Import service modules
from app.services.nlp_analyzer import analyze_with_nlp, generate_embeddings
from app.services.image_processor import process_image
from app.services.web_scraper import scrape_url
from app.services.evidence_retriever import query_pinecone

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# ==================== UTILITY FUNCTIONS ====================

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_image_sentiment(description: str) -> float:
    """Calculate sentiment score from image description"""
    sensational_words = [
        'shocking', 'dangerous', 'unbelievable', 'horrifying', 
        'urgent', 'alert', 'warning', 'critical'
    ]
    has_emotional_content = any(
        word in description.lower() for word in sensational_words
    )
    return 70.0 if has_emotional_content else 45.0

def calculate_fusion_score(
    nlp_score: float,
    evidence_score: float,
    image_score: float = None,
    has_image: bool = False
) -> float:
    """Combine NLP, Evidence, and Image scores"""
    if has_image and image_score is not None:
        # With image: NLP 60%, Evidence 25%, Image 15%
        return (nlp_score * 0.6) + (evidence_score * 0.25) + (image_score * 0.15)
    # Without image: NLP 75%, Evidence 25%
    return (nlp_score * 0.75) + (evidence_score * 0.25)

def determine_verdict(score: float) -> str:
    """Determine verdict based on final score"""
    if score >= 70:
        return 'FAKE'
    elif score <= 30:
        return 'REAL'
    else:
        return 'RUMOR'

def extract_key_signals(
    nlp_label: str,
    has_emotional_image: bool,
    evidence_sources: List[Dict]
) -> List[str]:
    """Extract key signals from analysis"""
    signals = []
    
    if nlp_label.lower() == 'fake':
        signals.append('NLP model indicates likely misinformation')
    
    if has_emotional_image:
        signals.append('Image contains sensational content')
    
    if not evidence_sources:
        signals.append('No corroborating evidence found')
    elif any(s.get('supports') == 'CONTRADICTS' for s in evidence_sources):
        signals.append('Found contradicting evidence')
    
    return signals if signals else ['Analysis complete']

# ==================== ROUTE HANDLERS ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'TruthLens AI Backend',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    """
    Main analysis endpoint
    Accepts FormData with:
    - text: Text to analyze
    - url: URL to scrape and analyze
    - image: Image file to process
    """
    
    if request.method == 'OPTIONS':
        return '', 204
    
    start_time = time.time()
    warnings = []
    
    try:
        # Parse incoming data
        text = request.form.get('text', '').strip() if request.form else ''
        url = request.form.get('url', '').strip() if request.form else ''
        image_file = request.files.get('image') if request.files else None
        
        # Validate input
        if not text and not url and not image_file:
            return jsonify({
                'error': 'At least one of text, url, or image must be provided'
            }), 400
        
        analyzed_text = text
        image_description = None
        
        # ========== Step 1: Image Processing ==========
        if image_file:
            if not allowed_file(image_file.filename):
                return jsonify({
                    'error': f'Invalid image format. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
                }), 400
            
            try:
                image_description = process_image(image_file)
                analyzed_text += f' [IMAGE CAPTION: {image_description}]'
            except Exception as e:
                warnings.append(f'Image processing failed: {str(e)}')
        
        # ========== Step 2: URL Scraping (Autopilot) ==========
        if url and not text:
            try:
                scraped_text = scrape_url(url)
                analyzed_text = scraped_text or analyzed_text
            except Exception as e:
                warnings.append(f'URL scraping failed: {str(e)}')
        
        # Ensure we have text to analyze
        if not analyzed_text.strip():
            return jsonify({
                'error': 'Unable to extract any text from provided inputs'
            }), 400
        
        # ========== Step 3: NLP Analysis ==========
        nlp_result = {'score': 50, 'label': 'neutral', 'confidence': 0.5}
        try:
            nlp_result = analyze_with_nlp(analyzed_text)
        except Exception as e:
            warnings.append(f'NLP analysis failed: {str(e)}')
        
        # ========== Step 4: Generate Embeddings ==========
        embeddings = []
        try:
            embeddings = generate_embeddings(analyzed_text)
        except Exception as e:
            warnings.append(f'Embedding generation failed: {str(e)}')
        
        # ========== Step 5: Evidence Retrieval ==========
        evidence_sources = []
        if embeddings:
            try:
                evidence_sources = query_pinecone(embeddings)
            except Exception as e:
                warnings.append(f'Evidence retrieval failed: {str(e)}')
        
        # ========== Step 6: Calculate Evidence Score ==========
        if evidence_sources:
            evidence_score = sum(s['relevance'] for s in evidence_sources) / len(evidence_sources)
        else:
            evidence_score = 50.0
        
        # ========== Step 7: Image Sentiment Score ==========
        image_score = None
        if image_description:
            image_score = calculate_image_sentiment(image_description)
        
        # ========== Step 8: Fusion Scoring ==========
        final_score = calculate_fusion_score(
            nlp_result['score'],
            evidence_score,
            image_score,
            bool(image_file)
        )
        verdict = determine_verdict(final_score)
        
        # ========== Step 9: Generate Key Signals ==========
        key_signals = extract_key_signals(
            nlp_result['label'],
            bool(image_file) and image_score and image_score > 60,
            evidence_sources
        )
        
        # ========== Step 10: Generate Summary ==========
        summary = f"This claim has a {round(final_score)}% likelihood of being {verdict.lower()}. "
        if evidence_sources:
            summary += f"Found {len(evidence_sources)} sources with relevant information. "
        else:
            summary += "No corroborating evidence found. "
        if image_description:
            summary += f"The image contains: \"{image_description[:100]}...\""
        
        # ========== Prepare Response ==========
        response_data = {
            'verdict': verdict,
            'confidence': round(final_score),
            'details': {
                'nlpScore': round(nlp_result['score']),
                'evidenceScore': round(evidence_score),
                'summary': summary,
                'keySignals': key_signals,
                'evidenceSources': evidence_sources
            },
            'processingTime': round((time.time() - start_time) * 1000)  # ms
        }
        
        if image_score is not None:
            response_data['details']['imageScore'] = round(image_score)
        
        if warnings:
            response_data['warnings'] = warnings
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f'Analysis error: {str(e)}')
        return jsonify({
            'error': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get recent analysis sessions (placeholder)"""
    return jsonify({
        'sessions': [],
        'total': 0
    }), 200

@app.route('/api/export/<result_id>', methods=['GET'])
def export_analysis(result_id):
    """Export analysis result as PDF or JSON (placeholder)"""
    return jsonify({
        'error': 'Export not yet implemented'
    }), 501

# ==================== ERROR HANDLERS ====================

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 10MB'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    port = int(os.getenv('BACKEND_PORT', 5000))
    
    print(f"Starting TruthLens AI Backend on port {port}")
    print(f"Debug mode: {debug_mode}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        use_reloader=debug_mode
    )
