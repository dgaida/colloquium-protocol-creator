# Project Work Grading Letters

## Overview

This tool generates formal grading letters for project work (Praxisprojekt) at TH Köln. It extracts metadata from the project PDF, automatically determines the appropriate formal address, and generates a LaTeX letter template with TH Köln formatting.

## Generated Files (Results)

### 1. LaTeX Grading Letter
**Filename:** `projektarbeit_brief_<matrikelnr>.tex`
A formal `scrlttr2` letter with TH Köln letterhead and footer.

### 2. Compiled PDF
**Filename:** `projektarbeit_brief_<matrikelnr>.pdf`
The ready-to-print PDF of the grading letter (requires LuaLaTeX).

### 3. Email for Examination Office
**Filename:** `projekt_anmeldung_<name>_<matrikelnr>.md`
A ready-to-use email template for submitting the grade to the examination office.

### 4. Student Feedback Email
**Filename:** `feedback_student_<name>_<matrikelnr>.md`
An automatically generated draft containing a summary of strengths/weaknesses and the final grade.

---

## Requirements

- Project work PDF with a title page (selectable text required)
- At least one configured LLM API key (OpenAI, Groq, Google Gemini) or local Ollama
- LaTeX installation (LuaLaTeX recommended)
- (Optional) Signature image at `data/signature.png`

## Usage

### Command Line (CLI)

```bash
# Basic usage
academic-doc-generator project /path/to/Praxisprojekt_Mueller.pdf

# Disable feedback mail (default is enabled)
academic-doc-generator project project.pdf --no-feedback-mail
```

## Feedback & Student Email

When `create_feedback_mail` is enabled (default), the tool:
1. Analyzes the project work using the LLM.
2. Extracts the student's email address from the title page.
3. Generates a Markdown file with a feedback summary.
4. Provides a draft email for the student.

---

## How It Works (Details)

1. **Metadata Extraction**: Automatically detects student name, ID, title, examiner, and student email.
2. **Gender Detection**: Uses an LLM to determine the appropriate formal German address (Herr/Frau) based on the first name.
3. **Semester Calculation**: Automatically determines the current semester (SoSe/WS).
4. **LaTeX Generation**: Creates a professional letter with TH Köln formatting.
5. **Signature Integration**: Automatically includes your signature image if available.

---

## Troubleshooting

### Student Email Not Extracted
- Ensure the email address is present on the title page and is selectable text.
- If it fails, you will need to add the recipient manually to the email draft.

### Incorrect Salutation (Mr/Ms)
- For ambiguous names, the detection might be incorrect. You can easily fix the salutation in the generated `.tex` file.

## Related Documentation

- [Installation Guide](INSTALL.md)
- [Colloquium Protocols](COLLOQUIUM.md)
- [Configuration Guide](configuration.md)
