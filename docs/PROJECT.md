# Project Work Grading Letters

## Overview

This tool generates formal grading letters for project work (Praxisprojekt) at TH Köln. It extracts metadata from the project PDF, automatically determines the appropriate formal address, and generates a LaTeX letter template with TH Köln formatting.

## What It Does

1. **Metadata Extraction**: Automatically extracts from the project PDF:
   - Student name (full name and first name)
   - Matriculation number
   - Project title
   - First examiner name and email
   - Type of work (Praxisprojekt, Projektarbeit, etc.)
   - **Student Email**: Extracted from the document for automated feedback
   - **Course of Study**: Extracted for administrative completeness

2. **Gender Detection**: Uses an LLM to determine the appropriate formal German address (Herr/Frau) from the student's first name

3. **Semester Calculation**: Automatically determines the current semester (SoSe/WS).

4. **LaTeX Letter Generation**: Creates a formal letter with TH Köln letterhead and footer.

5. **Signature Detection**: Automatically includes a signature image if `data/signature.png` is found.

6. **Feedback Generation**: Optionally generates a summary of strengths/weaknesses and a draft email to the student.

7. **PDF Compilation**: Optionally compiles the LaTeX file to PDF using LuaLaTeX.

## Requirements

- Project work PDF with title page
- At least one LLM API configured (OpenAI, Groq, Google Gemini, or Ollama)
- LaTeX installation (LuaLaTeX recommended)
- (Optional) Signature image at `data/signature.png`

## Usage

### Command Line (Recommended)

```bash
# Basic usage (auto-detects available API)
academic-doc-generator project /path/to/Praxisprojekt_Mueller.pdf

# Specify API and model
academic-doc-generator project project.pdf --api gemini --model gemini-2.0-flash-exp

# Enable/Disable feedback mail (default is True)
academic-doc-generator project project.pdf --no-feedback-mail
```

### Python API

```python
from llm_client import LLMClient
from academic_doc_generator.project.orchestrator import run_project_pipeline

# Create LLM client (auto-detects available API)
client = LLMClient()

# Run full pipeline
tex_file, pdf_file, email_service, email_student = run_project_pipeline(
    pdf_path="Praxisprojekt_Mueller.pdf",
    llm_client=client,
    output_folder="./out",
    compile_pdf=True,
    create_feedback_mail=True
)

print(f"LaTeX file: {tex_file}")
if email_student:
    print(f"Student Feedback: {email_student}")
```

## Feedback & Student Email

When `create_feedback_mail` is enabled (default), the tool:
1. Analyzes the project work using the LLM.
2. Extracts the student's email address from the title page.
3. Generates a Markdown file with a feedback summary.
4. Provides a draft email for the student.

## Output Files

### 1. LaTeX Letter
**Filename:** `projektarbeit_brief_<matrikelnr>.tex`

### 2. Compiled PDF
**Filename:** `projektarbeit_brief_<matrikelnr>.pdf`

### 3. Email (Prüfungsservice)
**Filename:** `projekt_anmeldung_<name>_<matrikelnr>.md`

### 4. Email (Student)
**Filename:** `feedback_student_<name>_<matrikelnr>.md` (if enabled)

## Signature Handling

The tool looks for a signature image in the `data/` directory:
- Recommended path: `data/signature.png`
- If found, it is automatically included in the LaTeX letter.
- You can also specify a custom path via `--signature` or in the JSON configuration.

## Troubleshooting

### Student Email Not Extracted
- Ensure the email address is present on the title page and is selectable text.
- If it fails, the student email path will be an empty string, and you'll need to send the feedback manually.

### Gender Detection Issues
- If a name is ambiguous, the tool might use "Herr/Frau". You can manually edit the generated LaTeX file.

## Related Documentation

- [Installation Guide](INSTALL.md)
- [Colloquium Protocols](COLLOQUIUM.md)
- [Configuration Guide](configuration.md)
