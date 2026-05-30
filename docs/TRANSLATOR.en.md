# Exam Translator (LaTeX & XML)

## Overview

This module automatically translates exam documents (LaTeX or XML/ILIAS) from German to English. It uses LLM APIs (OpenAI, Groq, Gemini, or Ollama) to create high-quality translations while preserving the entire structure, formatting, and technical content.

## Generated Files (Results)

### 1. Translated File
**Filename:** `<originalname>_engl.tex` or `<originalname>_engl.xml`
The translated file where all academic content has been transferred to English.

---

## Usage

### Command Line (CLI)

The tool automatically detects the format based on the file extension (`.tex` or `.xml`).

```bash
# LaTeX translation
academic-doc-generator translator Exam.tex

# XML translation (e.g., ILIAS export)
academic-doc-generator translator Exam.xml
```

### Python API

```python
from llm_client import LLMClient
from academic_doc_generator.exam_translator import translate_latex_exam, translate_xml_exam

# Create LLM client
client = LLMClient()

# Translate LaTeX
translate_latex_exam("Exam.tex", client)

# Translate XML
translate_xml_exam("Exam.xml", client)
```

## Key Features

- ✅ **Format Preservation**: Maintains the entire structure and all technical tags.  
- ✅ **LaTeX Specialization**: Intelligently splits LaTeX documents (`exam` class) into questions.  
- ✅ **XML/ILIAS Support**: Specifically translates content in `<mattext>` tags and protects HTML entities.  
- ✅ **Math Protection**: Mathematical formulas remain untouched.  
- ✅ **Comment Protection**: Masks LaTeX comments to preserve their exact position.  

---

## How It Works (Details)

### LaTeX Translation  
1. **Structure Analysis**: The document is split into preamble, questions, and postamble.  
2. **Masking**: Comments are temporarily masked.  
3. **Translation**: Prose text and task descriptions are translated, commands remain unchanged.  

### XML Translation (e.g., ILIAS)
The tool searches for `<mattext texttype="text/xhtml">...</mattext>` tags. The text within is translated, while internal HTML tags and XML entities (e.g., `&lt;`, `&#13;`) are preserved.

---

## Limitations & Tips

1. **File Extensions**: Use `.tex` for LaTeX and `.xml` for ILIAS exports.  
2. **AI Choice**: Use **OpenAI (GPT-4o)** for the highest quality in complex academic formulations.  
3. **Speed**: Use **Groq** or **Gemini** for very fast and often free translations.  

## Related Documentation

- [Main Documentation](index.en.md)  
- [Configuration Guide](configuration.en.md)  
