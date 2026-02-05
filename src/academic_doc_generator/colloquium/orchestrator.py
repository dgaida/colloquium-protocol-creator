# src/academic_doc_generator/colloquium/orchestrator.py
"""High-level pipeline with comprehensive type annotations for colloquium protocol generation."""

from typing import Tuple, Optional
from pathlib import Path
from datetime import datetime
from llm_client import LLMClient
from ..core import llm_interface, latex_generation, utils, pdf_processing
from ..core.web_metadata import generate_web_metadata_file
from . import pdf_form_filler
from . import email_generator
from .gemini_thesis_evaluator import GeminiThesisEvaluator
from .calendar_generator import CalendarGenerator
from .outlook_mail_generator import OutlookMailGenerator
from ..core.types import LocationType, LLMClientProtocol

# ============================================================================
# Public Functions
# ============================================================================


def run_pipeline(
    pdf_path: str | Path,
    date_colloquium: str,  # Format: DD.MM.YYYY
    uhrzeit_colloquium: str,  # Format: HH:MM
    llm_client: Optional[LLMClientProtocol] = None,
    groq_free: bool = False,
    output_folder: Optional[str | Path] = None,
    compile_pdf: bool = True,
    fill_form_only: bool = False,
    location_type: LocationType = "campus",
    room: Optional[str] = None,
    company_name: Optional[str] = None,
    company_address: Optional[str] = None,
    zoom_link: Optional[str] = None,
    zoom_meeting_access: Optional[str] = None,
    gemini_evaluation_enabled: bool = False,
    gemini_model: Optional[str] = None,
) -> Tuple[str, str, str, str]:
    """Execute the full colloquium protocol generation pipeline.

    This function orchestrates the complete workflow for creating a LaTeX
    template (and optionally a compiled PDF) that documents the protocol
    of a thesis colloquium. It processes the thesis PDF, extracts metadata,
    rewrites examiner comments, and generates a formal letter in LaTeX format.

    The pipeline performs the following steps:
        1. Parse the thesis PDF for annotations and extract comments.
        2. Rewrite rough comments into clear, polite questions using an LLM.
        3. Detect the language (German/English) of the comments.
        4. Summarize the thesis and extract metadata such as author, matriculation number,
           title, and examiner names.
        5. Optionally: Send thesis to Google Gemini for automatic evaluation.
        6. Concatenate and LaTeX-format the rewritten comments.
        7. Create a formal letter as a `.tex` file using the collected data.
        8. Optionally compile the `.tex` file into a PDF.
        9. Fill the official grading form PDF with metadata.
        10. Generate colloquium registration email.

    Args:
        pdf_path: Path to the thesis PDF file.
        date_colloquium: Colloquium date in format "DD.MM.YYYY".
        uhrzeit_colloquium: Colloquium time in format "HH:MM".
        llm_client: LLM client instance implementing LLMClientProtocol. If None,
            creates a new one with automatic API selection. Defaults to None.
        groq_free: Whether to apply request throttling to comply with
            free-tier rate limits. Adds delays between API calls. Defaults to False.
        output_folder: Directory where outputs will be written. If None, defaults
            to the folder containing `pdf_path`. Defaults to None.
        compile_pdf: If True, compile the generated `.tex` file into a PDF
            using `lualatex`. Defaults to True.
        fill_form_only: If True, only fill the PDF form without generating the
            protocol letter. Useful for quick form generation. Defaults to False.
        location_type: Type of colloquium venue. Must be one of:
            - "campus": On-campus colloquium (requires `room`)
            - "company": At company location (requires `company_name`)
            - "online": Virtual colloquium (requires `zoom_link`)
            Defaults to "campus".
        room: Room number for campus colloquium (e.g., "3.217").
            Required if location_type="campus". Defaults to None.
        company_name: Company name for company colloquium (e.g., "Beispiel GmbH").
            Required if location_type="company". Defaults to None.
        company_address: Full company address (optional for company colloquium).
            Defaults to None.
        zoom_link: Zoom meeting URL for online colloquium.
            Required if location_type="online". Defaults to None.
        zoom_meeting_access: Zoom meeting meeting_access (optional for online colloquium).
            Defaults to None.
        gemini_evaluation_enabled: If True, automatically evaluate the thesis
            using Google Gemini and include the evaluation in the protocol.
            Defaults to False.
        gemini_model: Specific Gemini model to use for evaluation
            (e.g., "gemini-2.0-flash-exp"). Defaults to None (uses default model).

    Returns:
        Tuple of (tex_path, pdf_path, email_path, web_metadata_path):
        - tex_path: Path to the generated `.tex` file
        - pdf_path: Path to the generated `.pdf` if `compile_pdf=True`,
          otherwise empty string
        - email_path: Path to the generated email markdown file
        - web_metadata_path: Path to the generated Jekyll-style .md file

    Raises:
        FileNotFoundError: If the provided `pdf_path` does not exist.
        ValueError: If required location parameters are missing (e.g., room for campus).
        subprocess.CalledProcessError: If LaTeX compilation fails when `compile_pdf=True`.
        Exception: Any errors raised by the LLM API (e.g., authentication issues).

    Example:
        >>> from llm_client import LLMClient
        >>> client = LLMClient()  # Automatic API selection
        >>> tex_file, pdf_file, email_file = run_pipeline(
        ...     pdf_path="Bachelorarbeit_Mueller.pdf",
        ...     date_colloquium="15.01.2026",
        ...     uhrzeit_colloquium="10:00",
        ...     llm_client=client,
        ...     groq_free=True,
        ...     output_folder="./out",
        ...     compile_pdf=True,
        ...     location_type="campus",
        ...     room="3.217"
        ... )
        >>> print(tex_file)
        ./out/bewertung_brief_123456.tex
        >>> print(pdf_file)
        ./out/bewertung_brief_123456.pdf
        >>> print(email_file)
        ./out/kolloquium_anmeldung_Mueller_123456.md

    Notes:
        - The generated `.tex` file is always created, regardless of `compile_pdf`.
        - If the matriculation number cannot be detected, the output file name
          defaults to `bewertung_brief_unknown.tex`.
        - The pipeline **does not grade a thesis**; it only generates a template
          for documenting the colloquium protocol.
        - Gemini evaluation requires a valid Google Gemini API key.
    """
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
        rewritten, stats = llm_interface.rewrite_comments_in_pdf(
            str(pdf_path), llm_client, groq_free=groq_free
        )

        # 2) detect language
        language = llm_interface.detect_language(rewritten, llm_client, groq_free)
    else:
        # TODO: Could determine this dynamically from first pages
        # For now, manually set as determining from rewritten text is overkill
        language = "German"

    # 3) summary & metadata
    pages_text = pdf_processing.extract_text_per_page(str(pdf_path))
    summary, metadata = llm_interface.get_summary_and_metadata_of_pdf(
        str(pdf_path), language, llm_client, groq_free
    )

    if not fill_form_only:
        # Apply stats-based modifications to summary
        # If many source comments, add note about missing citations
        if stats["quelle"] > 4:
            # Check if summary ends with \end{itemize}, don't add line break (causes error)
            if summary.strip()[-1] == "}":
                summary = summary + "Häufig fehlen Quellenangaben."
            else:
                summary = summary + "\\\\Häufig fehlen Quellenangaben."
            print("Häufig fehlen Quellenangaben")

        # If many language comments, add note about language errors
        if stats["language"] > 5:
            # Check if summary ends with \end{itemize}, don't add line break (causes error)
            if summary.strip()[-1] == "}":
                summary = summary + "Viele sprachliche Fehler."
            else:
                summary = summary + "\\\\Viele sprachliche Fehler."
            print("Viele sprachliche Fehler")

    print(metadata)

    author = metadata.get("author", "Unknown")
    matriculation = metadata.get("matriculation_number", "unknown")
    first_examiner = metadata.get("first_examiner", "Unbekannt")
    second_examiner = metadata.get("second_examiner", "Unbekannt")
    first_examiner_mail = f"{metadata.get('first_examiner_christian', '')}.{metadata.get('first_examiner_family', '')}@th-koeln.de"
    degree = metadata.get("bachelor_master", "Bachelor")
    thesis_title = metadata.get("title", "")

    # 4) Optional: Gemini evaluation
    gemini_evaluation_text: Optional[str] = None
    if gemini_evaluation_enabled:
        try:
            # Create separate Gemini client
            gemini_client = LLMClient(
                api_choice="gemini",
                llm=gemini_model or "gemini-2.0-flash-exp",
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
        questions = latex_generation.concatenate_comments(rewritten, language)

        tex_name = f"bewertung_brief_{matriculation}.tex"
        tex_path = str(Path(output_folder) / tex_name)

        latex_generation.create_formal_letter_tex(
            filename=tex_path,
            recipient="Prüfungsausschuss der TH Köln",
            subject=f"Bewertung {degree} von {author.title()}",
            title=thesis_title,
            author=f"{author.title()}, Matr.-Nr. {matriculation}",
            summary=summary,
            # .title() sorgt dafür, dass nur erste Buchstabe groß ist und Rest klein. falls Nachname in thesis komplett groß geschrieben sein sollte
            first_examiner=first_examiner.title(),
            second_examiner=second_examiner.title(),
            first_examiner_mail=first_examiner_mail,
            questions=questions,
            gemini_evaluation=gemini_evaluation_text,
        )

        pdf_path_str = ""
        if compile_pdf:
            pdf_path_str = latex_generation.compile_latex_to_pdf(
                tex_path, output_dir=output_folder
            )
            if pdf_path_str:
                print(f"✅ PDF compiled: {pdf_path_str}")
    else:
        tex_path = ""
        pdf_path_str = ""

    # 6) Fill PDF form
    daten = {
        # Student data
        "name_student": author,
        "MatrNr": matriculation,
    }

    # Map course of study to checkboxes
    course_map = {
        "Informatik": "KontrollInformatik",
        "Wirtschaftsinformatik": "ControlWI",
        "Medieninformatik": "KontrollMedien",
        "IT-Management": "KontrollITM",
    }
    course_of_study = metadata.get("course_of_study")
    if course_of_study in course_map:
        daten[course_map[course_of_study]] = True

    # Add other fields to daten
    daten.update(
        {
            # Thesis - First examiner
            "Datum_schrift_Erstpruefer": date_colloquium,
            "Schrift_Begruendung": True,  # Checkbox "Begründung liegt bei"
            # Thesis - Second examiner
            "Datum_schrift_Zweitpruefer": date_colloquium,
            "Schrift_Anschluss_Begruendung": True,  # "Anschluss an Begründung"
            # Colloquium - Details
            "Datum der Prüfung": date_colloquium,
            "Startzeit": uhrzeit_colloquium,
            "Pruefungsfragen_Protokoll": True,  # Checkbox
            # Colloquium - First examiner
            "Datum_kolloq_Erstpruefer": date_colloquium,
            "Kolloq_Begruendung": True,
            # Colloquium - Second examiner
            "Datum_kolloq_Zweitpruefer": date_colloquium,
            "Kolloq_Anschluss_Begruendung": True,
        }
    )

    pdf_form_filler.fill_form(
        daten,
        output_folder,
        degree,
        location_type=location_type,
        room=room,
        company_name=company_name,
    )

    # 7) Generate email
    mymailgen = email_generator.EmailGenerator()
    student_first_name, student_last_name = utils.split_student_name(author)

    registration_email_text = mymailgen.generate_colloquium_email(
        llm_client=llm_client,
        student_first_name=student_first_name,
        student_last_name=student_last_name,
        matriculation_number=matriculation,
        date_colloquium=date_colloquium,
        time_colloquium=uhrzeit_colloquium,
        first_examiner=first_examiner,
        location_type=location_type,
        room=room,
        company_name=company_name,
        company_address=company_address,
        zoom_link=zoom_link,
        zoom_meeting_access=zoom_meeting_access,
    )
    email_path = mymailgen.save_email_to_markdown(
        output_folder=output_folder,
        student_last_name=student_last_name,
        matriculation_number=matriculation,
    )

    # Generate final grade email template
    mymailgen.generate_final_grade_email(
        evaluator_client=llm_client,
        first_name=student_first_name,
        last_name=student_last_name,
        student_identifier=matriculation,
        examiner_name=first_examiner,
    )
    mymailgen.save_email_to_markdown(
        output_folder=output_folder,
        student_last_name=student_last_name,
        matriculation_number=matriculation,
        filename_prefix="bewertung_thesis_email",
    )

    # 8) Generate ICS calendar file
    print("\n📅 Erstelle Kalender-Datei...")
    calendar_gen = CalendarGenerator()
    try:
        ics_path = calendar_gen.generate_ics(
            output_folder=output_folder,
            student_name=author,
            date_colloquium=date_colloquium,
            time_colloquium=uhrzeit_colloquium,
            duration_minutes=45,
            location_type=location_type,
            room=room,
            company_name=company_name,
            company_address=company_address,
        )
    except Exception as e:
        print(f"⚠️  Fehler beim Erstellen der Kalender-Datei: {e}")
        ics_path = None

    # 9) Create Outlook mail draft
    print("\n📧 Erstelle Outlook-Mail...")
    outlook_gen = OutlookMailGenerator()
    try:
        outlook_success = outlook_gen.create_outlook_mail(
            student_name=author,
            email_text=registration_email_text,
            attachment_path=ics_path,  # ICS-Datei als Anhang
            verbose=False,
        )
        if not outlook_success:
            print("ℹ️  Outlook-Mail konnte nicht automatisch erstellt werden")
            print(f"   Bitte öffne die Datei manuell: {email_path}")

        # Öffne ICS-Datei direkt in Outlook (nur Windows)
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
        dt_colloquium = datetime.strptime(date_colloquium, "%d.%m.%Y")
        semester_name = utils.get_semester(dt_colloquium)
        web_md_path = generate_web_metadata_file(
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

    return tex_path, pdf_path_str, email_path, web_md_path
