#!/usr/bin/env python3
"""
Test end-to-end image description functionality
"""
import sys
import os
from pathlib import Path
import asyncio

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_full_flow():
    """Test the complete flow from question to answer"""
    print("🔍 Testing complete image description flow...")
    
    try:
        from src.agent.client import DocsNavigatorClient
        
        # Initialize client
        client = DocsNavigatorClient()
        
        print("📡 Connecting to MCP server...")
        await client.connect('src/server/server.py')
        print("✅ Connected successfully!")
        
        # Test listing docs
        print("📋 Testing document listing...")
        result = await client.session.call_tool('list_docs', {})
        docs = result.content[0].text.split()
        image_docs = [doc for doc in docs if 'images/' in doc]
        print(f"   Found {len(docs)} total docs, {len(image_docs)} image files")
        
        if image_docs:
            print(f"   Sample images: {image_docs[:3]}")
            
            # Test reading a specific image
            test_image = 'images/aurora_diagram.png'
            if test_image in image_docs:
                print(f"📖 Testing image reading: {test_image}")
                result = await client.session.call_tool('read_doc', {'relative_path': test_image})
                content = result.content[0].text
                print(f"   Content length: {len(content)}")
                print(f"   OCR detected: {'OCR' in content}")
                
                # Test search functionality
                print("🔍 Testing search for image content...")
                result = await client.session.call_tool('search_docs', {'query': 'aurora diagram', 'max_results': 5})
                search_results = eval(result.content[0].text)  # Parse the results
                image_results = [r for r in search_results if 'images/' in r['path']]
                print(f"   Found {len(image_results)} image matches")
                
                # Finally, test the actual AI question
                print("🤖 Testing AI image description question...")
                answer = await client.answer("Can you describe the contents of the aurora_diagram.png image?")
                print("=" * 60)
                print("AI Response:")
                print(answer)
                print("=" * 60)
                
                # Check if the response indicates it found and processed the image
                success_indicators = [
                    "OCR" in answer,
                    "image" in answer.lower(),
                    "diagram" in answer.lower(),
                    "embedding" in answer.lower(),  # Content from the actual image
                    "transformer" in answer.lower()
                ]
                
                successful_indicators = sum(success_indicators)
                print(f"\\n✅ Success indicators found: {successful_indicators}/5")
                
                if successful_indicators >= 3:
                    print("🎉 SUCCESS: Image description is working!")
                    return True
                else:
                    print("⚠️ PARTIAL: AI responded but may not have processed the image correctly")
                    return False
            else:
                print(f"❌ Test image {test_image} not found in document list")
                return False
        else:
            print("❌ No image files found")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            await client.close()
        except:
            pass

def main():
    """Run the test"""
    try:
        result = asyncio.run(test_full_flow())
        if result:
            print("\\n🎉 OVERALL RESULT: SUCCESS - Image description is working!")
        else:
            print("\\n❌ OVERALL RESULT: FAILED - Image description needs fixes")
            print("\\n🔧 Possible issues:")
            print("   1. MCP server not finding images")
            print("   2. OCR not working properly")  
            print("   3. AI not understanding how to use image tools")
            print("   4. Client-server communication issues")
    except KeyboardInterrupt:
        print("\\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\\n💥 Test failed with error: {e}")

if __name__ == "__main__":
    main()