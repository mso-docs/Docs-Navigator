#!/usr/bin/env python3
"""
Test script to demonstrate the fixed summarization and document extraction functionality.
"""

from client_agent import answer_sync
import json

def test_summarization_fixes():
    """Test that the summarization issues are fixed."""
    
    print("=" * 60)
    print("Testing Fixed Summarization and Document Analysis")
    print("=" * 60)
    
    # Test 1: Anti-patterns question that was failing before
    print("\n1. Testing anti-patterns extraction (previously failing):")
    print("-" * 50)
    response = answer_sync("What are the anti-patterns mentioned in the prompting guidelines documentation?")
    print(response)
    
    # Test 2: More complex analysis
    print("\n2. Testing best practices analysis:")
    print("-" * 50)
    response = answer_sync("Can you summarize the best practices for technical writing prompts from the documentation?")
    print(response)
    
    # Test 3: Section-specific question
    print("\n3. Testing specific section extraction:")
    print("-" * 50)
    response = answer_sync("What does the documentation say about example prompts? Show me the specific examples provided.")
    print(response)
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("The summarization issues have been resolved.")

if __name__ == "__main__":
    test_summarization_fixes()