# colloquium_pipeline/orchestrator.py
"""High-level pipeline glue: parse PDF -> LLM -> tex -> pdf."""

from typing import Tuple
import os
from colloquium_creator import pdf_processing, llm_interface, latex_generation, utils


def run_pipeline(pdf_path: str, groq_api_key: str, groq_free: bool = False, output_folder: str = None,
                 compile_pdf: bool = True) -> Tuple[str, str]:
    """Execute the full colloquium protocol generation pipeline.

    This function orchestrates the complete workflow for creating a LaTeX
    template (and optionally a compiled PDF) that documents the protocol
    of a thesis colloquium. It processes the thesis PDF, extracts metadata,
    rewrites examiner comments, and generates a formal letter in LaTeX format.

    The pipeline performs the following steps:
        1. Parse the thesis PDF for annotations and extract comments.
        2. Rewrite rough comments into clear, polite questions using a Groq LLM.
        3. Detect the language (German/English) of the comments.
        4. Summarize the thesis and extract metadata such as author, matriculation number,
           title, and examiner names.
        5. Concatenate and LaTeX-format the rewritten comments.
        6. Create a formal letter as a `.tex` file using the collected data.
        7. Optionally compile the `.tex` file into a PDF.

    Args:
        pdf_path: Path to the thesis PDF file.
        groq_api_key: API key for accessing the Groq LLM service.
        groq_free: Whether to apply request throttling to comply with
            Groq's free-tier rate limits. Defaults to False.
        output_folder: Directory where the output `.tex` (and `.pdf` if compiled)
            will be written. If None, defaults to the folder containing `pdf_path`.
        compile_pdf: If True, the generated `.tex` file is compiled into a PDF
            using `lualatex`. Defaults to True.

    Returns:
        tuple[str, str]: A tuple `(tex_path, pdf_path_or_empty)` where:
            - `tex_path`: Path to the generated `.tex` file.
            - `pdf_path_or_empty`: Path to the generated `.pdf` if `compile_pdf=True`,
              otherwise an empty string.

    Raises:
        FileNotFoundError: If the provided `pdf_path` does not exist.
        subprocess.CalledProcessError: If LaTeX compilation fails when `compile_pdf=True`.
        Exception: Any errors raised by the Groq API (e.g., authentication issues).

    Example:
        >>> tex_file, pdf_file = run_pipeline(
        ...     pdf_path="Bachelorarbeit_Mueller.pdf",
        ...     groq_api_key="sk-123...",
        ...     groq_free=True,
        ...     output_folder="./out",
        ...     compile_pdf=True
        ... )
        >>> print(tex_file)
        ./out/bewertung_brief_123456.tex
        >>> print(pdf_file)
        ./out/bewertung_brief_123456.pdf

    Notes:
        - The generated `.tex` file is always created, regardless of the value of
          `compile_pdf`.
        - If the matriculation number cannot be detected, the output file name
          defaults to `bewertung_brief_unknown.tex`.
        - The pipeline **does not grade a thesis**; it only generates a template
          for documenting the colloquium protocol.
    """
    if output_folder is None:
        output_folder = os.path.dirname(pdf_path)

    # 1) rewrite comments
    rewritten, stats = llm_interface.rewrite_comments_in_pdf(pdf_path, groq_api_key, groq_free=groq_free)

    # 2) detect language
    language = llm_interface.detect_language(rewritten, groq_api_key, groq_free)

    # 3) summary & metadata
    summary, metadata = llm_interface.get_summary_and_metadata_of_pdf(pdf_path, language, groq_api_key, groq_free)

    # Example for stats: {"quelle": 3, "language": 7}
    if stats["quelle"] > 4:
        summary = summary + "\\\\Häufig fehlen Quellenangaben."
        print("Häufig fehlen Quellenangaben")
    if stats["language"] > 5:
        summary = summary + "\\\\Viele sprachliche Fehler."
        print("Viele sprachliche Fehler")

    author = metadata.get("author", "Unknown")
    matriculation = metadata.get("matriculation_number", "unknown")
    first_examiner = metadata.get("first_examiner", "Unbekannt")
    second_examiner = metadata.get("second_examiner", "Unbekannt")
    first_examiner_mail = \
        f"{metadata.get('first_examiner_christian','')}.{metadata.get('first_examiner_family','')}@th-koeln.de"

    # 4) concatenate comments and escape/format as needed
    # The rewritten entries are expected to be LaTeX snippets; ensure safe handling:
    questions = latex_generation.concatenate_comments(rewritten, language)

    tex_name = f"bewertung_brief_{matriculation}.tex"
    tex_path = os.path.join(output_folder, tex_name)

    latex_generation.create_formal_letter_tex(
        filename=tex_path,
        recipient="Prüfungsausschuss der TH Köln",
        subject=f"Bewertung {metadata.get('bachelor_master', 'Arbeit')} von {author}",
        title=metadata.get("title", ""),
        author=f"{author}, Matr.-Nr. {matriculation}",
        summary=summary,
        first_examiner=first_examiner,
        second_examiner=second_examiner,
        first_examiner_mail=first_examiner_mail,
        questions=questions
    )

    pdf_path = ""
    if compile_pdf:
        pdf_path = latex_generation.compile_latex_to_pdf(tex_path, output_dir=output_folder)

    return tex_path, pdf_path
