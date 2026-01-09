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
- Extract and rewrite your rough annotations in the thesis into clear, polite questions
- Auto-detect student metadata (name, matriculation number, thesis title)
- Generate thesis summary from first pages
- Create LaTeX letter with TH Köln formatting
- Pre-fill official grading forms with dates and checkboxes
- Generate registration emails for the Prüfungsservice

[**→ Full Documentation**](docs/COLLOQUIUM.md)

```bash
colloquium-protocol-creator --config config_templates/config_colloquium_campus.json
```

### 2. 🎓 Project Work Grading Letters

Generate grading letters for project work (Praxisprojekt):
- Auto-extract project metadata from title page
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
from academic_doc_generator.review import orchestrator

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
- 📧 **Email Generation** - Creates registration emails for colloquium scheduling
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

#### Using JSON Configuration (Recommended)

1. Copy a json template file from `config_templates` into the folder in which the thesis/paper is located.

```bash
# List available templates
colloquium-protocol-creator --list-templates
```

2. Edit the json file.
3. Open `main.py` from the project folder and set `folder`, e.g.: `folder = os.path.join("..", "BachelorThesen", "2025_26_WS", "Musterfrau")`
4. Run `main.py`.
5. All files are being created in the specified folder.

Alternative to steps 3 and 4 if you want to run from cli:

```bash
# Use a configuration template
colloquium-protocol-creator --config path_to_thesis_folder/config_colloquium_campus.json
```

#### Python API (Not Recommended - is used internally)

```python
from llm_client import LLMClient
from academic_doc_generator.colloquium import orchestrator

# Auto-detects available API
client = LLMClient()

# Generate protocol letter, form, and email
tex, pdf, email = orchestrator.run_pipeline(
    pdf_path="thesis.pdf",
    date_colloquium="15.01.2026",
    uhrzeit_colloquium="10:00",
    llm_client=client,
    location_type="campus",
    room="3.217"
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

## Configuration Templates

The tool now supports JSON configuration files for easier workflow management:

### Available Templates

- **`config_colloquium_campus.json`** - Colloquium on campus (requires room number)
- **`config_colloquium_company.json`** - Colloquium at company location
- **`config_colloquium_online.json`** - Online colloquium via Zoom
- **`config_project_template.json`** - Project work grading letter
- **`config_review_template.json`** - Peer review comments

### Configuration Structure

```json
{
  "task": "colloquium",
  "pdf": {
    "filename": "Bachelorarbeit_Mustermann.pdf"
  },
  "colloquium": {
    "date": "20.01.2026",
    "time": "14:00",
    "location_type": "campus",
    "room": "3.217"
  },
  "llm": {
    "api_choice": null,
    "model": null,
    "groq_free": true
  },
  "output": {
    "folder": null,
    "compile_pdf": true,
    "fill_form_only": false
  }
}
```

[**→ Full Configuration Documentation**](config_templates/README.md)

## Documentation

### Use Cases
- [📝 Thesis Colloquium Protocols](docs/COLLOQUIUM.md)
- [🎓 Project Work Grading Letters](docs/PROJECT.md)
- [📄 Peer Review Comments](docs/REVIEW.md)

### Guides
- [💿 Installation Guide](docs/INSTALL.md)
- [🧪 Testing Guide](docs/TESTING.md)
- [⚙️ Configuration Templates](config_templates/README.md)

## Project Structure

```
colloquium-protocol-creator/
├── src/
│   └── academic_doc_generator/
│       ├── core/                    # Core: PDF processing, LLM, LaTeX
│       │   ├── pdf_processing.py
│       │   ├── llm_interface.py
│       │   ├── latex_generation.py
│       │   └── utils.py
│       ├── colloquium/             # Colloquium protocols
│       │   ├── orchestrator.py
│       │   ├── email_generator.py
│       │   └── pdf_form_filler.py
│       ├── project/                # Project work grading letters
│       │   ├── orchestrator.py
│       │   ├── latex_generation.py
│       │   └── llm_interface.py
│       ├── review/                 # Peer review comments
│       │   ├── orchestrator.py
│       │   ├── md_generator.py
│       │   └── __init__.py
│       ├── config_loader.py        # JSON configuration loader
│       └── cli.py                  # Unified CLI entry point
├── config_templates/               # JSON configuration templates
├── docs/                          # Documentation
├── tests/                         # Test suite
├── main.py                        # Example: Thesis colloquium
└── pyproject.toml                 # Package configuration
```

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

### Colloquium Registration Email
```markdown
Lieber Prüfungsservice,
hiermit möchte ich Herr Max Mustermann (123456) zum Kolloquium anmelden. 
Dieses findet statt am:
Montag, 20.01.2026, um 14:00,
in Raum 3.217 am Campus GM.

Herr Mustermann: Bitte bereiten Sie eine max. 15-minütige Präsentation zu 
Ihrer Arbeit vor (wenn möglich inkl. Demo).

Viele Grüße,
Prof. Dr. Müller
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

See [CONTRIBUTING](CONTRIBUTING.md).

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
