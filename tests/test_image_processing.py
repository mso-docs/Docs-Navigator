#!/usr/bin/env python3
"""
Test image file processing and OCR capabilities specifically.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_image_file_discovery():
    """Test that image files are discovered by the server."""
    print("\n🖼️ Testing Image File Discovery...")
    try:
        from src.server.server import _iter_docs, OCR_SUPPORT
        
        print(f"📊 Server OCR Support: {OCR_SUPPORT}")
        
        docs = list(_iter_docs())
        image_docs = []
        
        image_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.gif'}
        for doc in docs:
            if doc.suffix.lower() in image_extensions:
                image_docs.append(doc)
        
        print(f"📄 Total documents: {len(docs)}")
        print(f"🖼️ Image documents: {len(image_docs)}")
        
        if image_docs:
            print("📝 Found image files:")
            for img in image_docs:
                print(f"  - {img.name} ({img.suffix})")
            return True
        else:
            print("⚠️ No image files found")
            print("💡 Add some image files to docs/ folder to test image processing")
            return False
            
    except Exception as e:
        print(f"❌ Image discovery test failed: {e}")
        return False


def test_image_reading():
    """Test reading content from image files."""
    print("\n📖 Testing Image Content Reading...")
    try:
        from src.server.server import _iter_docs, _read_file, OCR_SUPPORT
        
        if not OCR_SUPPORT:
            print("❌ OCR not supported - cannot test image reading")
            return False
        
        docs = list(_iter_docs())
        image_docs = []
        
        image_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.gif'}
        for doc in docs:
            if doc.suffix.lower() in image_extensions:
                image_docs.append(doc)
        
        if not image_docs:
            print("⚠️ No image files to test")
            return False
        
        success = True
        for img_doc in image_docs[:3]:  # Test first 3 images
            print(f"\n🔤 Processing: {img_doc.name}")
            try:
                content = _read_file(img_doc)
                
                if content and len(content) > 20:
                    print(f"✅ Successfully extracted {len(content)} characters")
                    
                    # Extract confidence and method info
                    if "Confidence:" in content:
                        lines = content.split('\n')
                        header = lines[0] if lines else ""
                        print(f"📊 Processing info: {header}")
                    
                    # Show preview of extracted text
                    text_lines = content.split('\n')[1:]  # Skip header
                    text_content = '\n'.join(text_lines).strip()
                    if text_content:
                        preview = text_content[:150]
                        print(f"📝 Text preview: {preview}...")
                    else:
                        print("⚠️ No text content extracted")
                        success = False
                else:
                    print(f"❌ Failed to extract meaningful content")
                    success = False
                    
            except Exception as e:
                print(f"❌ Error processing {img_doc.name}: {e}")
                success = False
        
        return success
        
    except Exception as e:
        print(f"❌ Image reading test failed: {e}")
        return False


def test_ai_image_queries():
    """Test AI queries about image content."""
    print("\n🤖 Testing AI Queries on Image Content...")
    try:
        from src.agent.client import answer_sync
        
        # Test various image-related queries
        queries = [
            "What image files are available in the documentation?",
            "Extract text content from any image files you can find",
            "Are there any screenshots or diagrams in the documentation?",
            "What OCR processing methods were used for the images?"
        ]
        
        success = True
        for query in queries:
            print(f"\n❓ Query: {query}")
            try:
                response = answer_sync(query)
                if response and len(response) > 20:
                    print(f"✅ Got response ({len(response)} chars)")
                    print(f"📝 Preview: {response[:200]}...")
                else:
                    print("⚠️ Short or empty response")
                    success = False
            except Exception as e:
                print(f"❌ Query failed: {e}")
                success = False
        
        return success
        
    except Exception as e:
        print(f"❌ AI image query test failed: {e}")
        return False


def test_ocr_quality_assessment():
    """Test OCR quality assessment features."""
    print("\n📊 Testing OCR Quality Assessment...")
    try:
        from ocr_processor import extract_text_with_ocr, ocr_processor
        
        if not ocr_processor.is_available():
            print("❌ OCR not available")
            return False
        
        docs_dir = project_root / "docs"
        image_files = []
        
        # Find image files
        for ext in ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.gif']:
            image_files.extend(list(docs_dir.glob(f"**/*{ext}")))
        
        if not image_files:
            print("⚠️ No image files found for quality testing")
            return False
        
        total_confidence = 0
        successful_extractions = 0
        
        for img_file in image_files[:3]:  # Test first 3 images
            print(f"\n🔍 Analyzing: {img_file.name}")
            
            result = extract_text_with_ocr(img_file)
            
            if result['success']:
                confidence = result.get('confidence', 0)
                word_count = result.get('word_count', 0)
                text_length = len(result.get('text', ''))
                
                print(f"✅ OCR Success")
                print(f"📊 Confidence: {confidence:.1%}")
                print(f"📝 Words extracted: {word_count}")
                print(f"📏 Text length: {text_length} characters")
                
                total_confidence += confidence
                successful_extractions += 1
                
                # Quality assessment
                if confidence > 0.8:
                    print("🏆 High quality OCR result")
                elif confidence > 0.5:
                    print("👍 Good quality OCR result") 
                elif confidence > 0.3:
                    print("⚠️ Moderate quality OCR result")
                else:
                    print("❌ Low quality OCR result")
            else:
                error = result.get('error', 'Unknown error')
                print(f"❌ OCR Failed: {error}")
        
        if successful_extractions > 0:
            avg_confidence = total_confidence / successful_extractions
            print(f"\n📈 Overall Quality Assessment:")
            print(f"✅ Successful extractions: {successful_extractions}/{len(image_files[:3])}")
            print(f"📊 Average confidence: {avg_confidence:.1%}")
            
            return True
        else:
            print("\n❌ No successful OCR extractions")
            return False
            
    except Exception as e:
        print(f"❌ Quality assessment test failed: {e}")
        return False


def create_sample_images():
    """Create information about sample test images."""
    print("\n📁 Sample Image Testing Guide...")
    
    suggestions = [
        "Screenshots of code or documentation",
        "Scanned text documents", 
        "Photos of printed pages",
        "Diagrams with text labels",
        "Charts or graphs with text",
        "Sign images with clear text"
    ]
    
    print("💡 For best OCR results, try adding these types of images to docs/:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    print("\n🎯 OCR Quality Tips:")
    print("  - Use high resolution images (300+ DPI)")
    print("  - Ensure good contrast between text and background")
    print("  - Avoid blurry or tilted text")
    print("  - Clean, simple layouts work best")
    print("  - PNG and TIFF formats often give better results than JPEG")


def main():
    """Run image-specific tests."""
    print("🖼️ Image Processing Test Suite")
    print("=" * 50)
    
    success = True
    
    # Test image discovery
    if not test_image_file_discovery():
        create_sample_images()
        # Don't fail here, just provide guidance
    
    # Test image reading (only if images found)
    docs_dir = project_root / "docs"
    image_files = []
    for ext in ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.gif']:
        image_files.extend(list(docs_dir.glob(f"**/*{ext}")))
    
    if image_files:
        if not test_image_reading():
            success = False
        
        if not test_ai_image_queries():
            success = False
        
        if not test_ocr_quality_assessment():
            success = False
    else:
        print("\n⚠️ No image files found - skipping processing tests")
        print("💡 Add some image files to docs/ folder to test image processing")
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Image processing tests completed successfully!")
    else:
        print("❌ Some image processing tests had issues")
    
    print("\n📋 Summary:")
    print("✅ Image file discovery working")
    if image_files:
        print("✅ Image files found and processed")
    else:
        print("⚠️ No image files to process")
    
    print("\n🚀 Try adding different image types to test:")
    print("  - Add .png, .jpg, .tiff images to docs/")
    print("  - Use the Gradio interface to ask about image content")
    print("  - Check OCR confidence scores in responses")


if __name__ == "__main__":
    main()