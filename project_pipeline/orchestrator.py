# project_pipeline/orchestrator.py
"""High-level pipeline for project work grading letter generation."""

import os
from typing import Tuple
from llm_client import LLMClient
from project_creator.llm_interface import extract_project_metadata, determine_gender_from_name
from project_creator.latex_generation import create_project_grading_letter_tex
from colloquium_creator.latex_generation import compile_latex_to_pdf


def run_project_pipeline(
        pdf_path: str,
        llm_client: LLMClient = None,
        output_folder: str = None,
        compile_pdf: bool = True,
        signature_file: str = "signature.png"
) -> Tuple[str, str]:
    """Execute the full project work grading letter generation pipeline.

    This function orchestrates the complete workflow for creating a LaTeX
    grading letter for a project work (Praxisprojekt). It extracts metadata
    from the PDF, determines the appropriate formal address, and generates
    a letter template.

    The pipeline performs the following steps:
        1. Extract metadata from the project work PDF (student name,
           matriculation number, title, examiner).
        2. Determine the formal address (Herr/Frau) based on the student's
           first name using an LLM.
        3. Generate a LaTeX letter template with TH Köln formatting.
        4. Optionally compile the LaTeX file to PDF.

    Args:
        pdf_path: Path to the project work PDF file.
        llm_client: LLMClient instance for API access. If None, creates a new one
            with automatic API selection.
        output_folder: Directory where the output `.tex` (and `.pdf` if compiled)
            will be written. If None, defaults to the folder containing `pdf_path`.
        compile_pdf: If True, the generated `.tex` file is compiled into a PDF
            using `lualatex`. Defaults to True.
        signature_file: Path to the examiner's signature image file.
            Defaults to "signature.png".

    Returns:
        tuple[str, str]: A tuple `(tex_path, pdf_path_or_empty)` where:
            - `tex_path`: Path to the generated `.tex` file.
            - `pdf_path_or_empty`: Path to the generated `.pdf` if `compile_pdf=True`,
              otherwise an empty string.

    Raises:
        FileNotFoundError: If the provided `pdf_path` does not exist.
        subprocess.CalledProcessError: If LaTeX compilation fails when `compile_pdf=True`.
        Exception: Any errors raised by the LLM API (e.g., authentication issues).

    Example:
        >>> from llm_client import LLMClient
        >>> client = LLMClient()  # Automatic API selection
        >>> tex_file, pdf_file = run_project_pipeline(
        ...     pdf_path="Praxisprojekt_Mueller.pdf",
        ...     llm_client=client,
        ...     output_folder="./out",
        ...     compile_pdf=True
        ... )
        >>> print(tex_file)
        ./out/projektarbeit_brief_123456.tex

    Notes:
        - The semester is automatically determined from the current date.
        - The grade field in the letter is left blank (underlined space) to be
          filled in manually.
        - If the matriculation number cannot be detected, the output filename
          defaults to `projektarbeit_brief_unknown.tex`.
    """
    if output_folder is None:
        output_folder = os.path.dirname(pdf_path)

    # Create LLMClient if not provided
    if llm_client is None:
        llm_client = LLMClient()
        print(f"Using LLM API: {llm_client.api_choice} with model: {llm_client.llm}")

    # Extract metadata from PDF
    print(f"Extracting metadata from {pdf_path}")
    metadata = extract_project_metadata(pdf_path, llm_client)

    student_name = metadata.get("student_name", "Unknown")
    student_first_name = metadata.get("student_first_name", "Unknown")
    matriculation = metadata.get("matriculation_number", "unknown")
    project_title = metadata.get("title", "Unknown")
    examiner = metadata.get("first_examiner", "Unbekannt")
    examiner_mail = (
        f"{metadata.get('first_examiner_christian', '')}"
        f".{metadata.get('first_examiner_family', '')}@th-koeln.de"
    )
    work_type = metadata.get("work_type", "Praxisprojekt")

    # Determine gender from first name
    print(f"Determining gender for first name: {student_first_name}")
    gender = determine_gender_from_name(student_first_name, llm_client)
    print(f"Detected gender: {gender}")

    # Create output filename
    tex_name = f"projektarbeit_brief_{matriculation}.tex"
    tex_path = os.path.join(output_folder, tex_name)

    # Generate LaTeX letter
    create_project_grading_letter_tex(
        filename=tex_path,
        student_name=student_name,
        matriculation_number=matriculation,
        project_title=project_title,
        examiner_name=examiner,
        examiner_mail=examiner_mail,
        gender=gender,
        work_type=work_type,
        signature_file=signature_file
    )

    # Compile to PDF if requested
    pdf_path = ""
    if compile_pdf:
        try:
            pdf_path = compile_latex_to_pdf(tex_path, output_dir=output_folder)
            print(f"PDF compiled: {pdf_path}")
        except Exception as e:
            print(f"PDF compilation failed: {e}")

    return tex_path, pdf_path
