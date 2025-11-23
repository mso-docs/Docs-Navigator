#!/usr/bin/env python3
"""
Enhanced Gradio app with direct image processing capabilities
"""
import gradio as gr
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import enhanced OCR and MCP server functions directly
try:
    from enhanced_ocr_processor import get_ocr_status, extract_text_with_ocr
    from src.server.server import list_docs, read_doc, search_docs, DOCS_ROOT
    OCR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import enhanced functionality: {e}")
    OCR_AVAILABLE = False

def process_image_question_directly(query: str) -> str:
    """Process questions about images directly without MCP client"""
    try:
        query_lower = query.lower()
        
        # Check if this is an image-related question
        image_keywords = ["image", "picture", "photo", "diagram", "chart", "figure", "visual", "describe", "show", "png", "jpg", "jpeg"]
        is_image_question = any(keyword in query_lower for keyword in image_keywords)
        
        if not is_image_question:
            return None  # Let normal processing handle it
        
        if not OCR_AVAILABLE:
            return "❌ OCR functionality is not available. Please install the required dependencies."
        
        # Get OCR status
        ocr_status = get_ocr_status()
        if not ocr_status.get("available", False):
            return f"❌ OCR is not available: {ocr_status.get('error', 'Unknown error')}"
        
        # List available documents
        docs = list_docs()
        image_docs = [doc for doc in docs if doc.startswith('images/') and any(doc.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'])]
        
        if not image_docs:
            return "❌ No image files found in the documentation."
        
        # If specific image mentioned, try to find it
        specific_image = None
        for doc in image_docs:
            filename = Path(doc).name.lower()
            if filename.replace(' ', '').replace('_', '').replace('-', '') in query_lower.replace(' ', '').replace('_', '').replace('-', ''):
                specific_image = doc
                break
        
        response_parts = []
        response_parts.append(f"🖼️ **Image Analysis Results**")
        response_parts.append(f"📊 OCR Status: {ocr_status.get('active_backend', 'Unknown')} backend available")
        
        if specific_image:
            # Process specific image
            response_parts.append(f"\\n🎯 **Analyzing specific image: {specific_image}**")
            try:
                content = read_doc(specific_image)
                if "OCR Failed" in content:
                    response_parts.append(f"❌ Failed to extract text from {specific_image}")
                else:
                    # Extract OCR information
                    if "Confidence:" in content:
                        confidence_start = content.find("Confidence: ") + 12
                        confidence_end = content.find("%", confidence_start)
                        confidence = content[confidence_start:confidence_end]
                        response_parts.append(f"🎯 OCR Confidence: {confidence}%")
                    
                    # Extract the actual text
                    if "---\\n" in content:
                        text_start = content.find("---\\n") + 4
                        extracted_text = content[text_start:].strip()
                    else:
                        extracted_text = content.strip()
                    
                    response_parts.append(f"\\n📄 **Extracted Text:**")
                    response_parts.append(extracted_text)
                    
                    # Provide description based on content
                    if extracted_text:
                        response_parts.append(f"\\n📝 **Description:**")
                        response_parts.append(f"This image contains text related to: {extracted_text[:200]}...")
                        
                        # Identify content type
                        content_lower = extracted_text.lower()
                        if any(word in content_lower for word in ["transformer", "embedding", "model"]):
                            response_parts.append("🤖 This appears to be a technical diagram related to AI/ML models.")
                        elif any(word in content_lower for word in ["architecture", "system", "component"]):
                            response_parts.append("🏗️ This appears to be an architectural or system diagram.")
                        elif any(word in content_lower for word in ["flow", "process", "step"]):
                            response_parts.append("🔄 This appears to be a process flow or workflow diagram.")
            except Exception as e:
                response_parts.append(f"❌ Error processing {specific_image}: {str(e)}")
        else:
            # Process all images
            response_parts.append(f"\\n📋 **Found {len(image_docs)} image files:**")
            
            processed_count = 0
            for doc in image_docs[:5]:  # Limit to first 5 to avoid overwhelming response
                try:
                    content = read_doc(doc)
                    filename = Path(doc).name
                    
                    if "OCR Failed" not in content:
                        processed_count += 1
                        response_parts.append(f"\\n🖼️ **{filename}:**")
                        
                        # Extract confidence
                        if "Confidence:" in content:
                            confidence_start = content.find("Confidence: ") + 12
                            confidence_end = content.find("%", confidence_start)
                            confidence = content[confidence_start:confidence_end]
                            response_parts.append(f"   • OCR Confidence: {confidence}%")
                        
                        # Extract brief text sample
                        if "---\\n" in content:
                            text_start = content.find("---\\n") + 4
                            extracted_text = content[text_start:].strip()
                        else:
                            extracted_text = content.strip()
                        
                        if extracted_text:
                            preview = extracted_text[:150] + "..." if len(extracted_text) > 150 else extracted_text
                            response_parts.append(f"   • Content: {preview}")
                except Exception as e:
                    response_parts.append(f"\\n❌ Error processing {doc}: {str(e)}")
            
            if processed_count == 0:
                response_parts.append("❌ Could not extract text from any images.")
            else:
                response_parts.append(f"\\n✅ Successfully processed {processed_count} images")
            
            if len(image_docs) > 5:
                response_parts.append(f"\\n📝 (Showing first 5 of {len(image_docs)} images. Ask about specific images for detailed analysis.)")
        
        # Add usage tip
        response_parts.append("\\n💡 **Tip:** Ask about specific images by name (e.g., 'describe aurora_diagram.png') for detailed analysis.")
        
        return "\\n".join(response_parts)
        
    except Exception as e:
        return f"❌ Error processing image question: {str(e)}"

def enhanced_chat_fn(message: str, history: list[dict]):
    """Enhanced chat function with direct image processing"""
    try:
        if not message.strip():
            return "Please enter a question about the documentation."
        
        # First try direct image processing
        image_response = process_image_question_directly(message)
        if image_response:
            return image_response
        
        # Fall back to normal MCP processing
        try:
            from src.agent.client import answer_sync
            reply = answer_sync(message)
            return reply
        except Exception as mcp_error:
            # If MCP fails, try to provide helpful direct response
            return f"⚠️ I encountered an issue with the documentation system: {str(mcp_error)}\\n\\nFor image-related questions, I can still help you directly. Try asking about specific images or image content."
            
    except Exception as e:
        return f"⚠️ I encountered an error while processing your question: {str(e)}\\n\\nPlease try again or rephrase your question."

# Professional theme configuration  
professional_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate", 
    neutral_hue="gray",
    font=[
        gr.themes.GoogleFont("Inter"),
        "ui-sans-serif",
        "system-ui",
        "sans-serif"
    ]
).set(
    body_background_fill="*neutral_50",
    panel_background_fill="white",
    button_primary_background_fill="*primary_600",
    button_primary_background_fill_hover="*primary_700",
    input_background_fill="white"
)

# Custom CSS
custom_css = """
.gradio-container {
    max-width: 1000px !important;
    margin: 0 auto !important;
}

.chat-interface {
    border-radius: 12px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
}

.message {
    border-radius: 8px !important;
    margin: 6px 0 !important;
}

/* Enhanced input styling */
.input-container textarea {
    border-radius: 8px !important;
    border: 2px solid #e5e7eb !important;
    transition: all 0.2s ease !important;
}

.input-container textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}
"""

# Create enhanced description
enhanced_description = """🤖 **AI-Powered Documentation Assistant with Image Analysis**

Ask questions about your documentation and get intelligent, contextual answers. I can:
• 📚 Search and analyze text documents 
• 🖼️ **Extract and analyze text from images using OCR**
• 📄 Process PDF files with text or image content
• 🔍 Find specific information across your documentation

**Image Analysis Features:**
• Supports PNG, JPG, TIFF, BMP, and other common image formats
• Advanced OCR with confidence scores
• Multiple OCR backends for best results

Powered by Claude AI and Model Context Protocol."""

demo = gr.ChatInterface(
    fn=enhanced_chat_fn,
    type="messages",
    title="📚 Docs Navigator MCP with Image Analysis",
    description=enhanced_description,
    theme=professional_theme,
    css=custom_css,
    chatbot=gr.Chatbot(
        height=500,
        show_label=False,
        type="messages",
        avatar_images=(
            "https://api.dicebear.com/7.x/thumbs/svg?seed=user&backgroundColor=3b82f6",
            "https://api.dicebear.com/7.x/bottts/svg?seed=docs&backgroundColor=1e40af"
        )
    ),
    textbox=gr.Textbox(
        placeholder="💭 Ask me about your documentation or describe any images...",
        container=False,
        scale=7
    ),
    examples=[
        "🚀 How do I get started with this project?",
        "🖼️ What images are available in the documentation?",
        "📄 Describe the contents of aurora_diagram.png",
        "🔤 Extract text from all images in the docs",
        "⚙️ What configuration options are available?",
        "🔧 How do I troubleshoot connection issues?",
        "📊 Show me OCR analysis of the training images",
        "🎯 What does the Aurora architecture diagram show?"
    ]
)

def main():
    """Main entry point for the enhanced application."""
    print("🚀 Starting Enhanced Docs Navigator MCP...")
    print("🖼️ With Advanced Image Analysis Capabilities")
    print("📚 AI-Powered Documentation Assistant")
    print("🌐 The app will be available at: http://127.0.0.1:7866")
    print("💡 Ask questions about your documentation and images!")
    print("-" * 50)
    
    # Check OCR status
    if OCR_AVAILABLE:
        from enhanced_ocr_processor import get_ocr_status
        status = get_ocr_status()
        if status.get("available"):
            print(f"✅ OCR ready with backends: {', '.join(status.get('available_backends', []))}")
        else:
            print(f"⚠️ OCR issue: {status.get('error', 'Unknown')}")
    else:
        print("⚠️ OCR functionality limited - install enhanced dependencies for full features")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7866,
        show_error=True,
        share=False
    )

if __name__ == "__main__":
    main()