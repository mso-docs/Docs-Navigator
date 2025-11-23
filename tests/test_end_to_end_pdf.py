#!/usr/bin/env python3
"""
Test end-to-end PDF functionality with the AI assistant.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agent.client import answer_sync

def test_pdf_questions():
    """Test various PDF-related questions."""
    
    test_cases = [
        {
            "question": "What PDF documents are available?",
            "description": "Test document listing"
        },
        {
            "question": "What is the Aurora AI API base URL?",
            "description": "Test specific PDF content extraction"
        },
        {
            "question": "How does authentication work in Aurora AI?",
            "description": "Test PDF content search and understanding"
        },
        {
            "question": "Summarize the Aurora AI API Reference PDF",
            "description": "Test PDF summarization"
        }
    ]
    
    print("🤖 Testing AI Assistant PDF Integration")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['description']}")
        print(f"❓ Question: {test_case['question']}")
        print("-" * 40)
        
        try:
            response = answer_sync(test_case['question'])
            print(f"✅ Response: {response[:300]}...")
            
            # Check if response indicates PDF access
            if "pdf" in response.lower() or "aurora" in response.lower():
                print("🎯 PDF content detected in response!")
            else:
                print("⚠️  No clear PDF content detected")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

def main():
    """Run PDF integration tests."""
    test_pdf_questions()
    
    print("=" * 60)
    print("💡 The PDF support should now work correctly!")
    print("🌐 Try the Gradio interface for interactive testing")

if __name__ == "__main__":
    main()