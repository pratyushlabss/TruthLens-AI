"""Image preprocessing and OCR grid splitting for screenshot analysis."""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
import pytesseract
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class ImageGridSplitter:
    """Processes images using grid-based OCR for improved text extraction."""

    def __init__(self, grid_size: int = 3, overlap: float = 0.1):
        """
        Initialize image processor.

        Args:
            grid_size: Size of grid (e.g., 3 = 3x3 grid)
            overlap: Overlap ratio between grid cells (0-1)
        """
        self.grid_size = grid_size
        self.overlap = overlap

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image: resize, denoise, normalize brightness.

        Args:
            image_path: Path to image file

        Returns:
            Preprocessed OpenCV image
        """
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")

        logger.info(f"Original image shape: {img.shape}")

        # Resize to standard dimensions
        height, width = img.shape[:2]
        max_dim = 1920
        if max(height, width) > max_dim:
            scale = max_dim / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height))
            logger.info(f"Resized to: {img.shape}")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Denoise using bilateral filter
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        logger.info("Applied denoising")

        # Normalize brightness using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        normalized = clahe.apply(denoised)
        logger.info("Applied brightness normalization")

        # Apply thresholding for better OCR
        _, binary = cv2.threshold(normalized, 150, 255, cv2.THRESH_BINARY)

        return binary

    def split_into_grid(
        self, image: np.ndarray
    ) -> List[Tuple[np.ndarray, Tuple[int, int]]]:
        """
        Split image into N x N grid with overlap.

        Args:
            image: Input image as numpy array

        Returns:
            List of (grid_block, (row, col)) tuples
        """
        height, width = image.shape[:2]

        # Calculate grid cell dimensions with overlap
        cell_height = height // self.grid_size
        cell_width = width // self.grid_size
        overlap_h = int(cell_height * self.overlap)
        overlap_w = int(cell_width * self.overlap)

        grid_blocks = []

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                # Calculate coordinates with overlap
                y_start = max(0, row * cell_height - overlap_h)
                y_end = min(height, (row + 1) * cell_height + overlap_h)
                x_start = max(0, col * cell_width - overlap_w)
                x_end = min(width, (col + 1) * cell_width + overlap_w)

                # Extract block
                block = image[y_start:y_end, x_start:x_end]

                grid_blocks.append((block, (row, col)))

        logger.info(f"Split image into {len(grid_blocks)} grid blocks")
        return grid_blocks

    def extract_text_from_block(self, block: np.ndarray) -> str:
        """
        Extract text from image block using Tesseract OCR.

        Args:
            block: Image block as numpy array

        Returns:
            Extracted text
        """
        try:
            # Configure Tesseract
            config = r"--oem 3 --psm 6"
            text = pytesseract.image_to_string(block, config=config)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return ""

    def process_grid_blocks(
        self, grid_blocks: List[Tuple[np.ndarray, Tuple[int, int]]]
    ) -> Dict[Tuple[int, int], str]:
        """
        Extract text from all grid blocks.

        Args:
            grid_blocks: List of grid blocks

        Returns:
            Dictionary mapping grid position to extracted text
        """
        grid_text = {}

        for block, (row, col) in grid_blocks:
            text = self.extract_text_from_block(block)
            grid_text[(row, col)] = text
            logger.debug(f"Grid [{row},{col}] extracted {len(text)} characters")

        return grid_text

    def merge_grid_text(
        self, grid_text: Dict[Tuple[int, int], str]
    ) -> str:
        """
        Merge text from all grid cells into single document.

        Args:
            grid_text: Dictionary of grid position to text

        Returns:
            Merged text document
        """
        merged_lines = []

        for row in range(self.grid_size):
            row_texts = []
            for col in range(self.grid_size):
                text = grid_text.get((row, col), "")
                row_texts.append(text)
            merged_lines.append(" ".join(row_texts))

        merged_text = "\n".join(merged_lines)
        logger.info(f"Merged {len(merged_text)} characters")
        return merged_text

    def process_image(self, image_path: str) -> Dict:
        """
        Complete pipeline: preprocess → split → extract → merge.

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with extracted text and metadata
        """
        logger.info(f"Processing image: {image_path}")

        # Preprocess
        preprocessed = self.preprocess_image(image_path)

        # Split into grid
        grid_blocks = self.split_into_grid(preprocessed)

        # Extract text from each block
        grid_text = self.process_grid_blocks(grid_blocks)

        # Merge text
        merged_text = self.merge_grid_text(grid_text)

        # Get file info
        file_path = Path(image_path)
        file_size = file_path.stat().st_size

        return {
            "extracted_text": merged_text,
            "grid_text": grid_text,
            "file_name": file_path.name,
            "file_size": file_size,
            "grid_size": self.grid_size,
            "character_count": len(merged_text),
        }

    def extract_text_regions(
        self, image_path: str
    ) -> List[Dict]:
        """
        Extract text regions with bounding boxes for visualization.

        Args:
            image_path: Path to image file

        Returns:
            List of text regions with coordinates
        """
        img = cv2.imread(image_path)
        preprocessed = self.preprocess_image(image_path)

        # Detect contours
        contours, _ = cv2.findContours(
            preprocessed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 10 and h > 10:  # Filter small noise
                region_img = preprocessed[y : y + h, x : x + w]
                text = self.extract_text_from_block(region_img)

                if text.strip():  # Only include regions with text
                    regions.append(
                        {
                            "text": text,
                            "x": int(x),
                            "y": int(y),
                            "width": int(w),
                            "height": int(h),
                        }
                    )

        logger.info(f"Extracted {len(regions)} text regions")
        return regions
