# src/academic_doc_generator/project/orchestrator.py
"""High-level pipeline for project work grading letter generation."""

import os
from pathlib import Path

from llm_client import LLMClient

from ..colloquium.email_generator import EmailGenerator
from ..colloquium.outlook_mail_generator import OutlookMailGenerator
from ..core import pdf
from ..core.email import EmailRecipient
from ..core.latex import compile_latex_to_pdf
from ..core.llm import determine_gender_from_name
from ..core.metadata import generate_metadata_file
from ..core.types import (
    ProjectWorkflowConfig,
    ProjectWorkflowResult,
)
from ..core.utils import get_semester, load_global_config, split_student_name
from .feedback_generator import generate_feedback_summary
from .latex import create_project_grading_letter_tex
from .llm import (
    extract_project_metadata,
)


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
    output_folder_path = config.output_folder
    llm_client = config.llm_client
    compile_pdf = config.compile_pdf
    signature_file = config.signature_file
    mark_result = config.mark
    create_feedback_mail = config.create_feedback_mail

    if output_folder_path is None:
        output_folder = str(Path(pdf_path).parent)
    else:
        output_folder = str(output_folder_path)

    # Create LLMClient if not provided
    if llm_client is None:
        llm_client = LLMClient()
        print(f"Using LLM API: {llm_client.api_choice} with model: {llm_client.llm}")

    # Load global config
    global_config = load_global_config()
    global_first_examiner = global_config.get("first_examiner")

    # Extract metadata and text from PDF
    print(f"Extracting metadata from {pdf_path}")
    pages_text = pdf.extract_text_per_page(str(pdf_path))
    metadata = extract_project_metadata(str(pdf_path), llm_client)

    students = metadata.get("students", [])
    if not students:
        students = [
            {
                "name": metadata.get("student_name", "Unknown"),
                "first_name": metadata.get("student_first_name"),
                "id_number": metadata.get("id_number", "unknown"),
                "email": metadata.get("student_email"),
            }
        ]

    # Process all students: split names and detect genders
    for s in students:
        if not s.get("first_name") or not s.get("last_name"):
            first, last = split_student_name(s.get("name", "Unknown"))
            s["first_name"] = s.get("first_name") or first
            s["last_name"] = s.get("last_name") or last

        print(f"Determining gender for student: {s.get('name')}")
        s["gender"] = determine_gender_from_name(s["first_name"], llm_client)
        print(f"Detected gender: {s['gender']}")

    # For legacy variables and filenames, use the first student
    first_student = students[0]
    student_name = first_student.get("name", "Unknown")
    student_first_name = first_student.get("first_name", "Unknown")
    student_last_name = first_student.get("last_name", "Name")
    id_number = first_student.get("id_number", "unknown")
    gender = first_student.get("gender", "Herr/Frau")

    # Check if first name was recognized
    # We consider it recognized if the LLM explicitly found it AND the whole name is not "Unknown"
    first_name_recognized = (
        first_student.get("first_name") is not None and student_name != "Unknown"
    )

    project_title = metadata.get("title", "Unknown")

    # Use global examiner if provided, otherwise from metadata
    examiner_name = global_first_examiner or metadata.get("first_examiner") or "Unbekannt"

    # Robust email generation
    ex_christian = metadata.get("first_examiner_christian") or ""
    ex_family = metadata.get("first_examiner_family") or ""
    examiner_email = f"{ex_christian}.{ex_family}@th-koeln.de"
    # Prioritize work_type from config, then from metadata, then default
    work_type = config.work_type or metadata.get("work_type", "Praxisprojekt")

    # Check for signature in data/
    data_signature = os.path.join("data", "signature.png")
    if os.path.exists(data_signature):
        signature_file = data_signature
        print(f"Using signature found in {data_signature}")

    # Create output filename
    # For groups, we could join IDs, but using the first one is simpler for filenames
    tex_name = f"bewertung_projekt_{id_number}.tex"
    tex_path = os.path.join(output_folder, tex_name)

    # Generate LaTeX letter
    create_project_grading_letter_tex(
        filename=tex_path,
        author=f"{student_name}, Matrikelnr. {id_number}",
        title=project_title,
        examiner=examiner_name,
        contact=examiner_email,
        gender=gender,
        work_type=work_type,
        signature_file=signature_file,
        grade_mark=mark_result,
        students=students,
    )

    # Compile to PDF if requested
    compiled_pdf_path = ""
    if compile_pdf:
        compiled_pdf_path = compile_latex_to_pdf(tex_path, output_dir=output_folder)
        if compiled_pdf_path:
            print(f"✅ PDF compiled: {compiled_pdf_path}")

    # Generate email for Prüfungsservice
    mymailgen = EmailGenerator()
    grading_email_text = ""
    email_path = ""

    # Convert student list to EmailRecipient objects for joint emails
    recipients = [
        EmailRecipient(
            first_name=s.get("first_name", ""),
            last_name=s.get("last_name", ""),
            gender=s.get("gender", "Herr/Frau"),
            identifier=s.get("id_number", ""),
        )
        for s in students
    ]

    if first_name_recognized:
        grading_email_text = mymailgen.generate_final_mark_email(
            evaluator_client=llm_client,
            first_name=student_first_name,
            last_name=student_last_name,
            id_number=id_number,
            examiner_name=examiner_name,
            students=recipients,
        )
        email_path = mymailgen.save_email_to_markdown(
            output_folder=output_folder,
            student_last_name=student_last_name,
            id_number=id_number,
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
            mark=mark_result if mark_result else "[NOTE]",
            feedback_bulletpoints=feedback_bullets,
            examiner_name=examiner_name,
            students=recipients,
        )
        student_email_path = mymailgen.save_email_to_markdown(
            output_folder=output_folder,
            student_last_name=student_last_name,
            id_number=id_number,
            filename_prefix="feedback_projekt_email",
        )

    # Create Outlook mail drafts if mark_result is provided
    if mark_result is not None:
        outlook_gen = OutlookMailGenerator()

        # 1. Draft for Prüfungsservice
        if first_name_recognized:
            print("\n📧 Erstelle Outlook-Mail für Prüfungsservice...")
            try:
                outlook_gen.create_outlook_mail(
                    student_name=student_name,
                    email_text=grading_email_text,
                    attachment_path=compiled_pdf_path if compiled_pdf_path else None,
                    subject=f"Bewertung {work_type} {gender} {student_first_name} {student_last_name}",
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
                        subject=f"Feedback zu Ihrem {work_type} - {student_name}",
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
            work_type=work_type,
            semester=semester_name,
            copy_to_web_folder=first_name_recognized,
            students=students,
        )
        print(f"✅ Web-Metadaten erstellt: {web_md_path}")
    except Exception as e:
        print(f"⚠️  Fehler beim Erstellen der Web-Metadaten: {e}")
        web_md_path = ""

    if not first_name_recognized:
        print(
            "\n⚠️  Warnung: Vorname wurde nicht erkannt. "
            "Die Email zur Einreichung der Note wurde nicht erstellt und "
            "die Web-Metadaten wurden nicht in den globalen Ordner kopiert."
        )

    return ProjectWorkflowResult(
        tex_path=tex_path,
        pdf_path=compiled_pdf_path,
        service_email_path=email_path,
        student_email_path=student_email_path,
        metadata_path=web_md_path,
    )
