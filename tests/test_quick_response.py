#!/usr/bin/env python3
"""
Quick test to verify the assistant is responding properly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agent.client import answer_sync

def test_basic_response():
    """Test basic response functionality"""
    print("🧪 Testing basic assistant response...")
    
    try:
        # Simple test question
        print("📞 Calling answer_sync...")
        response = answer_sync("Hello! Are you working?")
        print(f"✅ Response received ({len(response)} chars): {response[:200]}...")
        
        if "timeout" in response.lower():
            print("❌ Response indicates a timeout")
            return False
        elif "error" in response.lower():
            print("❌ Response indicates an error")
            return False
        else:
            print("✅ Assistant is responding normally")
            return True
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_response()
    if success:
        print("\n🎉 Assistant test passed! The app should be working normally.")
    else:
        print("\n💥 Assistant test failed. There may still be issues.")
    
    sys.exit(0 if success else 1)