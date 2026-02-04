# LLM Interface API

Detailed API reference for LLM-based text processing functions.

## Overview

The LLM interface module provides high-level functions for:

- Comment rewriting (rough → polished questions)
- Language detection
- Metadata extraction
- Thesis summarization
- Gender determination

All functions support multiple LLM providers through the `llm_client` package.

## Comment Rewriting

### `rewrite_comments()`

```python
def rewrite_comments(
    context_dict: Dict[int, List[AnnotationContext]],
    llm_client: LLMClientProtocol,
    groq_free: bool = False,
    verbose: bool = False
) -> Dict[int, List[RewrittenComment]]
```

Rewrite annotations into clear, polite questions.

**Parameters:**

- `context_dict` (dict): Annotations with context (from `find_annotation_context()`)
- `llm_client` (LLMClientProtocol): LLM client instance
- `groq_free` (bool): Enable rate limiting (4s per request, 10s every 5)
- `verbose` (bool): Print API responses

**Returns:** `dict` mapping pages to rewritten comments

**Processing Rules:**

- **"llm" comments**: Rewritten by LLM
- **"quelle" comments**: Skipped (not rewritten)
- **"language" comments**: Skipped
- **"ignore" comments**: Excluded entirely

**Example:**

```python
from llm_client import LLMClient
from academic_doc_generator.core.pdf_processing import (
    extract_text_with_positions,
    extract_annotations_with_positions,
    find_annotation_context
)
from academic_doc_generator.core.llm_interface import rewrite_comments

# Extract annotations
pages_words = extract_text_with_positions("thesis.pdf")
annotations, stats = extract_annotations_with_positions("thesis.pdf")
context = find_annotation_context(pages_words, annotations)

# Rewrite
client = LLMClient()
rewritten = rewrite_comments(context, client, groq_free=True)

for page, items in rewritten.items():
    for item in items:
        print(f"Original: {item['original']}")
        print(f"Rewritten: {item['rewritten']}")
```

**Prompt Template:**

The LLM receives:

```
Paragraph: [context paragraph]
Highlighted text: [exact words]
Original Comment: [rough note]

Task: Rewrite into clear, polite question in SAME language
```

### `rewrite_comments_in_pdf()`

```python
def rewrite_comments_in_pdf(
    pdf_path: str,
    llm_client: Optional[LLMClientProtocol] = None,
    groq_free: bool = False,
    verbose: bool = False,
    pdf_processor: Any = None
) -> Tuple[Dict[int, List[RewrittenComment]], CommentStats]
```

Complete pipeline: extract → rewrite → return with stats.

**Parameters:**

- `pdf_path` (str): Path to annotated PDF
- `llm_client` (LLMClientProtocol | None): LLM client (auto-creates if None)
- `groq_free` (bool): Rate limiting
- `verbose` (bool): Debug output
- `pdf_processor` (Any): PDF module (for testing/injection)

**Returns:** `(rewritten, stats)` tuple

**Example:**

```python
from llm_client import LLMClient
from academic_doc_generator.core.llm_interface import rewrite_comments_in_pdf

client = LLMClient()
rewritten, stats = rewrite_comments_in_pdf("thesis.pdf", client)

print(f"✅ {len(rewritten)} pages with comments")
print(f"📊 Stats: {stats}")
# {'quelle': 5, 'language': 3, 'ignore': 1}
```

## Language Detection

### `detect_language()`

```python
def detect_language(
    results: Dict[int, List[RewrittenComment]],
    llm_client: LLMClientProtocol,
    groq_free: bool,
    sample_size: int = 3
) -> str
```

Detect language from rewritten comments.

**Parameters:**

- `results` (dict): Rewritten comments
- `llm_client` (LLMClientProtocol): LLM client
- `groq_free` (bool): Rate limiting (adds 2s delay)
- `sample_size` (int): Number of comments to analyze

**Returns:** `str` - "German" or "English"

**Example:**

```python
from llm_client import LLMClient
from academic_doc_generator.core.llm_interface import detect_language

client = LLMClient()
comments = {
    1: [{'rewritten': 'Warum wurde diese Methode gewählt?'}],
    2: [{'rewritten': 'Könnten Sie das näher erläutern?'}]
}

lang = detect_language(comments, client, groq_free=False)
print(lang)  # "German"
```

**Prompt:**

```
Decide if the following text is written in German or English.
Respond with exactly one word: "German" or "English".

Text:
[sample comments]
```

## Metadata Extraction

### `extract_document_metadata()`

```python
def extract_document_metadata(
    pages_text: Dict[int, str],
    language: str,
    llm_client: LLMClientProtocol,
    pdf_path: str = None
) -> ThesisMetadata
```

Extract thesis metadata from first pages.

**Parameters:**

- `pages_text` (dict): Page texts (from `extract_text_per_page()`)
- `language` (str): Document language
- `llm_client` (LLMClientProtocol): LLM client
- `pdf_path` (str | None): PDF path for fallback degree detection

**Returns:** `ThesisMetadata` dict with keys:

- `author` (str | None): Student full name
- `matriculation_number` (str | None): Matrikelnummer
- `title` (str | None): Thesis title
- `first_examiner` (str | None): Examiner name
- `first_examiner_christian` (str | None): First name
- `first_examiner_family` (str | None): Last name
- `second_examiner` (str | None): Second examiner
- `bachelor_master` (str | None): "Bachelor" or "Master"

**Example:**

```python
from llm_client import LLMClient
from academic_doc_generator.core.pdf_processing import extract_text_per_page
from academic_doc_generator.core.llm_interface import extract_document_metadata

client = LLMClient()
pages_text = extract_text_per_page("thesis.pdf", max_pages=2)
metadata = extract_document_metadata(pages_text, "German", client)

print(f"Author: {metadata['author']}")
print(f"Matrikelnr.: {metadata['matriculation_number']}")
print(f"Title: {metadata['title']}")
print(f"Degree: {metadata['bachelor_master']}")
```

**Fallback Behavior:**

If `bachelor_master` cannot be determined from document:

1. Tries filename detection via `detect_degree_from_filename()`
2. Sets to `None` if both fail

### `detect_degree_from_filename()`

```python
def detect_degree_from_filename(pdf_path: str, llm_client: LLMClient) -> str
```

Detect Bachelor/Master from filename.

**Parameters:**

- `pdf_path` (str): PDF file path
- `llm_client` (LLMClient): LLM client

**Returns:** `str` - "Bachelor", "Master", or `None`

**Example:**

```python
from llm_client import LLMClient
from academic_doc_generator.core.llm_interface import detect_degree_from_filename

client = LLMClient()
degree = detect_degree_from_filename("Bachelorarbeit_Mueller.pdf", client)
print(degree)  # "Bachelor"
```

## Summarization

### `summarize_thesis()`

```python
def summarize_thesis(
    pages_text: Dict[int, str],
    language: str,
    llm_client: LLMClientProtocol
) -> str
```

Generate LaTeX-formatted thesis summary.

**Parameters:**

- `pages_text` (dict): Page texts (first 10 pages)
- `language` (str): "German" or "English"
- `llm_client` (LLMClientProtocol): LLM client

**Returns:** `str` - LaTeX-safe summary

**Prompt Requirements:**

- Format: LaTeX text (not Markdown)
- Use line breaks (`\\`)
- Optional: `\begin{itemize}` for structure
- No special chars that break LaTeX

**Example:**

```python
from llm_client import LLMClient
from academic_doc_generator.core.pdf_processing import extract_text_per_page
from academic_doc_generator.core.llm_interface import summarize_thesis

client = LLMClient()
pages_text = extract_text_per_page("thesis.pdf", max_pages=10)
summary = summarize_thesis(pages_text, "German", client)

print(summary)
# Die Arbeit untersucht den Einsatz von KI... \\
# Es werden folgende Methoden verwendet... \\
# Die Ergebnisse zeigen...
```

### `get_summary_and_metadata_of_pdf()`

```python
def get_summary_and_metadata_of_pdf(
    pdf_path: str,
    language: str,
    llm_client: Optional[LLMClientProtocol] = None,
    groq_free: bool = False,
    verbose: bool = False
) -> Tuple[str, ThesisMetadata]
```

Combined metadata + summary extraction.

**Parameters:**

- `pdf_path` (str): Path to PDF
- `language` (str): Document language
- `llm_client` (LLMClientProtocol | None): LLM client
- `groq_free` (bool): Rate limiting (20s after metadata, 2s after summary)
- `verbose` (bool): Print summary

**Returns:** `(summary, metadata)` tuple

**Example:**

```python
from llm_client import LLMClient
from academic_doc_generator.core.llm_interface import get_summary_and_metadata_of_pdf

client = LLMClient()
summary, metadata = get_summary_and_metadata_of_pdf(
    "thesis.pdf", "German", client, groq_free=True
)

print(f"Author: {metadata['author']}")
print(f"\nSummary:\n{summary}")
```

## Rate Limiting

### Groq Free Tier

When `groq_free=True`:

**`rewrite_comments()`:**
- 4 seconds per request
- Additional 10 seconds every 5 requests

**`get_summary_and_metadata_of_pdf()`:**
- 20 seconds after metadata
- 2 seconds after summary

**Example:**

```python
# Total time for 10 comments with groq_free=True:
# 10 * 4s = 40s (base)
# 2 * 10s = 20s (every 5 requests)
# Total: ~60 seconds
```

## Error Handling

### API Errors

```python
from llm_client import LLMClient
from academic_doc_generator.core.llm_interface import rewrite_comments_in_pdf

try:
    client = LLMClient()
    rewritten, stats = rewrite_comments_in_pdf("thesis.pdf", client)
    
except Exception as e:
    if "Too Many Requests" in str(e):
        print("⚠️  Rate limit exceeded. Enable groq_free=True")
    elif "Authentication" in str(e):
        print("❌ Check API keys in secrets.env")
    else:
        print(f"❌ Error: {e}")
```

### Validation

```python
from academic_doc_generator.core.llm_interface import extract_document_metadata

metadata = extract_document_metadata(pages_text, "German", client)

# Check for missing data
if metadata.get("author") is None:
    print("⚠️  Could not detect student name")
    
if metadata.get("bachelor_master") is None:
    print("⚠️  Could not determine degree type")
```

## Advanced Usage

### Custom Prompts

The module uses predefined prompts, but you can use `llm_client` directly for custom prompts:

```python
from llm_client import LLMClient

client = LLMClient()

custom_prompt = """
Rewrite this comment in academic style:
[comment]
"""

messages = [{"role": "user", "content": custom_prompt}]
response = client.chat_completion(messages)
```

### Multi-Language Support

```python
# Detect and process in original language
rewritten, _ = rewrite_comments_in_pdf("thesis.pdf", client)
lang = detect_language(rewritten, client, groq_free=False)

if lang == "German":
    summary, metadata = get_summary_and_metadata_of_pdf(
        "thesis.pdf", "German", client
    )
else:
    summary, metadata = get_summary_and_metadata_of_pdf(
        "thesis.pdf", "English", client
    )
```

## See Also

- [Core Modules API](core.md)
- [Configuration Loader API](config_loader.md)
- [LLM Client Documentation](https://github.com/dgaida/llm_client)
