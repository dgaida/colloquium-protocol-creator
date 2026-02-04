# Core Modules API

API reference for the core modules used across all use cases.

## Overview

The core modules provide shared functionality for:

- PDF processing (text extraction, annotation parsing)
- LLM interface (comment rewriting, metadata extraction)
- LaTeX generation (escaping, template creation)
- Utilities (file finding, name parsing)

## PDF Processing (`pdf_processing.py`)

### Functions

#### `extract_text_with_positions()`

```python
def extract_text_with_positions(pdf_path: str) -> Dict[int, List[WordBox]]
```

Extract text and bounding boxes using Docling.

**Parameters:**

- `pdf_path` (str): Path to PDF file

**Returns:** `dict` mapping page indices (0-based) to word lists

**Example:**

```python
from academic_doc_generator.core.pdf_processing import extract_text_with_positions

words = extract_text_with_positions("thesis.pdf")
print(words[0][0])
# {'text': 'Introduction', 'bbox': (72.0, 720.0, 150.0, 735.0)}
```

#### `extract_annotations_with_positions()`

```python
def extract_annotations_with_positions(
    pdf_path: str,
    ignore_source: bool = True
) -> Tuple[Dict[int, List[AnnotationData]], CommentStats]
```

Extract PDF annotations with categorization.

**Parameters:**

- `pdf_path` (str): Path to PDF
- `ignore_source` (bool): Categorize source comments as "quelle"

**Returns:** `(annotations, stats)` tuple

**Categories:**

- `"llm"` - Regular comments (sent to LLM)
- `"quelle"` - Source-related (counted only)
- `"language"` - Grammar/spelling (counted only)
- `"ignore"` - "ab hier" markers (excluded)

**Example:**

```python
from academic_doc_generator.core.pdf_processing import extract_annotations_with_positions

annotations, stats = extract_annotations_with_positions("thesis.pdf")
print(stats)
# {'quelle': 5, 'language': 3, 'ignore': 1}
```

#### `find_annotation_context()`

```python
def find_annotation_context(
    pages_words: Dict[int, List[WordBox]],
    annotations: Dict[int, List[AnnotationData]]
) -> Dict[int, List[AnnotationContext]]
```

Match annotations to words and paragraphs.

**Parameters:**

- `pages_words` (dict): Words per page from `extract_text_with_positions()`
- `annotations` (dict): Annotations from `extract_annotations_with_positions()`

**Returns:** `dict` mapping page numbers (1-based) to contexts

**Example:**

```python
from academic_doc_generator.core.pdf_processing import (
    extract_text_with_positions,
    extract_annotations_with_positions,
    find_annotation_context
)

pages_words = extract_text_with_positions("thesis.pdf")
annotations, _ = extract_annotations_with_positions("thesis.pdf")
context = find_annotation_context(pages_words, annotations)

for page, contexts in context.items():
    for ctx in contexts:
        print(f"Page {page}: {ctx['comment']}")
        print(f"Highlighted: {ctx['highlighted']}")
```

#### `is_quelle_comment()`

```python
def is_quelle_comment(text: str, max_length: int = 20) -> bool
```

Check if comment is source-related.

**Parameters:**

- `text` (str): Comment text
- `max_length` (int): Maximum length for source comments

**Returns:** `bool` - True if source comment

**Detection Rules:**

- ≤20 characters long
- Contains "quelle" or "source" as whole word

**Example:**

```python
from academic_doc_generator.core.pdf_processing import is_quelle_comment

print(is_quelle_comment("Quelle?"))  # True
print(is_quelle_comment("Source missing"))  # True
print(is_quelle_comment("Consequent"))  # False (not whole word)
print(is_quelle_comment("Quelle fehlt hier komplett"))  # False (too long)
```

## LLM Interface (`llm_interface.py`)

### Functions

#### `rewrite_comments_in_pdf()`

```python
def rewrite_comments_in_pdf(
    pdf_path: str,
    llm_client: Optional[LLMClientProtocol] = None,
    groq_free: bool = False,
    verbose: bool = False
) -> Tuple[Dict[int, List[RewrittenComment]], CommentStats]
```

Extract and rewrite PDF comments.

**Parameters:**

- `pdf_path` (str): Path to PDF
- `llm_client` (LLMClientProtocol | None): LLM client
- `groq_free` (bool): Enable rate limiting
- `verbose` (bool): Print debug info

**Returns:** `(rewritten_comments, stats)` tuple

**Example:**

```python
from llm_client import LLMClient
from academic_doc_generator.core.llm_interface import rewrite_comments_in_pdf

client = LLMClient()
rewritten, stats = rewrite_comments_in_pdf("thesis.pdf", client)

print(f"Statistics: {stats}")
# {'quelle': 3, 'language': 2, 'ignore': 0}

for page, items in rewritten.items():
    for item in items:
        print(f"Page {page}: {item['rewritten']}")
```

#### `get_summary_and_metadata_of_pdf()`

```python
def get_summary_and_metadata_of_pdf(
    pdf_path: str,
    language: str,
    llm_client: Optional[LLMClientProtocol] = None,
    groq_free: bool = False,
    verbose: bool = False
) -> Tuple[str, ThesisMetadata]
```

Extract metadata and generate summary.

**Parameters:**

- `pdf_path` (str): Path to PDF
- `language` (str): "German" or "English"
- `llm_client` (LLMClientProtocol | None): LLM client
- `groq_free` (bool): Enable rate limiting
- `verbose` (bool): Print summary

**Returns:** `(summary, metadata)` tuple

**Example:**

```python
from llm_client import LLMClient
from academic_doc_generator.core.llm_interface import get_summary_and_metadata_of_pdf

client = LLMClient()
summary, metadata = get_summary_and_metadata_of_pdf(
    "thesis.pdf", "German", client
)

print(f"Author: {metadata['author']}")
print(f"Title: {metadata['title']}")
print(f"Degree: {metadata['bachelor_master']}")
```

#### `detect_language()`

```python
def detect_language(
    results: Dict[int, List[RewrittenComment]],
    llm_client: LLMClientProtocol,
    groq_free: bool
) -> str
```

Detect language from rewritten comments.

**Parameters:**

- `results` (dict): Rewritten comments
- `llm_client` (LLMClientProtocol): LLM client
- `groq_free` (bool): Enable rate limiting

**Returns:** `str` - "German" or "English"

**Example:**

```python
from llm_client import LLMClient
from academic_doc_generator.core.llm_interface import detect_language

client = LLMClient()
comments = {1: [{'rewritten': 'Warum wurde das gewählt?'}]}
lang = detect_language(comments, client, groq_free=False)
print(lang)  # "German"
```

## LaTeX Generation (`latex_generation.py`)

### Functions

#### `escape_for_latex()`

```python
def escape_for_latex(text: str, preserve_latex: bool = True) -> str
```

Escape special characters for LaTeX.

**Parameters:**

- `text` (str): Input text
- `preserve_latex` (bool): Keep LaTeX commands intact

**Returns:** `str` - LaTeX-safe string

**Escapes:**

- Special chars: `&`, `%`, `$`, `#`, `_`
- German ß: `{\ss}`
- Dash-like Unicode: `{-}` or `-`

**Example:**

```python
from academic_doc_generator.core.latex_generation import escape_for_latex

text = "Smith & Jones (2024) found α = 50%"
safe = escape_for_latex(text)
print(safe)
# "Smith \& Jones (2024) found α = 50\%"
```

#### `create_formal_letter_tex()`

```python
def create_formal_letter_tex(
    filename: str,
    recipient: str,
    subject: str,
    title: str,
    author: str,
    summary: str,
    first_examiner: str,
    second_examiner: str,
    first_examiner_mail: str,
    questions: str,
    place: str = "Gummersbach",
    date: str = r"\today",
    gemini_evaluation: Optional[str] = None
)
```

Create LaTeX letter with TH Köln formatting.

**Parameters:**

- `filename` (str): Output path
- `recipient` (str): Letter recipient
- `subject` (str): Subject line
- `title` (str): Thesis title
- `author` (str): Student name
- `summary` (str): Thesis summary (LaTeX)
- `first_examiner` (str): First examiner name
- `second_examiner` (str): Second examiner name
- `first_examiner_mail` (str): Examiner email
- `questions` (str): Formatted questions (LaTeX)
- `place` (str): Place of issue
- `date` (str): Date string
- `gemini_evaluation` (str | None): Optional Gemini evaluation

**Example:**

```python
from academic_doc_generator.core.latex_generation import create_formal_letter_tex

create_formal_letter_tex(
    filename="bewertung.tex",
    recipient="Prüfungsausschuss der TH Köln",
    subject="Bewertung Bachelor Arbeit",
    title="KI-basierte Objekterkennung",
    author="Max Mustermann, Matr.-Nr. 123456",
    summary="Die Arbeit untersucht...",
    first_examiner="Prof. Dr. Müller",
    second_examiner="Prof. Dr. Schmidt",
    first_examiner_mail="anna.mueller@th-koeln.de",
    questions="Seite 5: Warum wurde diese Methode gewählt?"
)
```

#### `compile_latex_to_pdf()`

```python
def compile_latex_to_pdf(
    tex_path: str,
    output_dir: str = None,
    engine: str = "lualatex"
) -> str
```

Compile LaTeX to PDF.

**Parameters:**

- `tex_path` (str): Path to `.tex` file
- `output_dir` (str | None): Output directory
- `engine` (str): LaTeX engine ("lualatex" or "pdflatex")

**Returns:** `str` - Path to generated PDF (or empty on error)

**Example:**

```python
from academic_doc_generator.core.latex_generation import compile_latex_to_pdf

pdf_path = compile_latex_to_pdf("bewertung.tex")
if pdf_path:
    print(f"PDF created: {pdf_path}")
```

#### `concatenate_comments()`

```python
def concatenate_comments(
    results: Dict[int, list],
    language: str,
    verbose: bool = False
) -> str
```

Concatenate comments into LaTeX string.

**Parameters:**

- `results` (dict): Rewritten comments per page
- `language` (str): "German" or "English"
- `verbose` (bool): Print result

**Returns:** `str` - LaTeX-formatted questions

**Example:**

```python
from academic_doc_generator.core.latex_generation import concatenate_comments

results = {
    1: [{'rewritten': 'Why was this approach chosen?'}],
    2: [{'rewritten': 'How does this scale?'}]
}

questions = concatenate_comments(results, "English")
# "page 1: Why was this approach chosen? \\\n\\\npage 2: How does this scale?"
```

## Utilities (`utils.py`)

### Functions

#### `split_student_name()`

```python
def split_student_name(full_name: str) -> Tuple[str, str]
```

Split name into first and last.

**Parameters:**

- `full_name` (str): Full name ("Last, First" or "First Last")

**Returns:** `(first_name, last_name)` tuple

**Example:**

```python
from academic_doc_generator.core.utils import split_student_name

first, last = split_student_name("Mustermann, Max")
print(first, last)  # "Max" "Mustermann"

first, last = split_student_name("Max Mustermann")
print(first, last)  # "Max" "Mustermann"
```

#### `find_latest_tex()`

```python
def find_latest_tex(
    folder: str,
    pattern: str = "bewertung_brief_*.tex"
) -> Optional[str]
```

Find newest matching `.tex` file.

**Parameters:**

- `folder` (str): Search folder
- `pattern` (str): Glob pattern

**Returns:** `str | None` - Path to newest file

**Example:**

```python
from academic_doc_generator.core.utils import find_latest_tex

tex_file = find_latest_tex("/path/to/output")
if tex_file:
    print(f"Latest: {tex_file}")
```

## Type Definitions

See [`types.py`](../types.md) for complete type definitions.

### Key Types

```python
from academic_doc_generator.core.types import (
    WordBox,
    AnnotationData,
    AnnotationContext,
    RewrittenComment,
    ThesisMetadata,
    CommentStats
)
```

## See Also

- [LLM Interface API](llm_interface.md)
- [Configuration Loader API](config_loader.md)
- [Type Definitions](../types.md)
