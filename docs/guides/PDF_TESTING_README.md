# PDF & OCR Support Testing

## How to Test PDF & Image Processing

1. **Add files** to the `docs/` folder:
   - PDF documents (text-based or scanned/image-based)
   - Image files (`.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.gif`)

2. **Run test scripts**:
   - `python tests/test_pdf_support.py` - Test PDF functionality
   - `python tests/test_ocr.py` - Test OCR capabilities (new)

3. **Use the Gradio interface** to ask questions about your content

## Supported Features

### PDF Processing
- **Text-based PDFs**: Direct text extraction (fastest)
- **Image-based/Scanned PDFs**: OCR text extraction using Tesseract
- **Hybrid PDFs**: Automatic detection and appropriate processing
- **Page-by-page processing**: Maintains page structure and references

### Image Processing
- **Direct OCR**: Extract text from standalone image files
- **Multiple formats**: PNG, JPEG, TIFF, BMP, GIF support
- **Confidence scoring**: Quality assessment of OCR results
- **Preprocessing**: Automatic image optimization for better OCR

### AI Integration
- Full-text search across all extracted content
- AI-powered Q&A over PDF and image documents
- Section analysis and intelligent summarization
- Content integrated seamlessly with other documentation

## OCR Setup Requirements

### Install Tesseract OCR Engine

**Windows:**
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use chocolatey:
choco install tesseract

# Or use conda:
conda install -c conda-forge tesseract
```

**macOS:**
```bash
brew install tesseract
brew install poppler  # For PDF image conversion
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install poppler-utils
```

### Install Python Dependencies
```bash
pip install pytesseract pdf2image Pillow
```

### Test OCR Installation
```python
import pytesseract
print(pytesseract.get_tesseract_version())
```

## Example Questions to Try

### PDF Questions
- "What topics are covered in the PDF documents?"
- "Summarize the main points from the scanned PDF"
- "Search for [specific term] in all documents including PDFs"
- "Compare information between the markdown docs and PDF files"

### Image Questions
- "What text content is in the image files?"
- "Extract the main headings from the screenshot"
- "What code examples are shown in the images?"

### General Questions
- "Which documents contain information about [topic]?"
- "Get OCR status and supported file types"
- "Show me all documents that were processed using OCR"

## File Processing Methods

The system automatically selects the best processing method:

1. **Text Extraction** (PDF): Fast, high accuracy for text-based PDFs
2. **OCR Processing** (PDF): Slower, for scanned/image-based PDFs  
3. **Hybrid Processing** (PDF): Tries text extraction first, falls back to OCR
4. **Direct OCR** (Images): For standalone image files

## Quality and Performance

### OCR Quality Factors
- **Image resolution**: Higher DPI = better results (300+ DPI recommended)
- **Text clarity**: Clean, high-contrast text works best
- **Language**: English optimized (additional language packs available)
- **Layout**: Simple layouts process more accurately than complex ones

### Performance Notes
- **Text PDFs**: Process in milliseconds
- **OCR PDFs**: Process in seconds (depends on page count and image quality)
- **Large files**: Processing time scales with file size and page count
- **Confidence scoring**: Provides quality assessment of extracted text

## Troubleshooting

### Common Issues

1. **"Tesseract not found"**: Install Tesseract OCR engine (see setup above)
2. **Poor OCR quality**: Try higher resolution images or cleaner scans
3. **Empty OCR results**: Check image format support and file integrity
4. **Slow processing**: Normal for image-based content; consider file size

### Debug OCR Status
Use the AI interface to ask: "What is the OCR status?" to get detailed information about:
- OCR availability and version
- Supported file formats
- Document processing statistics
- Any configuration issues

## Notes

- **Confidence scoring**: OCR results include confidence percentages
- **Page preservation**: Page numbers and structure are maintained
- **Fallback processing**: If OCR fails, basic text extraction is attempted
- **Format detection**: Automatic selection of best processing method
- **Language support**: Additional Tesseract language packs can be installed
