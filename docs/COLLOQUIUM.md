# Colloquium Protocol Generator

## Overview

This tool generates a formal LaTeX protocol letter for thesis colloquiums (Bachelor/Master) at TH Köln. It extracts annotations from an annotated thesis PDF, rewrites them into clear questions using an LLM, and generates both a LaTeX letter and a pre-filled grading form.

## What It Does

1. **Extracts PDF Annotations**: Reads comments you've added to the thesis PDF during review
2. **Context-Aware Processing**: Maps annotations to exact highlighted text and surrounding paragraphs
3. **Intelligent Comment Categorization**:
   - **LLM comments**: Regular annotations that get rewritten into clear questions
   - **Quelle comments**: Source-related notes (e.g., "Quelle?", "Source missing") - counted but not rewritten
   - **Language comments**: Grammar/spelling notes - counted but not rewritten
   - **Ignore comments**: "ab hier" markers - completely excluded
4. **Question Refinement**: Rewrites rough annotations (e.g., "Why?", "unclear") into polite, well-phrased questions
5. **Metadata Extraction**: Automatically extracts student name, matriculation number, thesis title, course of study, and examiner names
6. **Thesis Summary**: Generates a concise summary from the first 10 pages
7. **LaTeX Letter Generation**: Creates a formal `scrlttr2` letter with TH Köln footer
8. **Registration Email**: Generate colloquium registration email for Prüfungsservice
9. **Outlook Integration**: Automatically creates an Outlook mail draft with the registration text and an ICS calendar attachment (Windows/macOS)
10. **PDF Form Pre-filling**: Automatically fills the official grading form with dates, names, and checkboxes (mapped to course of study)
11. **Signature Detection**: Automatically includes a signature image if `data/signature.png` is found
12. **PDF Compilation**: Optionally compiles the LaTeX file to PDF using LuaLaTeX

## Requirements

- Annotated thesis PDF (with comments/highlights)
- At least one LLM API configured (OpenAI, Groq, Google Gemini, or Ollama)
- LaTeX installation (LuaLaTeX recommended for full Unicode support)
- (Optional) Signature image at `data/signature.png`

## Usage

### Command Line (Recommended)

The unified CLI is the preferred way to run the pipeline:

```bash
# Basic usage (auto-detects available API)
academic-doc-generator colloquium /path/to/Bachelorarbeit_Mueller.pdf --date 20.01.2026 --time 14:00 --room 3.217

# Using a config file
academic-doc-generator --config config_colloquium_campus.json
```

### Python API

```python
from llm_client import LLMClient
from academic_doc_generator.colloquium.orchestrator import run_pipeline

# Create LLM client (auto-detects available API)
client = LLMClient()
print(f"Using: {client.api_choice} with {client.llm}")

# Run full pipeline
tex_file, pdf_file, email_file = run_pipeline(
    pdf_path="Bachelorarbeit_Mueller.pdf",
    date_colloquium="15.01.2026",
    uhrzeit_colloquium="10:00",
    llm_client=client,
    groq_free=True,  # Enable rate limiting if using free tier
    compile_pdf=True,
    location_type="campus",
    room="3.217"
)

print(f"LaTeX file: {tex_file}")
print(f"PDF file: {pdf_file}")
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

### How Comments Are Categorized

The tool automatically categorizes annotations into four types:

#### 1. LLM Comments (Default)
Regular comments that get rewritten by the LLM into clear, polite questions.

**Examples:**
- "Why?" → "Could you explain the reasoning behind this decision?"
- "unclear" → "Could you clarify this statement?"
- "What about X?" → "How does this relate to X?"

#### 2. Quelle Comments
Source-related comments that are **counted** in statistics but **not rewritten**.

**Detection Rules:**
- ≤20 characters long (configurable)
- Contains "quelle" or "source" as a whole word (case-insensitive)

**Impact:** If >4 "Quelle" comments are detected, the summary gets the note: "Häufig fehlen Quellenangaben."

#### 3. Language Comments
Grammar/spelling comments that are **counted** but **not rewritten**.

**Impact:** If >5 language comments are detected, the summary gets the note: "Viele sprachliche Fehler."

#### 4. Ignore Comments
Special markers that are **completely excluded** from processing.

**Detection Rules:** Exact match (case-insensitive): "ab hier"

## Output Files

### 1. LaTeX Protocol Letter
**Filename:** `bewertung_brief_<matrikelnr>.tex`

### 2. Compiled PDF
**Filename:** `bewertung_brief_<matrikelnr>.pdf`

### 3. Pre-filled Grading Form
**Filename:** `Bewertung <Bachelor/Master>arbeit_Kolloq Inf_<student_name>.pdf`

### 4. Email & Outlook Draft
**Filename:** `kolloquium_anmeldung_<name>_<matrikelnr>.md`

Additionally, if Outlook is detected, a draft is created automatically with:
- Correct recipient (studium-gm@th-koeln.de)
- Generated body text
- ICS calendar attachment for the colloquium date

## Signature Handling

The tool looks for a signature image in the `data/` directory:
- Recommended path: `data/signature.png`
- If found, it is automatically included in the LaTeX protocol letter.
- You can also specify a custom path in the JSON configuration.

## Troubleshooting

### Outlook Draft Not Created
- Ensure Outlook is open before running the tool.
- On macOS, ensure the application has permissions to control Outlook.

### Course of Study Not Detected
- Ensure the course name (Informatik, Medieninformatik, etc.) appears clearly on the title page.
- You can manually set `course_of_study` in the JSON config if extraction fails.

## Related Documentation

- [Installation Guide](INSTALL.md)
- [Project Grading Letters](PROJECT.md)
- [Configuration Guide](configuration.md)
