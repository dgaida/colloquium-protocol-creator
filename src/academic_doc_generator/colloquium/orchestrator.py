# colloquium_pipeline/orchestrator.py
"""High-level pipeline glue: parse PDF -> LLM -> tex -> pdf."""

from typing import Tuple, Optional
import os
from llm_client import LLMClient
from ..core import llm_interface, latex_generation
from . import pdf_form_filler
from . import email_generator
from .gemini_thesis_evaluator import GeminiThesisEvaluator
from .calendar_generator import CalendarGenerator
from .outlook_mail_generator import OutlookMailGenerator


def run_pipeline(
    pdf_path: str,
    date_colloquium: str,
    uhrzeit_colloquium: str,
    llm_client: LLMClient = None,
    groq_free: bool = False,
    output_folder: str = None,
    compile_pdf: bool = True,
    fill_form_only: bool = False,
    location_type: str = "campus",
    room: Optional[str] = None,
    company_name: Optional[str] = None,
    company_address: Optional[str] = None,
    zoom_link: Optional[str] = None,
    zoom_passcode: Optional[str] = None,
    gemini_evaluation_enabled: bool = False,
    gemini_model: Optional[str] = None,
) -> Tuple[str, str, str]:
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
        9. Generate calendar ICS file for the colloquium.
        10. Create Outlook mail draft for registration.

    Args:
        pdf_path: Path to the thesis PDF file.
        date_colloquium: Kolloquiumsdatum im Format "DD.MM.YYYY".
        uhrzeit_colloquium: Kolloquiumszeit im Format "HH:MM".
        llm_client: LLMClient instance for API access. If None, creates a new one
            with automatic API selection.
        groq_free: Whether to apply request throttling to comply with
            free-tier rate limits. Defaults to False.
        output_folder: Directory where the output `.tex` (and `.pdf` if compiled)
            will be written. If None, defaults to the folder containing `pdf_path`.
        compile_pdf: If True, the generated `.tex` file is compiled into a PDF
            using `lualatex`. Defaults to True.
        fill_form_only: Wenn True, wird nur das PDF-Formular ausgefüllt.
        location_type: Art des Kolloquiums ("campus", "company", "online").
        room: Raumnummer (nur für "campus").
        company_name: Name der Firma (nur für "company").
        company_address: Adresse der Firma (nur für "company").
        zoom_link: Zoom-Meeting-Link (nur für "online").
        zoom_passcode: Zoom-Zugangscode (nur für "online").
        gemini_evaluation_enabled: Wenn True, wird automatische Gemini-Bewertung durchgeführt.
        gemini_model: Gemini-Modell für Bewertung (z.B. "gemini-2.0-flash-exp").

    Returns:
        tuple[str, str, str]: A tuple `(tex_path, pdf_path_or_empty, email_path)` where:
            - `tex_path`: Path to the generated `.tex` file.
            - `pdf_path_or_empty`: Path to the generated `.pdf` if `compile_pdf=True`,
              otherwise an empty string.
            - `email_path`: Path to the generated email markdown file.

    Raises:
        FileNotFoundError: If the provided `pdf_path` does not exist.
        subprocess.CalledProcessError: If LaTeX compilation fails when `compile_pdf=True`.
        Exception: Any errors raised by the LLM API (e.g., authentication issues).

    Example:
        >>> from llm_client import LLMClient
        >>> client = LLMClient()  # Automatic API selection
        >>> tex_file, pdf_file = run_pipeline(
        ...     pdf_path="Bachelorarbeit_Mueller.pdf",
        ...     llm_client=client,
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

    # Create LLMClient if not provided
    if llm_client is None:
        llm_client = LLMClient()
        print(f"Using LLM API: {llm_client.api_choice} with model: {llm_client.llm}")

    if not fill_form_only:
        # 1) rewrite comments
        rewritten, stats = llm_interface.rewrite_comments_in_pdf(
            pdf_path, llm_client, groq_free=groq_free
        )

        # 2) detect language
        language = llm_interface.detect_language(rewritten, llm_client, groq_free)
    else:
        # TODO: das könnte man noch dynamisch bestimmen lassen, bspw. aus den ersten 1-2 Seiten des Dokuments
        #  erstmal manuell gesetzt, da Bestimmung aus rewritten text overkill ist
        language = "German"

    # 3) summary & metadata
    summary, metadata = llm_interface.get_summary_and_metadata_of_pdf(
        pdf_path, language, llm_client, groq_free
    )

    if not fill_form_only:
        # Example for stats: {"quelle": 3, "language": 7}
        if stats["quelle"] > 4:
            # wenn summary endet mit \end{itemize}, dann keinen Zeilenumbruch einfügen, führt zu Fehler "no line to end"
            if summary.strip()[-1] == "}":
                summary = summary + "Häufig fehlen Quellenangaben."
            else:
                summary = summary + "\\\\Häufig fehlen Quellenangaben."
            print("Häufig fehlen Quellenangaben")
        if stats["language"] > 5:
            # wenn summary endet mit \end{itemize}, dann keinen Zeilenumbruch einfügen, führt zu Fehler "no line to end"
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

    # 4) Optional: Gemini-Bewertung
    gemini_evaluation_text = None
    if gemini_evaluation_enabled:  # and not fill_form_only:
        try:
            # Erstelle separaten Gemini-Client
            gemini_client = LLMClient(
                api_choice="gemini",
                llm=gemini_model or "gemini-2.0-flash-exp",
                max_tokens=4096,
            )

            evaluator = GeminiThesisEvaluator(gemini_client)
            evaluation = evaluator.evaluate_thesis(
                pdf_path=pdf_path,
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
        tex_path = os.path.join(output_folder, tex_name)

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
            gemini_evaluation=gemini_evaluation_text,  # Neue Parameter
        )

        pdf_path = ""
        if compile_pdf:
            pdf_path = latex_generation.compile_latex_to_pdf(
                tex_path, output_dir=output_folder
            )
    else:
        tex_path = pdf_path = ""

    # 6) fill form
    # Beispieldaten basierend auf den tatsächlichen Feldnamen
    daten = {
        # Studierenden-Daten
        "name_student": author,
        "MatrNr": matriculation,
        # Bachelorarbeit - Erstprüfer
        "Datum_schrift_Erstpruefer": date_colloquium,
        "Schrift_Begruendung": True,  # Checkbox "Begründung liegt bei"
        # Bachelorarbeit - Zweitprüfer
        "Datum_schrift_Zweitpruefer": date_colloquium,
        "Schrift_Anschluss_Begruendung": True,  # "Anschluss an Begründung"
        # Kolloquium - Details
        "Datum der Prüfung": date_colloquium,
        "Startzeit": uhrzeit_colloquium,
        "Pruefungsfragen_Protokoll": True,  # Checkbox
        # Kolloquium - Erstprüfer
        "Datum_kolloq_Erstpruefer": date_colloquium,
        "Kolloq_Begruendung": True,
        # Kolloquium - Zweitprüfer
        "Datum_kolloq_Zweitpruefer": date_colloquium,
        "Kolloq_Anschluss_Begruendung": True,
    }

    # fülle PDF Formular aus
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
    mymailgen.generate_and_save_email(
        llm_client=llm_client,
        output_folder=output_folder,
        author=author,
        matriculation=matriculation,
        date_colloquium=date_colloquium,
        uhrzeit_colloquium=uhrzeit_colloquium,
        first_examiner=first_examiner,
        location_type=location_type,
        room=room,
        company_name=company_name,
        company_address=company_address,
        zoom_link=zoom_link,
        zoom_passcode=zoom_passcode,
    )
    email_path = mymailgen.email_path

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
            email_text=mymailgen.email_text,
            verbose=False,
        )
        if not outlook_success:
            print("ℹ️  Outlook-Mail konnte nicht automatisch erstellt werden")
            print(f"   Bitte öffne die Datei manuell: {email_path}")
    except Exception as e:
        print(f"⚠️  Fehler beim Erstellen der Outlook-Mail: {e}")
        print(f"   Bitte öffne die Datei manuell: {email_path}")

    return tex_path, pdf_path, email_path
