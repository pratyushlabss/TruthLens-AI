"""File upload endpoint for images, documents, and screenshots with OCR."""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import Optional
import os
import aiofiles
import logging
from pathlib import Path
from utils.image_grid_splitter import ImageGridSplitter
from utils.aws_s3_handler import S3Handler
from services.preprocessing_service import TextPreprocessor
import tempfile

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/truthlens_uploads")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt", ".docx"}

# Initialize services
image_processor = ImageGridSplitter(grid_size=3)
text_preprocessor = TextPreprocessor()
s3_handler = S3Handler()

# Store processing status
upload_status = {}


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    session_id: Optional[str] = None,
    analyze: bool = False,
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    Upload screenshot, image, or document for analysis.
    
    Args:
        file: File to upload
        session_id: Optional session ID for tracking
        analyze: Whether to analyze image for text/claims
        background_tasks: Background task runner
        
    Returns:
        Upload confirmation with extracted data
    """
    try:
        # Validate file
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large (max 50MB)")

        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}",
            )

        # Create upload directory
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Save file temporarily
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        contents = await file.read()

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(contents)

        logger.info(f"Saved uploaded file: {file_path}")

        # Process image if requested
        extracted_text = None
        extracted_entities = None
        grid_data = None

        if analyze and file_ext in {".jpg", ".jpeg", ".png", ".gif"}:
            try:
                # Process image with grid splitting and OCR
                logger.info("Processing image with OCR")
                image_result = image_processor.process_image(file_path)
                extracted_text = image_result.get("extracted_text", "")

                # Preprocess extracted text
                if extracted_text:
                    preprocessing_result = text_preprocessor.preprocess(
                        extracted_text
                    )
                    extracted_entities = preprocessing_result.get("entities", {})
                    grid_data = image_result.get("grid_text", {})

                logger.info(f"Extracted {len(extracted_text)} characters from image")

            except Exception as e:
                logger.error(f"Image processing failed: {e}")
                extracted_text = None

        # Generate upload ID
        import uuid

        upload_id = str(uuid.uuid4())
        upload_status[upload_id] = {
            "status": "completed",
            "filename": file.filename,
            "size": len(contents),
            "has_text_extraction": extracted_text is not None,
        }

        # Upload to S3 if configured
        s3_url = None
        if s3_handler.s3_client:
            s3_key = f"uploads/{session_id or 'anonymous'}/{upload_id}/{file.filename}"
            s3_url = s3_handler.upload_file(file_path, s3_key)

        response = {
            "upload_id": upload_id,
            "filename": file.filename,
            "size": len(contents),
            "path": file_path,
            "s3_url": s3_url,
            "extracted_text": extracted_text[:500] if extracted_text else None,
            "entities": extracted_entities,
            "grid_data": {str(k): v for k, v in (grid_data or {}).items()},
            "message": "File uploaded and processed successfully",
        }

        # Background: cleanup temp file after 24 hours
        if s3_url:
            background_tasks.add_task(cleanup_old_uploads)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/upload/status/{upload_id}")
async def get_upload_status_endpoint(upload_id: str):
    """Get status of uploaded file processing."""
    if upload_id not in upload_status:
        raise HTTPException(status_code=404, detail="Upload not found")

    return {
        "upload_id": upload_id,
        "details": upload_status[upload_id],
    }


@router.post("/upload/ocr/{upload_id}")
async def extract_text_from_upload(upload_id: str, grid_size: int = 3):
    """
    Extract text from previously uploaded image.
    
    Args:
        upload_id: Upload ID
        grid_size: Grid size for splitting
        
    Returns:
        Extracted text and entities
    """
    try:
        if upload_id not in upload_status:
            raise HTTPException(status_code=404, detail="Upload not found")

        status = upload_status[upload_id]

        # Get file path (would need to store this in practice)
        file_path = status.get("file_path")

        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # Process with new grid size
        processor = ImageGridSplitter(grid_size=grid_size)
        result = processor.process_image(file_path)

        # Preprocess text
        preprocessing_result = text_preprocessor.preprocess(
            result.get("extracted_text", "")
        )

        return {
            "upload_id": upload_id,
            "extracted_text": result.get("extracted_text", ""),
            "entities": preprocessing_result.get("entities", {}),
            "key_phrases": preprocessing_result.get("key_phrases", []),
            "token_count": preprocessing_result.get("token_count", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")


def cleanup_old_uploads(days: int = 1):
    """Clean up old uploaded files."""
    try:
        from datetime import datetime, timedelta

        cutoff = datetime.now() - timedelta(days=days)
        cutoff_timestamp = cutoff.timestamp()

        for filename in os.listdir(UPLOAD_DIR):
            filepath = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(filepath):
                if os.path.getmtime(filepath) < cutoff_timestamp:
                    os.remove(filepath)
                    logger.info(f"Cleaned up old file: {filename}")

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
