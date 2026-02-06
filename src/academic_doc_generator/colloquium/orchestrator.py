# src/academic_doc_generator/colloquium/orchestrator.py
"""High-level pipeline with comprehensive type annotations for colloquium protocol generation."""

from typing import Optional
from pathlib import Path
from datetime import datetime
from llm_client import LLMClient
from ..core import llm, latex, utils, pdf
from ..domain.metadata import generate_metadata_file
from . import pdf_form_filler
from . import email_generator
from .gemini_thesis_evaluator import GeminiThesisEvaluator
from .calendar_generator import CalendarGenerator
from .outlook_mail_generator import OutlookMailGenerator
from ..core.types import (
    ColloquiumWorkflowConfig,
    ColloquiumWorkflowResult,
)

# ============================================================================
# Public Functions
# ============================================================================


def run_pipeline(config: ColloquiumWorkflowConfig) -> ColloquiumWorkflowResult:
    """Execute the full colloquium protocol generation pipeline.

    This function orchestrates the complete workflow for creating a LaTeX
    template (and optionally a compiled PDF) that documents the protocol
    of a thesis colloquium. It processes the thesis PDF, extracts metadata,
    rewrites examiner comments, and generates a formal letter in LaTeX format.

    Args:
        config: Configuration object for the colloquium workflow.

    Returns:
        ColloquiumWorkflowResult object containing paths to generated files.

    Raises:
        FileNotFoundError: If the provided `pdf_path` does not exist.
        ValueError: If required location parameters are missing (e.g., room for campus).
        subprocess.CalledProcessError: If LaTeX compilation fails when `compile_pdf=True`.
        Exception: Any errors raised by the LLM API (e.g., authentication issues).
    """
    pdf_path = config.pdf_path
    output_folder = config.output_folder
    llm_client = config.llm_client
    fill_form_only = config.fill_form_only
    groq_free = config.groq_free

    if output_folder is None:
        output_folder = str(Path(pdf_path).parent)
    else:
        output_folder = str(output_folder)

    # Create LLMClient if not provided
    if llm_client is None:
        llm_client = LLMClient()
        print(f"Using LLM API: {llm_client.api_choice} with model: {llm_client.llm}")

    if not fill_form_only:
        # 1) rewrite comments
        rewritten, stats = llm.rewrite_comments_in_pdf(
            str(pdf_path), llm_client, groq_free=groq_free
        )

        # 2) detect language
        language = llm.detect_language(rewritten, llm_client, groq_free)
    else:
        # TODO: Could determine this dynamically from first pages
        # For now, manually set as determining from rewritten text is overkill
        language = "German"

    # 3) summary & metadata
    pages_text = pdf.extract_text_per_page(str(pdf_path))
    summary, metadata = llm.get_summary_and_metadata_of_pdf(
        str(pdf_path), language, llm_client, groq_free
    )

    if not fill_form_only:
        # Apply stats-based modifications to summary
        if stats["quelle"] > 4:
            if summary.strip()[-1] == "}":
                summary = summary + "Häufig fehlen Quellenangaben."
            else:
                summary = summary + "\\\\Häufig fehlen Quellenangaben."
            print("Häufig fehlen Quellenangaben")

        if stats["language"] > 5:
            if summary.strip()[-1] == "}":
                summary = summary + "Viele sprachliche Fehler."
            else:
                summary = summary + "\\\\Viele sprachliche Fehler."
            print("Viele sprachliche Fehler")

    print(metadata)

    author = metadata.get("author", "Unknown")
    matriculation = metadata.get("stud_id", "unknown")
    first_examiner = metadata.get("first_examiner", "Unbekannt")
    second_examiner = metadata.get("second_examiner", "Unbekannt")
    first_examiner_contact = f"{metadata.get('first_examiner_christian', '')}.{metadata.get('first_examiner_family', '')}@th-koeln.de"
    degree = metadata.get("bachelor_master", "Bachelor")
    thesis_title = metadata.get("title", "")

    # 4) Optional: Gemini evaluation
    gemini_evaluation_text: Optional[str] = None
    if config.gemini_evaluation_enabled:
        try:
            # Create separate Gemini client
            gemini_client = LLMClient(
                api_choice="gemini",
                llm=config.gemini_model or "gemini-2.0-flash-exp",
                max_tokens=4096,
            )

            evaluator = GeminiThesisEvaluator(gemini_client)
            evaluation = evaluator.evaluate_thesis(
                pdf_path=str(pdf_path),
                thesis_title=thesis_title,
                degree=degree,
                verbose=False,
            )

            if evaluation:
                gemini_evaluation_text = evaluator.format_evaluation_for_latex(
                    evaluation
                )
                print("   ✅ Gemini-Bewertung erfolgreich zur LaTeX-Datei hinzugefügt")
            else:
                print("   ⚠️  Gemini-Bewertung fehlgeschlagen, fahre ohne fort")

        except Exception as e:
            print(f"   ⚠️  Fehler bei Gemini-Bewertung: {e}")
            print("   → Fahre ohne automatische Bewertung fort")

    if not fill_form_only:
        # 5) concatenate comments and escape/format as needed
        questions = latex.concatenate_comments(rewritten, language)

        tex_name = f"bewertung_brief_{matriculation}.tex"
        tex_path = str(Path(output_folder) / tex_name)

        latex.create_formal_letter_tex(
            filename=tex_path,
            recipient="Prüfungsausschuss der TH Köln",
            subject=f"Bewertung {degree} von {author.title()}",
            title=thesis_title,
            author=f"{author.title()}, Matr.-Nr. {matriculation}",
            summary=summary,
            first_examiner=first_examiner.title(),
            second_examiner=second_examiner.title(),
            first_examiner_contact=first_examiner_contact,
            questions=questions,
            gemini_evaluation=gemini_evaluation_text,
        )

        pdf_path_str = ""
        if config.compile_pdf:
            pdf_path_str = latex.compile_latex_to_pdf(
                tex_path, output_dir=output_folder
            )
            if pdf_path_str:
                print(f"✅ PDF compiled: {pdf_path_str}")
    else:
        tex_path = ""
        pdf_path_str = ""

    # 6) Fill PDF form
    daten = {
        "name_student": author,
        "MatrNr": matriculation,
    }

    course_map = {
        "Informatik": "KontrollInformatik",
        "Wirtschaftsinformatik": "ControlWI",
        "Medieninformatik": "KontrollMedien",
        "IT-Management": "KontrollITM",
    }
    course_of_study = metadata.get("course_of_study")
    if course_of_study in course_map:
        daten[course_map[course_of_study]] = True

    daten.update(
        {
            "Datum_schrift_Erstpruefer": config.date,
            "Schrift_Begruendung": True,
            "Datum_schrift_Zweitpruefer": config.date,
            "Schrift_Anschluss_Begruendung": True,
            "Datum der Prüfung": config.date,
            "Startzeit": config.time,
            "Pruefungsfragen_Protokoll": True,
            "Datum_kolloq_Erstpruefer": config.date,
            "Kolloq_Begruendung": True,
            "Datum_kolloq_Zweitpruefer": config.date,
            "Kolloq_Anschluss_Begruendung": True,
        }
    )

    pdf_form_filler.fill_form(
        daten,
        output_folder,
        degree,
        location_type=config.location_type,
        room=config.room,
        company_name=config.company_name,
    )

    # 7) Generate email
    mymailgen = email_generator.EmailGenerator()
    student_first_name, student_last_name = utils.split_stud_name(author)

    registration_email_text = mymailgen.generate_colloquium_email(
        llm_client=llm_client,
        student_first_name=student_first_name,
        student_last_name=student_last_name,
        stud_id=matriculation,
        date_colloquium=config.date,
        time_colloquium=config.time,
        first_examiner=first_examiner,
        location_type=config.location_type,
        room=config.room,
        company_name=config.company_name,
        company_address=config.company_address,
        zoom_link=config.zoom_link,
        z_code=config.z_code,
    )
    email_path = mymailgen.save_email_to_markdown(
        output_folder=output_folder,
        student_last_name=student_last_name,
        stud_id=matriculation,
    )

    # Generate final valuation email template
    mymailgen.generate_final_valuation_email(
        evaluator_client=llm_client,
        first_name=student_first_name,
        last_name=student_last_name,
        stud_identifier=matriculation,
        examiner_name=first_examiner,
    )
    mymailgen.save_email_to_markdown(
        output_folder=output_folder,
        student_last_name=student_last_name,
        stud_id=matriculation,
        filename_prefix="bewertung_thesis_email",
    )

    # 8) Generate ICS calendar file
    print("\n📅 Erstelle Kalender-Datei...")
    calendar_gen = CalendarGenerator()
    try:
        ics_path = calendar_gen.generate_ics(
            output_folder=output_folder,
            stud_name=author,
            date_colloquium=config.date,
            time_colloquium=config.time,
            duration_minutes=45,
            location_type=config.location_type,
            room=config.room,
            company_name=config.company_name,
            company_address=config.company_address,
        )
    except Exception as e:
        print(f"⚠️  Fehler beim Erstellen der Kalender-Datei: {e}")
        ics_path = None

    # 9) Create Outlook mail draft
    print("\n📧 Erstelle Outlook-Mail...")
    outlook_gen = OutlookMailGenerator()
    try:
        outlook_success = outlook_gen.create_outlook_mail(
            stud_name=author,
            email_text=registration_email_text,
            attachment_path=ics_path,
            verbose=False,
        )
        if not outlook_success:
            print("ℹ️  Outlook-Mail konnte nicht automatisch erstellt werden")
            print(f"   Bitte öffne die Datei manuell: {email_path}")

        if ics_path and outlook_success:
            import platform

            if platform.system() == "Windows":
                print("\n📅 Öffne Kalender-Eintrag in Outlook...")
                outlook_gen.open_ics_in_outlook(ics_path, verbose=False)
    except Exception as e:
        print(f"⚠️  Fehler beim Erstellen der Outlook-Mail: {e}")
        print(f"   Bitte öffne die Datei manuell: {email_path}")

    # 10) Generate web metadata
    print("\n🌐 Erstelle Web-Metadaten...")
    try:
        dt_colloquium = datetime.strptime(config.date, "%d.%m.%Y")
        semester_name = utils.get_semester(dt_colloquium)
        web_md_path = generate_metadata_file(
            output_folder=output_folder,
            title=thesis_title,
            author=author,
            pages_text=pages_text,
            llm_client=llm_client,
            work_type=f"{degree}thesis",
            semester=semester_name,
            date_str=dt_colloquium.strftime("%Y-%m-%d"),
        )
        print(f"✅ Web-Metadaten erstellt: {web_md_path}")
    except Exception as e:
        print(f"⚠️  Fehler beim Erstellen der Web-Metadaten: {e}")
        web_md_path = ""

    return ColloquiumWorkflowResult(
        tex_path=tex_path,
        pdf_path=pdf_path_str,
        email_path=email_path,
        metadata_path=web_md_path,
    )
