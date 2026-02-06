# src/academic_doc_generator/project/orchestrator.py
"""High-level pipeline for project work grading letter generation."""

import os
from pathlib import Path
from llm_client import LLMClient
from ..core import pdf
from ..domain.metadata import generate_metadata_file
from .llm import (
    extract_project_metadata,
)
from ..core.llm import determine_gender_from_name
from .feedback_generator import generate_feedback_summary
from ..core.utils import split_student_name, get_semester
from .latex import create_project_grading_letter_tex
from ..core.latex import compile_latex_to_pdf
from ..core.types import (
    ProjectWorkflowResult,
    ProjectWorkflowConfig,
)
from ..colloquium.email_generator import EmailGenerator
from ..colloquium.outlook_mail_generator import OutlookMailGenerator


def run_project_pipeline(config: ProjectWorkflowConfig) -> ProjectWorkflowResult:
    """Execute the full project work grading letter generation pipeline.

    This function orchestrates the complete workflow for creating a LaTeX
    grading letter for a project work (Praxisprojekt). It extracts metadata
    from the PDF, determines the appropriate formal address, and generates
    a letter template.

    Args:
        config: Configuration object for the project workflow.

    Returns:
        ProjectWorkflowResult object containing paths to generated files.

    Raises:
        FileNotFoundError: If the provided `pdf_path` does not exist.
        subprocess.CalledProcessError: If LaTeX compilation fails when `compile_pdf=True`.
        Exception: Any errors raised by the LLM API (e.g., authentication issues).
    """
    pdf_path = config.pdf_path
    output_folder = config.output_folder
    llm_client = config.llm_client
    compile_pdf = config.compile_pdf
    signature_file = config.signature_file
    grade = config.grade
    create_feedback_mail = config.create_feedback_mail

    if output_folder is None:
        output_folder = str(Path(pdf_path).parent)
    else:
        output_folder = str(output_folder)

    # Create LLMClient if not provided
    if llm_client is None:
        llm_client = LLMClient()
        print(f"Using LLM API: {llm_client.api_choice} with model: {llm_client.llm}")

    # Extract metadata and text from PDF
    print(f"Extracting metadata from {pdf_path}")
    pages_text = pdf.extract_text_per_page(str(pdf_path))
    metadata = extract_project_metadata(str(pdf_path), llm_client)

    student_name = metadata.get("student_name", "Unknown")
    student_first_name, student_last_name = split_student_name(student_name)
    matriculation = metadata.get("id_number", "unknown")
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
        id_number=matriculation,
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
        id_number=matriculation,
        filename_prefix="bewertung_projekt_email",
    )

    # Generate student feedback email
    student_email_path = ""
    if create_feedback_mail:
        print("\n📝 Generiere Feedback-Zusammenfassung...")
        feedback_bullets = generate_feedback_summary(str(pdf_path), llm_client)

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
            id_number=matriculation,
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

    # Generate web metadata
    print("\n🌐 Erstelle Web-Metadaten...")
    try:
        semester_name = get_semester()
        web_md_path = generate_metadata_file(
            output_folder=output_folder,
            title=project_title,
            author=student_name,
            pages_text=pages_text,
            llm_client=llm_client,
            work_type="Praxisprojekt",
            semester=semester_name,
        )
        print(f"✅ Web-Metadaten erstellt: {web_md_path}")
    except Exception as e:
        print(f"⚠️  Fehler beim Erstellen der Web-Metadaten: {e}")
        web_md_path = ""

    return ProjectWorkflowResult(
        tex_path=tex_path,
        pdf_path=compiled_pdf_path,
        service_email_path=email_path,
        student_email_path=student_email_path,
        metadata_path=web_md_path,
    )
