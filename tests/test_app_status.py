#!/usr/bin/env python3
"""
Simple test client to verify the assistant is working
"""

import requests
import json

def test_gradio_app():
    """Test the Gradio app is responding via HTTP"""
    try:
        # Test if the app is running
        response = requests.get("http://127.0.0.1:7863", timeout=5)
        if response.status_code == 200:
            print("✅ Gradio app is running and accessible")
            return True
        else:
            print(f"❌ Gradio app returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Gradio app - is it running?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Gradio app connection timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing Gradio app: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Gradio application...")
    success = test_gradio_app()
    
    if success:
        print("\n🎉 The assistant is ready!")
        print("📱 Open your browser to: http://127.0.0.1:7863")
        print("💬 Try asking: '👋 Hello! Are you working?'")
    else:
        print("\n💥 The assistant may not be ready yet.")
        print("🔄 Try starting it with: python app_gradio.py")