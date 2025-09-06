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

## Installation

You can install the project either with **pip** or with **Anaconda/Miniconda**.  

### Option 1: For developers (recommended)

Clone the repository and install in editable mode. This will pick up all dependencies
from `pyproject.toml` and let you make changes to the source code without reinstalling:

```bash
git clone https://github.com/your-username/colloquium-protocol-creator.git
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
- TeX (LuaLaTeX recommended for full Unicode)
- Groq API key
- Docling-parse, pypdf, groq Python packages

## License
This project is released under the MIT License (see LICENSE).

## Disclaimer
This tool aids in producing a protocol template for the colloquium — it does not grade or make evaluative decisions automatically.
