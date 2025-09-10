#

import os
import time
from typing import Dict, List, Tuple
from groq import Groq
from colloquium_creator import latex_generation  # reuse escape_for_latex


def estimate_line_number(y_coord: float, page_height: float, line_height: float = 12.0) -> int:
    """Estimate the line number of a comment based on its y-coordinate.

    Args:
        y_coord: Y-coordinate of the annotation rectangle (PDF origin is bottom-left).
        page_height: Total height of the PDF page.
        line_height: Approximate line spacing in points (default 12pt).

    Returns:
        Estimated line number (1-based).
    """
    # PDF y=0 is bottom, so invert
    distance_from_top = page_height - y_coord
    return max(1, int(distance_from_top / line_height) + 1)


def find_line_number_from_text(words: list, annot_bbox: tuple, x_threshold: float = 20.0) -> int:
    """Try to find a printed line number near the annotation by scanning
    words at the left margin of the page.

    Args:
        words: List of word dicts with "text" and "bbox".
        annot_bbox: (x0, y0, x1, y1) of the annotation.
        x_threshold: Max x-position to still be considered a margin line number.

    Returns:
        int: Detected line number, or -1 if none found.
    """
    ax0, ay0, ax1, ay1 = annot_bbox
    candidate = None

    for w in words:
        wx0, wy0, wx1, wy1 = w["bbox"]
        if wx1 < x_threshold:  # very left margin
            if (wy0 <= ay1 and wy1 >= ay0):  # overlaps in vertical range
                if w["text"].isdigit():
                    candidate = int(w["text"])
                    break

    return candidate if candidate is not None else -1


def find_annotation_context_with_lines(pages_words: dict, annotations: dict, page_heights: dict) -> Dict[int, List[dict]]:
    """Like find_annotation_context, but also attach estimated line numbers.

    Args:
        pages_words: Dictionary of words with positions per page.
        annotations: Extracted annotations per page.
        page_heights: Mapping page index -> page height in points.

    Returns:
        Dict mapping page numbers to list of annotations with line info.
    """
    context_dict = {}
    for page_num, annots in annotations.items():
        page_results = []
        for annot in annots:
            rect = annot["rect"]
            if not rect:
                continue
            x0, y0, x1, y1 = rect

            line_number = find_line_number_from_text(pages_words[page_num], rect)

            if line_number == -1:
                # fallback to geometric estimation
                line_number = estimate_line_number(y1, page_heights[page_num])  # top of rect

            page_results.append({
                "comment": annot["comment"],
                "highlighted": "",
                "paragraph": "",
                "category": annot.get("category", "llm"),
                "line": line_number
            })
        if page_results:
            context_dict[page_num + 1] = page_results
    return context_dict


def rewrite_comments_markdown(context_dict: Dict[int, List[dict]], groq_api_key: str,
                              groq_free: bool = False, verbose: bool = False) -> Dict[int, List[dict]]:
    """Rewrite comments for peer review (Markdown output).

    Args:
        context_dict: Mapping page numbers to annotation dicts including "line".
        groq_api_key: Groq API key.
        groq_free: Whether to apply throttling for free-tier.
        verbose: Print debugging info.

    Returns:
        Dict with rewritten comments per page.
    """
    client = Groq(api_key=groq_api_key)
    rewritten = {}

    for page_num, items in context_dict.items():
        rewritten_items = []

        if groq_free and (len(rewritten) + 1) % 5 == 0:
            print("Waiting 10s for Groq free-tier rate limit")
            time.sleep(10)

        for item in items:
            if item["category"] != "llm":
                continue  # skip non-LLM comments (Quelle, etc.)

            comment = item["comment"]
            paragraph = item.get("paragraph", "")
            highlighted = item.get("highlighted", "")

            prompt = f"""
You are reviewing an academic paper.
Rewrite the following rough reviewer comment into a clear, polite, and constructive
remark addressed to the authors. Keep the meaning, but phrase it in professional
review style. Always write it in English.

Paragraph (if available):
{paragraph}

Highlighted text (if available):
{highlighted}

Original Comment:
{comment}

Rewritten comment (Markdown):
"""

            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
            )

            rewritten_raw = response.choices[0].message.content.strip()

            rewritten_items.append({
                "original": comment,
                "rewritten": rewritten_raw,
                "line": item["line"],
                "page": page_num
            })

        if rewritten_items:
            rewritten[page_num] = rewritten_items

    if verbose:
        print(rewritten)

    return rewritten


def create_review_markdown(rewritten: Dict[int, List[dict]], output_file: str):
    """Create a Markdown review document from rewritten comments.

    Args:
        rewritten: Dictionary of rewritten comments with page/line info.
        output_file: Path to the markdown file.
    """
    lines = ["# Peer Review", "", "Dear authors,", "", "here are my comments on your manuscript:", ""]
    for page, items in rewritten.items():
        for item in items:
            lines.append(f"- Page {page}, Line {item['line']}: {item['rewritten']}")
    text = "\n".join(lines)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Markdown review saved to {output_file}")
