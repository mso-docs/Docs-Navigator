# test_intelligent_tools.py
"""
Test script to demonstrate the new intelligent document analysis tools.
"""

import asyncio
from client_agent import DocsNavigatorClient


async def test_intelligent_tools():
    """Test the new intelligent documentation tools."""
    client = DocsNavigatorClient()
    
    try:
        await client.connect("server_docs.py")
        print("Connected to docs navigator server\n")
        
        # Test 1: Intelligent summarization
        print("=== Testing Intelligent Summarization ===")
        result = await client.session.call_tool("intelligent_summarize", {
            "relative_path": "overview.md",
            "summary_type": "medium"
        })
        print("Summary result:")
        print(result.content)
        print("\n" + "="*50 + "\n")
        
        # Test 2: Extract Q&A pairs
        print("=== Testing Q&A Extraction ===")
        result = await client.session.call_tool("extract_qa_pairs", {})
        print("Q&A extraction result:")
        print(result.content)
        print("\n" + "="*50 + "\n")
        
        # Test 3: Find related documents
        print("=== Testing Related Document Finding ===")
        result = await client.session.call_tool("find_related_documents", {
            "query": "configuration setup troubleshooting",
            "max_results": 3
        })
        print("Related documents result:")
        print(result.content)
        print("\n" + "="*50 + "\n")
        
        # Test 4: Document structure analysis
        print("=== Testing Document Structure Analysis ===")
        result = await client.session.call_tool("analyze_document_structure", {
            "relative_path": "setup.md"
        })
        print("Structure analysis result:")
        print(result.content)
        print("\n" + "="*50 + "\n")
        
        # Test 5: Documentation gaps analysis
        print("=== Testing Documentation Gaps Analysis ===")
        result = await client.session.call_tool("analyze_document_gaps", {})
        print("Gaps analysis result:")
        print(result.content)
        print("\n" + "="*50 + "\n")
        
        # Test 6: Generate documentation index
        print("=== Testing Documentation Index Generation ===")
        result = await client.session.call_tool("generate_documentation_index", {})
        print("Documentation index result:")
        print(result.content)
        
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        await client.close()


def test_intelligent_tools_sync():
    """Synchronous wrapper for testing."""
    asyncio.run(test_intelligent_tools())


if __name__ == "__main__":
    test_intelligent_tools_sync()