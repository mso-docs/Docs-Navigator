#!/usr/bin/env python3
"""
Simple test to simulate asking about image description
"""
import sys
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_image_question():
    """Test asking about an image"""
    print("🤖 Testing image description question...")
    
    try:
        from src.agent.client import answer_sync
        
        # Test questions about images
        test_questions = [
            "Can you describe what's in the aurora_diagram.png image?",
            "What text can you extract from the images in the docs?",
            "Describe the contents of any images in the documentation",
            "What images are available and what do they contain?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{'='*60}")
            print(f"Test {i}: {question}")
            print("="*60)
            
            try:
                print("⏳ Processing...")
                start_time = time.time()
                
                # Use a timeout approach
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("Operation timed out")
                
                # Set timeout for 60 seconds
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(60)
                
                try:
                    answer = answer_sync(question)
                    signal.alarm(0)  # Cancel timeout
                    
                    elapsed = time.time() - start_time
                    print(f"⏱️ Completed in {elapsed:.1f} seconds")
                    
                    print(f"\n🤖 AI Response:")
                    print("-" * 40)
                    print(answer)
                    print("-" * 40)
                    
                    # Analyze the response
                    indicators = {
                        "found_images": any(word in answer.lower() for word in ["image", "png", "jpg", "jpeg"]),
                        "used_ocr": "OCR" in answer or "optical character recognition" in answer.lower(),
                        "mentioned_confidence": "confidence" in answer.lower(),
                        "extracted_text": any(word in answer.lower() for word in ["text", "extract", "contain"]),
                        "specific_content": any(word in answer.lower() for word in ["embedding", "transformer", "diagram"])
                    }
                    
                    score = sum(indicators.values())
                    print(f"\n📊 Analysis (Score: {score}/5):")
                    for indicator, found in indicators.items():
                        status = "✅" if found else "❌"
                        print(f"   {status} {indicator.replace('_', ' ').title()}")
                    
                    if score >= 3:
                        print("🎉 SUCCESS: AI properly processed image content!")
                        return True
                    elif score >= 1:
                        print("⚠️ PARTIAL: AI found some image content but may need improvement")
                    else:
                        print("❌ FAILED: AI didn't seem to process image content")
                        
                except TimeoutError:
                    signal.alarm(0)
                    print("⏰ TIMEOUT: Question took too long to process")
                    
            except KeyboardInterrupt:
                print("⏹️ Test interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
            # Only test the first question for now
            break
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    return False

if __name__ == "__main__":
    print("🧪 Testing Image Description Functionality")
    print("=" * 50)
    
    try:
        success = test_image_question()
        print("\n" + "="*50)
        if success:
            print("🎉 RESULT: Image description functionality is working!")
        else:
            print("❌ RESULT: Image description needs further investigation")
            print("\n💡 Next steps:")
            print("   1. Check if MCP server is starting properly")
            print("   2. Verify OCR tools are available to AI")
            print("   3. Test manually in Gradio interface")
    except KeyboardInterrupt:
        print("\n⏹️ Test cancelled by user")