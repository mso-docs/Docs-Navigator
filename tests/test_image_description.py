#!/usr/bin/env python3
"""
Test script for image description functionality
"""
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Test OCR functionality
print("🔍 Testing OCR functionality...")
try:
    from enhanced_ocr_processor import extract_text_with_ocr, get_ocr_status
    
    # Check status
    status = get_ocr_status()
    print(f"OCR available: {status['available']}")
    print(f"Available backends: {status.get('available_backends', [])}")
    
    # Test image processing
    image_path = Path("docs/images/aurora_diagram.png")
    if image_path.exists():
        print(f"\n📸 Testing image: {image_path.name}")
        result = extract_text_with_ocr(image_path)
        print(f"Success: {result['success']}")
        print(f"Confidence: {result.get('confidence', 0)*100:.1f}%")
        print(f"Text (first 200 chars): {result.get('text', '')[:200]}...")
    else:
        print(f"❌ Image not found: {image_path}")
        
except Exception as e:
    print(f"❌ OCR test failed: {e}")
    import traceback
    traceback.print_exc()

# Test MCP server functions
print("\n🔧 Testing MCP server functions...")
try:
    from src.server.server import read_doc, list_docs, search_docs
    
    # List docs to find images
    docs = list_docs()
    image_docs = [doc for doc in docs if 'images/' in doc]
    print(f"Found {len(image_docs)} image files")
    
    if image_docs:
        # Test reading an image
        sample_image = image_docs[0]
        print(f"\n📖 Testing read_doc for: {sample_image}")
        content = read_doc(sample_image)
        print(f"Content length: {len(content)}")
        print(f"Content preview: {content[:150]}...")
        
        # Test searching for image content
        print(f"\n🔍 Testing search_docs for 'diagram'...")
        search_results = search_docs("diagram", max_results=3)
        for i, result in enumerate(search_results):
            print(f"  {i+1}. {result['path']} (score: {result.get('score', 'N/A')})")
            
except Exception as e:
    print(f"❌ MCP server test failed: {e}")
    import traceback
    traceback.print_exc()

# Test simulated AI response about images
print("\n🤖 Testing simulated AI response...")
try:
    from src.server.server import read_doc, list_docs
    
    # Simulate what the AI should do when asked about an image
    docs = list_docs()
    image_docs = [doc for doc in docs if 'aurora_diagram' in doc]
    
    if image_docs:
        target_image = image_docs[0]
        print(f"Found target image: {target_image}")
        
        # Read the image content
        image_content = read_doc(target_image)
        print(f"Image content extracted: {len(image_content)} characters")
        
        # Simulate AI analysis
        if "OCR" in image_content and "Confidence" in image_content:
            confidence_start = image_content.find("Confidence: ") + 12
            confidence_end = image_content.find("%", confidence_start)
            confidence = image_content[confidence_start:confidence_end]
            
            # Extract the actual text after the header
            text_start = image_content.find("---\n") + 4
            extracted_text = image_content[text_start:].strip()
            
            print(f"\n✅ SUCCESSFUL IMAGE ANALYSIS:")
            print(f"   Image: {target_image}")
            print(f"   OCR Confidence: {confidence}%")
            print(f"   Extracted Text: {extracted_text}")
            print(f"\n🎯 AI should respond with:")
            print(f"   'Based on the OCR analysis of {target_image}, I can see this image contains text about: {extracted_text}'")
        else:
            print("❌ Image content doesn't contain expected OCR metadata")
    else:
        print("❌ Target image not found")
        
except Exception as e:
    print(f"❌ Simulation test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n✨ Test complete!")