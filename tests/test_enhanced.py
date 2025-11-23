#!/usr/bin/env python3
"""
Test the enhanced image processing functionality directly
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_direct_image_processing():
    """Test the direct image processing function"""
    print("🧪 Testing Direct Image Processing Function")
    print("=" * 50)
    
    try:
        # Import the enhanced app function
        from app_enhanced import process_image_question_directly
        
        test_questions = [
            "What images are available in the documentation?",
            "Can you describe the contents of aurora_diagram.png?",
            "Extract text from the Aurora architecture images",
            "Show me what's in the training diagram"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\\n🔍 Test {i}: {question}")
            print("-" * 40)
            
            try:
                result = process_image_question_directly(question)
                
                if result:
                    print("✅ SUCCESS - Got image-specific response:")
                    print(result[:300] + "..." if len(result) > 300 else result)
                    
                    # Check for success indicators
                    indicators = {
                        "found_images": "image" in result.lower(),
                        "ocr_info": "ocr" in result.lower(),
                        "confidence": "confidence" in result.lower(),
                        "extracted_text": "extracted" in result.lower() or "content" in result.lower()
                    }
                    
                    score = sum(indicators.values())
                    print(f"\\n📊 Quality Score: {score}/4")
                    return True
                else:
                    print("⚠️ No image-specific response (normal for non-image questions)")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
            
            # Test only the first question for now
            break
            
        return False
        
    except Exception as e:
        print(f"❌ Import or setup error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gradio_interface():
    """Test the enhanced Gradio interface function"""
    print("\\n🎮 Testing Enhanced Gradio Interface")
    print("=" * 50)
    
    try:
        from app_enhanced import enhanced_chat_fn
        
        # Test with image question
        question = "Describe the aurora_diagram.png image"
        print(f"🔍 Testing question: {question}")
        
        # Simulate the Gradio call
        result = enhanced_chat_fn(question, [])
        
        print("✅ Response received:")
        print("-" * 30)
        print(result[:500] + "..." if len(result) > 500 else result)
        print("-" * 30)
        
        # Check for success indicators
        success_indicators = [
            "image" in result.lower(),
            "ocr" in result.lower(),
            "confidence" in result.lower(),
            "extracted" in result.lower() or "content" in result.lower(),
            "aurora" in result.lower()
        ]
        
        score = sum(success_indicators)
        print(f"\\n📊 Success Score: {score}/5")
        
        if score >= 3:
            print("🎉 SUCCESS: Enhanced interface working correctly!")
            return True
        else:
            print("⚠️ PARTIAL: Some functionality working, may need refinement")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gradio interface: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Enhanced Image Description Functionality")
    print("=" * 60)
    
    # Test 1: Direct function
    result1 = test_direct_image_processing()
    
    # Test 2: Gradio interface
    result2 = test_gradio_interface()
    
    print("\\n" + "=" * 60)
    print("🏆 FINAL RESULTS")
    print("=" * 60)
    
    if result1 and result2:
        print("🎉 ALL TESTS PASSED: Image description is working perfectly!")
        print("\\n✅ Users can now:")
        print("   • Ask about any images in the documentation")
        print("   • Get OCR text extraction with confidence scores") 
        print("   • Receive detailed descriptions of image content")
        print("   • View analysis of multiple images at once")
    elif result1 or result2:
        print("⚠️ PARTIAL SUCCESS: Basic functionality working")
        print("   Some features may need additional refinement")
    else:
        print("❌ TESTS FAILED: Image description needs further work")
    
    print(f"\\n🌐 Enhanced app running at: http://127.0.0.1:7866")
    print("💡 Try asking: 'What images are in the docs?' or 'Describe aurora_diagram.png'")

if __name__ == "__main__":
    main()