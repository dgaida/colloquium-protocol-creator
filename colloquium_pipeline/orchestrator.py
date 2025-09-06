# colloquium_pipeline/orchestrator.py
"""High-level pipeline glue: parse PDF -> LLM -> tex -> pdf."""

from typing import Tuple
import os
from colloquium_creator import pdf_processing, llm_interface, latex_generation, utils


def run_pipeline(pdf_path: str, groq_api_key: str, groq_free: bool = False, output_folder: str = None,
                 compile_pdf: bool = True) -> Tuple[str, str]:
    """Run the full pipeline. Returns (tex_path, pdf_path_or_empty).

    Steps:
      - parse PDF for annotations
      - rewrite comments via LLM
      - detect language
      - produce summary & metadata
      - create tex file (bewertung_brief_<matr>.tex)
      - optionally compile to PDF
    """
    if output_folder is None:
        output_folder = os.path.dirname(pdf_path)

    # 1) rewrite comments
    rewritten = llm_interface.rewrite_comments_in_pdf(pdf_path, groq_api_key, groq_free=groq_free)

    # 2) detect language
    language = llm_interface.detect_language(rewritten, groq_api_key, groq_free)

    # 3) summary & metadata
    summary, metadata = llm_interface.get_summary_and_metadata_of_pdf(pdf_path, language, groq_api_key, groq_free)

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
