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
5. **Metadata Extraction**: Automatically extracts student name, matriculation number, thesis title, and examiner names
6. **Thesis Summary**: Generates a concise summary from the first 10 pages
7. **LaTeX Letter Generation**: Creates a formal `scrlttr2` letter with TH Köln footer
8. **Registration Email**: Generate colloquium registration email for Prüfungsservice
9. **PDF Form Pre-filling**: Automatically fills the official grading form with dates, names, and checkboxes
10. **PDF Compilation**: Optionally compiles the LaTeX file to PDF using LuaLaTeX

## Requirements

- Annotated thesis PDF (with comments/highlights)
- At least one LLM API configured (OpenAI, Groq, Google Gemini, or Ollama)
- LaTeX installation (LuaLaTeX recommended for full Unicode support)

## Usage

### Command Line

```bash
# Basic usage (auto-detects available API)
colloquium-protocol-creator /path/to/Bachelorarbeit_Mueller.pdf

# Specify API and model
colloquium-protocol-creator thesis.pdf --api gemini --model gemini-2.0-flash-exp

# Without PDF compilation
colloquium-protocol-creator thesis.pdf --no-compile

# With custom output folder
colloquium-protocol-creator thesis.pdf --out ./output

# With rate limiting for free tiers
colloquium-protocol-creator thesis.pdf --groq-free
```

### Python API

```python
from llm_client import LLMClient
from colloquium_pipeline import orchestrator

# Create LLM client (auto-detects available API)
client = LLMClient()
print(f"Using: {client.api_choice} with {client.llm}")

# Run full pipeline
tex_file, pdf_file = orchestrator.run_pipeline(
    pdf_path="Bachelorarbeit_Mueller.pdf",
    date_colloquium="15.01.2026",
    uhrzeit_colloquium="10:00",
    llm_client=client,
    groq_free=True,  # Enable rate limiting if using free tier
    compile_pdf=True
)

print(f"LaTeX file: {tex_file}")
print(f"PDF file: {pdf_file}")
```

### Workflow Integration

```python
# Example: Process thesis in a specific folder
import os
from llm_client import LLMClient
from colloquium_pipeline import orchestrator

folder = os.path.join("..", "BachelorThesen", "2025_26_WS", "Mueller")
pdf_filename = "Bachelorarbeit_Mueller.pdf"
pdf_path = os.path.join(folder, pdf_filename)

llm_client = LLMClient()  # Auto-detects API

tex, pdf = orchestrator.run_pipeline(
    pdf_path=pdf_path,
    date_colloquium="20.01.2026",
    uhrzeit_colloquium="14:00",
    llm_client=llm_client,
    groq_free=True
)
```

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

**Examples:**
- ✅ "Quelle?"
- ✅ "Quelle fehlt"
- ✅ "source"
- ✅ "Source missing"
- ❌ "Quelle fehlt hier an dieser Stelle komplett" (too long)
- ❌ "Consequent" (not a whole word match)

**Impact:** If >4 "Quelle" comments are detected, the summary gets the note: "Häufig fehlen Quellenangaben."

#### 3. Language Comments
Grammar/spelling comments that are **counted** but **not rewritten**.

**Detection Rules:**
Contains keywords: "rechtschreibung", "grammatik", "tippfehler", "ausdruck"

**Examples:**
- "Rechtschreibung"
- "Grammatik"
- "Tippfehler"

**Impact:** If >5 language comments are detected, the summary gets the note: "Viele sprachliche Fehler."

#### 4. Ignore Comments
Special markers that are **completely excluded** from processing.

**Detection Rules:**
Exact match (case-insensitive): "ab hier"

**Usage:** Mark a point in the thesis where you stopped detailed review (e.g., "ab hier" = "from here onwards")

## Output Files

### 1. LaTeX Protocol Letter
**Filename:** `bewertung_brief_<matrikelnr>.tex`

Contains:
- Formal TH Köln letterhead
- Thesis metadata (title, author, matriculation number)
- Thesis summary (from first 10 pages)
- Rewritten questions from first examiner
- Template for second examiner questions
- Presentation evaluation criteria
- Colloquium metadata (duration, demo, question answering)

### 2. Compiled PDF
**Filename:** `bewertung_brief_<matrikelnr>.pdf`

PDF-compiled version of the LaTeX letter (if `compile_pdf=True`)

### 3. Pre-filled Grading Form
**Filename:** `Bewertung <Bachelor/Master>arbeit_Kolloq Inf_<student_name>.pdf`

Automatically filled PDF form with:
- Student name and matriculation number
- Colloquium date and time
- Checkboxes for "Begründung liegt bei" and "Protokoll liegt bei"
- Pre-filled examiner dates
- Start and end times (automatically calculated)

The form remains **editable** so you can still add grades manually.

## Advanced Configuration

### Rate Limiting for Free Tiers

```python
# Enable throttling for Groq free tier
tex, pdf = orchestrator.run_pipeline(
    pdf_path="thesis.pdf",
    date_colloquium="15.01.2026",
    uhrzeit_colloquium="10:00",
    llm_client=client,
    groq_free=True  # Adds delays between API calls
)
```

### Custom LLM Parameters

```python
from llm_client import LLMClient

# Use specific API with custom settings
client = LLMClient(
    api_choice="openai",
    llm="gpt-4o",
    temperature=0.5,      # Lower = more deterministic
    max_tokens=2048       # Longer responses
)
```

### Ollama Local Usage

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.2:1b

# Use without any API keys
colloquium-protocol-creator thesis.pdf
```

## Troubleshooting

### No Annotations Extracted
- Ensure your PDF has actual annotations (not just highlighted text without comments)
- Some PDF viewers don't save annotations properly - try Adobe Acrobat or PDF Expert

### Language Detection Fails
- The tool needs at least 3 comments to detect language
- If you have fewer comments, manually specify the language in the code

### PDF Compilation Fails
- Check that LaTeX is installed: `lualatex --version`
- Install missing LaTeX packages: `tlmgr install <package>`
- Use `--no-compile` flag to skip compilation and check the `.tex` file manually

### Form Pre-filling Fails
- Ensure the correct form template is in the `data/` folder
- Form field names must match exactly (see `pdf_form_filler.py` for field names)

## Statistics Output

The tool provides statistics about comment categories:

```
✅ 23 comments extracted
   • 15 LLM comments (will be rewritten)
   • 5 Quelle comments (counted only)
   • 3 Language comments (counted only)
   • 0 Ignore comments (excluded)
```

If thresholds are exceeded:
- `quelle > 4` → "Häufig fehlen Quellenangaben." added to summary
- `language > 5` → "Viele sprachliche Fehler." added to summary

## Tips for Best Results

1. **Annotate Clearly**: Write comments in full sentences rather than single words
2. **Use Highlights**: Highlight the exact text you're referring to
3. **Be Specific**: Instead of "???" write "Why was this approach chosen?"
4. **Mark Sources**: Use "Quelle?" or "Source?" for missing citations
5. **Language Notes**: Use keywords like "Rechtschreibung" for spelling issues
6. **Stop Point**: Use "ab hier" to mark where you stopped detailed review

## Example Workflow

1. **Annotate PDF**: Read thesis and add comments/highlights
2. **Run Tool**: `colloquium-protocol-creator thesis.pdf`
3. **Review Output**: Check `bewertung_brief_<matrikelnr>.tex`
4. **Edit if Needed**: Manually adjust questions or add notes
5. **Compile Final**: `lualatex bewertung_brief_<matrikelnr>.tex`
6. **Fill Form**: Open `Bewertung Bachelorarbeit_Kolloq Inf_<name>.pdf` and add grades
7. **Print/Send**: Use both documents for the colloquium

## Related Documentation

- [Installation Guide](INSTALL.md)
- [Project Grading Letters](PROJECT.md)
- [Peer Review Comments](REVIEW.md)
- [Testing Guide](TESTING.md)
