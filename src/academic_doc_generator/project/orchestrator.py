# project_pipeline/orchestrator.py
"""High-level pipeline for project work grading letter generation."""

import os
from typing import Optional
from pathlib import Path
from llm_client import LLMClient
from .llm_interface import (
    extract_project_metadata,
    determine_gender_from_name,
)
from .feedback_generator import generate_feedback_summary
from ..core.utils import split_student_name
from .latex_generation import create_project_grading_letter_tex
from ..core.latex_generation import compile_latex_to_pdf
from ..core.types import ProjectResult, LLMClientProtocol
from ..colloquium.email_generator import EmailGenerator
from ..colloquium.outlook_mail_generator import OutlookMailGenerator


def run_project_pipeline(
    pdf_path: str | Path,
    llm_client: Optional[LLMClientProtocol] = None,
    output_folder: Optional[str | Path] = None,
    compile_pdf: bool = True,
    signature_file: str = "signature.png",
    grade: Optional[str] = None,
    create_feedback_mail: bool = True,
) -> ProjectResult:
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
        5. Generate grading email template.
        6. Optionally create Outlook mail draft.

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
        grade: The grade obtained for the project.
        create_feedback_mail: If True, generates a feedback summary and an email
            template for the student. Defaults to True.

    Returns:
        tuple[str, str, str, str]: A tuple `(tex_path, pdf_path, service_email_path, student_email_path)` where:
            - `tex_path`: Path to the generated `.tex` file.
            - `pdf_path`: Path to the generated `.pdf` if `compile_pdf=True`,
              otherwise an empty string.
            - `service_email_path`: Path to the generated email markdown file for the examination service.
            - `student_email_path`: Path to the generated email markdown file for the student (empty if disabled).

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
    student_first_name, student_last_name = split_student_name(student_name)
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

    # Check for signature in data/
    data_signature = os.path.join("data", "signature.png")
    if os.path.exists(data_signature):
        signature_file = data_signature
        print(f"Using signature found in {data_signature}")

    # Create output filename
    tex_name = f"bewertung_projekt_{matriculation}.tex"
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
        signature_file=signature_file,
        grade=grade,
    )

    # Compile to PDF if requested
    compiled_pdf_path = ""
    if compile_pdf:
        compiled_pdf_path = compile_latex_to_pdf(tex_path, output_dir=output_folder)
        if compiled_pdf_path:
            print(f"✅ PDF compiled: {compiled_pdf_path}")

    # Generate email for Prüfungsservice
    mymailgen = EmailGenerator()
    grading_email_text = mymailgen.generate_final_grade_email(
        evaluator_client=llm_client,
        first_name=student_first_name,
        last_name=student_last_name,
        student_identifier=matriculation,
        examiner_name=examiner,
    )
    email_path = mymailgen.save_email_to_markdown(
        output_folder=output_folder,
        student_last_name=student_last_name,
        matriculation_number=matriculation,
        filename_prefix="bewertung_projekt_email",
    )

    # Generate student feedback email
    student_email_path = ""
    if create_feedback_mail:
        print("\n📝 Generiere Feedback-Zusammenfassung...")
        feedback_bullets = generate_feedback_summary(pdf_path, llm_client)

        student_email_text = mymailgen.generate_student_feedback_email(
            gender=gender,
            last_name=student_last_name,
            grade=grade if grade else "[NOTE]",
            feedback_bulletpoints=feedback_bullets,
            examiner_name=examiner,
        )
        student_email_path = mymailgen.save_email_to_markdown(
            output_folder=output_folder,
            student_last_name=student_last_name,
            matriculation_number=matriculation,
            filename_prefix="feedback_projekt_email",
        )

    # Create Outlook mail drafts if grade is provided
    if grade is not None:
        outlook_gen = OutlookMailGenerator()

        # 1. Draft for Prüfungsservice
        print("\n📧 Erstelle Outlook-Mail für Prüfungsservice...")
        try:
            outlook_gen.create_outlook_mail(
                student_name=student_name,
                email_text=grading_email_text,
                attachment_path=compiled_pdf_path if compiled_pdf_path else None,
                subject=f"Bewertung Praxisprojekt {gender} {student_first_name} {student_last_name}",
                verbose=False,
            )
        except Exception as e:
            print(f"⚠️  Fehler beim Erstellen der Outlook-Mail (Service): {e}")

        # 2. Draft for Student (only if Outlook is open)
        if create_feedback_mail:
            if outlook_gen.is_outlook_open():
                print("\n📧 Erstelle Outlook-Mail für Studierenden...")
                student_email_addr = metadata.get("student_email")
                try:
                    outlook_gen.create_outlook_mail(
                        student_name=student_name,
                        email_text=student_email_text,
                        attachment_path=None,
                        subject=f"Feedback zu Ihrem Praxisprojekt - {student_name}",
                        recipient=student_email_addr if student_email_addr else "",
                        verbose=False,
                    )
                except Exception as e:
                    print(f"⚠️  Fehler beim Erstellen der Outlook-Mail (Student): {e}")
            else:
                print(
                    "\nℹ️  Outlook ist nicht geöffnet. Student-Feedback-Mail nur als .md gespeichert."
                )

    return tex_path, compiled_pdf_path, email_path, student_email_path
