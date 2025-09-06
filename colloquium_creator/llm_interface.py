# colloquium_creator/llm_interface.py
"""LLM (Groq) wrapper: rewriting, summarization, metadata extraction."""

from typing import Dict, Tuple
import json
import time
from groq import Groq
from colloquium_creator import pdf_processing


def rewrite_comments(context_dict: Dict[int, list], groq_api_key: str, groq_free: bool = False,
                     verbose: bool = False) -> Dict[int, list]:
    """Rewrite rough comments into clear, polite questions using Groq.

    Args:
        context_dict (dict): Mapping page numbers to annotation contexts
            with 'comment', 'highlighted', and 'paragraph'.
        groq_api_key (str): API key for Groq.
        groq_free (bool): Whether to apply request throttling to stay under
            Groq's free-tier rate limits.
        verbose (bool, optional): If True, prints debug information. Defaults to False.

    Returns:
        dict: Dictionary mapping page numbers to rewritten comments.
    """
    client = Groq(api_key=groq_api_key)
    rewritten = {}

    for page_num, items in context_dict.items():
        rewritten_items = []
        # TODO: only go over first 4 comments. delete this in final version
        # print(len(rewritten))
        # if len(rewritten) > 10:
        #     print("stop")
        #     break

        if groq_free and (len(rewritten) + 1) % 5 == 0:
            print("Waiting for 10 seconds to avoid error from Groq: Too Many Requests")
            time.sleep(10)

        for item in items:
            if groq_free:  # always wait 2 seconds, because rate limit of 30 requests per minute
                # https://console.groq.com/docs/rate-limits
                time.sleep(3)

            comment = item["comment"]
            paragraph = item["paragraph"]
            highlighted = item["highlighted"]

            prompt = f"""
You are given a PDF paragraph, a highlighted text (the exact words the reader commented on),
and the original rough comment/annotation.

Your task: Rewrite the comment into a clear, polite, and specific question or feedback that
directly refers to the highlighted text and is understandable in the context of the paragraph.

IMPORTANT:
- Detect the language of the original comment.
- Always produce the rewritten comment in the SAME language (usually German, sometimes English).
- Format the summary so that it can be directly inserted into a LaTeX document.
- Use normal LaTeX text, not markdown.

Paragraph:
{paragraph}

Highlighted text:
{highlighted}

Original Comment:
{comment}

Rewritten Comment (same language as original):
"""

            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
            )

            if verbose:
                print(response)

            rewritten_raw = response.choices[0].message.content.strip()
            rewritten_text = escape_for_latex(rewritten_raw, preserve_latex=True)

            rewritten_items.append({
                "original": comment,
                "rewritten": rewritten_text,
                "highlighted": highlighted,
                "paragraph": paragraph
            })

        rewritten[page_num] = rewritten_items

    return rewritten


def extract_document_metadata(pages_text: Dict[int, str], language: str, groq_api_key: str) -> dict:
    """Extract author, matriculation number, title, and examiners from the first two pages.

    Args:
        pages_text (dict): Dictionary mapping page indices to text.
        language (str): Language the thesis is written in. Either German or English.
        groq_api_key (str): API key for Groq.

    Returns:
        dict: Dictionary with keys "author", "matriculation_number", "title",
        "first_examiner", "second_examiner".
    """
    # Collect first two pages of text (if available)
    sample_text = "\n\n".join([pages_text.get(i, "") for i in sorted(pages_text.keys())[:2]])

    client = Groq(api_key=groq_api_key)

    prompt = f"""
You are given the first pages of a thesis submitted at a University. 
It is written in {language}. 
Extract the following information if available:

- Author full name
- Matriculation number (Matrikelnr.)
- Title of the thesis
- First examiner (Erstprüfer)
- Christian name of first examiner
- Family name of first examiner
- Second examiner (Zweitprüfer)
- 'Bachelor' if it is a Bachelor thesis or 'Master' if it is a Master thesis

Return the result as a valid JSON object with keys:
"author", "matriculation_number", "title", "first_examiner", "first_examiner_christian", "first_examiner_family", 
"second_examiner", "bachelor_master".

If something is missing, use null as the value.
Do not include any extra text.

Document text:
{sample_text}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    content = response.choices[0].message.content.strip()

    try:
        metadata = json.loads(content)
    except json.JSONDecodeError:
        metadata = {"error": "Could not parse JSON", "raw": content}

    return metadata


def summarize_thesis(pages_text: Dict[int, str], language: str, groq_api_key: str) -> str:
    """Summarize the thesis from the first 10 pages in LaTeX-friendly format.

    Args:
        pages_text (dict): Dictionary mapping page indices to text.
        language (str): Language the thesis is written in. Either German or English.
        groq_api_key (str): API key for Groq.

    Returns:
        str: A LaTeX-formatted summary.
    """
    client = Groq(api_key=groq_api_key)

    full_text = "\n\n".join([pages_text.get(i, "") for i in sorted(pages_text.keys())])

    prompt = f"""
You are given the first ten pages of a thesis submitted to a University. 
Please provide a concise summary in {language}. 

Format the summary so that it can be directly inserted into a LaTeX document.

Formatting rules:
- Use normal LaTeX text, not markdown.
- Use line breaks (`\\\\`) between sentences to improve readability.
- If appropriate, structure the summary as an itemized list with `\\begin{{itemize}} ... \\end{{itemize}}`.
- If you use itemize, then do not add line breaks (`\\\\`) at the end of an item. 
- Avoid special characters that break LaTeX (like unescaped #, $, %, &, _, {{, }}).

The summary should highlight:
- The main topic of the thesis
- The research questions or goals
- The methods used
- The key results (if available in the text)

Text:
{full_text}

Now provide the LaTeX-formatted summary:
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    latex_summary_raw = response.choices[0].message.content.strip()
    return escape_for_latex(latex_summary_raw, preserve_latex=True)


def detect_language(results: Dict[int, list], groq_api_key: str, groq_free: bool, sample_size: int = 3) -> str:
    """Detect the language (German or English) of the comments.

    Args:
        results (dict): Dictionary containing rewritten comments per page.
        groq_api_key (str): API key for Groq.
        groq_free (bool): Whether to apply request throttling to stay under
            Groq's free-tier rate limits.
        sample_size (int, optional): Number of sample comments to analyze. Defaults to 3.

    Returns:
        str: "German" if German, "English" if English.
    """
    client = Groq(api_key=groq_api_key)

    # Collect a few rewritten comments for language detection
    texts = []
    for page, items in results.items():
        for item in items:
            texts.append(item["rewritten"])
            if len(texts) >= sample_size:
                break
        if len(texts) >= sample_size:
            break

    sample_text = "\n".join(texts)

    prompt = f"""
Decide if the following text is written in German or English.
Respond with exactly one word: "German" or "English".

Text:
{sample_text}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    lang = response.choices[0].message.content.strip()

    if groq_free:  # wait 2 seconds, 30 RPM
        # https://console.groq.com/docs/rate-limits
        time.sleep(2)

    return lang


def rewrite_comments_in_pdf(pdf_path: str, groq_api_key: str, groq_free: bool = False, verbose: bool = False,
                            pdf_processor=None):
    """Extract and rewrite PDF comments into clear, polite questions.

    This function parses the given PDF, extracts annotations, finds their
    textual context, and uses a Groq LLM to rewrite rough comments into
    more understandable, well-phrased questions or feedback.

    Args:
        pdf_path (str): Path to the PDF file containing comments/annotations.
        groq_api_key (str): API key for accessing Groq's LLM.
        groq_free (bool): Whether to apply request throttling to stay under
            Groq's free-tier rate limits.
        verbose (bool, optional): If True, prints detailed information about
            original and rewritten comments. Defaults to False.
        pdf_processor:

    Returns:
        dict: A dictionary mapping page numbers (int) to lists of dictionaries
        with the following keys:
            - "original" (str): The raw comment text.
            - "rewritten" (str): The improved, LLM-rewritten comment.
            - "highlighted" (str): The exact highlighted text the comment refers to.
            - "paragraph" (str): The paragraph providing context for the comment.
    """
    if pdf_processor is None:
        from .pdf_processing import extract_text_with_positions, extract_annotations_with_positions, \
            find_annotation_context
    else:
        extract_text_with_positions = pdf_processor.extract_text_with_positions
        extract_annotations_with_positions = pdf_processor.extract_annotations_with_positions
        find_annotation_context = pdf_processor.find_annotation_context

    print(f"Starting to rewrite comments in the thesis {pdf_path}")

    pages_words = extract_text_with_positions(pdf_path)

    annotations = extract_annotations_with_positions(pdf_path)

    context_dict = find_annotation_context(pages_words, annotations)

    comments_rewritten = rewrite_comments(context_dict, groq_api_key, groq_free)

    if verbose:
        # Print results
        for page, items in comments_rewritten.items():
            print(f"\n--- Page {page} ---")
            for item in items:
                print("Original:", item["original"])
                print("Rewritten:", item["rewritten"])
                print("Highlighted:", item["highlighted"])
                print("Paragraph:", item["paragraph"])
                print()

    return comments_rewritten


def get_summary_and_metadata_of_pdf(pdf_path: str, language: str, groq_api_key: str,
                                    groq_free: bool, verbose: bool = False):
    """Extract thesis metadata and generate a summary from the PDF.

    This function uses the first pages of the PDF to detect metadata such as
    author, matriculation number, thesis title, and examiners, and generates
    a LaTeX-formatted summary of the thesis content using a Groq LLM.

    Args:
        pdf_path (str): Path to the thesis PDF.
        language (str): Language the thesis is written in. Either German or English.
        groq_api_key (str): API key for accessing Groq's LLM.
        groq_free (bool): Whether to apply request throttling to stay under
            Groq's free-tier rate limits.
        verbose (bool, optional): If True, prints the generated summary.
            Defaults to False.

    Returns:
        tuple: A tuple (summary, metadata) where:
            - summary (str): LaTeX-formatted summary of the thesis.
            - metadata (dict): Extracted metadata with keys:
                "author", "matriculation_number", "title",
                "first_examiner", "second_examiner".
    """
    print("Starting to get summary and metadata of the thesis.")

    # get plain text (for metadata detection)
    pages_text = pdf_processing.extract_text_per_page(pdf_path)

    # pages_text = {1: "...", 2: "..."} from your Docling parsing
    metadata = extract_document_metadata(pages_text, language, groq_api_key)

    if groq_free:
        print("Waiting for 20 seconds to avoid error from Groq: Too Many Requests")
        time.sleep(20)

    summary = summarize_thesis(pages_text, language, groq_api_key)

    if verbose:
        print("Summary of thesis:\n", summary)

    if groq_free:  # wait 2 seconds, 30 RPM
        # https://console.groq.com/docs/rate-limits
        time.sleep(2)

    return summary, metadata

