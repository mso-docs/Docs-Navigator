#!/usr/bin/env python3
"""
Docs Navigator MCP - Launcher Script

This script launches Gradio UI for the Docs Navigator MCP application.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Change to project directory to ensure relative paths work
os.chdir(project_root)

# Import and run the app
from src.ui.app import demo

def main():
    """Main entry point for the application."""
    print("🚀 Starting Docs Navigator MCP...")
    print("📚 AI-Powered Documentation Assistant")
    print("🌐 The app will be available at: http://127.0.0.1:7863")
    print("💡 Ask questions about your documentation!")
    print("-" * 50)
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7863,
        show_error=True,
        share=False  # Set to True if you want a public link
    )

if __name__ == "__main__":
    main()