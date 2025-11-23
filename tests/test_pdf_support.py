#!/usr/bin/env python3
"""
Test PDF support functionality for the docs navigator.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent.client import answer_sync

def create_test_pdf():
    """Create a simple test PDF for testing (if none exists)."""
    docs_dir = project_root / "docs"
    test_pdf_path = docs_dir / "test_document.pdf"
    
    if test_pdf_path.exists():
        print(f"Test PDF already exists: {test_pdf_path}")
        return test_pdf_path
    
    # Create a simple text file that explains how to test with PDFs
    readme_path = docs_dir / "PDF_TESTING_README.md"
    readme_content = """# PDF Support Testing

## How to Test PDF Functionality

1. **Add a PDF file** to the `docs/` folder
2. **Run the test script**: `python tests/test_pdf_support.py`
3. **Use the Gradio interface** to ask questions about your PDF content

## Supported PDF Features

- Text extraction from all pages
- Full-text search across PDF content  
- AI-powered Q&A over PDF documents
- Section analysis and summarization
- PDF content integrated with other docs

## Example Questions to Try

- "What topics are covered in the PDF?"
- "Summarize the main points from the PDF"
- "Search for [specific term] in all documents"

## Notes

- PDFs with images/scanned text require OCR (not yet implemented)
- Complex layouts may have formatting issues
- Page numbers are preserved for reference
"""
    
    readme_path.write_text(readme_content, encoding='utf-8')
    print(f"Created PDF testing guide: {readme_path}")
    return None

def test_pdf_listing():
    """Test that PDF files are included in document listing."""
    print("🔍 Testing PDF file discovery...")
    
    try:
        # Test with a general question that should trigger list_docs
        result = answer_sync("What documentation files are available? List all formats.")
        print("✅ Document listing test completed")
        print("Response snippet:", result[:200] + "..." if len(result) > 200 else result)
        
        if ".pdf" in result.lower():
            print("✅ PDF files detected in listing!")
        else:
            print("ℹ️ No PDF files mentioned (may not have any PDF files in docs/)")
            
    except Exception as e:
        print("❌ Error in PDF listing test:")
        print(f"{type(e).__name__}: {e}")

def test_pdf_search():
    """Test searching across PDF content."""
    print("\n🔍 Testing PDF content search...")
    
    try:
        # Search for common terms that might be in PDFs
        search_terms = ["PDF", "document", "page", "text"]
        
        for term in search_terms:
            print(f"Searching for '{term}'...")
            result = answer_sync(f"Search for '{term}' in all documents. Show me any matches from PDF files specifically.")
            
            if "pdf" in result.lower():
                print(f"✅ Found PDF content for term '{term}'")
                break
        else:
            print("ℹ️ No specific PDF content found (may not have searchable PDFs)")
            
    except Exception as e:
        print("❌ Error in PDF search test:")
        print(f"{type(e).__name__}: {e}")

def test_pdf_analysis():
    """Test PDF-specific analysis features."""
    print("\n📊 Testing PDF analysis capabilities...")
    
    try:
        # Test document analysis that should include PDFs
        result = answer_sync("Analyze the structure of all documents. Are there any PDF files? What do they contain?")
        print("✅ PDF analysis test completed")
        print("Response snippet:", result[:300] + "..." if len(result) > 300 else result)
        
    except Exception as e:
        print("❌ Error in PDF analysis test:")
        print(f"{type(e).__name__}: {e}")

def main():
    """Run all PDF support tests."""
    print("🚀 Testing PDF Support in Docs Navigator MCP")
    print("=" * 60)
    
    # Create test setup
    test_pdf = create_test_pdf()
    
    # Check if we have actual PDFs to test
    docs_dir = project_root / "docs"
    pdf_files = list(docs_dir.glob("**/*.pdf"))
    
    print(f"\n📁 Found {len(pdf_files)} PDF files in docs/:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name}")
    
    if not pdf_files:
        print("\n⚠️ No PDF files found for testing.")
        print("To test PDF functionality:")
        print("1. Add a PDF file to the docs/ folder")
        print("2. Re-run this test script")
        print("3. Or use the Gradio interface to ask questions")
        return
    
    # Run tests
    test_pdf_listing()
    test_pdf_search()
    test_pdf_analysis()
    
    print("\n" + "=" * 60)
    print("🎉 PDF testing completed!")
    print("💡 Try the Gradio interface to interactively test PDF queries")

if __name__ == "__main__":
    main()