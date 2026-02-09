# src/academic_doc_generator/core/llm.py
"""LLM interface with comprehensive type annotations for API interactions."""

from typing import Dict, List, Optional, Any, Tuple
import json
import time
from llm_client import LLMClient
from . import pdf, latex
from .types import RewrittenComment, ThesisMetadata, LLMClientProtocol
from .prompts import PromptTemplate, build_prompt

# ============================================================================
# Type Definitions and Protocols
# ============================================================================
# Redundant type definitions removed to avoid F811.
# Using definitions from .types instead.


# ============================================================================
# Public Functions
# ============================================================================


def rewrite_comments(
    context_dict: Dict[int, List[pdf.AnnotationContext]],
    llm_client: LLMClientProtocol,
    groq_free: bool = False,
    verbose: bool = False,
) -> Dict[int, List[RewrittenComment]]:
    """Rewrite rough comments into clear, polite questions using LLMClient.

    Only comments categorized as "llm" are rewritten. Comments with category
    "quelle" or "language" are skipped but retained in the results for later
    analysis. Comments with category "ignore" are excluded entirely.

    Args:
        context_dict: Mapping of page numbers to annotation contexts, where each
            annotation dict contains comment, highlighted text, paragraph, and category.
        llm_client: LLM client instance implementing the LLMClientProtocol.
        groq_free: Whether to apply request throttling to stay under Groq's
            free-tier rate limits (4s per request, 10s every 5 requests).
            Defaults to False.
        verbose: If True, prints debug information about responses. Defaults to False.

    Returns:
        Dictionary mapping page numbers to rewritten comments. Skipped comments
        (quelle/language) are excluded from the output.

    Example:
        >>> context = {1: [{'comment': 'Why?', 'highlighted': 'text',
        ...                 'paragraph': 'context', 'category': 'llm'}]}
        >>> client = LLMClient()
        >>> result = rewrite_comments(context, client)
        >>> result[1][0]['rewritten']
        'Could you explain the reasoning behind this approach?'
    """
    rewritten: Dict[int, List[RewrittenComment]] = {}

    for page_num, items in context_dict.items():
        rewritten_items: List[RewrittenComment] = []

        if groq_free and (len(rewritten) + 1) % 5 == 0:
            print("Waiting for 10 seconds to avoid error from API: Too Many Requests")
            time.sleep(10)

        for item in items:
            category = item.get("category", "llm")

            # Skip ignored comments and non-LLM categories
            if category != "llm":
                continue

            if (
                groq_free
            ):  # always wait 4 seconds for rate limit of 30 requests per minute
                time.sleep(4)

            comment = item["comment"]
            paragraph = item["paragraph"]
            highlighted = item["highlighted"]

            prompt = build_prompt(
                PromptTemplate.REWRITE_COMMENT,
                paragraph=paragraph,
                highlighted=highlighted,
                comment=comment,
            )

            messages = [{"role": "user", "content": prompt}]
            rewritten_raw = llm_client.chat_completion(messages)

            if verbose:
                print(f"Response: {rewritten_raw}")

            rewritten_text = latex.escape_for_latex(rewritten_raw, preserve_latex=True)

            rewritten_items.append(
                {
                    "original": comment,
                    "rewritten": rewritten_text,
                    "highlighted": highlighted,
                    "paragraph": paragraph,
                    "category": category,
                }
            )

        if rewritten_items:
            rewritten[page_num] = rewritten_items

    return rewritten


def determine_gender_from_name(first_name: str, llm_client: LLMClientProtocol) -> str:
    """Determine the formal German address (Herr/Frau) from a first name using LLM.

    Args:
        first_name: First/given name of the person.
        llm_client: LLMClient instance for API access.

    Returns:
        str: Either "Herr" or "Frau" based on the name.
    """
    prompt = build_prompt(PromptTemplate.DETERMINE_GENDER, first_name=first_name)

    messages = [{"role": "user", "content": prompt}]
    result = llm_client.chat_completion(messages)

    # Ensure valid output
    if result not in ["Herr", "Frau", "Herr/Frau"]:
        return "Herr/Frau"

    return result


def detect_degree_from_filename(pdf_path: str, llm_client: LLMClientProtocol) -> str:
    """Detect if thesis is Bachelor or Master from PDF filename.

    Args:
        pdf_path: Path to the PDF file.
        llm_client: LLMClient instance for API access.

    Returns:
        str: "Bachelor" or "Master", or None if unable to determine.
    """
    import os

    filename = os.path.basename(pdf_path)

    prompt = build_prompt(PromptTemplate.DETECT_DEGREE, filename=filename)

    messages = [{"role": "user", "content": prompt}]
    response = llm_client.chat_completion(messages).strip()

    # Normalize response
    if "bachelor" in response.lower():
        return "Bachelor"
    elif "master" in response.lower():
        return "Master"
    else:
        return None


def extract_document_metadata(
    pages_text: Dict[int, str],
    language: str,
    llm_client: LLMClientProtocol,
    pdf_path: str = None,
) -> ThesisMetadata:
    """Extract author, matriculation number, title, and examiners from the first two pages.

    Args:
        pages_text: Dictionary mapping page indices to text content.
        language: Language the thesis is written in ("German" or "English").
        llm_client: LLM client instance for API access.
        pdf_path (str, optional): Path to PDF file for fallback degree detection from filename.

    Returns:
        Dictionary with extracted metadata. If any field cannot be extracted,
        it will contain None as the value.

    Example:
        >>> text = {0: "Bachelor Thesis by Max Mustermann (123456)"}
        >>> client = LLMClient()
        >>> metadata = extract_document_metadata(text, "German", client)
        >>> metadata['author']
        'Max Mustermann'
        >>> metadata['sid']
        '123456'
    """
    # Collect first two pages of text (if available)
    sample_text = "\n\n".join(
        [pages_text.get(i, "") for i in sorted(pages_text.keys())[:2]]
    )

    prompt = build_prompt(
        PromptTemplate.EXTRACT_METADATA, language=language, text=sample_text
    )

    messages = [{"role": "user", "content": prompt}]
    content = llm_client.chat_completion(messages)

    try:
        metadata: ThesisMetadata = json.loads(content)
    except json.JSONDecodeError:
        # Return empty metadata or handle error as needed
        # ThesisMetadata is TypedDict(total=False), so {} is valid
        return {}

    # Fallback: Wenn bachelor_master nicht bestimmt werden konnte, versuche es über Dateinamen
    if pdf_path and (
        not metadata.get("bachelor_master") or metadata.get("bachelor_master") is None
    ):
        print("   ⚠️  Bachelor/Master konnte nicht aus Dokument bestimmt werden")
        print("   🔄 Versuche Bestimmung über Dateinamen...")
        degree_from_filename = detect_degree_from_filename(pdf_path, llm_client)
        if degree_from_filename:
            from .types import DegreeType

            metadata["bachelor_master"] = degree_from_filename  # type: ignore[typeddict-item]
            print(f"   ✅ Aus Dateinamen bestimmt: {degree_from_filename}")
        else:
            print("   ❌ Konnte Bachelor/Master auch nicht aus Dateinamen bestimmen")

    return metadata


def summarize_thesis(
    pages_text: Dict[int, str], language: str, llm_client: LLMClientProtocol
) -> str:
    """Summarize the thesis from the first 10 pages in LaTeX-friendly format.

    Args:
        pages_text: Dictionary mapping page indices to text content.
        language: Language the thesis is written in ("German" or "English").
        llm_client: LLM client instance for API access.

    Returns:
        A LaTeX-formatted summary string with escaped special characters.

    Example:
        >>> text = {0: "This thesis examines...", 1: "The methodology..."}
        >>> client = LLMClient()
        >>> summary = summarize_thesis(text, "German", client)
        >>> "untersucht" in summary
        True
        >>> "\\\\\\" in summary  # LaTeX line breaks
        True
    """
    full_text = "\n\n".join([pages_text.get(i, "") for i in sorted(pages_text.keys())])

    prompt = build_prompt(
        PromptTemplate.SUMMARIZE_THESIS, language=language, text=full_text
    )

    messages = [{"role": "user", "content": prompt}]
    latex_summary_raw = llm_client.chat_completion(messages)

    return latex.escape_for_latex(latex_summary_raw, preserve_latex=True)


def detect_language(
    results: Dict[int, List[RewrittenComment]],
    llm_client: LLMClientProtocol,
    groq_free: bool,
    sample_size: int = 3,
) -> str:
    """Detect the language (German or English) of the comments.

    Args:
        results: Dictionary containing rewritten comments per page.
        llm_client: LLM client instance for API access.
        groq_free: Whether to apply request throttling (2 second delay).
        sample_size: Number of sample comments to analyze for language detection.
            Defaults to 3.

    Returns:
        "German" if German language detected, "English" if English.

    Example:
        >>> comments = {1: [{'rewritten': 'Warum wurde das gewählt?'}]}
        >>> client = LLMClient()
        >>> lang = detect_language(comments, client, groq_free=False)
        >>> lang
        'German'
    """
    # Collect a few rewritten comments for language detection
    texts: List[str] = []
    for page, items in results.items():
        for item in items:
            texts.append(item["rewritten"])
            if len(texts) >= sample_size:
                break
        if len(texts) >= sample_size:
            break

    sample_text = "\n".join(texts)

    prompt = build_prompt(PromptTemplate.DETECT_LANGUAGE, text=sample_text)

    messages = [{"role": "user", "content": prompt}]
    lang = llm_client.chat_completion(messages)

    if groq_free:  # wait 2 seconds
        time.sleep(2)

    return lang


def rewrite_comments_in_pdf(
    pdf_path: str,
    llm_client: Optional[LLMClientProtocol] = None,
    groq_free: bool = False,
    verbose: bool = False,
    pdf_processor: Any = None,  # For dependency injection in tests
) -> Tuple[Dict[int, List[RewrittenComment]], pdf.CommentStats]:
    """Extract and rewrite PDF comments into clear, polite questions.

    This function parses the given PDF, extracts annotations, finds their
    textual context, and uses an LLM to rewrite rough comments into
    more understandable, well-phrased questions or feedback.

    Args:
        pdf_path: Path to the PDF file containing comments/annotations.
        llm_client: LLM client instance. If None, creates a new one with
            automatic API selection.
        groq_free: Whether to apply request throttling to stay under
            free-tier rate limits. Defaults to False.
        verbose: If True, prints detailed information about original and
            rewritten comments. Defaults to False.
        pdf_processor: Optional PDF processor module for dependency injection
            in tests. Defaults to None (uses the standard module).

    Returns:
        Tuple of (rewritten_comments, stats):
        - rewritten_comments: Dictionary mapping page numbers (1-based) to lists
          of rewritten comment dicts
        - stats: Statistics about comment categories (quelle, language, ignore counts)

    Example:
        >>> from llm_client import LLMClient
        >>> client = LLMClient()
        >>> rewritten, stats = rewrite_comments_in_pdf("thesis.pdf", client)
        >>> stats
        {'quelle': 3, 'language': 2, 'ignore': 0}
        >>> rewritten[1][0]['category']
        'llm'
    """
    if llm_client is None:
        llm_client = LLMClient()
        print(f"Using LLM API: {llm_client.api_choice} with model: {llm_client.llm}")

    if pdf_processor is None:
        from . import pdf as pdf_proc

        extract_text_with_positions = pdf_proc.extract_text_with_positions
        extract_annotations_with_positions = pdf_proc.extract_annotations_with_positions
        find_annotation_context = pdf_proc.find_annotation_context
    else:
        extract_text_with_positions = pdf_processor.extract_text_with_positions
        extract_annotations_with_positions = (
            pdf_processor.extract_annotations_with_positions
        )
        find_annotation_context = pdf_processor.find_annotation_context

    print(f"Starting to rewrite comments in the thesis {pdf_path}")

    pages_words = extract_text_with_positions(pdf_path)
    annotations, stats = extract_annotations_with_positions(pdf_path)
    context_dict = find_annotation_context(pages_words, annotations)
    comments_rewritten = rewrite_comments(context_dict, llm_client, groq_free)

    if verbose:
        print(stats)
        for page, items in comments_rewritten.items():
            print(f"\n--- Page {page} ---")
            for item in items:
                print("Original:", item["original"])
                print("Rewritten:", item["rewritten"])
                print("Highlighted:", item["highlighted"])
                print("Paragraph:", item["paragraph"])
                print()

    return comments_rewritten, stats


def get_summary_and_metadata_of_pdf(
    pdf_path: str,
    language: str,
    llm_client: Optional[LLMClientProtocol] = None,
    groq_free: bool = False,
    verbose: bool = False,
) -> Tuple[str, ThesisMetadata]:
    """Extract thesis metadata and generate a summary from the PDF.

    This function uses the first pages of the PDF to detect metadata such as
    author, matriculation number, thesis title, and examiners, and generates
    a LaTeX-formatted summary of the thesis content using an LLM.

    Args:
        pdf_path: Path to the thesis PDF.
        language: Language the thesis is written in ("German" or "English").
        llm_client: LLM client instance. If None, creates a new one with
            automatic API selection.
        groq_free: Whether to apply request throttling to stay under
            free-tier rate limits. Adds 20s delay after metadata extraction
            and 2s delay after summarization. Defaults to False.
        verbose: If True, prints the generated summary. Defaults to False.

    Returns:
        Tuple of (summary, metadata):
        - summary: LaTeX-formatted summary of the thesis
        - metadata: Extracted thesis metadata including author, title, examiners

    Example:
        >>> from llm_client import LLMClient
        >>> client = LLMClient()
        >>> summary, metadata = get_summary_and_metadata_of_pdf(
        ...     "thesis.pdf", "German", client
        ... )
        >>> metadata['bachelor_master']
        'Bachelor'
        >>> "untersucht" in summary
        True
    """
    if llm_client is None:
        llm_client = LLMClient()
        print(f"Using LLM API: {llm_client.api_choice} with model: {llm_client.llm}")

    print("Starting to get summary and metadata of the thesis.")

    # get plain text (for metadata detection)
    pages_text = pdf.extract_text_per_page(pdf_path)

    # Extract metadata (mit pdf_path für Fallback)
    metadata = extract_document_metadata(
        pages_text, language, llm_client, pdf_path=pdf_path
    )

    if groq_free:
        print("Waiting for 20 seconds to avoid error: Too Many Requests")
        time.sleep(20)

    summary = summarize_thesis(pages_text, language, llm_client)

    if verbose:
        print("Summary of thesis:\n", summary)

    if groq_free:
        time.sleep(2)

    return summary, metadata
