# Getting Started with Docs Navigator MCP

Welcome! This guide will walk you through setting up and using the Docs Navigator MCP system step by step. By the end, you'll have a working AI assistant that can answer questions about your documentation.

## 📋 Prerequisites

Before you begin, make sure you have:

- **Python 3.10+** installed on your system
- **An Anthropic API key** (sign up at [console.anthropic.com](https://console.anthropic.com))
- **Command line access** (Terminal on macOS/Linux, Command Prompt on Windows)
- **UV package manager** (recommended) or pip

### Installing UV (Recommended)

UV provides faster dependency management than pip:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 🛠️ Step-by-Step Setup

### Step 1: Get the Code

Clone or download this repository:

```bash
git clone <your-repo-url>
cd docs-navigator
```

### Step 2: Set Up Python Environment

**Using UV (recommended):**
```bash
uv sync
```

**Using pip:**
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Your API Key

Create a `.env` file in the project root:

```bash
# Create the file
touch .env  # On macOS/Linux
# Or just create the file manually on Windows
```

Add your Anthropic API key to the `.env` file:

```
ANTHROPIC_API_KEY= your-actual-api-key-here
```

**Important**: Never commit your `.env` file to version control!

### Step 4: Verify Your API Key

Test that your API key works:

```bash
# Using UV
uv run test_anthropic.py

# Using Python directly
python test_anthropic.py
```

You should see output like:
```
Testing model: claude-3-haiku-20240307
✅ claude-3-haiku-20240307: API working
Done testing models.
```

### Step 5: Add Your Documentation

Place your documentation files in the `docs/` folder. The system supports:

- **Markdown files** (`.md`)
- **Text files** (`.txt`) 
- **reStructuredText files** (`.rst`)

Example structure:
```
docs/
├── getting-started.md
├── api-reference.md
├── troubleshooting.txt
├── faq.md
└── installation.rst
```

**Sample content to try**: The project already includes sample docs you can test with:
- `overview.md`
- `setup.md`
- `troubleshooting.md`
- `prompting-guidelines.md`
- `auroraai_report.txt`

### Step 6: Test the MCP Server

Verify that the MCP server can read your docs:

```bash
# Using UV
uv run test_mcp.py

# Using Python directly
python test_mcp.py
```

Expected output:
```
Connecting to MCP server...
Listing available docs...
Available tools: ['list_docs', 'search_docs']
Available docs: [overview.md, setup.md, ...]
Search results for 'setup': [{"path": "setup.md", "snippet": "..."}]
✅ MCP connection and tools working correctly!
```

### Step 7: Test End-to-End Functionality

Run a complete test:

```bash
# Using UV
uv run test_complete.py

# Using Python directly
python test_complete.py
```

This will ask the AI a question about your docs and show you the response.

### Step 8: Launch the Web Interface

Start the Gradio app:

```bash
# Using UV
uv run app_gradio.py

# Using Python directly
python app_gradio.py
```

You'll see:
```
* Running on local URL:  http://127.0.0.1:7860
* To create a public link, set `share=True` in `launch()`.
```

Open http://127.0.0.1:7860 in your browser.

## 💬 Using the Chat Interface

Once the web interface opens, you can:

### Example Questions to Try:

1. **Discovery**: "What documentation do you have available?"

2. **Specific lookup**: "How do I set up authentication?"

3. **Troubleshooting**: "What should I do if I get connection errors?"

4. **Summarization**: "Give me an overview of the main features"

5. **Search**: "Find information about API endpoints"

### How It Works:

1. **You ask a question** in the chat interface
2. **The AI agent** receives your question
3. **MCP tools search** through your documentation files
4. **Claude AI analyzes** the search results
5. **You get an answer** with references to source files

## 🔍 Understanding the Components

### Files You'll Work With:

- **`app_gradio.py`**: The web interface (you probably won't need to modify this)
- **`client_agent.py`**: Connects to Claude AI and MCP server  
- **`server_docs.py`**: Provides document search tools to the AI
- **`docs/`**: Your documentation files go here
- **`.env`**: Your API key and other secrets

### What Happens When You Ask a Question:

```
Your Question → Gradio → Client Agent → Claude AI
                                         ↓
                                    "I need to search docs"
                                         ↓
                                    MCP Server → docs/ folder
                                         ↓
                                    Search Results
                                         ↓
                               Claude AI (generates answer)
                                         ↓
                              Gradio → Your Answer
```

## ⚙️ Customization Options

### Change the AI Model

Edit `client_agent.py` and modify the model name:

```python
model="claude-3-haiku-20240307"  # Current model
model="claude-3-5-sonnet-20241022"  # Higher quality (requires API access)
```

### Change the Port

Edit `app_gradio.py`:

```python
demo.launch()  # Default port 7860
demo.launch(server_port=8080)  # Custom port
```

### Add More File Types

Edit `server_docs.py`:

```python
exts = {".md", ".txt", ".rst"}  # Current formats
exts = {".md", ".txt", ".rst", ".pdf", ".docx"}  # Add more (requires additional code)
```

## 🐛 Troubleshooting Common Issues

### "Model not found" Error

**Problem**: Your API key doesn't have access to the specified Claude model.

**Solution**: The system will automatically test and find a working model. If this fails, check that your API key is valid.

### "No such file or directory" Error

**Problem**: Python path or virtual environment issues.

**Solution**: 
```bash
# Make sure you're in the right directory
pwd  # Should show /path/to/docs-navigator

# Make sure virtual environment is activated
which python  # Should show .venv path
```

### No Documents Found

**Problem**: The system can't find your documentation files.

**Solution**: 
- Check that files are in the `docs/` folder
- Verify file extensions (`.md`, `.txt`, `.rst`)
- Check file permissions

### Port Already in Use

**Problem**: Port 7860 is already taken.

**Solution**: 
- Stop other applications using the port
- Or change the port in `app_gradio.py`

### Connection Refused

**Problem**: MCP server can't start.

**Solution**:
- Check that `server_docs.py` is executable
- Verify all dependencies are installed
- Check for Python syntax errors

## 📈 Next Steps

Once you have the basic system working:

1. **Add more documentation**: Populate the `docs/` folder with your content

2. **Customize prompts**: Modify the system prompts in `client_agent.py` to better suit your use case

3. **Improve search**: Enhance the search functionality in `server_docs.py`

4. **Add more tools**: Create additional MCP tools for specific documentation tasks

5. **Deploy**: Set up the system on a server for team access

## 💡 Tips for Better Results

### Organizing Your Docs:

- Use clear, descriptive filenames
- Include section headings in markdown
- Keep related information in the same file
- Use consistent terminology

### Writing Good Questions:

- Be specific about what you need
- Reference topics from your documentation
- Ask for examples when appropriate
- Request sources for verification

### Optimizing Performance:

- Keep individual doc files reasonably sized
- Use markdown headers for better structure
- Remove irrelevant or outdated content
- Test questions regularly to improve prompts

## 🆘 Getting Help

If you run into issues:

1. **Check the test scripts**: Run `test_mcp.py` and `test_anthropic.py`
2. **Review the logs**: Look for error messages in the terminal
3. **Verify your setup**: Double-check API keys and file paths
4. **Start fresh**: Create a new virtual environment if needed

## 🎉 Success!

You should now have a working documentation assistant! The AI can search through your docs and provide intelligent answers to your questions.

Try asking: "What can you help me with?" to get started!