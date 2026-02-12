# src/academic_doc_generator/colloquium/orchestrator.py
"""High-level pipeline with comprehensive type annotations for colloquium protocol generation."""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from llm_client import LLMClient

from ..core import latex, llm, pdf, utils
from ..core.metadata import generate_metadata_file
from ..core.types import (
    ColloquiumWorkflowConfig,
    ColloquiumWorkflowResult,
)
from . import email_generator, pdf_form_filler
from .calendar_generator import CalendarGenerator
from .gemini_thesis_evaluator import GeminiThesisEvaluator
from .outlook_mail_generator import OutlookMailGenerator

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
    # 1. Initialize
    llm_client, output_folder = _initialize_pipeline(config)

    # 2. Extract & Process
    rewritten, stats, metadata, summary, language, pages_text = _extract_and_process_thesis(
        config, llm_client
    )

    # 3. Optional: Gemini emark
    gemini_emark_text = _get_gemini_emark(config, metadata)

    # 4. Generate LaTeX Output
    tex_path, pdf_path_str = _generate_latex_outputs(
        config, rewritten, metadata, summary, language, output_folder, gemini_emark_text
    )

    # 5. Fill PDF form
    _fill_grading_form(config, metadata, output_folder)

    # 6. Generate Emails and Calendar
    registration_email_text, email_path, ics_path = _generate_emails_and_calendar(
        config, metadata, llm_client, output_folder
    )

    # 7. Create Outlook mail draft
    _create_outlook_draft(metadata, registration_email_text, ics_path, email_path)

    # 8. Generate web metadata
    web_md_path = _generate_web_metadata(config, metadata, pages_text, llm_client, output_folder)

    return ColloquiumWorkflowResult(
        tex_path=tex_path,
        pdf_path=pdf_path_str,
        email_path=email_path,
        metadata_path=web_md_path,
    )


def _initialize_pipeline(config: ColloquiumWorkflowConfig) -> tuple[LLMClient, str]:
    """Initialize pipeline with validated configuration."""
    output_folder = (
        str(config.output_folder) if config.output_folder else str(config.pdf_path.parent)
    )

    llm_client = config.llm_client
    if llm_client is None:
        llm_client = LLMClient()
        print(f"Using LLM API: {llm_client.api_choice} with model: {llm_client.llm}")

    return llm_client, output_folder


def _extract_and_process_thesis(config: ColloquiumWorkflowConfig, llm_client: LLMClient):
    """Extract information from thesis PDF and process it with LLM."""
    pdf_path_str = str(config.pdf_path)

    if not config.fill_form_only:
        # rewrite comments
        rewritten, stats = llm.rewrite_comments_in_pdf(
            pdf_path_str, llm_client, groq_free=config.groq_free
        )
        # detect language
        language = llm.detect_language(rewritten, llm_client, config.groq_free)
    else:
        rewritten, stats = {}, {"quelle": 0, "language": 0, "ignore": 0}
        language = "German"

    # summary & metadata
    pages_text = pdf.extract_text_per_page(pdf_path_str)
    summary, metadata = llm.get_summary_and_metadata_of_pdf(
        pdf_path_str, language, llm_client, config.groq_free
    )

    if not config.fill_form_only:
        # Apply stats-based modifications to summary
        if stats["quelle"] > 4:
            summary += (
                "Häufig fehlen Quellenangaben."
                if summary.strip()[-1] == "}"
                else "\\\\Häufig fehlen Quellenangaben."
            )
            print("Häufig fehlen Quellenangaben")

        if stats["language"] > 5:
            summary += (
                "Viele sprachliche Fehler."
                if summary.strip()[-1] == "}"
                else "\\\\Viele sprachliche Fehler."
            )
            print("Viele sprachliche Fehler")

    print(metadata)
    return rewritten, stats, metadata, summary, language, pages_text


def _get_gemini_emark(config: ColloquiumWorkflowConfig, metadata: dict) -> Optional[str]:
    """Generate an automatic grade evaluation using Gemini if enabled."""
    if not config.gemini_emark_enabled:
        return None

    try:
        gemini_client = LLMClient(
            api_choice="gemini",
            llm=config.gemini_model or "gemini-2.0-flash-exp",
            max_tokens=4096,
        )
        evaluator = GeminiThesisEvaluator(gemini_client)
        emark = evaluator.evaluate_thesis(
            pdf_path=str(config.pdf_path),
            thesis_title=metadata.get("title", ""),
            degree=metadata.get("bachelor_master", "Bachelor"),
            use_text_extraction=config.gemini_use_text_extraction,
            verbose=False,
        )

        if emark:
            print("   ✅ Gemini-Bewertung erfolgreich zur LaTeX-Datei hinzugefügt")
            return evaluator.format_emark_for_latex(emark)

        print("   ⚠️  Gemini-Bewertung fehlgeschlagen, fahre ohne fort")
    except Exception as e:
        print(f"   ⚠️  Fehler bei Gemini-Bewertung: {e}")
        print("   → Fahre ohne automatische Bewertung fort")

    return None


def _generate_latex_outputs(
    config: ColloquiumWorkflowConfig,
    rewritten: dict,
    metadata: dict,
    summary: str,
    language: str,
    output_folder: str,
    gemini_emark_text: Optional[str],
) -> tuple[str, str]:
    """Generate LaTeX source and compile to PDF."""
    if config.fill_form_only:
        return "", ""

    questions = latex.concatenate_comments(rewritten, language)  # type: ignore[arg-type]
    author = metadata.get("author", "Unknown")
    matriculation = metadata.get("id_number", "unknown")
    degree = metadata.get("bachelor_master", "Bachelor")

    tex_name = f"bewertung_brief_{matriculation}.tex"
    tex_path = str(Path(output_folder) / tex_name)

    # Load global config
    global_config = utils.load_global_config()
    global_first_examiner = global_config.get("first_examiner")

    # Use global examiner if provided, otherwise from metadata
    first_ex = global_first_examiner or metadata.get("first_examiner") or "Unbekannt"
    second_ex = metadata.get("second_examiner") or "Unbekannt"

    latex.create_formal_letter_tex(
        filename=tex_path,
        recipient="Prüfungsausschuss der TH Köln",
        subject=f"Bewertung {degree} von {author.title()}",
        title=metadata.get("title", ""),
        author=f"{author.title()}, Matr.-Nr. {matriculation}",
        summary=summary,
        first_examiner=first_ex.title(),
        second_examiner=second_ex.title(),
        examiner_email=f"{metadata.get('first_examiner_christian', '')}.{metadata.get('first_examiner_family', '')}@th-koeln.de",
        questions=questions,
        gemini_emark=gemini_emark_text,
    )

    pdf_path_str = ""
    if config.compile_pdf:
        pdf_path_str = latex.compile_latex_to_pdf(tex_path, output_dir=output_folder)
        if pdf_path_str:
            print(f"✅ PDF compiled: {pdf_path_str}")

    return tex_path, pdf_path_str


def _fill_grading_form(config: ColloquiumWorkflowConfig, metadata: dict, output_folder: str):
    """Fill the official grading form PDF."""
    daten: dict[str, Any] = {
        "name_student": metadata.get("author", "Unknown"),
        "MatrNr": metadata.get("id_number", "unknown"),
    }

    course_map = {
        "Informatik": "KontrollInformatik",
        "Wirtschaftsinformatik": "KontrollWI",
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
        metadata.get("bachelor_master", "Bachelor"),
        location_type=config.location_type,
        room=config.room,
        company_name=config.company_name,
    )


def _generate_emails_and_calendar(
    config: ColloquiumWorkflowConfig, metadata: dict, llm_client: LLMClient, output_folder: str
) -> tuple[str, str, Optional[str]]:
    """Generate registration/feedback emails and calendar entry."""
    mymailgen = email_generator.EmailGenerator()
    author = metadata.get("author", "Unknown")
    id_number = metadata.get("id_number", "unknown")
    student_first_name, student_last_name = utils.split_student_name(author)

    # Load global config
    global_config = utils.load_global_config()
    global_first_examiner = global_config.get("first_examiner")
    first_ex = global_first_examiner or metadata.get("first_examiner") or "Unbekannt"

    registration_email_text = mymailgen.generate_colloquium_email(
        llm_client=llm_client,
        student_first_name=student_first_name,
        student_last_name=student_last_name,
        id_number=id_number,
        date_colloquium=config.date,
        time_colloquium=config.time,
        first_examiner=first_ex,
        location_type=config.location_type,
        room=config.room,
        company_name=config.company_name,
        company_address=config.company_address,
        zoom_link=config.zoom_link,
        zcode=config.zcode,
    )
    email_path = mymailgen.save_email_to_markdown(
        output_folder=output_folder,
        student_last_name=student_last_name,
        id_number=id_number,
    )

    # Generate final mark email template
    mymailgen.generate_final_mark_email(
        evaluator_client=llm_client,
        first_name=student_first_name,
        last_name=student_last_name,
        id_number=id_number,
        examiner_name=first_ex,
    )
    mymailgen.save_email_to_markdown(
        output_folder=output_folder,
        student_last_name=student_last_name,
        id_number=id_number,
        filename_prefix="bewertung_thesis_email",
    )

    # Calendar
    print("\n📅 Erstelle Kalender-Datei...")
    calendar_gen = CalendarGenerator()
    try:
        ics_path = calendar_gen.generate_ics(
            output_folder=output_folder,
            student_name=author,
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

    return registration_email_text, email_path, ics_path


def _create_outlook_draft(
    metadata: dict, registration_email_text: str, ics_path: Optional[str], email_path: str
):
    """Create a draft email in Outlook if possible."""
    print("\n📧 Erstelle Outlook-Mail...")
    author = metadata.get("author", "Unknown")
    outlook_gen = OutlookMailGenerator()
    try:
        outlook_success = outlook_gen.create_outlook_mail(
            student_name=author,
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


def _generate_web_metadata(
    config: ColloquiumWorkflowConfig,
    metadata: dict,
    pages_text: dict,
    llm_client: LLMClient,
    output_folder: str,
) -> str:
    """Generate Jekyll-compatible metadata for the website."""
    print("\n🌐 Erstelle Web-Metadaten...")
    try:
        dt_colloquium = datetime.strptime(config.date, "%d.%m.%Y")
        semester_name = utils.get_semester(dt_colloquium)
        web_md_path = generate_metadata_file(
            output_folder=output_folder,
            title=metadata.get("title", ""),
            author=metadata.get("author", "Unknown"),
            pages_text=pages_text,
            llm_client=llm_client,
            work_type=f"{metadata.get('bachelor_master', 'Bachelor')}thesis",
            semester=semester_name,
            date_str=dt_colloquium.strftime("%Y-%m-%d"),
        )
        print(f"✅ Web-Metadaten erstellt: {web_md_path}")
        return web_md_path
    except Exception as e:
        print(f"⚠️  Fehler beim Erstellen der Web-Metadaten: {e}")
        return ""
