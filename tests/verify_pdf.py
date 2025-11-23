#!/usr/bin/env python3
"""
Quick verification that PDF support is working correctly.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_pdf_import():
    """Test that PDF library is imported correctly."""
    print("Testing PDF import...")
    try:
        import PyPDF2
        print("✅ PyPDF2 imported successfully")
        return True
    except ImportError as e:
        print(f"❌ PyPDF2 import failed: {e}")
        return False

def test_server_pdf_support():
    """Test that the server recognizes PDF files."""
    print("\nTesting server PDF recognition...")
    try:
        from src.server.server import _iter_docs, PDF_SUPPORT
        
        print(f"PDF Support enabled: {PDF_SUPPORT}")
        
        # Get list of docs
        docs = list(_iter_docs())
        pdf_docs = [doc for doc in docs if doc.suffix.lower() == '.pdf']
        
        print(f"Total documents found: {len(docs)}")
        print(f"PDF documents found: {len(pdf_docs)}")
        
        for pdf_doc in pdf_docs:
            print(f"  📄 {pdf_doc.name}")
            
        return len(pdf_docs) > 0
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False

def test_pdf_reading():
    """Test that we can read a PDF file."""
    print("\nTesting PDF reading...")
    try:
        from src.server.server import _iter_docs, _read_file
        
        docs = list(_iter_docs())
        pdf_docs = [doc for doc in docs if doc.suffix.lower() == '.pdf']
        
        if not pdf_docs:
            print("⚠️  No PDF files to test reading")
            return True
            
        # Try to read the first PDF
        pdf_file = pdf_docs[0]
        print(f"Reading: {pdf_file.name}")
        
        content = _read_file(pdf_file)
        
        if content and len(content) > 10:
            print(f"✅ Successfully read PDF content ({len(content)} characters)")
            print("First 100 characters:", content[:100])
            return True
        else:
            print("❌ PDF content seems empty or invalid")
            return False
            
    except Exception as e:
        print(f"❌ PDF reading test failed: {e}")
        return False

def main():
    """Run basic PDF support verification."""
    print("🔍 Quick PDF Support Verification")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_pdf_import():
        success = False
    
    # Test server support
    if not test_server_pdf_support():
        success = False
    
    # Test reading
    if not test_pdf_reading():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 PDF support verification PASSED!")
        print("💡 You can now:")
        print("   - Add PDF files to the docs/ folder")
        print("   - Use the Gradio interface at http://127.0.0.1:7863")
        print("   - Ask questions about PDF content")
    else:
        print("❌ PDF support verification FAILED!")
        print("Please check the error messages above")

if __name__ == "__main__":
    main()