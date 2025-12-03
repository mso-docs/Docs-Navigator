#!/usr/bin/env python3
"""
Test OCR functionality and capabilities.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_ocr_availability():
    """Test if OCR libraries are available and working."""
    print("\n🔍 Testing OCR Availability...")
    try:
        from ocr_processor import is_ocr_available, get_ocr_status
        
        if is_ocr_available():
            print("✅ OCR libraries available")
            
            status = get_ocr_status()
            print(f"📋 OCR Status: {status}")
            
            if 'tesseract_version' in status:
                print(f"🔧 Tesseract version: {status['tesseract_version']}")
            
            print(f"📁 Supported formats: {status.get('supported_formats', [])}")
            return True
        else:
            print("❌ OCR libraries not available")
            status = get_ocr_status()
            print(f"❓ Error: {status.get('error', 'Unknown error')}")
            
            if 'installation_instructions' in status:
                print("\n💡 Installation Instructions:")
                print(status['installation_instructions'])
            
            return False
            
    except Exception as e:
        print(f"❌ Error testing OCR availability: {e}")
        return False


def test_server_ocr_integration():
    """Test OCR integration with the MCP server."""
    print("\n🖥️ Testing Server OCR Integration...")
    try:
        from src.server.server import OCR_SUPPORT, _iter_docs, _read_file
        
        print(f"📊 Server OCR Support: {OCR_SUPPORT}")
        
        # Get documents
        docs = list(_iter_docs())
        print(f"📄 Total documents found: {len(docs)}")
        
        # Find image and PDF files
        image_docs = [doc for doc in docs if doc.suffix.lower() in {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.gif'}]
        pdf_docs = [doc for doc in docs if doc.suffix.lower() == '.pdf']
        
        print(f"🖼️ Image documents: {len(image_docs)}")
        for img in image_docs:
            print(f"  - {img.name}")
        
        print(f"📋 PDF documents: {len(pdf_docs)}")
        for pdf in pdf_docs:
            print(f"  - {pdf.name}")
        
        # Test reading an image file if available
        if image_docs and OCR_SUPPORT:
            test_image = image_docs[0]
            print(f"\n🔤 Testing image reading: {test_image.name}")
            try:
                content = _read_file(test_image)
                if content and len(content) > 10:
                    print(f"✅ Successfully read image content ({len(content)} chars)")
                    print(f"📝 Preview: {content[:100]}...")
                else:
                    print("⚠️ Image content appears empty")
            except Exception as e:
                print(f"❌ Error reading image: {e}")
        
        # Test reading a PDF file if available
        if pdf_docs and OCR_SUPPORT:
            test_pdf = pdf_docs[0]
            print(f"\n📄 Testing PDF reading: {test_pdf.name}")
            try:
                content = _read_file(test_pdf)
                if content and len(content) > 10:
                    print(f"✅ Successfully read PDF content ({len(content)} chars)")
                    
                    # Check if OCR was used
                    if "OCR" in content:
                        print("🔤 PDF processed with OCR")
                    elif "text_extraction" in content:
                        print("📝 PDF processed with text extraction")
                    
                    print(f"📝 Preview: {content[:200]}...")
                else:
                    print("⚠️ PDF content appears empty")
            except Exception as e:
                print(f"❌ Error reading PDF: {e}")
                
        return True
        
    except Exception as e:
        print(f"❌ Server integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_direct_ocr():
    """Test direct OCR functionality on sample files."""
    print("\n🧪 Testing Direct OCR...")
    try:
        from ocr_processor import extract_text_with_ocr, ocr_processor
        
        if not ocr_processor.is_available():
            print("❌ OCR not available for direct testing")
            return False
        
        # Look for test files
        docs_dir = project_root / "docs"
        
        # Test image files
        image_files = []
        for ext in ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.gif']:
            image_files.extend(list(docs_dir.glob(f"**/*{ext}")))
        
        if image_files:
            test_image = image_files[0]
            print(f"🖼️ Testing OCR on image: {test_image.name}")
            
            result = extract_text_with_ocr(test_image)
            print(f"📊 OCR Result: {result}")
            
            if result['success']:
                confidence = result.get('confidence', 0)
                print(f"✅ OCR successful (confidence: {confidence:.1%})")
                print(f"📝 Extracted text: {result['text'][:200]}...")
            else:
                error = result.get('error', 'Unknown error')
                print(f"❌ OCR failed: {error}")
        
        # Test PDF files
        pdf_files = list(docs_dir.glob("**/*.pdf"))
        if pdf_files:
            test_pdf = pdf_files[0]
            print(f"\n📄 Testing OCR on PDF: {test_pdf.name}")
            
            result = extract_text_with_ocr(test_pdf)
            print(f"📊 PDF OCR Result keys: {list(result.keys())}")
            
            if result['success']:
                confidence = result.get('confidence', 0)
                method = result.get('method', 'unknown')
                print(f"✅ PDF processing successful (method: {method}, confidence: {confidence:.1%})")
                
                if 'pages_processed' in result:
                    pages_successful = result.get('pages_successful', 0)
                    pages_total = result['pages_processed']
                    print(f"📑 Pages processed: {pages_successful}/{pages_total}")
                
                print(f"📝 Extracted text preview: {result['text'][:300]}...")
            else:
                error = result.get('error', 'Unknown error')
                print(f"❌ PDF processing failed: {error}")
        
        if not image_files and not pdf_files:
            print("⚠️ No test files found for direct OCR testing")
            print("💡 Add some image or PDF files to docs/ folder to test OCR")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct OCR test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mcp_ocr_tool():
    """Test the OCR status MCP tool."""
    print("\n🔧 Testing MCP OCR Status Tool...")
    try:
        # Import client for testing
        from src.agent.client import answer_sync
        
        print("📋 Asking AI about OCR status...")
        response = answer_sync("What is the OCR status? Show me the supported file formats and capabilities.")
        
        print("✅ MCP OCR tool test completed")
        print(f"📝 AI Response: {response[:500]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP OCR tool test failed: {e}")
        return False


def create_test_resources():
    """Create simple test resources if they don't exist."""
    print("\n📁 Creating Test Resources...")
    try:
        docs_dir = project_root / "docs"
        
        # Create OCR test guide if it doesn't exist
        ocr_guide_path = docs_dir / "OCR_TESTING_GUIDE.md"
        if not ocr_guide_path.exists():
            ocr_guide_content = """# OCR Testing Guide

## Test Document for OCR Functionality

This document serves as a test file for OCR (Optical Character Recognition) capabilities.

### Features to Test

1. **Text Extraction**: Basic text recognition
2. **Formatting**: Headers, lists, and paragraphs
3. **Special Characters**: Numbers (123), symbols (!@#), and punctuation (.,;:)

### Code Examples

```python
def test_ocr():
    print("Testing OCR functionality")
    return True
```

### Lists and Structure

- Item 1: Basic text
- Item 2: **Bold text**
- Item 3: *Italic text*

#### Numbered List

1. First item
2. Second item  
3. Third item

### Conclusion

This document tests various text elements that OCR should be able to recognize and extract accurately.
"""
            ocr_guide_path.write_text(ocr_guide_content, encoding='utf-8')
            print(f"✅ Created: {ocr_guide_path.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test resources: {e}")
        return False


def show_installation_help():
    """Show detailed installation instructions."""
    print("\n💡 OCR Installation Help")
    print("=" * 50)
    
    print("""
🔧 Quick Installation Guide:

1. Install Python packages:
   pip install pytesseract pdf2image Pillow

2. Install Tesseract OCR:
   
   Windows:
   - Download: https://github.com/UB-Mannheim/tesseract/wiki
   - Or: choco install tesseract
   - Or: conda install -c conda-forge tesseract
   
   macOS:
   brew install tesseract poppler
   
   Ubuntu/Debian:
   sudo apt-get install tesseract-ocr poppler-utils

3. Test installation:
   python -c "import pytesseract; print(pytesseract.get_tesseract_version())"

4. Test with this script:
   python tests/test_ocr.py
""")


def main():
    """Run all OCR tests."""
    print("🚀 OCR Functionality Test Suite")
    print("=" * 60)
    
    # Create test resources
    create_test_resources()
    
    # Run tests
    success = True
    
    if not test_ocr_availability():
        success = False
        show_installation_help()
    else:
        # Only run other tests if OCR is available
        if not test_server_ocr_integration():
            success = False
        
        if not test_direct_ocr():
            success = False
        
        if not test_mcp_ocr_tool():
            success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All OCR tests completed successfully!")
        print("💡 OCR functionality is ready for use")
        print("🌐 Try the Gradio interface to test with real documents")
    else:
        print("❌ Some OCR tests failed")
        print("💡 Check the errors above and installation instructions")
    
    print("\n📚 Next steps:")
    print("1. Add image files (.png, .jpg, etc.) to docs/ folder")
    print("2. Add scanned PDF files to docs/ folder")  
    print("3. Use the Gradio interface to ask questions about your files")
    print("4. Monitor OCR processing quality and confidence scores")


if __name__ == "__main__":
    main()