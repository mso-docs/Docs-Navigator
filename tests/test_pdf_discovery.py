#!/usr/bin/env python3
"""
Test that newly added PDFs are automatically discovered.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def show_current_pdfs():
    """Show all currently detected PDF files."""
    print("🔍 Scanning for PDF files...")
    
    try:
        from src.server.server import _iter_docs
        
        # Get all documents
        all_docs = list(_iter_docs())
        pdf_docs = [doc for doc in all_docs if doc.suffix.lower() == '.pdf']
        
        print(f"📊 Total documents found: {len(all_docs)}")
        print(f"📄 PDF documents found: {len(pdf_docs)}")
        
        if pdf_docs:
            print("\n📋 Current PDF files:")
            for i, pdf_doc in enumerate(pdf_docs, 1):
                rel_path = pdf_doc.relative_to(project_root / "docs")
                size_kb = pdf_doc.stat().st_size // 1024
                print(f"  {i}. {rel_path} ({size_kb} KB)")
        else:
            print("⚠️  No PDF files found in docs/ folder")
            
        return pdf_docs
        
    except Exception as e:
        print(f"❌ Error scanning for PDFs: {e}")
        return []

def test_pdf_reading(pdf_files):
    """Test reading content from each PDF."""
    if not pdf_files:
        print("\n⏭️  Skipping PDF reading test - no PDFs found")
        return
        
    print(f"\n📖 Testing PDF content extraction...")
    
    try:
        from src.server.server import _read_file
        
        for pdf_file in pdf_files[:3]:  # Test first 3 PDFs only
            print(f"\n📄 Reading: {pdf_file.name}")
            content = _read_file(pdf_file)
            
            if content and len(content) > 10:
                print(f"  ✅ Successfully extracted {len(content)} characters")
                # Show first meaningful line (skip page markers)
                lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('---')]
                if lines:
                    print(f"  📝 Preview: {lines[0][:80]}...")
            else:
                print(f"  ⚠️  No content extracted or file might be empty/corrupted")
                
    except Exception as e:
        print(f"❌ Error reading PDFs: {e}")

def show_instructions():
    """Show instructions for adding new PDFs."""
    print(f"\n💡 To add more PDFs:")
    print(f"1. Copy any PDF file to the docs/ folder:")
    print(f"   cp your-document.pdf {project_root}/docs/")
    print(f"2. Or create subfolders:")
    print(f"   mkdir {project_root}/docs/reports")
    print(f"   cp report.pdf {project_root}/docs/reports/")
    print(f"3. Re-run this script to see them detected automatically")
    print(f"4. Or use the Gradio interface - PDFs are available immediately!")

def main():
    """Show current PDF support status."""
    print("📂 PDF Auto-Discovery Test")
    print("=" * 40)
    
    # Show current PDFs
    pdf_files = show_current_pdfs()
    
    # Test reading them
    test_pdf_reading(pdf_files)
    
    # Show instructions
    show_instructions()
    
    print("\n" + "=" * 40)
    print("🎯 Summary: Any PDF files you add to docs/ (or subfolders)")
    print("   will be automatically discovered and available for AI queries!")

if __name__ == "__main__":
    main()