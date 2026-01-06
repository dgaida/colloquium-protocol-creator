# Installation Guide

## System Requirements

- **Python**: 3.9 or higher
- **Operating System**: Linux, macOS, or Windows
- **LaTeX**: LuaLaTeX recommended for full Unicode support
- **API Access**: At least one of:
  - OpenAI API key
  - Groq API key
  - Google Gemini API key
  - Ollama (local installation)

## Quick Start

For most users, the recommended installation method is:

```bash
# Clone repository
git clone https://github.com/dgaida/colloquium-protocol-creator.git
cd colloquium-protocol-creator

# Install in editable mode
pip install -e .

# Configure API keys (see API Setup section)
```

## Installation Methods

### Method 1: For Developers (Recommended)

Install in editable mode to allow modifications to the source code:

```bash
git clone https://github.com/dgaida/colloquium-protocol-creator.git
cd colloquium-protocol-creator
pip install -e .
```

**Benefits:**
- Changes to source code take effect immediately
- Easy to contribute improvements
- All dependencies automatically installed
- Command-line tools (`colloquium-protocol-creator`, `project-grading-letter`) available globally

### Method 2: For Users with pip

Install dependencies from requirements.txt (no editable mode):

```bash
git clone https://github.com/dgaida/colloquium-protocol-creator.git
cd colloquium-protocol-creator
pip install -r requirements.txt
```

**Use case:** You just want to use the tool without modifying the code

### Method 3: With Anaconda/Miniconda

Create an isolated conda environment:

```bash
git clone https://github.com/dgaida/colloquium-protocol-creator.git
cd colloquium-protocol-creator
conda env create -f environment.yml
conda activate colloquium-protocol-creator
```

**Benefits:**
- Isolated environment
- No conflicts with other Python packages
- Reproducible setup

## LaTeX Installation

The tool requires LaTeX for compiling protocol letters and grading forms.

### Linux (Ubuntu/Debian)

```bash
# Full installation (recommended)
sudo apt-get update
sudo apt-get install texlive-full

# Minimal installation
sudo apt-get install texlive-latex-base texlive-latex-extra texlive-luatex
```

### macOS

```bash
# Using Homebrew
brew install --cask mactex

# Or download from: https://www.tug.org/mactex/
```

### Windows

1. Download MiKTeX: https://miktex.org/download
2. Run installer
3. Add MiKTeX to PATH during installation
4. Install missing packages on-the-fly when first compiling

### Verify Installation

```bash
# Check LuaLaTeX
lualatex --version

# Should output: "This is LuaTeX, Version X.X.X"
```

## API Setup

The tool uses [llm_client](https://github.com/dgaida/llm_client) which automatically detects available APIs. You need at least one API configured.

### Configuration File

Create a `secrets.env` file in the project root:

```bash
# Choose one or more APIs

# OpenAI (paid, reliable)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Groq (fast, free tier available)
GROQ_API_KEY=gsk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google Gemini (fast, free tier available)
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Ollama - no key needed (see Ollama section)
```

### API-Specific Setup

#### OpenAI

1. Create account: https://platform.openai.com/signup
2. Add payment method: https://platform.openai.com/account/billing
3. Generate API key: https://platform.openai.com/api-keys
4. Add to `secrets.env`: `OPENAI_API_KEY=sk-...`

**Cost:** ~$0.01-0.05 per thesis (GPT-4o-mini)

#### Groq

1. Create account: https://console.groq.com/signup
2. Generate API key: https://console.groq.com/keys
3. Add to `secrets.env`: `GROQ_API_KEY=gsk-...`

**Cost:** Free tier available (30 requests/minute)

#### Google Gemini

1. Create account: https://aistudio.google.com/
2. Generate API key: https://aistudio.google.com/apikey
3. Add to `secrets.env`: `GEMINI_API_KEY=AIzaSy...`

**Cost:** Free tier available (60 requests/minute)

#### Ollama (Local, Free)

1. Install Ollama:
```bash
# Linux/macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.com/download
```

2. Pull a model:
```bash
ollama pull llama3.2:1b
```

3. No API key needed - tool automatically detects Ollama

**Benefits:**
- Completely free
- No API rate limits
- Data stays local
- No internet required

**Drawbacks:**
- Requires ~4GB RAM
- Slower than cloud APIs
- Quality depends on model size

## Verify Installation

### Test Python Installation

```python
# Run Python and import packages
python3 -c "import pypdf; import docling_parse; import docling_core; print('✓ All dependencies installed')"
```

### Test LLM Client

```python
from llm_client import LLMClient

# This will auto-detect available API
client = LLMClient()
print(f"Using: {client.api_choice} with {client.llm}")

# Test API call
result = client.chat_completion([{"role": "user", "content": "Hello"}])
print(f"✓ API working: {result[:50]}...")
```

### Test Command-Line Tools

```bash
# Test colloquium protocol tool
colloquium-protocol-creator --help

# Test project grading tool
project-grading-letter --help

# Should display help text without errors
```

### Run Example

```bash
# If you have a sample annotated PDF
colloquium-protocol-creator sample_thesis.pdf

# Or run the main.py example
python main.py
```

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'llm_client'`

**Solution:**
```bash
# Reinstall in editable mode
pip install -e .

# Or install llm_client directly
pip install git+https://github.com/dgaida/llm_client.git
```

### LaTeX Not Found

**Problem:** `FileNotFoundError: lualatex not found`

**Solution:**
```bash
# Check if LaTeX is installed
which lualatex

# If not found, install (see LaTeX Installation section)

# Check PATH includes LaTeX
echo $PATH

# Add to PATH if needed (Linux/macOS)
export PATH="/usr/local/texlive/2024/bin/x86_64-linux:$PATH"
```

### API Key Not Working

**Problem:** `Authentication failed` or `Invalid API key`

**Solution:**
```bash
# Verify secrets.env exists
ls secrets.env

# Check format (no spaces around =)
cat secrets.env
# Should be: OPENAI_API_KEY=sk-xxx (no spaces!)

# Test API key manually
python3 -c "from llm_client import LLMClient; c = LLMClient(); print(c.api_choice)"
```

### Ollama Not Detected

**Problem:** Tool doesn't find Ollama even though installed

**Solution:**
```bash
# Check Ollama is running
ollama list

# Start Ollama service
ollama serve &

# Pull a small model
ollama pull llama3.2:1b

# Test
python3 -c "from llm_client import LLMClient; c = LLMClient(api_choice='ollama'); print(c.llm)"
```

### Permission Errors (Linux/macOS)

**Problem:** `Permission denied` when installing

**Solution:**
```bash
# Use --user flag
pip install --user -e .

# Or create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Dependency Conflicts

**Problem:** Package version conflicts

**Solution:**
```bash
# Create fresh virtual environment
python3 -m venv fresh_env
source fresh_env/bin/activate
pip install -e .

# Or use conda
conda create -n cpc python=3.11
conda activate cpc
pip install -e .
```

## Development Setup

### Install Development Dependencies

```bash
# Install with dev extras
pip install -e ".[dev]"

# Or from requirements
pip install -r requirements_dev.txt
```

This installs additional tools:
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking support
- **ruff**: Fast Python linter
- **black**: Code formatter
- **mypy**: Type checker

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=colloquium_creator --cov=colloquium_pipeline

# Run specific test file
pytest tests/test_colloquium_creator.py
```

### Code Quality Checks

```bash
# Format code
black .

# Lint code
ruff check .

# Type check
mypy colloquium_creator --ignore-missing-imports
```

## Updating

### Update Tool

```bash
# Pull latest changes
git pull origin master

# Reinstall (if dependencies changed)
pip install -e .
```

### Update Dependencies

```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update llm_client
pip install --upgrade git+https://github.com/dgaida/llm_client.git
```

## Uninstallation

```bash
# Remove package
pip uninstall colloquium-protocol-creator

# Remove repository
cd ..
rm -rf colloquium-protocol-creator

# Remove conda environment (if used)
conda env remove -n colloquium-protocol-creator
```

## Platform-Specific Notes

### Windows

- Use `python` instead of `python3`
- Use backslashes in paths: `C:\Users\...` or use raw strings: `r"C:\Users\..."`
- PowerShell requires quotes around git URLs: `pip install "git+https://..."`
- MiKTeX may need manual package installation on first run

### macOS

- May need Xcode Command Line Tools: `xcode-select --install`
- If using Apple Silicon (M1/M2), ensure ARM-compatible packages
- Use Homebrew for easiest LaTeX installation

### Linux

- Ubuntu/Debian users should install `python3-pip` if not available
- Some systems need `python3-venv` for virtual environments
- LaTeX installation can be large (4-6 GB for full texlive)

## Docker (Optional)

For reproducible environments:

```dockerfile
FROM python:3.11-slim

# Install LaTeX
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-luatex \
    && rm -rf /var/lib/apt/lists/*

# Install tool
WORKDIR /app
COPY . .
RUN pip install -e .

CMD ["bash"]
```

```bash
# Build and run
docker build -t colloquium-protocol-creator .
docker run -v $(pwd)/data:/data colloquium-protocol-creator \
    colloquium-protocol-creator /data/thesis.pdf
```

## Getting Help

If you encounter issues not covered here:

1. Check [GitHub Issues](https://github.com/dgaida/colloquium-protocol-creator/issues)
2. Check [llm_client documentation](https://github.com/dgaida/llm_client)
3. Open a new issue with:
   - Python version: `python --version`
   - OS and version
   - Installation method used
   - Full error message
   - Steps to reproduce

## Next Steps

After successful installation:

1. Configure your preferred LLM API (see API Setup)
2. Read use case documentation:
   - [Colloquium Protocols](COLLOQUIUM.md)
   - [Project Grading Letters](PROJECT.md)
   - [Peer Review Comments](REVIEW.md)
3. Try the examples in `main.py`, `main_project.py`, or `main_review.py`
4. Annotate a test PDF and run the tool
