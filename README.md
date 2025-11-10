# Colloquium Protocol Creator

**Project name:** colloquium-protocol-creator

**Short:** Create a LaTeX protocol letter for a thesis colloquium by extracting annotations and producing a template with rewritten questions.

## Application scenario 
When grading a thesis, you may annotate the PDF with comments that reflect the questions you want to ask in the colloquium. This tool can then help by automatically generating a LaTeX letter template to accompany the official assessment form. The generated letter includes:

- Your annotated questions, rewritten by an LLM into clear and well-phrased questions.
- A summary of the thesis based on its first pages.
- The student's name, matriculation number, and the thesis title.

This way, you receive a ready-to-use protocol template for the colloquium.

**Important:** This project **does not grade** a thesis. It extracts comments/annotations from a thesis PDF, rewrites them into clearer questions using a language model, summarizes the thesis (first pages), and generates a LaTeX template that can be used for the colloquium's protocol.

## Features
- 🔍 **Multiple LLM Support** - Works with OpenAI, Groq, Google Gemini, or Ollama
- 🤖 **Automatic API Detection** - Uses available API keys or falls back to local Ollama
- 📄 **PDF Annotation Extraction** - Extract text and annotation positions with Docling + PyPDF
- 🎯 **Context-Aware Rewriting** - Maps annotations to exact highlighted words and paragraph context
- ✍️ **Question Refinement** - Rewrites terse comments (e.g. "Why?") to full, polite questions
- 📝 **LaTeX Generation** - Creates `scrlttr2` letters with TH Köln footer
- 🔧 **PDF Compilation** - Optionally compiles to PDF (LuaLaTeX recommended)
- 🌐 **Unicode Support** - Handles Unicode dashes and German `ß` for LaTeX-safe output
- 📊 **Project Work Support** - Generate grading letters for project work (Praxisprojekt)
- 📖 **Peer Review Support** - Generate peer reviews for journal/conference papers

## Quickstart

1. Clone repo and install dependencies:
```bash
pip install -e .
```

2. The tool uses the universal [llm_client](https://github.com/dgaida/llm_client) which automatically detects available APIs:

   - **OpenAI**: Set `OPENAI_API_KEY` in `secrets.env` or environment
   - **Groq**: Set `GROQ_API_KEY` in `secrets.env` or environment  
   - **Google Gemini**: Set `GEMINI_API_KEY` in `secrets.env` or environment
   - **Ollama**: No API key needed, runs locally (requires [Ollama installation](https://ollama.com/))

3. Run the CLI:
```bash
colloquium-protocol-creator /path/to/Bachelorarbeit_xy.pdf
```

Or specify the API explicitly:
```bash
colloquium-protocol-creator /path/to/Bachelorarbeit_xy.pdf --api gemini --model gemini-2.0-flash-exp
```

A `bewertung_brief_matrikelnr.tex` (and `.pdf` if compilation succeeds) will be written into the thesis folder.

### Project Work Grading Letters

Generate grading letters for project work (Praxisprojekt):

```bash
project-grading-letter /path/to/Praxisprojekt.pdf
```

Or via Python:
```python
from llm_client import LLMClient
from project_pipeline import orchestrator

client = LLMClient()  # Auto-detects available API
tex, pdf = orchestrator.run_project_pipeline(
    pdf_path="Praxisprojekt_Mueller.pdf",
    llm_client=client
)
```

### Peer Review Support

Generate peer reviews for papers:

```python
from llm_client import LLMClient
from review_pipeline import orchestrator

client = LLMClient()
md_path = orchestrator.run_review_pipeline(
    pdf_path="paper.pdf",
    llm_client=client
)
```

## Installation

You can install the project either with **pip** or with **Anaconda/Miniconda**.  

### Option 1: For developers (recommended)

Clone the repository and install in editable mode. This will pick up all dependencies
from `pyproject.toml` and let you make changes to the source code without reinstalling:

```bash
git clone https://github.com/dgaida/colloquium-protocol-creator.git
cd colloquium-protocol-creator
pip install -e .
```

### Option 2: For users with pip
If you just want to use the tool without editing the source code, install the dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

### Option 3: With Anaconda/Miniconda
If you prefer conda, use the provided environment.yml:

```bash
conda env create -f environment.yml
conda activate colloquium-protocol-creator
```

## Requirements
- Python 3.9+
- [TeX](https://www.latex-project.org/get/) (LuaLaTeX recommended for full Unicode)
- At least one of:
  - [OpenAI API key](https://platform.openai.com/api-keys)
  - [Groq API key](https://console.groq.com/keys)
  - [Google Gemini API key](https://aistudio.google.com/apikey)
  - [Ollama](https://ollama.com/) (local, no API key needed)
- Python packages (automatically installed):
  - [llm-client](https://github.com/dgaida/llm_client) - Universal LLM interface
  - [docling-parse](https://pypi.org/project/docling-parse/)
  - [docling-core](https://pypi.org/project/docling-core/)
  - [pypdf](https://pypi.org/project/pypdf/)

## Configuration

### API Keys Setup

Create a `secrets.env` file in the project root:

```bash
# Choose one or more APIs (tool will auto-select based on availability)

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxx

# Groq (fast, free tier available)
GROQ_API_KEY=gsk-xxxxxxxx

# Google Gemini
GEMINI_API_KEY=AIzaSy-xxxxxxxx

# Ollama - no key needed (local installation required)
```

### Supported APIs

| API | Default Model | API Key Required | Notes |
|-----|---------------|------------------|-------|
| OpenAI | `gpt-4o-mini` | Yes | Reliable, paid |
| Groq | `moonshotai/kimi-k2-instruct-0905` | Yes | Very fast, free tier |
| Google Gemini | `gemini-2.0-flash-exp` | Yes | Fast, free tier |
| Ollama | `llama3.2:1b` | No | Runs locally |

The tool automatically selects the best available API based on your configuration.

## Usage Examples

### Basic Usage (Auto API Detection)

```python
from llm_client import LLMClient
from colloquium_pipeline import orchestrator

# LLMClient auto-detects available API
client = LLMClient()
print(f"Using: {client.api_choice} with {client.llm}")

tex, pdf = orchestrator.run_pipeline(
    pdf_path="Bachelorarbeit_Mueller.pdf",
    llm_client=client,
    groq_free=True  # Enable rate limiting if using free tier
)
```

### Specify API and Model

```python
from llm_client import LLMClient
from colloquium_pipeline import orchestrator

# Use Google Gemini explicitly
client = LLMClient(
    api_choice="gemini",
    llm="gemini-2.0-flash-exp",
    temperature=0.7
)

tex, pdf = orchestrator.run_pipeline(
    pdf_path="Masterarbeit_Schmidt.pdf",
    llm_client=client
)
```

### Command Line with Options

```bash
# Use specific API
colloquium-protocol-creator thesis.pdf --api gemini --model gemini-2.0-flash-exp

# Without PDF compilation
colloquium-protocol-creator thesis.pdf --no-compile

# With custom output folder
colloquium-protocol-creator thesis.pdf --out ./output

# With rate limiting (free tier)
colloquium-protocol-creator thesis.pdf --groq-free
```

## Project Structure

```
colloquium-protocol-creator/
├── colloquium_creator/          # Core functionality
│   ├── pdf_processing.py        # PDF text & annotation extraction
│   ├── llm_interface.py         # LLM interaction (via llm_client)
│   ├── latex_generation.py      # LaTeX generation & compilation
│   └── utils.py                 # Helper functions
├── colloquium_pipeline/         # Orchestration
│   ├── orchestrator.py          # Main pipeline
│   └── cli.py                   # Command-line interface
├── project_creator/             # Project work grading letters
│   ├── llm_interface.py         # Metadata extraction & gender detection
│   └── latex_generation.py      # Project letter generation
├── project_pipeline/            # Project work orchestration
│   ├── orchestrator.py
│   └── cli.py
├── review_creator/              # Peer review support
│   └── md_generator.py          # Markdown review generation
├── review_pipeline/             # Review orchestration
│   └── orchestrator.py
├── main.py                      # Example: Thesis colloquium
├── main_project.py              # Example: Project work
├── main_review.py               # Example: Peer review
├── pyproject.toml              # Package configuration
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## How It Works

### Colloquium Protocol Generation

1. **Extract PDF Annotations**: Uses Docling to parse PDF structure and PyPDF to extract annotations with positions
2. **Context Mapping**: Matches annotations to exact highlighted text and surrounding paragraphs
3. **LLM Rewriting**: Rewrites rough annotations into clear, polite questions using configured LLM
4. **Metadata Extraction**: Extracts student name, matriculation number, thesis title, and examiner names
5. **Thesis Summary**: Generates a concise summary from the first 10 pages
6. **LaTeX Generation**: Creates a formal letter with TH Köln formatting
7. **PDF Compilation**: Optionally compiles the LaTeX file to PDF

### Project Work Grading

1. **Metadata Extraction**: Reads student info from project title page
2. **Gender Detection**: Automatically determines formal address (Herr/Frau) from first name
3. **Semester Calculation**: Auto-detects current semester (WS/SoSe) based on date
4. **Letter Generation**: Creates LaTeX grading letter with placeholders for grade

### Peer Review Generation

1. **Annotation Extraction**: Extracts review comments with line numbers
2. **Comment Refinement**: Rewrites informal notes into professional reviewer feedback
3. **Markdown Output**: Generates formatted review document with page/line references

## Advanced Configuration

### Custom LLM Parameters

```python
from llm_client import LLMClient

client = LLMClient(
    api_choice="openai",
    llm="gpt-4o",
    temperature=0.5,      # Lower = more deterministic
    max_tokens=2048       # Longer responses
)
```

### Rate Limiting for Free Tiers

```python
# Enable throttling for Groq free tier
tex, pdf = orchestrator.run_pipeline(
    pdf_path="thesis.pdf",
    llm_client=client,
    groq_free=True  # Adds delays between API calls
)
```

### Ollama Local Usage

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.2:1b

# Use without any API keys
colloquium-protocol-creator thesis.pdf
```

## License
This project is released under the MIT License (see LICENSE).

## Related Projects

- [llm_client](https://github.com/dgaida/llm_client) - Universal Python LLM client (OpenAI, Groq, Gemini, Ollama)

## Disclaimer
This tool aids in producing a protocol template for the colloquium — it does not grade or make evaluative decisions automatically.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/dgaida/colloquium-protocol-creator/issues) page
2. Open a new issue with details about your problem
3. Include your Python version, OS, and API choice

## Acknowledgments

- Uses [Docling](https://github.com/DS4SD/docling) for PDF processing
- LaTeX template based on KOMA-Script's `scrlttr2` class
