# Colloquium Protocol Creator

**Create LaTeX protocol letters and grading documents for academic work at TH Köln**

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/dgaida/colloquium-protocol-creator/branch/master/graph/badge.svg)](https://codecov.io/gh/dgaida/colloquium-protocol-creator)
[![Tests](https://github.com/dgaida/colloquium-protocol-creator/actions/workflows/tests.yml/badge.svg)](https://github.com/dgaida/colloquium-protocol-creator/actions/workflows/tests.yml)
[![Code Quality](https://github.com/dgaida/colloquium-protocol-creator/actions/workflows/lint.yml/badge.svg)](https://github.com/dgaida/colloquium-protocol-creator/actions/workflows/lint.yml)
[![CodeQL](https://github.com/dgaida/colloquium-protocol-creator/actions/workflows/codeql.yml/badge.svg)](https://github.com/dgaida/colloquium-protocol-creator/actions/workflows/codeql.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## What Is This?

A tool that transforms annotated PDFs into professional LaTeX documents using AI. Extract your PDF annotations, rewrite them into clear questions or feedback, and generate formatted letters automatically.

## Three Use Cases

### 1. 📝 Thesis Colloquium Protocols

Generate formal protocol letters for Bachelor/Master thesis colloquiums:
- Extract and rewrite your rough annotations into clear, polite questions
- Auto-detect student metadata (name, matriculation number, thesis title)
- Generate thesis summary from first pages
- Create LaTeX letter with TH Köln formatting
- Pre-fill official grading forms with dates and checkboxes

[**→ Full Documentation**](docs/COLLOQUIUM.md)

```bash
colloquium-protocol-creator /path/to/Bachelorarbeit.pdf
```

### 2. 🎓 Project Work Grading Letters

Generate grading letters for project work (Praxisprojekt):
- Auto-extract project metadata from title page
- Detect appropriate formal address (Herr/Frau) from student's first name
- Auto-calculate current semester (WS/SoSe)
- Create LaTeX grading letter template

[**→ Full Documentation**](docs/PROJECT.md)

```bash
project-grading-letter /path/to/Praxisprojekt.pdf
```

### 3. 📄 Peer Review Comments

Generate professional peer review feedback for papers:
- Extract and rewrite informal reviewer notes into constructive feedback
- Auto-detect line numbers from PDF margins
- Generate Markdown review document with page/line references
- Always output in English for international publications

[**→ Full Documentation**](docs/REVIEW.md)

```python
from llm_client import LLMClient
from review_pipeline import orchestrator

client = LLMClient()
md_file = orchestrator.run_review_pipeline("paper.pdf", client)
```

## Key Features

- 🔍 **Multiple LLM Support** - Works with OpenAI, Groq, Google Gemini, or Ollama
- 🤖 **Automatic API Detection** - Uses available API keys or falls back to local Ollama
- 📄 **PDF Annotation Extraction** - Extract text and annotation positions with Docling + PyPDF
- 🎯 **Context-Aware Rewriting** - Maps annotations to exact highlighted text and paragraphs
- ✍️ **Intelligent Comment Refinement** - Rewrites terse notes (e.g., "Why?") into full questions
- 📝 **LaTeX Generation** - Creates `scrlttr2` letters with TH Köln footer
- 📋 **PDF Form Pre-filling** - Auto-fills official grading forms
- 🔧 **PDF Compilation** - Optionally compiles to PDF (LuaLaTeX recommended)
- 🌐 **Unicode Support** - Handles Unicode dashes and German `ß` for LaTeX-safe output

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/dgaida/colloquium-protocol-creator.git
cd colloquium-protocol-creator

# Install
pip install -e .
```

[**→ Full Installation Guide**](docs/INSTALL.md)

### API Configuration

Create `secrets.env` in project root with at least one API key:

```bash
# Choose one or more
OPENAI_API_KEY=sk-xxxxxxxx          # Paid, reliable
GROQ_API_KEY=gsk-xxxxxxxx           # Free tier available
GEMINI_API_KEY=AIzaSy-xxxxxxxx      # Free tier available
# Or use Ollama (no key needed)
```

### Usage Example

```python
from llm_client import LLMClient
from colloquium_pipeline import orchestrator

# Auto-detects available API
client = LLMClient()

# Generate protocol letter
tex, pdf = orchestrator.run_pipeline(
    pdf_path="thesis.pdf",
    date_colloquium="15.01.2026",
    uhrzeit_colloquium="10:00",
    llm_client=client
)
```

## Requirements

- **Python**: 3.9 or higher
- **LaTeX**: LuaLaTeX recommended (for Unicode support)
- **LLM API**: At least one of:
  - [OpenAI API](https://platform.openai.com/api-keys) (paid)
  - [Groq API](https://console.groq.com/keys) (free tier)
  - [Google Gemini API](https://aistudio.google.com/apikey) (free tier)
  - [Ollama](https://ollama.com/) (local, free)

## Supported APIs

| API | Default Model | API Key Required | Notes |
|-----|---------------|------------------|-------|
| OpenAI | `gpt-4o-mini` | Yes | Reliable, ~$0.01-0.05/thesis |
| Groq | `moonshotai/kimi-k2-instruct-0905` | Yes | Very fast, free tier (30 req/min) |
| Google Gemini | `gemini-2.0-flash-exp` | Yes | Fast, free tier (60 req/min) |
| Ollama | `llama3.2:1b` | No | Runs locally, completely free |

The tool automatically selects the best available API based on your configuration.

## Documentation

### Use Cases
- [📝 Thesis Colloquium Protocols](docs/COLLOQUIUM.md)
- [🎓 Project Work Grading Letters](docs/PROJECT.md)
- [📄 Peer Review Comments](docs/REVIEW.md)

### Guides
- [💿 Installation Guide](docs/INSTALL.md)
- [🧪 Testing Guide](docs/TESTING.md)

## Project Structure

```
colloquium-protocol-creator/
├── src/
│   ├── colloquium_creator/      # Core: PDF processing, LLM, LaTeX
│   ├── colloquium_pipeline/     # Orchestration: Colloquium protocols
│   ├── project_creator/         # Project work grading letters
│   ├── project_pipeline/        # Orchestration: Project letters
│   ├── review_creator/          # Peer review comments
│   └── review_pipeline/         # Orchestration: Reviews
├── docs/                        # Documentation
├── tests/                       # Test suite
├── main.py                      # Example: Thesis colloquium
├── main_project.py              # Example: Project work
├── main_review.py               # Example: Peer review
└── pyproject.toml              # Package configuration
```

## How It Works

### Colloquium Protocols
1. Extract PDF annotations with context (Docling + PyPDF)
2. Categorize comments (LLM, Quelle, Language, Ignore)
3. Rewrite annotations into clear questions (LLM)
4. Extract metadata and summarize thesis
5. Generate LaTeX letter with TH Köln formatting
6. Pre-fill official grading form
7. Optionally compile to PDF

### Project Grading Letters
1. Extract metadata from project title page
2. Determine formal address (Herr/Frau) from first name
3. Auto-calculate current semester
4. Generate LaTeX grading letter
5. Optionally compile to PDF

### Peer Review Comments
1. Extract annotations with line numbers
2. Rewrite informal notes into professional feedback
3. Generate Markdown review document
4. Include page/line references

## Example Outputs

### Thesis Colloquium Letter
```latex
\documentclass[11pt,ngerman,parskip=full]{scrlttr2}
% TH Köln letterhead
\setkomavar{subject}{Bewertung Bachelor Arbeit von Max Mustermann}

% Summary
\textbf{Zusammenfassung der Thesis:}
Die Arbeit behandelt...

% Questions
\textbf{Fragen Prof. Dr. Müller:}
Seite 5: Könnten Sie die Wahl dieser Methodik näher begründen?
Seite 12: Wie verhält sich der Algorithmus bei größeren Datenmengen?
```

### Project Grading Letter
```latex
\setkomavar{subject}{Praxisprojekt Herr Max Mustermann}

Herr Max Mustermann, Matrikelnr. 123456,
hat im SoSe25 sein Praxisprojekt bei mir gemacht. 
Er hat die Note _______ erhalten.

Das Thema war:
Entwicklung einer Mobile App für...
```

### Peer Review Comments
```markdown
# Peer Review

- Page 1, Line 15: This point requires clarification...
- Page 2, Line 42: The explanation could be clearer by...
- Page 3, Line 78: The authors should consider recent work by...
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `pytest`
5. Format code: `black .` and `ruff check .`
6. Submit a pull request

## Related Projects

- [llm_client](https://github.com/dgaida/llm_client) - Universal Python LLM client (OpenAI, Groq, Gemini, Ollama)

## License

This project is released under the MIT License (see [LICENSE](LICENSE)).

## Disclaimer

This tool aids in producing document templates — it does not grade or make evaluative decisions automatically. All academic assessments remain the responsibility of the examiner.

## Support

If you encounter issues:
1. Check the [documentation](docs/)
2. Search [existing issues](https://github.com/dgaida/colloquium-protocol-creator/issues)
3. Open a new issue with:
   - Python version and OS
   - API choice and model
   - Full error message
   - Steps to reproduce

## Acknowledgments

- Uses [Docling](https://github.com/DS4SD/docling) for PDF processing
- LaTeX template based on KOMA-Script's `scrlttr2` class
- LLM interface via [llm_client](https://github.com/dgaida/llm_client)
