# project_creator/feedback_generator.py
"""Logic for extracting and summarizing feedback from PDF annotations."""

from llm_client import LLMClient
from ..core.pdf_processing import (
    extract_annotations_with_positions,
    find_annotation_context,
    extract_text_with_positions,
)


def generate_feedback_summary(pdf_path: str, llm_client: LLMClient) -> str:
    """Extract annotations from PDF, rewrite them to feedback, and summarize.

    Args:
        pdf_path: Path to the PDF file.
        llm_client: LLMClient instance for API access.

    Returns:
        A string containing 3-4 bullet points of summarized feedback in German.
    """
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

            prompt = f"""
Du bist ein Professor und bewertest ein Praxisprojekt eines Studierenden.
Schreibe den folgenden kurzen Korrekturkommentar in ein klares, höfliches und konstruktives
Feedback an den Studierenden um. Behalte die Bedeutung bei, aber formuliere es als professionelles
Feedback (KEINE Fragen, sondern direkte Rückmeldung). Schreibe immer auf Deutsch.

Hervorgehobener Text (falls vorhanden):
{highlighted}

Ursprünglicher Kommentar:
{comment}

Umgeschriebenes Feedback:
"""
            messages = [{"role": "user", "content": prompt}]
            rewritten = llm_client.chat_completion(messages)
            rewritten_feedbacks.append(rewritten)

    if not rewritten_feedbacks:
        return "- Keine spezifischen Anmerkungen im Dokument gefunden."

    # 4. Summarize feedbacks into 3-4 bullet points (German)
    all_feedbacks_text = "\n".join([f"- {fb}" for fb in rewritten_feedbacks])

    summary_prompt = f"""
Hier sind verschiedene Feedback-Punkte zu einer studentischen Arbeit:
{all_feedbacks_text}

Fasse dieses Feedback in 3 bis 4 prägnanten Bulletpoints zusammen.
Die Bulletpoints sollen die wichtigsten Stärken und Schwächen der Arbeit hervorheben.
Schreibe auf Deutsch. Starte direkt mit den Bulletpoints.
"""
    summary_messages = [{"role": "user", "content": summary_prompt}]
    summary = llm_client.chat_completion(summary_messages)

    return summary
