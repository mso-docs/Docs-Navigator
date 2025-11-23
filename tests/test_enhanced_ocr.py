#!/usr/bin/env python3
"""
Quick OCR Test Script

This script tests the enhanced OCR functionality with multiple backends.
"""

import sys
from pathlib import Path

def test_enhanced_ocr():
    """Test the enhanced OCR processor."""
    
    print("🧪 Testing Enhanced OCR Processor")
    print("=" * 50)
    
    try:
        # Import enhanced OCR
        from enhanced_ocr_processor import get_ocr_status, enhanced_ocr_processor, extract_text_with_ocr
        
        # Get status
        status = get_ocr_status()
        
        print("📊 OCR Status:")
        print(f"  ✅ Available: {status['available']}")
        
        if status['available']:
            print(f"  🔧 Available backends: {status['available_backends']}")
            if 'active_backend' in status:
                print(f"  🎯 Active backend: {status['active_backend']}")
            print(f"  📄 Supported formats: {status['supported_formats']}")
            
            # Test with a simple image if available
            docs_dir = Path(__file__).parent / "docs"
            test_files = list(docs_dir.glob("*.png")) + list(docs_dir.glob("*.jpg")) + list(docs_dir.glob("*.jpeg"))
            
            if test_files:
                test_file = test_files[0]
                print(f"\n🖼️ Testing with: {test_file.name}")
                
                result = extract_text_with_ocr(test_file)
                print(f"  📝 Success: {result['success']}")
                if result['success']:
                    print(f"  🎯 Confidence: {result.get('confidence', 'N/A')}")
                    print(f"  🔧 Backend: {result.get('backend', 'Unknown')}")
                    
                    text_preview = result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
                    print(f"  📄 Text preview: {text_preview}")
                else:
                    print(f"  ❌ Error: {result.get('error', 'Unknown error')}")
            else:
                print("\n⚠️ No test images found in docs/ folder")
                print("💡 You can add .png, .jpg, or .jpeg files to test OCR")
                
        else:
            print(f"  ❌ Error: {status.get('error', 'Unknown error')}")
            if 'installation_help' in status:
                print("\n📋 Installation Help:")
                print(status['installation_help'])
        
        return status['available']
        
    except ImportError as e:
        print(f"❌ Enhanced OCR not available: {e}")
        print("💡 Trying fallback to original OCR processor...")
        
        try:
            from ocr_processor import get_ocr_status
            
            status = get_ocr_status()
            print(f"\n📊 Original OCR Status:")
            print(f"  Available: {status['available']}")
            
            if status['available']:
                print(f"  Supported formats: {status['supported_formats']}")
                if 'tesseract_version' in status:
                    print(f"  Tesseract version: {status['tesseract_version']}")
            else:
                print(f"  Error: {status.get('error', 'Unknown error')}")
            
            return status['available']
            
        except ImportError:
            print("❌ No OCR processors available")
            return False
    
    except Exception as e:
        print(f"❌ Error testing OCR: {e}")
        return False


def show_installation_recommendations():
    """Show OCR installation recommendations."""
    
    print("\n💡 OCR Installation Recommendations")
    print("=" * 50)
    
    print("""
🎯 RECOMMENDED: Pure Python Setup (No external dependencies)
   pip install easyocr transformers torch
   
   ✅ Pros: Works immediately, no external installation needed
   ❌ Cons: Larger download (model files), slower on first run

🚀 PERFORMANCE: Mixed Setup (Best of both worlds)  
   pip install pytesseract easyocr pdf2image Pillow
   
   ✅ Pros: Fast OCR with Tesseract, EasyOCR backup if Tesseract fails
   ❌ Cons: Need to install Tesseract separately

🔧 COMPLETE: All Backends
   pip install pytesseract easyocr transformers torch pdf2image Pillow
   
   ✅ Pros: Maximum compatibility and options
   ❌ Cons: Largest installation

📋 To install, run:
   python setup_ocr.py
   
   Or manually:
   pip install -r requirements.txt
""")


def main():
    """Main test function."""
    
    if test_enhanced_ocr():
        print("\n🎉 OCR testing completed successfully!")
        print("\n📚 Next steps:")
        print("1. Add image files (.png, .jpg, etc.) to docs/ folder")
        print("2. Add scanned PDF files to docs/ folder") 
        print("3. Run: python app_gradio.py to start the interface")
        print("4. Ask OCR-related questions in the Gradio interface")
    else:
        print("\n❌ OCR not fully functional")
        show_installation_recommendations()


if __name__ == "__main__":
    main()