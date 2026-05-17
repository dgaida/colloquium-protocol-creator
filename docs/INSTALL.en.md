# Installation Guide

## System Requirements

- **Python**: 3.9 or higher  
- **Operating System**: Linux, macOS, or Windows  
- **LaTeX**: LuaLaTeX recommended for full Unicode support  
- **API Access**: At least one of OpenAI, Groq, Google Gemini, or Ollama  

## Quick Start

```bash
# Clone repository
git clone https://github.com/dgaida/colloquium-protocol-creator.git
cd colloquium-protocol-creator

# Install in editable mode
pip install -e .

# Verify
academic-doc-generator --help
```

## Installation Methods

### Method 1: For Developers (Recommended)

```bash
git clone https://github.com/dgaida/colloquium-protocol-creator.git
cd colloquium-protocol-creator
pip install -e .
```

This makes the unified command `academic-doc-generator` available globally.

### Method 2: With Anaconda/Miniconda

```bash
git clone https://github.com/dgaida/colloquium-protocol-creator.git
cd colloquium-protocol-creator
conda env create -f environment.yml
conda activate colloquium-protocol-creator
pip install -e .
```

## LaTeX Installation

The tool requires LaTeX for compiling protocol letters and grading forms.

### Linux (Ubuntu/Debian)
`sudo apt-get install texlive-full`

### macOS
`brew install --cask mactex`

### Windows
Download [MiKTeX](https://miktex.org/download) and run the installer.

## API Setup

Create a `secrets.env` file in the project root:

```bash
# OpenAI (paid, reliable)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Groq (fast, free tier available)
GROQ_API_KEY=gsk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google Gemini (fast, free tier available)
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Ollama - no key needed
```

## Verify Installation

### Test Command-Line Tool

```bash
academic-doc-generator --help
```

### Test Python Implementation

```python
from llm_client import LLMClient
client = LLMClient()
print(f"Using: {client.api_choice}")
```

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError: No module named 'llm_client'`, ensure you installed in editable mode or install it manually:
`pip install git+https://github.com/dgaida/llm_client.git`

### Command Not Found
If `academic-doc-generator` is not found, ensures your Python scripts directory is in your PATH.

## Development Setup

```bash
# Install with dev extras
pip install -e ".[dev]"

# Run tests
pytest
```

## Next Steps

1. [Colloquium Protocols](COLLOQUIUM.en.md)  
2. [Project Grading Letters](PROJECT.en.md)  
3. [Peer Review Comments](REVIEW.en.md)  
4. [Exam Translation](TRANSLATOR.en.md)  
