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

2. **Gender Detection**: Uses an LLM to determine the appropriate formal German address (Herr/Frau) from the student's first name

3. **Semester Calculation**: Automatically determines the current semester:
   - **Winter Semester (WS)**: October 1 - February 28/29
   - **Summer Semester (SoSe)**: March 1 - September 30

4. **LaTeX Letter Generation**: Creates a formal letter with:
   - TH Köln letterhead and footer
   - Student information
   - Project title
   - Semester information
   - Blank grade field (to be filled manually)
   - Optional signature placement

5. **PDF Compilation**: Optionally compiles the LaTeX file to PDF using LuaLaTeX

## Requirements

- Project work PDF with title page
- At least one LLM API configured (OpenAI, Groq, Google Gemini, or Ollama)
- LaTeX installation (LuaLaTeX recommended)
- (Optional) Signature image file

## Usage

### Command Line

```bash
# Basic usage (auto-detects available API)
project-grading-letter /path/to/Praxisprojekt_Mueller.pdf

# Specify API and model
project-grading-letter project.pdf --api gemini --model gemini-2.0-flash-exp

# Without PDF compilation
project-grading-letter project.pdf --no-compile

# With custom output folder
project-grading-letter project.pdf --out ./output

# With signature image
project-grading-letter project.pdf --signature ./signature.png
```

### Python API

```python
from llm_client import LLMClient
from project_pipeline import orchestrator

# Create LLM client (auto-detects available API)
client = LLMClient()

# Run full pipeline
tex_file, pdf_file = orchestrator.run_project_pipeline(
    pdf_path="Praxisprojekt_Mueller.pdf",
    llm_client=client,
    output_folder="./out",
    compile_pdf=True,
    signature_file="signature.png"  # optional
)

print(f"LaTeX file: {tex_file}")
if pdf_file:
    print(f"PDF file: {pdf_file}")
```

### Workflow Integration

```python
# Example: Process project work in a specific folder
import os
from llm_client import LLMClient
from project_pipeline import orchestrator

folder = os.path.join("..", "Projektarbeiten", "2025_SoSe", "Mueller")
pdf_filename = "Praxisprojekt_Mueller.pdf"
pdf_path = os.path.join(folder, pdf_filename)

llm_client = LLMClient()

tex, pdf = orchestrator.run_project_pipeline(
    pdf_path=pdf_path,
    llm_client=llm_client,
    compile_pdf=True
)
```

## Semester Calculation

The tool automatically determines the semester based on the current date:

| Date Range | Semester | Example |
|------------|----------|---------|
| March 1 - September 30 | SoSe\<YY\> | SoSe25 |
| October 1 - February 28/29 | WS\<YY\>/\<YY+1\> | WS25/26 |

**Examples:**
- Date: May 15, 2025 → Semester: SoSe25
- Date: January 5, 2026 → Semester: WS25/26
- Date: October 10, 2025 → Semester: WS25/26

## Gender Detection

The tool uses an LLM to determine the appropriate formal address:

### Supported Outputs
- **"Herr"**: Male form of address
- **"Frau"**: Female form of address
- **"Herr/Frau"**: Fallback when uncertain

### Gender-Specific Text
The letter adjusts pronouns based on detected gender:

| Gender | sein/ihr | Er/Sie | Example |
|--------|----------|--------|---------|
| Herr | sein | Er | "hat bei mir **sein** Praxisprojekt gemacht. **Er** hat..." |
| Frau | ihr | Sie | "hat bei mir **ihr** Praxisprojekt gemacht. **Sie** hat..." |

### How It Works

```python
# Gender determination example
from project_creator.llm_interface import determine_gender_from_name

gender = determine_gender_from_name("Max", llm_client)
# → "Herr"

gender = determine_gender_from_name("Anna", llm_client)
# → "Frau"

gender = determine_gender_from_name("Kim", llm_client)
# → "Herr/Frau" (uncertain)
```

## Output Files

### 1. LaTeX Letter
**Filename:** `projektarbeit_brief_<matrikelnr>.tex`

**Letter Structure:**
```
TH Köln Letterhead

Subject: Praxisprojekt [Herr/Frau] [Student Name]

Sehr geehrte Mitarbeiter*innen des Prüfungsservice,

[Herr/Frau]
[Student Name], Matrikelnr. [Number],

hat im [Semester] [sein/ihr] Praxisprojekt bei mir gemacht. 
[Er/Sie] hat die Note _______ erhalten.

Das Thema war:
[Project Title]

Danke und viele Grüße,

[Signature placeholder]

TH Köln Footer
```

### 2. Compiled PDF
**Filename:** `projektarbeit_brief_<matrikelnr>.pdf`

PDF-compiled version of the LaTeX letter (if `compile_pdf=True`)

## Adding a Signature

You can include a signature image in the letter:

### 1. Prepare Signature Image
- Format: PNG, JPG, or PDF
- Recommended size: ~4cm width
- Transparent background works best

### 2. Option A: Command Line
```bash
project-grading-letter project.pdf --signature ./signature.png
```

### 3. Option B: Python API
```python
tex, pdf = orchestrator.run_project_pipeline(
    pdf_path="project.pdf",
    llm_client=client,
    signature_file="./signature.png"
)
```

### 4. Option C: Manual LaTeX Edit
In the generated `.tex` file, find:
```latex
\iffalse
% Uncomment the following line and provide the path to your signature image
% \includegraphics[width=4cm]{signature.png}
\fi
```

Change to:
```latex
\includegraphics[width=4cm]{signature.png}
```

## Metadata Extraction Details

### What Gets Extracted

The tool reads the first two pages of the PDF and extracts:

```python
{
    "student_name": "Mustermann, Max",
    "student_first_name": "Max",
    "matriculation_number": "123456",
    "title": "Entwicklung einer Mobile App für...",
    "first_examiner": "Prof. Dr. Müller",
    "first_examiner_christian": "Anna",
    "first_examiner_family": "Müller",
    "work_type": "Praxisprojekt"
}
```

### Common Title Page Formats

The tool works with various title page formats:

**Format 1: TH Köln Standard**
```
TECHNISCHE HOCHSCHULE KÖLN
Campus Gummersbach

Praxisprojekt
im Studiengang Medieninformatik

Entwicklung einer...

Vorgelegt von:
Max Mustermann
Matrikelnummer: 123456

Erstprüfer: Prof. Dr. Anna Müller
```

**Format 2: Minimal**
```
Praxisprojekt

Titel: Entwicklung einer...

Autor: Max Mustermann (123456)
Betreuer: Prof. Dr. Müller
```

### Troubleshooting Extraction

If metadata extraction fails:

1. **Check PDF Text Layer**: Ensure the PDF has selectable text
2. **Manual Correction**: Edit the generated LaTeX file manually
3. **Fallback Values**: The tool uses these defaults:
   - Student name: "Unknown"
   - Matriculation: "unknown"
   - Title: "Unknown"
   - Examiner: "Unbekannt"

## Advanced Configuration

### Custom LLM Settings

```python
from llm_client import LLMClient

# Use specific model with custom temperature
client = LLMClient(
    api_choice="openai",
    llm="gpt-4o",
    temperature=0.3  # Lower = more deterministic for metadata
)
```

### Custom Work Types

The tool automatically detects work type, but you can override it:

```python
from project_creator.latex_generation import create_project_grading_letter_tex

create_project_grading_letter_tex(
    filename="output.tex",
    student_name="Mustermann, Max",
    matriculation_number="123456",
    project_title="My Project",
    examiner_name="Prof. Dr. Müller",
    examiner_mail="anna.mueller@th-koeln.de",
    gender="Herr",
    work_type="Projektarbeit",  # Custom work type
)
```

## Letter Customization

### Changing the Letterhead

Edit the generated `.tex` file:

```latex
% Current
\setkomavar{fromaddress}{Steinmüllerallee 1\\51643 Gummersbach}
\setkomavar{fromphone}{+49 2261-8196-6204}

% Customize
\setkomavar{fromaddress}{Your Address\\Your Postal Code City}
\setkomavar{fromphone}{Your Phone Number}
```

### Changing the Recipient

```latex
% Current
\begin{letter}{Prüfungsausschuss der TH Köln}

% Customize
\begin{letter}{Your Recipient}
```

### Adjusting Font Size

```latex
% Current
\documentclass[11pt,ngerman,parskip=full]{scrlttr2}

% Options: 10pt, 11pt, 12pt
\documentclass[12pt,ngerman,parskip=full]{scrlttr2}
```

## Troubleshooting

### Gender Detection Issues

**Problem:** Gender detection returns "Herr/Frau"

**Solutions:**
1. Use a more capable LLM model (e.g., GPT-4 instead of GPT-3.5)
2. Manually edit the generated `.tex` file:
   ```latex
   % Find and replace
   Herr/Frau → Herr  % or Frau
   sein/ihr → sein   % or ihr
   Er/Sie → Er       % or Sie
   ```

### Metadata Not Extracted

**Problem:** Student name or title shows as "Unknown"

**Solutions:**
1. Check if PDF has selectable text (not a scanned image)
2. Manually edit the `.tex` file with correct information
3. Verify title page uses standard format

### LaTeX Compilation Errors

**Problem:** Special characters in title or name break compilation

**Solutions:**
1. The tool automatically escapes characters, but if issues persist:
2. Manually escape in `.tex`: `&` → `\&`, `_` → `\_`, etc.
3. Use LuaLaTeX instead of pdfLaTeX: `lualatex filename.tex`

## Tips for Best Results

1. **Standard Title Page**: Use a clear, standard title page format
2. **Complete Information**: Ensure title page has all required fields
3. **German Names**: Works best with typical German first names for gender detection
4. **Proper PDF**: Ensure PDF is not a scanned image but has text layer

## Example Complete Workflow

```python
import os
from llm_client import LLMClient
from project_pipeline import orchestrator

# 1. Setup paths
project_folder = os.path.join("..", "Projektarbeiten", "2025_SoSe")
pdf_file = "Praxisprojekt_Mueller.pdf"
pdf_path = os.path.join(project_folder, pdf_file)

# 2. Create LLM client
client = LLMClient(api_choice="gemini", llm="gemini-2.0-flash-exp")

# 3. Generate letter
tex_file, pdf_file = orchestrator.run_project_pipeline(
    pdf_path=pdf_path,
    llm_client=client,
    compile_pdf=True,
    signature_file="signature.png"
)

# 4. Output paths
print(f"✓ LaTeX created: {tex_file}")
print(f"✓ PDF created: {pdf_file}")

# 5. Manual steps:
# - Open PDF and review
# - Fill in the grade (underlined space)
# - Print or send to Prüfungsservice
```

## Related Documentation

- [Installation Guide](INSTALL.md)
- [Colloquium Protocols](COLLOQUIUM.md)
- [Peer Review Comments](REVIEW.md)
