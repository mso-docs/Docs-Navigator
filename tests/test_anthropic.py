#!/usr/bin/env python3
"""
Test Anthropic API connection and available models.
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

def test_anthropic_api():
    """Test the Anthropic API with different model names."""
    client = Anthropic()
    
    # List of model names to try
    models_to_try = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620", 
        "claude-3-haiku-20240307",
        "claude-3-sonnet-20240229"
    ]
    
    test_message = "Hello, please respond with just 'API working' if you can understand this message."
    
    for model in models_to_try:
        try:
            print(f"Testing model: {model}")
            response = client.messages.create(
                model=model,
                max_tokens=50,
                messages=[{"role": "user", "content": test_message}]
            )
            print(f"✅ {model}: {response.content[0].text}")
            break
        except Exception as e:
            print(f"❌ {model}: {str(e)}")
    
    print("Done testing models.")

if __name__ == "__main__":
    test_anthropic_api()