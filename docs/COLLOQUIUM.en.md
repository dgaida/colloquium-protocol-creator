# Thesis Colloquium Protocol Generator

## Overview

This tool generates a formal LaTeX protocol letter for thesis colloquiums (Bachelor/Master) at TH Köln. It extracts annotations from an annotated thesis PDF, rewrites them into clear questions using an LLM, and generates both a LaTeX letter and a pre-filled grading form.

## Generated Files (Results)

### 1. LaTeX Protocol Letter
**Filename:** `bewertung_brief_<matrikelnr>.tex`
A formal `scrlttr2` letter with TH Köln letterhead and footer.

### 2. Compiled PDF
**Filename:** `bewertung_brief_<matrikelnr>.pdf`
The ready-to-print PDF of the protocol letter (requires LuaLaTeX).

### 3. Pre-filled Grading Form
**Filename:** `Bewertung <Bachelor/Master>arbeit_Kolloq Inf_<stud_name>.pdf`
The official TH Köln grading form, automatically filled with student data and correct checkboxes.

### 4. Email & Outlook Draft
**Filename:** `kolloquium_anmeldung_<name>_<matrikelnr>.md`
A ready-to-send email for the examination office. If Outlook is open, a draft is created automatically with an ICS calendar attachment.

---

## Requirements

- Annotated thesis PDF (with comments/highlights)
- At least one configured LLM API key (OpenAI, Groq, Google Gemini) or local Ollama
- LaTeX installation (LuaLaTeX recommended)
- (Optional) Signature image at `data/signature.png`

## Usage

### Command Line (CLI)

The recommended way to run the tool:

```bash
# Basic usage (auto-detects available API)
academic-doc-generator colloquium /path/to/Bachelorarbeit_Mueller.pdf --date 20.01.2026 --time 14:00 --room 3.217

# Using a config file
academic-doc-generator --config config_colloquium_campus.json
```

## Metadata & Course of Study

The tool extracts the `course_of_study` from the thesis title page and uses it to automatically check the correct box in the official TH Köln grading form:

| Course of Study | PDF Form Checkbox |
|-----------------|-------------------|
| Informatik | KontrollInformatik |
| Wirtschaftsinformatik | ControlWI |
| Medieninformatik | KontrollMedien |
| IT-Management | KontrollITM |

## Comment Categories

Annotations are automatically categorized into four types:

### 1. LLM Comments (Default)
Regular comments rewritten by the LLM into polite, clear questions.
*Example: "Why?" → "Could you explain the reasoning behind this decision?"*

### 2. Source Comments
Notes about missing sources. These are counted in statistics but not rewritten.
*Rule: Contains "quelle" or "source" and is short.*

### 3. Language Comments
Grammar or spelling notes. These are counted to provide a note on linguistic quality.

### 4. Ignore Comments
Markers like "ab hier" are completely excluded.

---

## How It Works (Details)

For those interested in the technical process:

1. **Annotation Extraction**: Reads comments and highlights from the PDF.
2. **Context-Aware Processing**: Maps each comment to the exactly highlighted text and surrounding paragraph.
3. **Intelligent Categorization**: Sorts comments by type (question, source, language).
4. **LLM Refinement**: Rewrites terse notes into full examination questions.
5. **Metadata Extraction**: Automatically detects student name, ID, title, and examiners.
6. **Thesis Summary**: Generates a concise summary based on the first 10 pages.
7. **Signature Integration**: Automatically includes your signature image if available.

---

## Troubleshooting

### Outlook Draft Not Created
- Ensure Outlook is open before running the tool.
- On macOS, ensure the application has permissions to control Outlook.

### Course of Study Not Detected
- Ensure the course name appears clearly on the title page.
- Alternatively, you can manually set `course_of_study` in the JSON config.

## Related Documentation

- [Installation Guide](INSTALL.md)
- [Project Grading](PROJECT.md)
- [Configuration Guide](configuration.md)
