#!/usr/bin/env python3
"""
Test the complete functionality of the docs navigator.
"""

from client_agent import answer_sync

def test_docs_navigator():
    """Test the docs navigator with a sample query."""
    
    print("Testing docs navigator with the question: 'What is AuroraAI?'")
    print("-" * 60)
    
    try:
        result = answer_sync("What is AuroraAI? Give me a brief overview.")
        print("✅ SUCCESS!")
        print("Response:")
        print(result)
    except Exception as e:
        print("❌ ERROR:")
        print(f"{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_docs_navigator()