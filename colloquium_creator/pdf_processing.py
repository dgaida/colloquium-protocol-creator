# colloquium_creator/pdf_processing.py
"""PDF processing utilities (Docling + pypdf)."""

from typing import Dict, List, Tuple
import re
from pypdf import PdfReader
from docling_parse.pdf_parser import DoclingPdfParser, PdfDocument
from docling_core.types.doc.page import TextCellUnit


def extract_text_with_positions(pdf_path: str) -> Dict[int, List[dict]]:
    """Extract text and bounding boxes for words from a PDF using Docling.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        dict[int, list[dict]]: Dictionary mapping 0-based page indices to
        a list of words, where each word is represented as a dictionary
        with keys 'text' and 'bbox'.
    """
    parser = DoclingPdfParser()
    pdf_doc = parser.load(path_or_stream=pdf_path)

    pages_words = {}  # keys WILL be 0-based: 0..N-1

    # Enumerate to force 0-based indexing, regardless of docling's page_no (1-based)
    for zero_idx, (_page_no, pred_page) in enumerate(pdf_doc.iterate_pages(), start=0):
        words = []
        for cell in pred_page.iterate_cells(unit_type=TextCellUnit.WORD):
            r = cell.rect  # BoundingRectangle with r_x0, r_y0, r_x1, r_y1 (bottom-left origin)

            # xs = [rect.r_x0, rect.r_x1, rect.r_x2, rect.r_x3]
            # ys = [rect.r_y0, rect.r_y1, rect.r_y2, rect.r_y3]
            # bbox = (min(xs), min(ys), max(xs), max(ys))

            words.append({
                "text": cell.text,
                "bbox": (float(r.r_x0), float(r.r_y0), float(r.r_x1), float(r.r_y1))
            })
        pages_words[zero_idx] = words

    return pages_words


def extract_annotations_with_positions_alt(pdf_path: str) -> Dict[int, List[dict]]:
    """Extract annotations (comments/highlights) and their positions using pypdf.

    Args:
        pdf_path: Path to PDF.

    Returns:
        Dict mapping 0-based page index -> list of annotation dicts:
        { "comment": str, "subtype": ..., "rect": [...], "quadpoints": [...] }
    """
    reader = PdfReader(pdf_path)
    annotations = {}

    for idx, page in enumerate(reader.pages):
        page_annots = []
        if "/Annots" in page:
            for annot_ref in page["/Annots"]:
                annot = annot_ref.get_object()
                subtype = annot.get("/Subtype")
                rect = annot.get("/Rect")
                quadpoints = annot.get("/QuadPoints")
                content = annot.get("/Contents")

                if content:
                    page_annots.append({
                        "comment": content.strip(),
                        "subtype": subtype,
                        "rect": rect,
                        "quadpoints": quadpoints
                    })
        if page_annots:
            annotations[idx] = page_annots
    return annotations


def extract_annotations_with_positions(pdf_path: str,
                                       ignore_source: bool = True) -> Tuple[Dict[int, List[dict]], Dict[str, int]]:
    """Extract annotations (comments/highlights) and their positions using pypdf,
    and categorize special comments.

    Args:
        pdf_path: Path to PDF.

    Returns:
        Tuple of:
        - annotations: Dict mapping 0-based page index -> list of annotation dicts:
            { "comment": str, "subtype": ..., "rect": [...], "quadpoints": [...],
              "category": "llm"|"quelle"|"language"|"ignore" }
        - stats: Dict with counts of special comment categories:
            { "quelle": int, "language": int }
    """
    reader = PdfReader(pdf_path)
    annotations: Dict[int, List[dict]] = {}
    stats = {"quelle": 0, "language": 0}

    for idx, page in enumerate(reader.pages):
        page_annots = []
        if "/Annots" in page:
            for annot_ref in page["/Annots"]:
                annot = annot_ref.get_object()
                subtype = annot.get("/Subtype")
                rect = annot.get("/Rect")
                quadpoints = annot.get("/QuadPoints")
                content = annot.get("/Contents")

                if content:
                    text = content.strip()
                    category = "llm"  # default

                    # --- Categorize ---
                    if text.lower() == "ab hier":
                        category = "ignore"

                    elif ignore_source and ("quelle" in text.lower() or "source" in text.lower()) and len(text) < 15:
                        category = "quelle"
                        stats["quelle"] += 1

                    elif any(kw in text.lower() for kw in ["rechtschreibung", "grammatik", "tippfehler", "ausdruck"]):
                        category = "language"
                        stats["language"] += 1

                    page_annots.append({
                        "comment": text,
                        "subtype": subtype,
                        "rect": rect,
                        "quadpoints": quadpoints,
                        "category": category
                    })

        if page_annots:
            annotations[idx] = page_annots

    return annotations, stats


def words_overlapping_rect(words: List[dict], rect: Tuple[float, float, float, float],
                           tol: float = 0.5) -> List[dict]:
    """Find all words that overlap with a given rectangle.

    Args:
        words (list): List of word dictionaries with 'text' and 'bbox'.
        rect (tuple): Annotation rectangle (x1, y1, x2, y2).
        tol (float, optional): Tolerance factor. Defaults to 0.5.

    Returns:
        list: List of word dictionaries overlapping with the rectangle.
    """
    x0, y0, x1, y1 = rect
    hits = []
    for w in words:
        wx0, wy0, wx1, wy1 = w["bbox"]
        if (wx1 >= x0 - tol and wx0 <= x1 + tol and
                wy1 >= y0 - tol and wy0 <= y1 + tol):
            hits.append(w)
    return hits


def get_words_for_annotation_on_page(pages_words: Dict[int, List[dict]], page_index: int,
                                     rect: Tuple[float, float, float, float]) -> Tuple[int, List[dict]]:
    """Get words that match an annotation rectangle, checking neighboring pages if necessary.

    Args:
        pages_words (dict): Dictionary of pages mapped to word lists.
        page_index (int): Index of the annotated page.
        rect (tuple): Annotation rectangle.

    Returns:
        tuple: (page_index_used, words) where page_index_used is the page
        where words were found, and words is the list of word dicts.
    """
    # Try the given page, then +1, then -1
    candidates = [page_index, page_index + 1, page_index - 1]
    for idx in candidates:
        if idx in pages_words:
            hits = words_overlapping_rect(pages_words[idx], rect)
            if hits:
                return idx, hits
    # fall back to the original page even if empty
    return page_index, []


def rect_overlap(word_bbox, annot_bbox):
    """Check if a word bounding box overlaps with an annotation rectangle.

    Args:
        word_bbox (tuple): Word bounding box (x1, y1, x2, y2).
        annot_bbox (tuple): Annotation bounding box (x1, y1, x2, y2).

    Returns:
        bool: True if the bounding boxes overlap, False otherwise.
    """
    x1, y1, x2, y2 = word_bbox
    ax1, ay1, ax2, ay2 = annot_bbox
    return not (x2 < ax1 or x1 > ax2 or y2 < ay1 or y1 > ay2)


def find_annotation_context(pages_words: Dict[int, List[dict]],
                            annotations: Dict[int, List[dict]]) -> Dict[int, List[dict]]:
    """Match annotations to the words and paragraphs they reference.

    Args:
        pages_words (dict): Words with bounding boxes per page.
        annotations (dict): Annotations per page with rects and comments.

    Returns:
        dict: Dictionary mapping 1-based page numbers to a list of dicts
        with 'comment', 'highlighted', and 'paragraph'.
    """
    context_dict = {}

    for page_num, annots in annotations.items():
        # words = pages_words.get(page_num, [])
        page_results = []

        # full_page_text = " ".join([w["text"] for w in words])
        # paragraphs = re.split(r"\n\s*\n| {2,}", full_page_text)

        for annot in annots:
            rect = annot["rect"]
            if rect:
                annot_bbox = tuple(rect)
            elif annot["quadpoints"]:
                qp = annot["quadpoints"]
                xs = qp[0::2]
                ys = qp[1::2]
                annot_bbox = (min(xs), min(ys), max(xs), max(ys))
            else:
                continue

            # Words under the annotation (with neighbor-page fallback)
            page_idx_for_words, hit_words = get_words_for_annotation_on_page(pages_words, page_num, annot_bbox)
            highlighted_text = " ".join([w["text"] for w in hit_words]).strip()

            # Use the full text of the page where words were actually found
            full_page_text = " ".join([w["text"] for w in pages_words.get(page_idx_for_words, [])])
            paragraphs = re.split(r"\n\s*\n| {2,}", full_page_text)

            # Find paragraph containing the highlighted words
            para_match = None
            for para in paragraphs:
                if highlighted_text and highlighted_text in para:
                    para_match = para
                    break

            if not para_match and paragraphs:
                para_match = paragraphs[0]  # fallback

            page_results.append({
                "comment": annot["comment"],
                "highlighted": highlighted_text,
                "paragraph": para_match
            })

        if page_results:
            # +1 so reported page number is human-readable
            context_dict[page_num + 1] = page_results

    return context_dict


def extract_text_per_page(pdf_path: str, max_pages: int = 10) -> Dict[int, str]:
    """Extract plain text (without positions) for the first `max_pages` pages.

    Args:
        pdf_path (str): Path to the PDF file.
        max_pages (int, optional): Maximum number of pages to read. Defaults to 10.

    Returns:
        dict[int, str]: Dictionary mapping 0-based page indices to the full
        concatenated text of that page.
    """
    parser = DoclingPdfParser()
    pdf_doc = parser.load(path_or_stream=pdf_path)

    pages_text = {}
    for zero_idx, (_page_no, pred_page) in enumerate(pdf_doc.iterate_pages(), start=0):
        if zero_idx >= max_pages:
            break
        words = [cell.text for cell in pred_page.iterate_cells(unit_type=TextCellUnit.WORD)]
        page_text = " ".join(words)
        pages_text[zero_idx] = page_text
    return pages_text
