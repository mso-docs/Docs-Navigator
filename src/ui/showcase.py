# gradio_ui_showcase.py
"""
Showcase different Gradio UI/UX options for the Docs Navigator
Run with: python gradio_ui_showcase.py [style_name]

Available styles:
- modern: Modern, clean design with animations
- dark: Dark theme professional interface  
- minimal: Minimal, distraction-free design
- corporate: Enterprise/business-focused styling
- glassmorphism: Modern glass-effect design
"""

import gradio as gr
from client_agent import answer_sync
import sys


def chat_fn(message: str, history: list[dict]):
    """Enhanced chat function"""
    try:
        if not message.strip():
            return "Please enter a question about the documentation."
        reply = answer_sync(message)
        return reply
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


def create_modern_interface():
    """Modern, animated interface with gradient backgrounds"""
    modern_css = """
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    .gradio-container {
        font-family: 'Poppins', sans-serif !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        min-height: 100vh !important;
    }
    
    .main-wrap {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        margin: 20px !important;
        padding: 30px !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25) !important;
    }
    
    .title {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
    }
    
    .chat-message {
        animation: slideIn 0.5s ease-out !important;
        margin: 10px 0 !important;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .input-wrap {
        border-radius: 25px !important;
        background: white !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1) !important;
        border: none !important;
    }
    
    .send-button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border: none !important;
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        transition: all 0.3s ease !important;
    }
    
    .send-button:hover {
        transform: scale(1.1) !important;
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4) !important;
    }
    """
    
    return gr.ChatInterface(
        fn=chat_fn,
        type="messages",
        title="✨ Docs Navigator AI",
        description="**Modern AI Documentation Assistant** - Powered by cutting-edge AI technology",
        css=modern_css,
        theme=gr.themes.Soft(),
        chatbot=gr.Chatbot(height=450, show_label=False),
        examples=["🚀 Quick Start Guide", "⚙️ Configuration", "🔍 Advanced Features"]
    )


def create_dark_interface():
    """Professional dark theme interface"""
    dark_css = """
    .gradio-container {
        background: #0f172a !important;
        color: #e2e8f0 !important;
    }
    
    .main-wrap, .panel {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
    }
    
    .chatbot {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
    }
    
    .message-wrap {
        background: #334155 !important;
        border-radius: 8px !important;
        margin: 8px !important;
        padding: 12px !important;
    }
    
    .user-message {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
        color: white !important;
    }
    
    .input-container textarea {
        background: #334155 !important;
        border: 1px solid #475569 !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
    }
    
    .input-container textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }
    """
    
    return gr.ChatInterface(
        fn=chat_fn,
        type="messages",
        title="🌙 Docs Navigator - Dark Mode",
        description="**Professional Dark Theme** - Easy on the eyes, powerful AI assistance",
        css=dark_css,
        theme=gr.themes.Monochrome().set(
            body_background_fill="#0f172a",
            panel_background_fill="#1e293b"
        ),
        chatbot=gr.Chatbot(height=450, show_label=False),
        examples=["📚 Documentation Overview", "🛠️ Setup Instructions", "❓ FAQ"]
    )


def create_minimal_interface():
    """Ultra-minimal, distraction-free interface"""
    minimal_css = """
    .gradio-container {
        max-width: 800px !important;
        margin: 0 auto !important;
        padding: 20px !important;
    }
    
    * {
        border-radius: 4px !important;
    }
    
    .title {
        font-size: 1.5rem !important;
        font-weight: 400 !important;
        color: #374151 !important;
        text-align: center !important;
        margin-bottom: 2rem !important;
    }
    
    .chatbot {
        border: 1px solid #e5e7eb !important;
        box-shadow: none !important;
    }
    
    .input-container {
        border: 1px solid #d1d5db !important;
        background: white !important;
    }
    """
    
    return gr.ChatInterface(
        fn=chat_fn,
        type="messages",
        title="Docs Navigator",
        description="Simple documentation assistant",
        css=minimal_css,
        theme=gr.themes.Base(),
        chatbot=gr.Chatbot(height=400, show_label=False),
        textbox=gr.Textbox(placeholder="Ask about docs...", container=False),
        examples=["Setup", "Config", "Help"]
    )


def create_corporate_interface():
    """Enterprise/business-focused styling"""
    corporate_css = """
    .gradio-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        background: #f8fafc !important;
    }
    
    .main-wrap {
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 24px !important;
        margin: 16px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1) !important;
    }
    
    .title {
        color: #1a202c !important;
        font-size: 1.875rem !important;
        font-weight: 600 !important;
        text-align: center !important;
        margin-bottom: 0.5rem !important;
    }
    
    .description {
        color: #4a5568 !important;
        text-align: center !important;
        margin-bottom: 2rem !important;
    }
    
    .chatbot {
        border: 1px solid #e2e8f0 !important;
        border-radius: 6px !important;
        background: #ffffff !important;
    }
    
    .input-container {
        border: 1px solid #cbd5e0 !important;
        border-radius: 6px !important;
        background: white !important;
    }
    
    .submit-button {
        background: #3182ce !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
    }
    
    .submit-button:hover {
        background: #2c5aa0 !important;
    }
    """
    
    return gr.ChatInterface(
        fn=chat_fn,
        type="messages",
        title="Enterprise Documentation Assistant",
        description="Professional AI-powered documentation system for enterprise environments",
        css=corporate_css,
        theme=gr.themes.Default().set(
            primary_hue="blue",
            secondary_hue="slate",
            neutral_hue="gray"
        ),
        chatbot=gr.Chatbot(height=450, show_label=False),
        examples=[
            "System Documentation",
            "API Reference",
            "Implementation Guide",
            "Security Protocols"
        ]
    )


def create_glassmorphism_interface():
    """Modern glass-effect design"""
    glass_css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        min-height: 100vh !important;
    }
    
    .gradio-container {
        font-family: 'Inter', sans-serif !important;
        background: transparent !important;
    }
    
    .main-wrap {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
        margin: 20px !important;
        padding: 30px !important;
        box-shadow: 
            0 8px 32px 0 rgba(31, 38, 135, 0.37),
            inset 0 1px 1px 0 rgba(255, 255, 255, 0.3) !important;
    }
    
    .title {
        color: white !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        font-size: 2.25rem !important;
        font-weight: 600 !important;
        text-align: center !important;
        margin-bottom: 1rem !important;
    }
    
    .description {
        color: rgba(255, 255, 255, 0.9) !important;
        text-align: center !important;
        font-size: 1.1rem !important;
        margin-bottom: 2rem !important;
    }
    
    .chatbot, .panel {
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
    }
    
    .input-container {
        background: rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
    }
    
    .input-container textarea {
        background: transparent !important;
        color: white !important;
        border: none !important;
    }
    
    .input-container textarea::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    .message-wrap {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(5px) !important;
        border-radius: 10px !important;
        margin: 8px !important;
        padding: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .user-message {
        background: rgba(59, 130, 246, 0.3) !important;
        color: white !important;
    }
    """
    
    return gr.ChatInterface(
        fn=chat_fn,
        type="messages",
        title="🔮 Docs Navigator Glass",
        description="Experience the future of documentation with glassmorphism design",
        css=glass_css,
        theme=gr.themes.Glass(),
        chatbot=gr.Chatbot(height=450, show_label=False),
        examples=["✨ Modern Features", "🎨 Design System", "🔧 Advanced Config"]
    )


if __name__ == "__main__":
    # Get style from command line or default to modern
    style = sys.argv[1] if len(sys.argv) > 1 else "modern"
    
    interfaces = {
        "modern": create_modern_interface,
        "dark": create_dark_interface,
        "minimal": create_minimal_interface,
        "corporate": create_corporate_interface,
        "glassmorphism": create_glassmorphism_interface
    }
    
    if style not in interfaces:
        print(f"Available styles: {', '.join(interfaces.keys())}")
        style = "modern"
    
    print(f"🎨 Launching {style} interface...")
    demo = interfaces[style]()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        show_error=True
    )