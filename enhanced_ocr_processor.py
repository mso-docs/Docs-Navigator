"""
Enhanced OCR (Optical Character Recognition) Module with Multiple Backends

This module provides OCR capabilities using multiple backends:
1. Tesseract OCR (requires external installation)
2. EasyOCR (pure Python, no external dependencies)
3. Transformers-based OCR (pure Python, uses Hugging Face models)

Automatically falls back to available backends if preferred ones are not available.
"""
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import logging

# Check if heavy models should be disabled
DISABLE_HEAVY_MODELS = os.getenv('DISABLE_TROCR', '').lower() in ('1', 'true', 'yes')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if DISABLE_HEAVY_MODELS:
    logger.info("Heavy OCR models disabled via environment variable")


class OCRBackend:
    """Base class for OCR backends."""
    
    def __init__(self, name: str):
        self.name = name
        self.available = False
    
    def is_available(self) -> bool:
        return self.available
    
    def extract_text_from_image(self, image) -> Dict[str, Any]:
        raise NotImplementedError()


class TesseractBackend(OCRBackend):
    """Tesseract OCR backend (requires external Tesseract installation)."""
    
    def __init__(self, languages: str = 'eng'):
        super().__init__("Tesseract")
        self.languages = languages
        self._initialize()
    
    def _initialize(self):
        try:
            import pytesseract
            from PIL import Image
            
            # Try to detect Tesseract installation
            try:
                pytesseract.get_tesseract_version()
                logger.info("Tesseract OCR engine detected and ready")
                self.available = True
                self.pytesseract = pytesseract
                return
            except Exception:
                logger.warning("Tesseract not found in PATH, trying common locations...")
                
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
                            pytesseract.get_tesseract_version()
                            logger.info(f"Found and configured Tesseract at: {path}")
                            self.available = True
                            self.pytesseract = pytesseract
                            return
                        except Exception:
                            continue
                
                logger.warning("Tesseract OCR not found")
                
        except ImportError:
            logger.warning("pytesseract not available")
    
    def extract_text_from_image(self, image) -> Dict[str, Any]:
        if not self.available:
            return {"text": "", "success": False, "error": "Tesseract not available"}
        
        try:
            # Get text with confidence scores
            ocr_data = self.pytesseract.image_to_data(
                image, 
                lang=self.languages,
                output_type=self.pytesseract.Output.DICT
            )
            
            # Extract text and calculate average confidence
            extracted_text = []
            confidences = []
            
            for i, text in enumerate(ocr_data['text']):
                confidence = int(ocr_data['conf'][i])
                if text.strip() and confidence > 30:  # Filter low confidence
                    extracted_text.append(text)
                    confidences.append(confidence)
            
            full_text = ' '.join(extracted_text)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                "text": full_text,
                "success": len(full_text.strip()) > 0,
                "confidence": avg_confidence / 100.0,
                "backend": self.name
            }
            
        except Exception as e:
            return {"text": "", "success": False, "error": str(e), "backend": self.name}


class EasyOCRBackend(OCRBackend):
    """EasyOCR backend (pure Python, no external dependencies)."""
    
    def __init__(self, languages: List[str] = ['en']):
        super().__init__("EasyOCR")
        self.languages = languages
        self.reader = None
        self._initialize()
    
    def _initialize(self):
        try:
            import easyocr
            import numpy as np
            from PIL import Image
            
            logger.info("Initializing EasyOCR (this may take a moment for first run)...")
            self.reader = easyocr.Reader(self.languages, gpu=False)  # CPU only for compatibility
            self.available = True
            logger.info("EasyOCR initialized successfully")
            
        except ImportError:
            logger.warning("EasyOCR not available")
        except Exception as e:
            logger.warning(f"EasyOCR initialization failed: {e}")
    
    def extract_text_from_image(self, image) -> Dict[str, Any]:
        if not self.available or self.reader is None:
            return {"text": "", "success": False, "error": "EasyOCR not available"}
        
        try:
            import numpy as np
            from PIL import Image
            
            # Convert PIL image to numpy array
            if hasattr(image, 'convert'):
                image_array = np.array(image.convert('RGB'))
            else:
                image_array = np.array(image)
            
            # Extract text
            results = self.reader.readtext(image_array, detail=1)
            
            # Process results
            extracted_text = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                if text.strip() and confidence > 0.3:  # Filter low confidence
                    extracted_text.append(text)
                    confidences.append(confidence)
            
            full_text = ' '.join(extracted_text)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                "text": full_text,
                "success": len(full_text.strip()) > 0,
                "confidence": avg_confidence,
                "backend": self.name
            }
            
        except Exception as e:
            return {"text": "", "success": False, "error": str(e), "backend": self.name}


class TransformersOCRBackend(OCRBackend):
    """Transformers-based OCR backend using TrOCR (pure Python)."""
    
    def __init__(self):
        super().__init__("TrOCR")
        self.processor = None
        self.model = None
        self._initialize()
    
    def _initialize(self):
        # Skip TrOCR if heavy models are disabled
        if DISABLE_HEAVY_MODELS:
            logger.info("TrOCR backend skipped (heavy models disabled)")
            return
            
        try:
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            from PIL import Image
            
            logger.info("Loading TrOCR model (this may take a moment)...")
            
            # Use Microsoft's TrOCR model
            model_name = "microsoft/trocr-base-printed"
            self.processor = TrOCRProcessor.from_pretrained(model_name)
            self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
            
            self.available = True
            logger.info("TrOCR model loaded successfully")
            
        except ImportError:
            logger.warning("Transformers not available for TrOCR")
        except Exception as e:
            logger.warning(f"TrOCR initialization failed: {e}")
    
    def extract_text_from_image(self, image) -> Dict[str, Any]:
        if not self.available:
            return {"text": "", "success": False, "error": "TrOCR not available"}
        
        try:
            from PIL import Image
            import torch
            
            # Ensure image is in RGB
            if hasattr(image, 'convert'):
                image = image.convert('RGB')
            
            # Process image
            pixel_values = self.processor(images=image, return_tensors="pt").pixel_values
            
            # Generate text
            generated_ids = self.model.generate(pixel_values)
            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            return {
                "text": generated_text,
                "success": len(generated_text.strip()) > 0,
                "confidence": 0.8,  # TrOCR doesn't provide confidence, assume decent quality
                "backend": self.name
            }
            
        except Exception as e:
            return {"text": "", "success": False, "error": str(e), "backend": self.name}


class EnhancedOCRProcessor:
    """Enhanced OCR processor with multiple backends and automatic fallback."""
    
    def __init__(self, 
                 confidence_threshold: float = 0.3,
                 min_text_length: int = 10,
                 preferred_backend: str = "auto"):
        """
        Initialize enhanced OCR processor.
        
        Args:
            confidence_threshold: Minimum confidence for text recognition (0.0-1.0)
            min_text_length: Minimum text length to consider extraction successful
            preferred_backend: Preferred backend ("tesseract", "easyocr", "trocr", "auto")
        """
        self.confidence_threshold = confidence_threshold
        self.min_text_length = min_text_length
        self.preferred_backend = preferred_backend
        
        # Initialize backends
        self.backends = {
            "tesseract": TesseractBackend(),
            "easyocr": EasyOCRBackend(),
        }
        
        # Only include TrOCR if heavy models are not disabled
        if not DISABLE_HEAVY_MODELS:
            self.backends["trocr"] = TransformersOCRBackend()
        
        # Find available backends
        self.available_backends = [name for name, backend in self.backends.items() if backend.is_available()]
        
        if self.available_backends:
            logger.info(f"Available OCR backends: {', '.join(self.available_backends)}")
        else:
            logger.warning("No OCR backends available!")
    
    def is_available(self) -> bool:
        """Check if any OCR functionality is available."""
        return len(self.available_backends) > 0
    
    def get_best_backend(self) -> Optional[OCRBackend]:
        """Get the best available backend based on preferences."""
        if not self.available_backends:
            return None
        
        # If specific backend requested and available
        if self.preferred_backend in self.available_backends:
            return self.backends[self.preferred_backend]
        
        # Auto selection priority: Tesseract > EasyOCR > TrOCR
        priority_order = ["tesseract", "easyocr", "trocr"]
        
        for backend_name in priority_order:
            if backend_name in self.available_backends:
                return self.backends[backend_name]
        
        # Fallback to first available
        return self.backends[self.available_backends[0]]
    
    def extract_text_from_image(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """Extract text from a single image file."""
        backend = self.get_best_backend()
        if not backend:
            return {
                "text": "",
                "success": False,
                "error": "No OCR backends available",
                "confidence": 0.0
            }
        
        try:
            from PIL import Image
            
            image_path = Path(image_path)
            
            # Open and preprocess image
            with Image.open(image_path) as image:
                # Convert to RGB if needed
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Extract text using selected backend
                result = backend.extract_text_from_image(image)
                
                # Add metadata
                result.update({
                    "source": str(image_path.name),
                    "word_count": len(result.get("text", "").split())
                })
                
                return result
                
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
        """Extract text from PDF by converting to images and applying OCR."""
        backend = self.get_best_backend()
        if not backend:
            return {
                "text": "",
                "success": False,
                "error": "No OCR backends available",
                "pages_processed": 0
            }
        
        try:
            from pdf2image import convert_from_path
            
            pdf_path = Path(pdf_path)
            
            # Convert PDF to images
            logger.info(f"Converting PDF to images: {pdf_path.name}")
            
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    images = convert_from_path(
                        str(pdf_path),
                        dpi=300,
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
                successful_pages = 0
                total_confidence = 0
                
                for page_num, image in enumerate(images, 1):
                    logger.info(f"Processing page {page_num}/{len(images)} with {backend.name}")
                    
                    # Extract text from this page
                    result = backend.extract_text_from_image(image)
                    
                    if result.get("success", False):
                        all_text.append(f"\n--- Page {page_num} (OCR: {backend.name}) ---\n{result['text']}\n")
                        successful_pages += 1
                        total_confidence += result.get("confidence", 0)
                    else:
                        all_text.append(f"\n--- Page {page_num} (OCR Failed: {backend.name}) ---\n")
                
                # Combine results
                combined_text = ''.join(all_text)
                avg_confidence = total_confidence / successful_pages if successful_pages > 0 else 0
                
                return {
                    "text": combined_text,
                    "success": len(combined_text.strip()) >= self.min_text_length,
                    "confidence": avg_confidence,
                    "pages_processed": len(images),
                    "pages_successful": successful_pages,
                    "source": str(pdf_path.name),
                    "method": f"OCR ({backend.name})",
                    "backend": backend.name
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
        """Hybrid approach: try text extraction first, fallback to OCR if needed."""
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
                        "confidence": 1.0,
                        "method": "text_extraction",
                        "source": str(pdf_path.name)
                    }
                
            except Exception as e:
                logger.warning(f"Text extraction failed for {pdf_path.name}: {e}")
            
            # Fallback to OCR
            backend = self.get_best_backend()
            if backend:
                logger.info(f"Text extraction insufficient, trying OCR with {backend.name} for {pdf_path.name}")
                return self.extract_text_from_pdf_images(pdf_path)
            else:
                return {
                    "text": text_extracted if text_extracted.strip() else "",
                    "success": bool(text_extracted.strip()),
                    "confidence": 0.3 if text_extracted.strip() else 0,
                    "method": "text_extraction_only",
                    "error": "No OCR backends available for fallback"
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
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed OCR status information."""
        status = {
            "available": self.is_available(),
            "available_backends": self.available_backends,
            "preferred_backend": self.preferred_backend,
            "supported_formats": []
        }
        
        if status["available"]:
            status["supported_formats"] = ['pdf'] + self.get_supported_image_formats()
            best_backend = self.get_best_backend()
            if best_backend:
                status["active_backend"] = best_backend.name
        else:
            status["error"] = "No OCR backends available"
            status["installation_help"] = self.get_installation_help()
        
        return status
    
    def get_installation_help(self) -> str:
        """Get installation help for OCR dependencies."""
        return """
Enhanced OCR Installation Options:

=== Option 1: Pure Python (Recommended for easy setup) ===
pip install easyocr transformers torch

This installs EasyOCR and TrOCR which work without external dependencies.
They may be slower on first run due to model downloads.

=== Option 2: Tesseract (Faster, requires external installation) ===
1. Install Python packages:
   pip install pytesseract pdf2image Pillow

2. Install Tesseract OCR engine:
   Windows: https://github.com/UB-Mannheim/tesseract/wiki
   macOS: brew install tesseract
   Ubuntu: sudo apt-get install tesseract-ocr

=== Option 3: Install Everything ===
pip install pytesseract pdf2image Pillow easyocr transformers torch

This gives you all backends for maximum compatibility and performance options.

The system will automatically use the best available backend.
"""


# Global enhanced OCR processor instance
enhanced_ocr_processor = EnhancedOCRProcessor()


def extract_text_with_ocr(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Convenience function to extract text from any supported file using enhanced OCR.
    
    Args:
        file_path: Path to image or PDF file
        
    Returns:
        Dictionary with extracted text and metadata
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    
    if suffix == '.pdf':
        return enhanced_ocr_processor.extract_text_from_pdf_hybrid(file_path)
    elif suffix in enhanced_ocr_processor.get_supported_image_formats():
        return enhanced_ocr_processor.extract_text_from_image(file_path)
    else:
        return {
            "text": "",
            "success": False,
            "error": f"Unsupported file format: {suffix}",
            "method": "unsupported"
        }


def is_ocr_available() -> bool:
    """Check if any OCR functionality is available."""
    return enhanced_ocr_processor.is_available()


def get_ocr_status() -> Dict[str, Any]:
    """Get detailed OCR availability status."""
    return enhanced_ocr_processor.get_status()


def switch_backend(backend_name: str) -> bool:
    """
    Switch to a specific OCR backend.
    
    Args:
        backend_name: Name of backend ("tesseract", "easyocr", "trocr", "auto")
        
    Returns:
        True if switch was successful
    """
    global enhanced_ocr_processor
    
    if backend_name == "auto" or backend_name in enhanced_ocr_processor.available_backends:
        enhanced_ocr_processor.preferred_backend = backend_name
        logger.info(f"Switched to OCR backend: {backend_name}")
        return True
    else:
        logger.error(f"Backend '{backend_name}' not available. Available: {enhanced_ocr_processor.available_backends}")
        return False