# Thesis Colloquium Protocol Generator

## Overview

This tool generates a formal LaTeX protocol letter for thesis colloquiums (Bachelor/Master) at TH Köln. It extracts annotations from an annotated thesis PDF, rewrites them into clear questions using an LLM, and generates both a LaTeX letter and a pre-filled grading form.

## Generated Files (Results)

A detailed overview with images can be found on the [Examples](EXAMPLES.en.md#thesis-colloquium) page.

### 1. [LaTeX Protocol Letter](EXAMPLES.en.md#latex-protocol-letter)
**Filename:** `bewertung_brief_<matrikelnr>.tex`
A formal `scrlttr2` letter with TH Köln letterhead and footer.

### 2. [Compiled PDF](EXAMPLES.en.md#compiled-pdf)
**Filename:** `bewertung_brief_<matrikelnr>.pdf`
The ready-to-print PDF of the protocol letter (requires LuaLaTeX).

### 3. [Pre-filled Grading Form](EXAMPLES.en.md#pre-filled-grading-form)
**Filename:** `Bewertung <Bachelor/Master>arbeit_Kolloq Inf_<stud_name>.pdf`
The official TH Köln grading form, automatically filled with student data and correct checkboxes.

### 4. [Email & Outlook Draft](EXAMPLES.en.md#email-outlook-draft)
**Filename:** `kolloquium_anmeldung_<name>_<matrikelnr>.md`
A ready-to-send email for the examination office. If Outlook is open, a draft is created automatically with an ICS calendar attachment.

### 5. [Web Metadata (Profile)](EXAMPLES.en.md#web-metadata-profile)
**Filename:** `YYYY-MM-DD-title.md`
A Jekyll-compatible profile of the work (summary, keywords, etc.) for your own website. The path where these files should be copied can be defined globally in `config.yaml`.

---

## Requirements

- Annotated thesis PDF (with comments/highlights)  
- At least one configured LLM API key (OpenAI, Groq, Google Gemini) or local Ollama  
- LaTeX installation (LuaLaTeX recommended)  
- (Optional) Signature image at `data/signature.png`  

## Usage

The recommended way is to use a [configuration file](configuration.en.md).

### Command Line (CLI)

```bash
# Using a config file
academic-doc-generator --config config_colloquium_campus.json

# Basic usage (auto-detects available API)
academic-doc-generator colloquium /path/to/Bachelorarbeit_Mueller.pdf --date 20.01.2026 --time 14:00 --room 3.217
```

### Usage via main.py

You can also run the tool via `main.py` by specifying the path to the thesis folder there. Details can be found in the [Configuration Guide](configuration.en.md#3-run-the-tool).

## Metadata & Course of Study

The tool extracts the `course_of_study` from the thesis title page and uses it to automatically check the correct box in the official TH Köln grading form:

| Course of Study | PDF Form Checkbox |
|-----------------|-------------------|
| Informatik | KontrollInformatik |
| Wirtschaftsinformatik | KontrollWI |
| Medieninformatik | KontrollMedien |
| IT-Management | KontrollITM |

## Comment Categories

The tool follows the author's workflow: to keep reading the thesis smoothly, only brief notes (annotations) are made in the PDF. The tool automatically categorizes these to prepare them appropriately in the protocol letter.

### 1. LLM Comments (Default)
Understanding questions or content-related notes rewritten by the LLM into polite, clear examination questions.
*Example: "Why?" → "Could you explain the reasoning behind this decision?"*

### 2. Source Comments
Notes about missing sources. The author usually just writes "Source?", "Source missing", or "Reference?". These are counted in statistics but not rewritten.
*Rule: Contains "quelle" or "source" and is short.*

### 3. Language Comments
Notes on grammar, spelling, or style. These are counted to provide a note on linguistic quality at the end.
*Examples: "Grammar", "Expression", "illegible", "Spelling".*

### 4. Ignore Comments / Markers
Special markers for own orientation.
*Example: "ab hier" (from here) – This comment only serves as a hint for the reader where to continue next time if the thesis is not read in one go. Such markers are ignored in the protocol.*

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

- [Installation Guide](INSTALL.en.md)  
- [Project Grading](PROJECT.en.md)  
- [Configuration Guide](configuration.en.md)  
