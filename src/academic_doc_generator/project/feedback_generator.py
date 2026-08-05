# project_creator/feedback_generator.py
"""Logic for extracting and summarizing feedback from PDF annotations."""

from llm_client import LLMClient

from ..core.pdf import (
    extract_annotations_with_positions,
    extract_text_with_positions,
    find_annotation_context,
)
from ..core.prompts import PromptTemplate, build_prompt


def generate_feedback_summary(pdf_path: str, llm_client: LLMClient) -> str:
    """Extract annotations from PDF, rewrite them to feedback, and summarize.

    Args:
        pdf_path: Path to the PDF file.
        llm_client: LLMClient instance for API access.

    Returns:
        A string containing 3-4 bullet points of summarized feedback in German.
    """
    if pdf_path.lower().endswith(".docx"):
        return "- Keine spezifischen Anmerkungen im Dokument gefunden."

    # 1. Extract annotations and text
    pages_words = extract_text_with_positions(pdf_path)
    annotations, _stats = extract_annotations_with_positions(pdf_path, ignore_source=True)

    # 2. Get context for each annotation
    context_dict = find_annotation_context(pages_words, annotations)

    # 3. Rewrite comments to constructive feedback (German)
    # Include all categories except "ignore" (e.g., "llm", "quelle", "language")
    rewritten_feedbacks = []
    for _page, contexts in context_dict.items():
        for ctx in contexts:
            if ctx["category"] == "ignore":
                continue

            comment = ctx["comment"]
            highlighted = ctx["highlighted"]

            prompt = build_prompt(
                PromptTemplate.REWRITE_TO_CONSTRUCTIVE_FEEDBACK,
                highlighted=highlighted,
                comment=comment,
            )
            messages = [{"role": "user", "content": prompt}]
            rewritten = llm_client.chat_completion(messages)
            rewritten_feedbacks.append(rewritten)

    if not rewritten_feedbacks:
        return "- Keine spezifischen Anmerkungen im Dokument gefunden."

    # 4. Summarize feedbacks into 3-4 bullet points (German)
    all_feedbacks_text = "\n".join([f"- {fb}" for fb in rewritten_feedbacks])

    summary_prompt = build_prompt(PromptTemplate.SUMMARIZE_FEEDBACKS, text=all_feedbacks_text)
    summary_messages = [{"role": "user", "content": summary_prompt}]
    summary = llm_client.chat_completion(summary_messages)

    return summary
