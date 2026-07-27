"""CLI command handlers for different tasks."""

import argparse
import sys
from pathlib import Path

from llm_client import LLMClient

from ..colloquium.orchestrator import run_pipeline
from ..config_loader import ConfigLoader, load_config
from ..core.types import ColloquiumWorkflowConfig, ProjectWorkflowConfig
from ..core.validation import validate_pdf_path
from ..exam_translator.translator import translate_latex_exam
from ..exam_translator.xml_translator import translate_xml_exam
from ..project.orchestrator import run_project_pipeline
from ..review.orchestrator import run_review_pipeline


def run_from_config(config_path: str | Path) -> ConfigLoader:
    """Execute a task based on a configuration file."""
    try:
        config: ConfigLoader = load_config(str(config_path))
        print(f"✓ Konfiguration geladen: {config}")
    except (FileNotFoundError, ValueError, Exception) as e:
        print(f"❌ Fehler beim Laden der Konfiguration: {e}")
        sys.exit(1)

    # Create LLM client
    llm_config = config.get_llm_config()
    try:
        llm_client = LLMClient(api_choice=llm_config.get("api_choice"), llm=llm_config.get("model"))
        print(f"✓ LLM: {llm_client.api_choice} / {llm_client.llm}")
    except Exception as e:
        print(f"❌ Fehler beim Initialisieren des LLM-Clients: {e}")
        sys.exit(1)

    # Execute task based on configuration
    task = config.get_task()
    output_config = config.get_output_config()

    # Validate PDF path
    try:
        pdf_filename = config.config["pdf"]["filename"]
        pdf_path = validate_pdf_path(str(config.folder_path), pdf_filename)
    except (KeyError, ValueError, FileNotFoundError) as e:
        print(f"❌ Fehler beim Validieren des PDF-Pfads: {e}")
        sys.exit(1)

    if task == "colloquium":
        coll_config = config.get_colloquium_config()
        gemini_config = config.get_gemini_emark_config()

        if coll_config is None:
            print("❌ Fehler: Kolloquium-Konfiguration fehlt")
            sys.exit(1)

        coll_workflow_config = ColloquiumWorkflowConfig(
            pdf_path=pdf_path,
            date=coll_config["date"],
            time=coll_config["time"],
            llm_client=llm_client,
            groq_free=llm_config.get("groq_free", False),
            output_folder=(Path(output_config["folder"]) if output_config.get("folder") else None),
            compile_pdf=output_config.get("compile_pdf", True),
            fill_form_only=output_config.get("fill_form_only", False),
            location_type=coll_config["location_type"],  # type: ignore
            room=coll_config.get("room"),
            company_name=coll_config.get("company_name"),
            company_address=coll_config.get("company_address"),
            zoom_link=coll_config.get("zoom_link"),
            zcode=coll_config.get("zcode"),
            gemini_emark_enabled=gemini_config.get("enabled", False),
            gemini_model=gemini_config.get("model"),
            gemini_use_text_extraction=gemini_config.get("use_text_extraction", True),
        )

        coll_result = run_pipeline(coll_workflow_config)

        print("\n✓ Kolloquium-Pipeline abgeschlossen:")
        if coll_result.tex_path:
            print(f"  • LaTeX: {coll_result.tex_path}")
        if coll_result.pdf_path:
            print(f"  • PDF: {coll_result.pdf_path}")
        if coll_result.email_path:
            print(f"  • E-Mail: {coll_result.email_path}")
        if coll_result.metadata_path:
            print(f"  • Web-Metadaten: {coll_result.metadata_path}")

    elif task == "project":
        proj_config = config.get_project_config() or {}
        # Support both 'mark' and 'grade' (alias)
        mark = proj_config.get("mark")
        if mark is None:
            mark = proj_config.get("grade")

        work_type = proj_config.get("work_type")

        proj_workflow_config = ProjectWorkflowConfig(
            pdf_path=pdf_path,
            llm_client=llm_client,
            output_folder=(Path(output_config["folder"]) if output_config.get("folder") else None),
            compile_pdf=output_config.get("compile_pdf", True),
            signature_file=output_config.get("signature_file", "signature.png"),
            mark=mark,
            create_feedback_mail=output_config.get("create_feedback_mail", True),
            work_type=work_type,
        )

        proj_result = run_project_pipeline(proj_workflow_config)

        print("\n✓ Projektarbeits-Pipeline abgeschlossen:")
        print(f"  • LaTeX: {proj_result.tex_path}")
        if proj_result.pdf_path:
            print(f"  • PDF: {proj_result.pdf_path}")
        if proj_result.service_email_path:
            print(f"  • E-Mail (Prüfungsservice): {proj_result.service_email_path}")
        if proj_result.student_email_path:
            print(f"  • E-Mail (Student): {proj_result.student_email_path}")
        if proj_result.metadata_path:
            print(f"  • Web-Metadaten: {proj_result.metadata_path}")

    elif task == "review":
        md_path = run_review_pipeline(
            pdf_path=pdf_path,
            llm_client=llm_client,
            groq_free=llm_config.get("groq_free", False),
            output_folder=output_config.get("folder"),
        )

        print("\n✓ Review-Pipeline abgeschlossen:")
        print(f"  • Markdown: {md_path}")

    return config


def run_colloquium_direct(args: argparse.Namespace) -> None:
    """Execute colloquium task with direct CLI arguments."""
    try:
        llm_client = LLMClient(api_choice=args.api, llm=args.model)
        print(f"✓ LLM: {llm_client.api_choice} / {llm_client.llm}")
    except Exception as e:
        print(f"❌ Fehler beim Initialisieren des LLM-Clients: {e}")
        print(
            "Stelle sicher, dass die API-Keys in secrets.env oder als Umgebungsvariablen gesetzt sind."
        )
        sys.exit(1)

    # Validate PDF path
    try:
        # Use parent folder of PDF as base
        pdf_full_path = Path(args.pdf).resolve()
        pdf_path = validate_pdf_path(str(pdf_full_path.parent), pdf_full_path.name)
    except (ValueError, FileNotFoundError) as e:
        print(f"❌ Fehler beim Validieren des PDF-Pfads: {e}")
        sys.exit(1)

    workflow_config = ColloquiumWorkflowConfig(
        pdf_path=pdf_path,
        date=args.date,
        time=args.time,
        llm_client=llm_client,
        groq_free=args.groq_free,
        output_folder=Path(args.out) if args.out else None,
        compile_pdf=not args.no_compile,
        fill_form_only=False,
        location_type=args.location_type,  # type: ignore
        room=args.room,
        company_name=args.company_name,
        company_address=args.company_address,
        zoom_link=args.zoom_link,
        zcode=args.zcode,
        gemini_emark_enabled=args.gemini_eval,
        gemini_model=args.gemini_model,
        gemini_use_text_extraction=not args.gemini_upload_pdf,
    )

    result = run_pipeline(workflow_config)

    print("\n✓ Kolloquium-Pipeline abgeschlossen:")
    if result.tex_path:
        print(f"  • LaTeX: {result.tex_path}")
    if result.pdf_path:
        print(f"  • PDF: {result.pdf_path}")
    if result.email_path:
        print(f"  • E-Mail: {result.email_path}")
    if result.metadata_path:
        print(f"  • Web-Metadaten: {result.metadata_path}")


def run_project_direct(args: argparse.Namespace) -> None:
    """Execute project task with direct CLI arguments."""
    try:
        llm_client = LLMClient(api_choice=args.api, llm=args.model)
        print(f"✓ LLM: {llm_client.api_choice} / {llm_client.llm}")
    except Exception as e:
        print(f"❌ Fehler beim Initialisieren des LLM-Clients: {e}")
        print(
            "Stelle sicher, dass die API-Keys in secrets.env oder als Umgebungsvariablen gesetzt sind."
        )
        sys.exit(1)

    # Validate PDF path
    try:
        pdf_full_path = Path(args.pdf).resolve()
        pdf_path = validate_pdf_path(str(pdf_full_path.parent), pdf_full_path.name)
    except (ValueError, FileNotFoundError) as e:
        print(f"❌ Fehler beim Validieren des PDF-Pfads: {e}")
        sys.exit(1)

    workflow_config = ProjectWorkflowConfig(
        pdf_path=pdf_path,
        llm_client=llm_client,
        output_folder=Path(args.out) if args.out else None,
        compile_pdf=not args.no_compile,
        signature_file=args.signature,
        mark=getattr(args, "mark", None),
        create_feedback_mail=args.create_feedback_mail,
        work_type=getattr(args, "work_type", None),
    )

    result = run_project_pipeline(workflow_config)

    print("\n✓ Projektarbeits-Pipeline abgeschlossen:")
    print(f"  • LaTeX: {result.tex_path}")
    if result.pdf_path:
        print(f"  • PDF: {result.pdf_path}")
    if result.service_email_path:
        print(f"  • E-Mail (Prüfungsservice): {result.service_email_path}")
    if result.student_email_path:
        print(f"  • E-Mail (Student): {result.student_email_path}")
    if result.metadata_path:
        print(f"  • Web-Metadaten: {result.metadata_path}")


def run_review_direct(args: argparse.Namespace) -> None:
    """Execute review task with direct CLI arguments."""
    try:
        llm_client = LLMClient(api_choice=args.api, llm=args.model)
        print(f"✓ LLM: {llm_client.api_choice} / {llm_client.llm}")
    except Exception as e:
        print(f"❌ Fehler beim Initialisieren des LLM-Clients: {e}")
        print(
            "Stelle sicher, dass die API-Keys in secrets.env oder als Umgebungsvariablen gesetzt sind."
        )
        sys.exit(1)

    md_path = run_review_pipeline(
        pdf_path=args.pdf,
        llm_client=llm_client,
        groq_free=args.groq_free,
        output_folder=args.out,
    )

    print("\n✓ Review-Pipeline abgeschlossen:")
    print(f"  • Markdown: {md_path}")


def run_translator_direct(args: argparse.Namespace) -> None:
    """Execute exam translation with direct CLI arguments."""
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Fehler: Datei nicht gefunden: {input_path}")
        sys.exit(1)

    # Determine file type
    is_xml = input_path.suffix.lower() == ".xml"
    is_tex = input_path.suffix.lower() == ".tex"

    if not is_xml and not is_tex:
        print(f"⚠️  Warnung: Datei hat keine .tex oder .xml Endung: {input_path.suffix}")

    # Create LLM client
    try:
        api_choice = args.api if args.api is not None else "kiconnect"
        llm_model = args.model if args.model is not None else "openai-gpt-oss-120b"
        llm_client = LLMClient(api_choice=api_choice, llm=llm_model)
        print(f"✓ LLM: {llm_client.api_choice} / {llm_client.llm}")
    except Exception as e:
        print(f"❌ Fehler beim Initialisieren des LLM-Clients: {e}")
        print(
            "Stelle sicher, dass die API-Keys in secrets.env oder als Umgebungsvariablen gesetzt sind."
        )
        sys.exit(1)

    # Translate exam
    try:
        if is_xml:
            output_path = translate_xml_exam(
                input_path=args.input,
                llm_client=llm_client,
                output_path=args.output,
                verbose=args.verbose,
            )
        else:
            # Default to LaTeX if not explicitly XML (backward compatibility)
            output_path = translate_latex_exam(
                input_path=args.input,
                llm_client=llm_client,
                output_path=args.output,
                verbose=args.verbose,
            )

        print("\n✅ Übersetzung erfolgreich!")
        print(f"📄 Original: {args.input}")
        print(f"📄 Übersetzt: {output_path}")

    except ValueError as e:
        print(f"❌ Fehler in der Dokumentstruktur: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
