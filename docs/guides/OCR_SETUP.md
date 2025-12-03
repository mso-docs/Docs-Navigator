# OCR Setup Guide for Docs Navigator

This guide will help you set up OCR (Optical Character Recognition) capabilities for the Docs Navigator project.

## Current Status

✅ **Python Dependencies**: Installed and working
- `pytesseract>=0.3.13` 
- `pdf2image>=1.17.0`
- `pillow>=11.3.0`

❌ **Tesseract OCR Engine**: Not installed
- Required for actual text extraction from images and scanned PDFs

## Quick Setup

### Option 1: Automatic Installation (Windows)

Run the provided batch script:
```batch
install_tesseract.bat
```

### Option 2: Manual Installation

#### Windows
1. **Download Tesseract:**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest Windows installer (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)

2. **Install Tesseract:**
   - Run the installer as administrator
   - **Important**: Check "Add to PATH" option during installation
   - Or install to `C:\Program Files\Tesseract-OCR\`

3. **Verify Installation:**
   ```bash
   tesseract --version
   ```

#### Alternative Windows Methods
```bash
# Using Chocolatey
choco install tesseract

# Using Scoop
scoop install tesseract

# Using Conda
conda install -c conda-forge tesseract
```

#### macOS
```bash
# Using Homebrew (recommended)
brew install tesseract poppler

# Using MacPorts
sudo port install tesseract3
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils

# For additional languages
sudo apt-get install tesseract-ocr-fra  # French
sudo apt-get install tesseract-ocr-deu  # German
sudo apt-get install tesseract-ocr-spa  # Spanish
```

#### Linux (CentOS/RHEL/Fedora)
```bash
sudo dnf install tesseract poppler-utils
# or
sudo yum install tesseract poppler-utils
```

## Testing Your Setup

### 1. Test Tesseract Installation
```bash
tesseract --version
```

### 2. Test Python Integration
```bash
cd c:/Code/test-mcp/docs-navigator
uv run python -c "import pytesseract; print('Tesseract version:', pytesseract.get_tesseract_version())"
```

### 3. Run Full OCR Test Suite
```bash
uv run python tests/test_ocr.py
```

### 4. Test with Sample Documents
```bash
# Start the Gradio interface
uv run python app_gradio.py

# Then ask questions like:
# - "What OCR capabilities are available?"
# - "Can you extract text from image files?"
# - "Process the PDFs in the docs folder"
```

## What OCR Enables

Once properly set up, OCR will allow you to:

### Document Types Supported
- **Image files**: `.png`, `.jpg`, `.jpeg`, `.tiff`, `.tif`, `.bmp`, `.gif`
- **Scanned PDFs**: PDFs that contain images of text rather than actual text
- **Mixed PDFs**: Documents with both text and scanned pages (hybrid processing)

### Features Available
1. **Text Extraction**: Extract text from images and scanned documents
2. **Confidence Scoring**: Get quality metrics for OCR results
3. **Multi-language Support**: Process documents in different languages
4. **Hybrid Processing**: Automatically choose between text extraction and OCR based on content quality
5. **Batch Processing**: Process multiple documents at once

### Quality Metrics
- **Confidence scores**: 0-100% accuracy estimates
- **Success/failure status**: Clear indication if OCR worked
- **Processing method**: Shows whether text extraction or OCR was used
- **Page-by-page results**: For PDFs, see results for each page

## Configuration Options

You can customize OCR behavior by modifying the `OCRProcessor` settings in `ocr_processor.py`:

```python
ocr_processor = OCRProcessor(
    confidence_threshold=0.3,  # Minimum confidence (0.0-1.0)
    min_text_length=10,       # Minimum text length for success
    languages='eng'           # Language codes (eng, fra, deu, etc.)
)
```

### Supported Languages
To use additional languages, install language packs and modify the `languages` parameter:

```python
languages='eng+fra+deu'  # English + French + German
```

## Troubleshooting

### Common Issues

1. **"tesseract is not installed or it's not in your PATH"**
   - Install Tesseract OCR engine
   - Make sure it's added to your system PATH
   - Restart your terminal/IDE after installation

2. **"No module named pytesseract"**
   - Run: `uv add pytesseract pdf2image Pillow`

3. **PDF processing fails**
   - Install poppler-utils for PDF to image conversion
   - Windows: Download from https://poppler.freedesktop.org/
   - macOS: `brew install poppler`
   - Linux: `sudo apt-get install poppler-utils`

4. **Low confidence scores**
   - Increase DPI settings for better quality
   - Preprocess images (contrast, brightness)
   - Try different language models

5. **Slow processing**
   - Reduce DPI for faster processing
   - Limit pages processed for large PDFs
   - Use text extraction for text-based PDFs

### Getting Help

1. **Check OCR status**: Ask the AI "What is the current OCR status?"
2. **Test files**: Add sample images/PDFs to the `docs/` folder
3. **Run diagnostics**: `uv run python tests/test_ocr.py`
4. **View logs**: Check console output for detailed error messages

## Performance Tips

- **For large PDFs**: Text extraction is faster than OCR when possible
- **For scanned documents**: OCR is necessary but may take longer
- **For mixed documents**: Hybrid mode automatically chooses the best method
- **For batch processing**: Process multiple small files rather than one large file

## Security Notes

- OCR processing happens locally on your machine
- No document content is sent to external services
- All processing uses the local Tesseract installation
- Images and PDFs are processed in temporary directories that are cleaned up automatically

---

## Next Steps

Once OCR is working:

1. **Add your documents**: Copy image files and PDFs to the `docs/` folder
2. **Start the interface**: `uv run python app_gradio.py`
3. **Ask questions**: "Extract text from my scanned documents"
4. **Monitor quality**: Check confidence scores and processing methods
5. **Optimize settings**: Adjust parameters based on your document types

For more help, run the test suite or ask the AI assistant about specific OCR capabilities!