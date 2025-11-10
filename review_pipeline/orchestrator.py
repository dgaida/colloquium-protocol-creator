# review_pipeline/orchestrator.py

import os
from typing import Tuple
from llm_client import LLMClient
from colloquium_creator.pdf_processing import extract_text_with_positions, extract_annotations_with_positions
from review_creator.md_generator import find_annotation_context_with_lines, rewrite_comments_markdown, create_review_markdown
from pypdf import PdfReader


def run_review_pipeline(pdf_path: str, llm_client: LLMClient = None, groq_free: bool = False,
                        output_folder: str = None) -> str:
    """Run the peer review pipeline and produce a Markdown review.

    Args:
        pdf_path: Path to the paper PDF.
        llm_client: LLMClient instance for API access. If None, creates a new one.
        groq_free: Whether to apply throttling for free-tier.
        output_folder: Folder to save the markdown. Defaults to PDF folder.

    Returns:
        Path to the generated markdown file.
    """
    if output_folder is None:
        output_folder = os.path.dirname(pdf_path)

    # Create LLMClient if not provided
    if llm_client is None:
        llm_client = LLMClient()
        print(f"Using LLM API: {llm_client.api_choice} with model: {llm_client.llm}")

    pages_words = extract_text_with_positions(pdf_path)
    annotations, stats = extract_annotations_with_positions(pdf_path, False)

    # Page heights (you can get this via PdfReader too)
    reader = PdfReader(pdf_path)
    page_heights = {i: float(p.mediabox.top) for i, p in enumerate(reader.pages)}

    context = find_annotation_context_with_lines(pages_words, annotations, page_heights)
    rewritten = rewrite_comments_markdown(context, llm_client, groq_free=groq_free)

    fileid = os.path.splitext(os.path.basename(pdf_path))[0]
    print(fileid)

    md_path = os.path.join(output_folder, f"review_comments_{fileid}.md")
    create_review_markdown(rewritten, md_path)

    return md_path
