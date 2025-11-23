# app_gradio_enhanced.py
import gradio as gr
from client_agent import answer_sync


def chat_fn(message: str, history: list[dict]):
    """Enhanced chat function with better error handling"""
    try:
        reply = answer_sync(message)
        return reply
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# Custom CSS for professional styling
custom_css = """
/* Main container styling */
.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto !important;
}

/* Header styling */
.header-text {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    font-weight: bold;
    margin-bottom: 1rem;
}

/* Chat message styling */
.message-wrap {
    border-radius: 12px !important;
    margin: 8px 0 !important;
    padding: 12px 16px !important;
}

.user-message {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
}

.bot-message {
    background: #f8f9fa !important;
    border-left: 4px solid #667eea !important;
}

/* Input styling */
.input-container {
    border-radius: 25px !important;
    border: 2px solid #e9ecef !important;
    transition: all 0.3s ease !important;
}

.input-container:focus-within {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}

/* Button styling */
.submit-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    border-radius: 20px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.submit-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
}

/* Status indicators */
.status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 500;
}

.status-online {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

/* Loading animation */
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.loading {
    animation: pulse 1.5s infinite;
}

/* Responsive design */
@media (max-width: 768px) {
    .gradio-container {
        padding: 10px !important;
    }
    
    .message-wrap {
        margin: 4px 0 !important;
        padding: 8px 12px !important;
    }
}

/* Dark mode support */
.dark .bot-message {
    background: #2d3748 !important;
    color: #e2e8f0 !important;
    border-left-color: #667eea !important;
}

.dark .input-container {
    background: #2d3748 !important;
    border-color: #4a5568 !important;
    color: #e2e8f0 !important;
}
"""


def create_enhanced_interface():
    """Create an enhanced Gradio interface with professional styling"""
    
    with gr.Blocks(
        css=custom_css,
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="purple",
            neutral_hue="slate",
            font=[
                gr.themes.GoogleFont("Inter"),
                "ui-sans-serif", 
                "system-ui", 
                "sans-serif"
            ]
        ),
        title="📚 Docs Navigator - AI-Powered Documentation Assistant",
        analytics_enabled=False
    ) as interface:
        
        # Header section
        with gr.Row():
            gr.Markdown(
                """
                # 📚 Docs Navigator MCP
                ### AI-Powered Documentation Assistant
                
                Ask questions about your documentation and get intelligent, contextual answers powered by Claude and MCP.
                """,
                elem_classes=["header-text"]
            )
        
        # Status indicator
        with gr.Row():
            gr.HTML(
                """
                <div class="status-indicator status-online">
                    <span>🟢</span>
                    <span>MCP Server Connected</span>
                </div>
                """,
                visible=True
            )
        
        # Main chat interface
        chat = gr.ChatInterface(
            fn=chat_fn,
            type="messages",
            chatbot=gr.Chatbot(
                height=500,
                show_label=False,
                container=True,
                bubble_full_width=False,
                avatar_images=(
                    "https://api.dicebear.com/7.x/thumbs/svg?seed=user&backgroundColor=667eea",
                    "https://api.dicebear.com/7.x/bottts/svg?seed=bot&backgroundColor=764ba2"
                )
            ),
            textbox=gr.Textbox(
                placeholder="Ask me anything about your documentation... 💭",
                container=False,
                scale=7,
                elem_classes=["input-container"]
            ),
            submit_btn=gr.Button(
                "Send 🚀", 
                variant="primary",
                elem_classes=["submit-btn"]
            ),
            retry_btn=gr.Button("🔄 Retry", variant="secondary"),
            undo_btn=gr.Button("↩️ Undo", variant="secondary"),
            clear_btn=gr.Button("🗑️ Clear", variant="secondary"),
            examples=[
                "How do I set up AuroraAI?",
                "What are the troubleshooting steps for connection issues?",
                "Tell me about the configuration options",
                "What does the overview documentation say?",
                "How do I get started with this project?"
            ]
        )
        
        # Footer section
        with gr.Row():
            gr.Markdown(
                """
                ---
                <div style="text-align: center; color: #6c757d; font-size: 14px; margin-top: 20px;">
                    <p>
                        🔧 Powered by <strong>Model Context Protocol (MCP)</strong> | 
                        🤖 <strong>Claude AI</strong> | 
                        🎨 <strong>Gradio</strong>
                    </p>
                    <p style="font-size: 12px; margin-top: 10px;">
                        💡 Tip: Ask specific questions about your documentation for the best results!
                    </p>
                </div>
                """,
                elem_classes=["footer"]
            )
    
    return interface


# Create the demo with different styling options
def create_minimal_interface():
    """Create a minimal, clean interface"""
    return gr.ChatInterface(
        fn=chat_fn,
        type="messages",
        title="📚 Docs Navigator",
        description="Clean, minimal documentation assistant",
        theme=gr.themes.Monochrome(),
        chatbot=gr.Chatbot(height=400, show_label=False),
        textbox=gr.Textbox(placeholder="Ask about your docs...", container=False),
        examples=["Setup guide", "Troubleshooting", "Configuration"]
    )


def create_corporate_interface():
    """Create a corporate/professional interface"""
    corporate_theme = gr.themes.Default(
        primary_hue="slate",
        secondary_hue="blue",
        neutral_hue="gray"
    ).set(
        body_background_fill="white",
        panel_background_fill="*neutral_50",
        button_primary_background_fill="*primary_600"
    )
    
    return gr.ChatInterface(
        fn=chat_fn,
        type="messages",
        title="Documentation Assistant",
        description="Enterprise AI Documentation System",
        theme=corporate_theme,
        chatbot=gr.Chatbot(
            height=450, 
            show_label=False,
            bubble_full_width=False
        ),
        textbox=gr.Textbox(
            placeholder="Enter your documentation question...",
            container=False
        )
    )


if __name__ == "__main__":
    import sys
    
    # Choose interface style based on command line argument
    style = sys.argv[1] if len(sys.argv) > 1 else "enhanced"
    
    if style == "minimal":
        demo = create_minimal_interface()
    elif style == "corporate":
        demo = create_corporate_interface()
    else:  # enhanced (default)
        demo = create_enhanced_interface()
    
    # Launch with professional settings
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False,
        favicon_path=None,  # You can add a custom favicon here
        ssl_verify=False,
        show_tips=True
    )