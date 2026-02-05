# Peer Review Comments

## Overview

This tool generates professional peer review feedback for papers. It extracts informal reviewer notes from an annotated PDF, auto-detects line numbers from the margins, and generates a structured Markdown document with page and line references.

## What It Does

1. **Annotation Extraction**: Reads highlights and comments from the paper PDF.
2. **Line Number Detection**: Automatically identifies line numbers from the PDF margins to provide exact references.
3. **Context-Aware Rewriting**: Maps your rough notes to the highlighted text and surrounding paragraphs.
4. **Professional Refinement**: Rewrites informal or terse comments (e.g., "Clarify this", "Ref missing") into constructive, polite feedback.
5. **English Output**: Always generates feedback in English, regardless of the input language, suitable for international journal and conference submissions.

## Requirements

- Annotated paper PDF (with comments/highlights)
- At least one LLM API configured (OpenAI recommended for highest quality)

## Usage

### Command Line (Recommended)

```bash
# Basic usage
academic-doc-generator review paper.pdf

# Specify output folder
academic-doc-generator review paper.pdf --out ./reviews
```

### Python API

```python
from llm_client import LLMClient
from academic_doc_generator.review.orchestrator import run_review_pipeline

# Create LLM client
client = LLMClient()

# Run review pipeline
md_file = run_review_pipeline(
    pdf_path="paper.pdf",
    llm_client=client,
    output_folder="./out"
)

print(f"Markdown review: {md_file}")
```

## Features

- ✅ **Automatic Line Mapping**: No need to manually type page and line numbers.
- ✅ **Constructive Tone**: Converts rough reviewer notes into professional academic prose.
- ✅ **Structured Output**: Generates a clean Markdown file ready for submission systems.
- ✅ **Language Translation**: Automatically translates German reviewer notes to English.

## Output Format

The tool generates a Markdown file with the following structure:

```markdown
# Peer Review

- **Page 1, Line 15**: [Rewritten feedback...]
- **Page 3, Line 42**: [Rewritten feedback...]
- **General Comments**: [Summarized feedback...]
```

## Tips for Reviewers

1. **Highlight Exactly**: Highlight the specific phrase or sentence you are commenting on.
2. **Short Notes Suffice**: You can write short notes like "Check citation" or "Vague", and the LLM will expand them into helpful suggestions.
3. **Line Numbers**: The tool works best with papers that have visible line numbers in the margins (standard for most journal submissions).

## Related Documentation

- [Installation Guide](INSTALL.md)
- [Colloquium Protocols](COLLOQUIUM.md)
- [Configuration Guide](configuration.md)
