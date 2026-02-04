# Academic Document Generator Documentation

Welcome to the Academic Document Generator documentation!

Transform annotated PDFs into professional LaTeX documents using AI. Generate thesis colloquium protocols, project grading letters, and peer review comments automatically.

## 🎯 Quick Links

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __Quick Start__

    ---

    Get started in minutes with our installation guide

    [:octicons-arrow-right-24: Installation](INSTALL.md)

-   :material-file-document:{ .lg .middle } __Use Cases__

    ---

    Learn about the three main use cases

    [:octicons-arrow-right-24: Colloquium Protocols](COLLOQUIUM.md)
    [:octicons-arrow-right-24: Project Grading](PROJECT.md)
    [:octicons-arrow-right-24: Peer Reviews](REVIEW.md)

-   :material-cog:{ .lg .middle } __Configuration__

    ---

    Configure your LLM APIs and templates

    [:octicons-arrow-right-24: Configuration Guide](configuration.md)

-   :material-code-braces:{ .lg .middle } __API Reference__

    ---

    Complete API documentation for developers

    [:octicons-arrow-right-24: API Docs](api/core.md)

</div>

## ✨ Key Features

- 🔍 **PDF Annotation Extraction** - Extract text and annotation positions with Docling + PyPDF
- 🤖 **Multiple LLM Support** - Works with OpenAI, Groq, Google Gemini, or Ollama
- 🎯 **Context-Aware Rewriting** - Maps annotations to exact highlighted text and paragraphs
- ✍️ **Intelligent Comment Refinement** - Rewrites terse notes into full questions
- 📝 **LaTeX Generation** - Creates professional letters with TH Köln formatting
- 📋 **PDF Form Pre-filling** - Auto-fills official grading forms
- 🌐 **Unicode Support** - Handles German special characters correctly

## 🎓 Three Main Use Cases

### 1. Thesis Colloquium Protocols

Generate formal protocol letters for Bachelor/Master thesis colloquiums:

```bash
colloquium-protocol-creator --config config_colloquium_campus.json
```

**Features:**
- Extract and rewrite annotations into clear questions
- Auto-detect student metadata
- Generate thesis summary
- Create LaTeX letter with TH Köln formatting
- Pre-fill grading forms

[→ Full Documentation](COLLOQUIUM.md)

### 2. Project Work Grading Letters

Generate grading letters for project work (Praxisprojekt):

```bash
project-grading-letter /path/to/Praxisprojekt.pdf
```

**Features:**
- Auto-extract project metadata
- Determine formal German address (Herr/Frau)
- Create LaTeX grading letter template

[→ Full Documentation](PROJECT.md)

### 3. Peer Review Comments

Generate professional peer review feedback for papers:

```python
from llm_client import LLMClient
from academic_doc_generator.review import orchestrator

client = LLMClient()
md_file = orchestrator.run_review_pipeline("paper.pdf", client)
```

**Features:**
- Extract and rewrite reviewer notes
- Auto-detect line numbers
- Generate Markdown review document
- Always output in English

[→ Full Documentation](REVIEW.md)

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/dgaida/colloquium-protocol-creator.git
cd colloquium-protocol-creator

# Install
pip install -e .
```

### API Configuration

Create `secrets.env` in project root:

```bash
# Choose one or more
OPENAI_API_KEY=sk-xxxxxxxx          # Paid, reliable
GROQ_API_KEY=gsk-xxxxxxxx           # Free tier available
GEMINI_API_KEY=AIzaSy-xxxxxxxx      # Free tier available
# Or use Ollama (no key needed)
```

### Basic Usage

```bash
# List available templates
colloquium-protocol-creator --list-templates

# Use a configuration template
colloquium-protocol-creator --config config_templates/config_colloquium_campus.json
```

## 📊 System Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Annotated     │         │   Multi-LLM      │         │   LaTeX         │
│   PDF           │────────►│   Processing     │────────►│   Document      │
│   (Thesis)      │ Extract │   (Rewriting)    │ Generate│   (Protocol)    │
└─────────────────┘         └──────────────────┘         └─────────────────┘
        │                            │                            │
        │                            │                            │
        ▼                            ▼                            ▼
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Docling +     │         │   OpenAI/Groq/   │         │   PDF Form      │
│   PyPDF         │         │   Gemini/Ollama  │         │   Pre-filling   │
└─────────────────┘         └──────────────────┘         └─────────────────┘
```

## 🤖 Supported LLM APIs

| API | Default Model | API Key Required | Notes |
|-----|---------------|------------------|-------|
| OpenAI | `gpt-4o-mini` | Yes | Reliable, ~$0.01-0.05/thesis |
| Groq | `moonshotai/kimi-k2-instruct-0905` | Yes | Very fast, free tier (30 req/min) |
| Google Gemini | `gemini-2.0-flash-exp` | Yes | Fast, free tier (60 req/min) |
| Ollama | `llama3.2:1b` | No | Runs locally, completely free |

The tool automatically selects the best available API based on your configuration.

## 📝 Configuration Templates

Pre-built JSON configurations for common workflows:

- `config_colloquium_campus.json` - Colloquium on campus
- `config_colloquium_company.json` - Colloquium at company
- `config_colloquium_online.json` - Online colloquium via Zoom
- `config_project_template.json` - Project work grading
- `config_review_template.json` - Peer review comments

[→ Configuration Guide](configuration.md)

## 🧪 Example Outputs

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

### Peer Review Comments

```markdown
# Peer Review

- Page 1, Line 15: This point requires clarification...
- Page 2, Line 42: The explanation could be clearer by...
- Page 3, Line 78: The authors should consider recent work by...
```

## 🛠️ Requirements

- **Python**: 3.9 or higher
- **LaTeX**: LuaLaTeX recommended (for Unicode support)
- **LLM API**: At least one of OpenAI, Groq, Gemini, or Ollama

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is released under the MIT License.

## 🔗 Related Projects

- [llm_client](https://github.com/dgaida/llm_client) - Universal Python LLM client

## 📞 Support

- 📖 [Documentation](https://dgaida.github.io/colloquium-protocol-creator/)
- 🐛 [Report Issues](https://github.com/dgaida/colloquium-protocol-creator/issues)
- 💬 [Discussions](https://github.com/dgaida/colloquium-protocol-creator/discussions)

---

**Note:** This tool aids in document template creation — it does not grade or make evaluative decisions automatically. All academic assessments remain the responsibility of the examiner.
