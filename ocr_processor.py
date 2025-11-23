"""
OCR (Optical Character Recognition) Module for Document Processing

This module provides OCR capabilities for extracting text from image-based PDFs
and standalone image files using Tesseract OCR engine.
"""
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
    
    # Try to detect Tesseract installation
    tesseract_found = False
    try:
        pytesseract.get_tesseract_version()
        logger.info("Tesseract OCR engine detected and ready")
        tesseract_found = True
    except Exception as e:
        logger.warning(f"Tesseract not found in PATH: {e}")
        # Common Windows installation paths
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', '')),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                try:
                    # Test if this path works
                    pytesseract.get_tesseract_version()
                    logger.info(f"Found and configured Tesseract at: {path}")
                    tesseract_found = True
                    break
                except Exception as test_e:
                    logger.warning(f"Path {path} exists but failed to work: {test_e}")
                    continue
        
        if not tesseract_found:
            logger.error("Tesseract OCR not found. Please install Tesseract OCR.")
            logger.error("Download from: https://github.com/UB-Mannheim/tesseract/wiki")
            OCR_AVAILABLE = False
    
    # Final check to set OCR_AVAILABLE flag
    if not tesseract_found:
        OCR_AVAILABLE = False

except ImportError as e:
    OCR_AVAILABLE = False
    logger.error(f"OCR dependencies not available: {e}")
    logger.error("Install with: pip install pytesseract pdf2image Pillow")


class OCRProcessor:
    """OCR processor for extracting text from images and image-based PDFs."""
    
    def __init__(self, 
                 confidence_threshold: float = 0.3,
                 min_text_length: int = 10,
                 languages: str = 'eng'):
        """
        Initialize OCR processor.
        
        Args:
            confidence_threshold: Minimum confidence for text recognition (0.0-1.0)
            min_text_length: Minimum text length to consider extraction successful
            languages: Tesseract language codes (e.g., 'eng', 'eng+fra', 'eng+deu')
        """
        self.confidence_threshold = confidence_threshold
        self.min_text_length = min_text_length
        self.languages = languages
        self.available = OCR_AVAILABLE
        
        if not self.available:
            logger.warning("OCR processor initialized but OCR libraries not available")
    
    def is_available(self) -> bool:
        """Check if OCR functionality is available."""
        return self.available
    
    def extract_text_from_image(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Extract text from a single image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        if not self.available:
            return {
                "text": "",
                "success": False,
                "error": "OCR libraries not available",
                "confidence": 0.0
            }
        
        try:
            image_path = Path(image_path)
            
            # Open and preprocess image
            with Image.open(image_path) as image:
                # Convert to RGB if needed
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Get text with confidence scores
                ocr_data = pytesseract.image_to_data(
                    image, 
                    lang=self.languages,
                    output_type=pytesseract.Output.DICT
                )
                
                # Extract text and calculate average confidence
                extracted_text = []
                confidences = []
                
                for i, text in enumerate(ocr_data['text']):
                    confidence = int(ocr_data['conf'][i])
                    if text.strip() and confidence > (self.confidence_threshold * 100):
                        extracted_text.append(text)
                        confidences.append(confidence)
                
                # Join text and calculate metrics
                full_text = ' '.join(extracted_text)
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                success = len(full_text) >= self.min_text_length and avg_confidence > (self.confidence_threshold * 100)
                
                return {
                    "text": full_text,
                    "success": success,
                    "confidence": avg_confidence / 100.0,
                    "word_count": len(extracted_text),
                    "source": str(image_path.name)
                }
                
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return {
                "text": "",
                "success": False,
                "error": str(e),
                "confidence": 0.0
            }
    
    def extract_text_from_pdf_images(self, pdf_path: Union[str, Path], 
                                   max_pages: Optional[int] = None) -> Dict[str, Any]:
        """
        Extract text from PDF by converting to images and applying OCR.
        
        Args:
            pdf_path: Path to the PDF file
            max_pages: Maximum number of pages to process (None for all)
            
        Returns:
            Dictionary with extracted text and metadata
        """
        if not self.available:
            return {
                "text": "",
                "success": False,
                "error": "OCR libraries not available",
                "pages_processed": 0
            }
        
        try:
            pdf_path = Path(pdf_path)
            
            # Convert PDF to images
            logger.info(f"Converting PDF to images: {pdf_path.name}")
            
            # Use tempdir for image processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Convert PDF pages to images
                try:
                    images = convert_from_path(
                        str(pdf_path),
                        dpi=300,  # High DPI for better OCR results
                        output_folder=temp_dir,
                        first_page=1,
                        last_page=max_pages,
                        fmt='png',
                        thread_count=4
                    )
                except Exception as e:
                    logger.error(f"Error converting PDF to images: {e}")
                    return {
                        "text": "",
                        "success": False,
                        "error": f"PDF conversion failed: {str(e)}",
                        "pages_processed": 0
                    }
                
                if not images:
                    return {
                        "text": "",
                        "success": False,
                        "error": "No images extracted from PDF",
                        "pages_processed": 0
                    }
                
                # Process each page
                all_text = []
                page_results = []
                successful_pages = 0
                
                for page_num, image in enumerate(images, 1):
                    logger.info(f"Processing page {page_num}/{len(images)}")
                    
                    # Save image temporarily
                    temp_image_path = Path(temp_dir) / f"page_{page_num}.png"
                    image.save(temp_image_path)
                    
                    # Extract text from this page
                    result = self.extract_text_from_image(temp_image_path)
                    
                    if result["success"]:
                        all_text.append(f"\n--- Page {page_num} (OCR) ---\n{result['text']}\n")
                        successful_pages += 1
                    else:
                        all_text.append(f"\n--- Page {page_num} (OCR Failed) ---\n")
                    
                    page_results.append(result)
                
                # Combine results
                combined_text = ''.join(all_text)
                overall_confidence = sum(r.get('confidence', 0) for r in page_results if r.get('success', False))
                if successful_pages > 0:
                    overall_confidence /= successful_pages
                
                return {
                    "text": combined_text,
                    "success": len(combined_text.strip()) >= self.min_text_length,
                    "confidence": overall_confidence,
                    "pages_processed": len(images),
                    "pages_successful": successful_pages,
                    "source": str(pdf_path.name),
                    "method": "OCR"
                }
                
        except Exception as e:
            logger.error(f"Error processing PDF with OCR {pdf_path}: {e}")
            return {
                "text": "",
                "success": False,
                "error": str(e),
                "pages_processed": 0
            }
    
    def extract_text_from_pdf_hybrid(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Hybrid approach: try text extraction first, fallback to OCR if needed.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        if not self.available:
            return {
                "text": "",
                "success": False,
                "error": "OCR libraries not available",
                "method": "none"
            }
        
        try:
            # First try regular text extraction
            import PyPDF2
            
            pdf_path = Path(pdf_path)
            text_extracted = ""
            
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        try:
                            page_text = page.extract_text()
                            if page_text:
                                text_extracted += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                        except Exception:
                            continue
                
                # Check if we got meaningful text
                meaningful_chars = sum(1 for c in text_extracted if c.isalnum())
                text_quality = meaningful_chars / len(text_extracted) if text_extracted else 0
                
                # If we got good quality text, use it
                if text_quality > 0.1 and len(text_extracted.strip()) > self.min_text_length:
                    return {
                        "text": text_extracted,
                        "success": True,
                        "confidence": 1.0,  # High confidence for direct text extraction
                        "method": "text_extraction",
                        "source": str(pdf_path.name)
                    }
                
            except Exception as e:
                logger.warning(f"Text extraction failed for {pdf_path.name}: {e}")
            
            # Fallback to OCR
            logger.info(f"Text extraction insufficient, trying OCR for {pdf_path.name}")
            ocr_result = self.extract_text_from_pdf_images(pdf_path)
            
            # Combine results if we have some text from both methods
            if text_extracted.strip() and ocr_result.get("success"):
                combined_text = f"{text_extracted}\n\n--- OCR Results ---\n{ocr_result['text']}"
                return {
                    "text": combined_text,
                    "success": True,
                    "confidence": ocr_result.get("confidence", 0.5),
                    "method": "hybrid",
                    "source": str(pdf_path.name)
                }
            
            # Return OCR result if it's successful
            if ocr_result.get("success"):
                return ocr_result
            
            # Return text extraction even if low quality, as last resort
            if text_extracted.strip():
                return {
                    "text": text_extracted,
                    "success": True,
                    "confidence": 0.3,  # Low confidence
                    "method": "text_extraction_low_quality",
                    "source": str(pdf_path.name)
                }
            
            # Nothing worked
            return {
                "text": "",
                "success": False,
                "error": "Both text extraction and OCR failed",
                "method": "failed",
                "source": str(pdf_path.name)
            }
            
        except Exception as e:
            logger.error(f"Hybrid processing failed for {pdf_path}: {e}")
            return {
                "text": "",
                "success": False,
                "error": str(e),
                "method": "error"
            }
    
    def get_supported_image_formats(self) -> List[str]:
        """Get list of supported image formats."""
        return ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.gif']
    
    def get_installation_instructions(self) -> str:
        """Get installation instructions for OCR dependencies."""
        return """
OCR Installation Instructions:

1. Install Python packages:
   pip install pytesseract pdf2image Pillow

2. Install Tesseract OCR engine:
   
   Windows:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install the executable
   - Add to PATH or the script will try to find it automatically
   
   macOS (with Homebrew):
   brew install tesseract
   
   Ubuntu/Debian:
   sudo apt-get install tesseract-ocr
   
   Additional language packs (optional):
   - Windows: Install during Tesseract installation
   - macOS: brew install tesseract-lang
   - Ubuntu: sudo apt-get install tesseract-ocr-[language_code]

3. For PDF processing, you may also need poppler-utils:
   
   Windows:
   - Download from: https://poppler.freedesktop.org/
   - Or install via conda: conda install -c conda-forge poppler
   
   macOS:
   brew install poppler
   
   Ubuntu/Debian:
   sudo apt-get install poppler-utils

4. Test the installation:
   python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
"""


# Global OCR processor instance
ocr_processor = OCRProcessor()


def extract_text_with_ocr(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Convenience function to extract text from any supported file.
    
    Args:
        file_path: Path to image or PDF file
        
    Returns:
        Dictionary with extracted text and metadata
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    
    if suffix == '.pdf':
        return ocr_processor.extract_text_from_pdf_hybrid(file_path)
    elif suffix in ocr_processor.get_supported_image_formats():
        return ocr_processor.extract_text_from_image(file_path)
    else:
        return {
            "text": "",
            "success": False,
            "error": f"Unsupported file format: {suffix}",
            "method": "unsupported"
        }


def is_ocr_available() -> bool:
    """Check if OCR functionality is available."""
    return ocr_processor.is_available()


def get_ocr_status() -> Dict[str, Any]:
    """Get detailed OCR availability status."""
    status = {
        "available": ocr_processor.is_available(),
        "supported_formats": []
    }
    
    if status["available"]:
        status["supported_formats"] = ['pdf'] + ocr_processor.get_supported_image_formats()
        try:
            import pytesseract
            version = pytesseract.get_tesseract_version()
            # Convert version to string for JSON serialization
            status["tesseract_version"] = str(version)
        except Exception as e:
            status["tesseract_version"] = f"unknown ({str(e)})"
    else:
        status["error"] = "OCR libraries not available"
        status["installation_instructions"] = ocr_processor.get_installation_instructions()
    
    return status