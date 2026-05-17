# Peer Review Comments

## Overview

This tool generates professional peer review feedback for papers. It extracts informal reviewer notes from an annotated PDF, auto-detects line numbers from the margins, and generates a structured Markdown document with page and line references.

## Generated Files (Results)

### 1. Markdown Review Document
**Filename:** `review_<filename>.md`
A structured document containing all comments sorted by page and line. Feedback is automatically rewritten into professional English.

---

## Requirements

- Annotated paper PDF (with comments/highlights)  
- At least one configured LLM API key (OpenAI recommended for highest quality)  

## Usage

### Command Line (CLI)

```bash
# Basic usage
academic-doc-generator review paper.pdf

# Specify output folder
academic-doc-generator review paper.pdf --out ./reviews
```

## Key Features

- ✅ **Automatic Line Mapping**: No need to manually type page and line numbers.  
- ✅ **Constructive Tone**: Converts rough reviewer notes into professional academic prose.  
- ✅ **Structured Output**: Generates a clean Markdown file ready for submission systems.  
- ✅ **Language Translation**: Automatically translates German reviewer notes to English.  

---

## How It Works (Details)

1. **Annotation Extraction**: Reads highlights and comments from the paper PDF.  
2. **Line Number Detection**: Automatically identifies line numbers from the PDF margins for exact references.  
3. **Context-Aware Rewriting**: Maps your rough notes to the highlighted text and surrounding paragraphs.  
4. **Professional Refinement**: Rewrites informal or terse comments into constructive, polite feedback.  
5. **English Output**: Always generates feedback in English, regardless of the input language.  

---

## Tips for Reviewers

1. **Highlight Exactly**: Highlight the specific phrase or sentence you are commenting on.  
2. **Short Notes Suffice**: You can write short notes like "Check citation" or "Vague", and the LLM will expand them into helpful suggestions.  
3. **Line Numbers**: The tool works best with papers that have visible line numbers in the margins.  

## Related Documentation

- [Installation Guide](INSTALL.en.md)  
- [Colloquium Protocols](COLLOQUIUM.en.md)  
- [Configuration Guide](configuration.en.md)  
