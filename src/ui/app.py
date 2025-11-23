# app_gradio.py
import gradio as gr
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.agent.client import answer_sync


def chat_fn(message: str, history: list[dict]):
    """Enhanced chat function with better error handling and user feedback"""
    try:
        if not message.strip():
            return "Please enter a question about the documentation."
        
        reply = answer_sync(message)
        return reply
    except Exception as e:
        return f"⚠️ I encountered an error while processing your question: {str(e)}\n\nPlease try again or rephrase your question."


def main():
    """Main entry point for the application when run via uv."""
    print("🚀 Starting Docs Navigator MCP...")
    print("📚 AI-Powered Documentation Assistant")
    print("🌐 The app will be available at: http://127.0.0.1:7862")
    print("💡 Ask questions about your documentation!")
    print("-" * 50)
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7862,
        show_error=True,
        share=False
    )


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

# Custom CSS for enhanced styling
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

demo = gr.ChatInterface(
    fn=chat_fn,
    type="messages",
    title="📚 Docs Navigator MCP",
    description="🤖 **AI-Powered Documentation Assistant**\n\nAsk questions about your documentation and get intelligent, contextual answers. Powered by Claude AI and Model Context Protocol.",
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
        placeholder="💭 Ask me anything about your documentation...",
        container=False,
        scale=7
    ),
    examples=[
        "🚀 How do I get started with this project?",
        "⚙️ What configuration options are available?", 
        "🔧 How do I troubleshoot connection issues?",
        "📖 Tell me about the setup process",
        "💡 What does the overview documentation explain?",
        "📄 What information is in the PDF documents?",
        "🔤 What is the OCR status and what file types are supported?",
        "🖼️ Extract text from any image files in the documentation",
        "📊 Show me OCR processing results and confidence scores"
    ]
)

if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        show_error=True
    )
