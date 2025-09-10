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

## Peer Review Support

Besides thesis colloquium protocols, the project can also assist with peer reviews of journal or conference papers.

When reviewing a paper, you can annotate the PDF with your comments. This tool will:

- Extract your annotations and identify the corresponding page and line number (using the printed line numbers in the PDF margin, or estimating them if necessary).

- Rewrite your short notes into clear, polite, and constructive comments suitable for authors.

- Generate a ready-to-send Markdown review document that starts with a courteous introduction, followed by your rephrased comments, each labeled with its page and line reference.

This extension provides a lightweight workflow to turn your raw margin notes into a professional-looking peer review.

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

Instead of step 2 and 3 you can also edit the file main.py and then run:

```bash
python main.py
```

A bewertung_brief_matrikelnr.tex (and .pdf if compilation succeeds) will be written into the thesis folder.

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
- [Groq API key](https://console.groq.com/keys)
- Python packages:
  - [docling-parse](https://pypi.org/project/docling-parse/)
  - [docling-core](https://pypi.org/project/docling-core/)
  - [pypdf](https://pypi.org/project/pypdf/)
  - [groq](https://pypi.org/project/groq/)

## License
This project is released under the MIT License (see LICENSE).

## Disclaimer
This tool aids in producing a protocol template for the colloquium — it does not grade or make evaluative decisions automatically.
