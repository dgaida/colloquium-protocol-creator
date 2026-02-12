# LaTeX Exam Translator

## Overview

This module automatically translates LaTeX exam documents using the `exam` class from German to English. It uses LLM APIs (OpenAI, Groq, Gemini, or Ollama) to create high-quality translations while preserving the entire LaTeX structure, formatting, and mathematical notation.

## Generated Files (Results)

### 1. Translated LaTeX File
**Filename:** `<originalname>_engl.tex`
The translated LaTeX file where all academic content has been transferred to English, while formulas and commands remain unchanged.

---

## Usage

### Command Line (CLI)

```bash
# Basic usage
academic-doc-generator translator Exam.tex
```

### Python API

```python
from llm_client import LLMClient
from academic_doc_generator.exam_translator import translate_latex_exam

# Create LLM client
client = LLMClient()

# Translate exam
output_path = translate_latex_exam("Exam.tex", client)
```

## Key Features

- ✅ **Structured Translation**: Intelligently splits the document into preamble and individual questions.
- ✅ **LaTeX Preservation**: Maintains all LaTeX commands and environments.
- ✅ **Math Protection**: Mathematical formulas remain untouched.
- ✅ **Comment Protection**: Masks LaTeX comments (`%`) to preserve their exact position and content.

---

## How It Works (Details)

### 1. Document Structure Analysis
The document is split into three parts:
- **Preamble**: Everything up to the first `\begin{questions}`.
- **Questions**: Each block starting with `\question`.
- **Postamble**: Everything after `\end{questions}`.

### 2. Comment Masking
To prevent the AI from translating or deleting LaTeX comments, they are replaced by placeholders before processing and reinserted at the exact location after translation.

### 3. What is Translated?
- **Translated**: Prose text, task descriptions, multiple-choice options, solution texts, headers/footers.
- **Unchanged**: Mathematical formulas (`$...$`, `\[...\]`), LaTeX commands (`\question[5]`), environments, comments.

---

## Limitations & Tips

1. **Exam Class Required**: The tool is specifically optimized for the LaTeX `exam` class.
2. **AI Choice**: Use **OpenAI (GPT-4o)** for the highest quality in complex academic formulations.
3. **Speed**: Use **Groq** or **Gemini** for very fast and often free translations.

## Related Documentation

- [Main Documentation](index.md)
- [Configuration Guide](configuration.md)
