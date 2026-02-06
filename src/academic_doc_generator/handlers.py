"""CLI command handlers for different tasks."""

import sys
import argparse
from pathlib import Path
from typing import List
from llm_client import LLMClient
from .config_loader import ConfigLoader, load_config
from .colloquium.orchestrator import run_pipeline
from .project.orchestrator import run_project_pipeline
from .review.orchestrator import run_review_pipeline
from .core.types import ColloquiumWorkflowConfig, ProjectWorkflowConfig
from .domain.validation import validate_pdf_path


def run_from_config(config_path: str | Path) -> None:
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
        llm_client = LLMClient(
            api_choice=llm_config.get("api_choice"), llm=llm_config.get("model")
        )
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
        pdf_path = validate_pdf_path(config.folder_path, pdf_filename)
    except (KeyError, ValueError, FileNotFoundError) as e:
        print(f"❌ Fehler beim Validieren des PDF-Pfads: {e}")
        sys.exit(1)

    if task == "colloquium":
        coll_config = config.get_colloquium_config()
        gemini_config = config.get_gemini_evaluation_config()

        if coll_config is None:
            print("❌ Fehler: Kolloquium-Konfiguration fehlt")
            sys.exit(1)

        workflow_config = ColloquiumWorkflowConfig(
            pdf_path=pdf_path,
            date=coll_config["date"],
            time=coll_config["time"],
            llm_client=llm_client,
            groq_free=llm_config.get("groq_free", False),
            output_folder=Path(output_config["folder"]) if output_config.get("folder") else None,
            compile_pdf=output_config.get("compile_pdf", True),
            fill_form_only=output_config.get("fill_form_only", False),
            location_type=coll_config["location_type"],  # type: ignore
            room=coll_config.get("room"),
            company_name=coll_config.get("company_name"),
            company_address=coll_config.get("company_address"),
            zoom_link=coll_config.get("zoom_link"),
            zoom_meeting_access=coll_config.get("zoom_meeting_access"),
            gemini_evaluation_enabled=gemini_config.get("enabled", False),
            gemini_model=gemini_config.get("model"),
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

    elif task == "project":
        proj_config = config.get_project_config() or {}
        grade = proj_config.get("grade")

        workflow_config = ProjectWorkflowConfig(
            pdf_path=pdf_path,
            llm_client=llm_client,
            output_folder=Path(output_config["folder"]) if output_config.get("folder") else None,
            compile_pdf=output_config.get("compile_pdf", True),
            signature_file=output_config.get("signature_file", "signature.png"),
            grade=grade,
            create_feedback_mail=output_config.get("create_feedback_mail", True),
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

    elif task == "review":
        md_path = run_review_pipeline(
            pdf_path=pdf_path,
            llm_client=llm_client,
            groq_free=llm_config.get("groq_free", False),
            output_folder=output_config.get("folder"),
        )

        print("\n✓ Review-Pipeline abgeschlossen:")
        print(f"  • Markdown: {md_path}")


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
        zoom_meeting_access=args.zoom_meeting_access,
        gemini_evaluation_enabled=args.gemini_eval,
        gemini_model=args.gemini_model,
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
        grade=getattr(args, "grade", None),
        create_feedback_mail=args.create_feedback_mail,
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
