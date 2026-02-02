# src/academic_doc_generator/cli.py
"""Unified CLI with comprehensive type annotations."""

import argparse
import sys
from pathlib import Path
from typing import List
from llm_client import LLMClient
from .config_loader import ConfigLoader, load_config
from .colloquium.orchestrator import run_pipeline
from .project.orchestrator import run_project_pipeline
from .review.orchestrator import run_review_pipeline


def run_from_config(config_path: str | Path) -> None:
    """Execute a task based on a configuration file.

    Args:
        config_path: Path to JSON configuration file.

    Raises:
        SystemExit: If configuration loading or task execution fails.

    Example:
        >>> run_from_config("config_templates/config_colloquium_campus.json")
    """
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
    pdf_path = config.get_pdf_path()

    if task == "colloquium":
        coll_config = config.get_colloquium_config()
        gemini_config = config.get_gemini_evaluation_config()

        if coll_config is None:
            print("❌ Fehler: Kolloquium-Konfiguration fehlt")
            sys.exit(1)

        tex, pdf, email = run_pipeline(
            pdf_path=pdf_path,
            date_colloquium=coll_config["date"],
            uhrzeit_colloquium=coll_config["time"],
            llm_client=llm_client,
            groq_free=llm_config.get("groq_free", False),
            output_folder=output_config.get("folder"),
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

        print("\n✓ Kolloquium-Pipeline abgeschlossen:")
        if tex:
            print(f"  • LaTeX: {tex}")
        if pdf:
            print(f"  • PDF: {pdf}")
        if email:
            print(f"  • E-Mail: {email}")

    elif task == "project":
        proj_config = config.get_project_config() or {}
        grade = proj_config.get("grade")

        tex, pdf, email, email_student = run_project_pipeline(
            pdf_path=pdf_path,
            llm_client=llm_client,
            output_folder=output_config.get("folder"),
            compile_pdf=output_config.get("compile_pdf", True),
            signature_file=output_config.get("signature_file", "signature.png"),
            grade=grade,
            create_feedback_mail=output_config.get("create_feedback_mail", True),
        )

        print("\n✓ Projektarbeits-Pipeline abgeschlossen:")
        print(f"  • LaTeX: {tex}")
        if pdf:
            print(f"  • PDF: {pdf}")
        if email:
            print(f"  • E-Mail (Prüfungsservice): {email}")
        if email_student:
            print(f"  • E-Mail (Student): {email_student}")

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
    """Execute colloquium task with direct CLI arguments.

    Args:
        args: Parsed command-line arguments from argparse.

    Raises:
        SystemExit: If LLM client initialization fails.
    """
    try:
        llm_client = LLMClient(api_choice=args.api, llm=args.model)
        print(f"✓ LLM: {llm_client.api_choice} / {llm_client.llm}")
    except Exception as e:
        print(f"❌ Fehler beim Initialisieren des LLM-Clients: {e}")
        print(
            "Stelle sicher, dass die API-Keys in secrets.env oder als Umgebungsvariablen gesetzt sind."
        )
        sys.exit(1)

    tex, pdf, email = run_pipeline(
        pdf_path=args.pdf,
        date_colloquium=args.date,
        uhrzeit_colloquium=args.time,
        llm_client=llm_client,
        groq_free=args.groq_free,
        output_folder=args.out,
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

    print("\n✓ Kolloquium-Pipeline abgeschlossen:")
    if tex:
        print(f"  • LaTeX: {tex}")
    if pdf:
        print(f"  • PDF: {pdf}")
    if email:
        print(f"  • E-Mail: {email}")


def run_project_direct(args: argparse.Namespace) -> None:
    """Execute project task with direct CLI arguments.

    Args:
        args: Parsed command-line arguments from argparse.

    Raises:
        SystemExit: If LLM client initialization fails.
    """
    try:
        llm_client = LLMClient(api_choice=args.api, llm=args.model)
        print(f"✓ LLM: {llm_client.api_choice} / {llm_client.llm}")
    except Exception as e:
        print(f"❌ Fehler beim Initialisieren des LLM-Clients: {e}")
        print(
            "Stelle sicher, dass die API-Keys in secrets.env oder als Umgebungsvariablen gesetzt sind."
        )
        sys.exit(1)

    tex, pdf, email, email_student = run_project_pipeline(
        pdf_path=args.pdf,
        llm_client=llm_client,
        output_folder=args.out,
        compile_pdf=not args.no_compile,
        signature_file=args.signature,
        grade=getattr(args, "grade", None),
        create_feedback_mail=args.create_feedback_mail,
    )

    print("\n✓ Projektarbeits-Pipeline abgeschlossen:")
    print(f"  • LaTeX: {tex}")
    if pdf:
        print(f"  • PDF: {pdf}")
    if email:
        print(f"  • E-Mail (Prüfungsservice): {email}")
    if email_student:
        print(f"  • E-Mail (Student): {email_student}")


def run_review_direct(args: argparse.Namespace) -> None:
    """Execute review task with direct CLI arguments.

    Args:
        args: Parsed command-line arguments from argparse.

    Raises:
        SystemExit: If LLM client initialization fails.
    """
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


def create_parser() -> argparse.ArgumentParser:
    """Create ArgumentParser with all subcommands.

    Returns:
        Configured ArgumentParser with colloquium, project, and review subcommands.
    """
    parser = argparse.ArgumentParser(
        prog="academic-doc-generator",
        description="Unified tool for thesis colloquiums, project grading, and peer reviews",
    )

    # Global arguments
    parser.add_argument(
        "--config", help="Path to JSON configuration file", metavar="CONFIG"
    )

    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available configuration templates",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Task to execute")

    # --- Colloquium Subcommand ---
    colloquium_parser = subparsers.add_parser(
        "colloquium", help="Generate colloquium protocol letter"
    )
    colloquium_parser.add_argument("pdf", help="Path to the thesis PDF")
    colloquium_parser.add_argument(
        "--date", required=True, help="Colloquium date (DD.MM.YYYY)"
    )
    colloquium_parser.add_argument(
        "--time", required=True, help="Colloquium time (HH:MM)"
    )
    colloquium_parser.add_argument(
        "--location-type",
        choices=["campus", "company", "online"],
        default="campus",
        help="Location type (default: campus)",
    )
    colloquium_parser.add_argument("--room", help="Room number (for campus)")
    colloquium_parser.add_argument("--company-name", help="Company name (for company)")
    colloquium_parser.add_argument(
        "--company-address", help="Company address (for company)"
    )
    colloquium_parser.add_argument("--zoom-link", help="Zoom meeting link (for online)")
    colloquium_parser.add_argument(
        "--zoom-meeting-access", help="Zoom access code (for online)"
    )
    colloquium_parser.add_argument(
        "--api",
        choices=["openai", "groq", "gemini", "ollama"],
        help="LLM API to use (auto-detected if omitted)",
    )
    colloquium_parser.add_argument("--model", help="LLM model to use")
    colloquium_parser.add_argument(
        "--groq-free", action="store_true", help="Use free-tier pacing"
    )
    colloquium_parser.add_argument(
        "--gemini-eval", action="store_true", help="Enable automatic Gemini evaluation"
    )
    colloquium_parser.add_argument(
        "--gemini-model",
        default="gemini-2.0-flash-exp",
        help="Gemini model for evaluation",
    )
    colloquium_parser.add_argument("--out", help="Output folder")
    colloquium_parser.add_argument(
        "--no-compile", action="store_true", help="Do not compile .tex to PDF"
    )

    # --- Project Subcommand ---
    project_parser = subparsers.add_parser(
        "project", help="Generate project work grading letter"
    )
    project_parser.add_argument("pdf", help="Path to the project work PDF")
    project_parser.add_argument("--grade", help="Grade for the project (e.g., 1.3)")
    project_parser.add_argument(
        "--api",
        choices=["openai", "groq", "gemini", "ollama"],
        help="LLM API to use (auto-detected if omitted)",
    )
    project_parser.add_argument("--model", help="LLM model to use")
    project_parser.add_argument("--out", help="Output folder")
    project_parser.add_argument(
        "--no-compile", action="store_true", help="Do not compile .tex to PDF"
    )
    project_parser.add_argument(
        "--signature", default="signature.png", help="Path to signature image"
    )
    project_parser.add_argument(
        "--create-feedback-mail",
        action="store_true",
        dest="create_feedback_mail",
        default=True,
        help="Generate feedback summary and student email (default: True)",
    )
    project_parser.add_argument(
        "--no-feedback-mail",
        action="store_false",
        dest="create_feedback_mail",
        help="Do not generate feedback summary and student email",
    )

    # --- Review Subcommand ---
    review_parser = subparsers.add_parser(
        "review", help="Generate peer review comments"
    )
    review_parser.add_argument("pdf", help="Path to the paper PDF")
    review_parser.add_argument(
        "--api",
        choices=["openai", "groq", "gemini", "ollama"],
        help="LLM API to use (auto-detected if omitted)",
    )
    review_parser.add_argument("--model", help="LLM model to use")
    review_parser.add_argument(
        "--groq-free", action="store_true", help="Use free-tier pacing"
    )
    review_parser.add_argument("--out", help="Output folder")

    return parser


def main() -> None:
    """Main CLI entry point.

    Handles all command-line arguments and routes to appropriate functions.

    Raises:
        SystemExit: On configuration errors or when listing templates.
    """
    parser = create_parser()
    args = parser.parse_args()

    # List available templates
    if args.list_templates:
        templates_dir = Path("config_templates")
        if not templates_dir.exists():
            print("❌ config_templates-Ordner nicht gefunden")
            sys.exit(1)

        templates: List[Path] = sorted(templates_dir.glob("*.json"))
        if not templates:
            print("❌ Keine Config-Templates gefunden")
            sys.exit(1)

        print("📋 Verfügbare Config-Templates:\n")
        for tmpl in templates:
            print(f"  • {tmpl.name}")
        print("\nVerwendung:")
        print(
            "  academic-doc-generator --config config_templates/config_colloquium_campus.json"
        )
        return

    # Config mode
    if args.config:
        run_from_config(args.config)
        return

    # Subcommand mode
    if args.command == "colloquium":
        run_colloquium_direct(args)
    elif args.command == "project":
        run_project_direct(args)
    elif args.command == "review":
        run_review_direct(args)
    else:
        # No subcommand → show help
        parser.print_help()
        print("\n💡 Tipp:")
        print("  • Verwenden Sie --list-templates für verfügbare Config-Templates")
        print(
            "  • Verwenden Sie ein Subcommand (colloquium, project, review) für direkte Ausführung"
        )
        print("\nBeispiele:")
        print("  academic-doc-generator --config config.json")
        print(
            "  academic-doc-generator colloquium thesis.pdf --date 20.01.2026 --time 14:00 --room 3.217"
        )
        print("  academic-doc-generator project project.pdf")
        print("  academic-doc-generator review paper.pdf")


def colloquium_main() -> None:
    """Entry point for colloquium-protocol-creator command.

    This entry point enables the use of the legacy command name
    with the new consolidated CLI structure.
    """
    sys.argv = ["academic-doc-generator", "colloquium"] + sys.argv[1:]
    main()


def project_main() -> None:
    """Entry point for project-grading-letter command.

    This entry point enables the use of the legacy command name
    with the new consolidated CLI structure.
    """
    sys.argv = ["academic-doc-generator", "project"] + sys.argv[1:]
    main()


if __name__ == "__main__":
    main()
