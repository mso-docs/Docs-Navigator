# PDF Support Testing

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
