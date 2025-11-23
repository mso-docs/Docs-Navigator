# Documents Folder Structure

This folder contains all documents that the AI assistant can analyze and search through.

## 📁 Folder Organization

### 📄 `/pdfs/`
- **Text-based PDFs**: Documents with selectable text
- **Scanned PDFs**: Image-based PDFs that require OCR
- **Mixed PDFs**: Documents with both text and images

### 🖼️ `/images/`
- **PNG, JPG, JPEG**: Screenshots, photos of documents
- **TIFF, TIF**: High-quality scanned images
- **BMP, GIF**: Other image formats
- All images will be processed with OCR to extract text

### 📝 `/text/`
- **Markdown (.md)**: Documentation files
- **Plain text (.txt)**: Simple text documents
- **reStructuredText (.rst)**: Technical documentation

### 🔧 `/guides/`
- Step-by-step guides and tutorials
- Implementation instructions
- Best practices documents

## 🚀 Supported File Types

The system automatically detects and processes:

- **Text Extraction**: `.md`, `.txt`, `.rst`, text-based PDFs
- **OCR Processing**: `.png`, `.jpg`, `.jpeg`, `.tiff`, `.tif`, `.bmp`, `.gif`, scanned PDFs
- **Hybrid Processing**: Mixed PDFs (automatically chooses best method)

## 💡 Usage Tips

1. **Add new files** to appropriate subfolders
2. **Mixed content** can go at the root level
3. **Large files** are automatically chunked for processing
4. **OCR confidence scores** are provided for image-based content
5. **Search works across all file types** regardless of location

## 🎯 Quick Start

1. Drop your files into the appropriate folders
2. Start the app: `uv run python app_gradio.py`
3. Ask questions like:
   - "What documents do I have about Aurora AI?"
   - "Extract text from the images in the images folder"
   - "Summarize all PDFs in the pdfs folder"
   - "Find information about API authentication"

The AI will automatically discover and process all supported files in this directory tree.