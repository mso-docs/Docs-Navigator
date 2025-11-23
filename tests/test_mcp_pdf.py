#!/usr/bin/env python3
"""
Test MCP server PDF functionality directly
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_mcp_pdf_tools():
    """Test MCP server tools for PDF functionality"""
    try:
        from src.agent.client import DocsNavigatorClient
        
        print("🔧 Testing MCP server PDF tools...")
        
        client = DocsNavigatorClient()
        await client.connect("src/server/server.py")
        
        print("✅ MCP client connected")
        
        # Test list_docs to see if PDFs are included
        print("\n📋 Testing list_docs...")
        result = await client.session.call_tool("list_docs", {})
        docs = result.content[0].text if result.content else "No content"
        print(f"Documents found: {docs}")
        
        # Test search_docs for PDF content
        print("\n🔍 Testing search_docs...")
        result = await client.session.call_tool("search_docs", {"query": "Aurora", "max_results": 5})
        search_results = result.content[0].text if result.content else "No content"
        print(f"Search results: {search_results}")
        
        # Test summarize_document for a PDF
        print("\n📄 Testing summarize_document on a PDF...")
        pdf_files = [doc for doc in docs.split('\n') if doc.strip().endswith('.pdf')]
        if pdf_files:
            pdf_file = pdf_files[0].strip()
            print(f"Summarizing: {pdf_file}")
            result = await client.session.call_tool("summarize_document", {
                "relative_path": pdf_file,
                "summary_type": "overview"
            })
            summary = result.content[0].text if result.content else "No content"
            print(f"Summary result: {summary[:500]}...")
        else:
            print("No PDF files found in document list")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error testing MCP tools: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run MCP PDF tests"""
    print("🧪 Testing MCP Server PDF Integration")
    print("=" * 50)
    
    asyncio.run(test_mcp_pdf_tools())

if __name__ == "__main__":
    main()