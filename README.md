# Colloquium Protocol Creator

**Project name:** colloquium-protocol-creator

**Short:** Create a LaTeX protocol letter for a thesis colloquium by extracting annotations and producing a template with rewritten questions.

**Important:** This project **does not grade** a thesis. It extracts comments/annotations from a thesis PDF, rewrites them into clearer questions using a language model, summarizes the thesis (first pages), and generates a LaTeX template that can be used for the colloquium's protocol.

## Features
- Extract text and annotation positions with Docling + PyPDF.
- Map annotations to the exact highlighted words and paragraph context.
- Rewrite terse comments (e.g. "Why?") to full, polite questions using Groq LLM.
- Create a LaTeX (`scrlttr2`) letter with TH Köln footer and optionally compile to PDF (LuaLaTeX recommended).
- Handles Unicode dashes and German `ß` for LaTeX-safe output.

## Quickstart

1. Clone repo and install dependencies:
```bash
pip install -e .
```

2. Set your Groq API key:
```bash
export GROQ_API_KEY="your_key_here"
```

3. Run the CLI:
```bash
colloquium-protocol-creator /path/to/Bachelorarbeit_xy.pdf --groq-key $GROQ_API_KEY
```

A bewertung_brief_<matr>.tex (and .pdf if compilation succeeds) will be written into the thesis folder.

## Requirements
- Python 3.9+
- TeX (LuaLaTeX recommended for full Unicode)
- Groq API key
- Docling-parse, pypdf, groq Python packages

## License
This project is released under the MIT License (see LICENSE).

## Disclaimer
This tool aids in producing a protocol template for the colloquium — it does not grade or make evaluative decisions automatically.
