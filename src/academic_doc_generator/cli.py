"""Unified CLI for academic-doc-generator.

This CLI supports both JSON configuration files and direct command-line arguments
for running colloquium, project, and review tasks.
"""

import argparse
import sys
from pathlib import Path
from llm_client import LLMClient
from .config_loader import load_config
from .colloquium.orchestrator import run_pipeline
from .project.orchestrator import run_project_pipeline
from .review.orchestrator import run_review_pipeline


def run_from_config(config_path: str) -> None:
    """Führt einen Task basierend auf einer Config-Datei aus.

    Args:
        config_path: Pfad zur JSON-Konfigurationsdatei.
    """
    try:
        config = load_config(config_path)
        print(f"✓ Konfiguration geladen: {config}")
    except (FileNotFoundError, ValueError, Exception) as e:
        print(f"❌ Fehler beim Laden der Konfiguration: {e}")
        sys.exit(1)

    # Erstelle LLM-Client
    llm_config = config.get_llm_config()
    try:
        llm_client = LLMClient(
            api_choice=llm_config.get("api_choice"),
            llm=llm_config.get("model")
        )
        print(f"✓ LLM: {llm_client.api_choice} / {llm_client.llm}")
    except Exception as e:
        print(f"❌ Fehler beim Initialisieren des LLM-Clients: {e}")
        sys.exit(1)

    # Führe Task aus
    task = config.get_task()
    output_config = config.get_output_config()
    pdf_path = config.get_pdf_path()

    if task == "colloquium":
        coll_config = config.get_colloquium_config()

        tex, pdf, email = run_pipeline(
            pdf_path=pdf_path,
            date_colloquium=coll_config["date"],
            uhrzeit_colloquium=coll_config["time"],
            llm_client=llm_client,
            groq_free=llm_config.get("groq_free", False),
            output_folder=output_config.get("folder"),
            compile_pdf=output_config.get("compile_pdf", True),
            fill_form_only=output_config.get("fill_form_only", False),
            location_type=coll_config["location_type"],
            room=coll_config.get("room"),
            company_name=coll_config.get("company_name"),
            company_address=coll_config.get("company_address"),
            zoom_link=coll_config.get("zoom_link"),
            zoom_passcode=coll_config.get("zoom_passcode")
        )

        print(f"\n✓ Kolloquium-Pipeline abgeschlossen:")
        if tex:
            print(f"  • LaTeX: {tex}")
        if pdf:
            print(f"  • PDF: {pdf}")
        if email:
            print(f"  • E-Mail: {email}")

    elif task == "project":
        tex, pdf = run_project_pipeline(
            pdf_path=pdf_path,
            llm_client=llm_client,
            output_folder=output_config.get("folder"),
            compile_pdf=output_config.get("compile_pdf", True),
            signature_file=output_config.get("signature_file", "signature.png")
        )

        print(f"\n✓ Projektarbeits-Pipeline abgeschlossen:")
        print(f"  • LaTeX: {tex}")
        if pdf:
            print(f"  • PDF: {pdf}")

    elif task == "review":
        md_path = run_review_pipeline(
            pdf_path=pdf_path,
            llm_client=llm_client,
            groq_free=llm_config.get("groq_free", False),
            output_folder=output_config.get("folder")
        )

        print(f"\n✓ Review-Pipeline abgeschlossen:")
        print(f"  • Markdown: {md_path}")


def run_colloquium_direct(args) -> None:
    """Führt Colloquium-Task mit direkten CLI-Argumenten aus.

    Args:
        args: Parsed command-line arguments.
    """
    try:
        llm_client = LLMClient(api_choice=args.api, llm=args.model)
        print(f"✓ LLM: {llm_client.api_choice} / {llm_client.llm}")
    except Exception as e:
        print(f"❌ Fehler beim Initialisieren des LLM-Clients: {e}")
        print("Stelle sicher, dass die API-Keys in secrets.env oder als Umgebungsvariablen gesetzt sind.")
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
        location_type=args.location_type,
        room=args.room,
        company_name=args.company_name,
        company_address=args.company_address,
        zoom_link=args.zoom_link,
        zoom_passcode=args.zoom_passcode
    )

    print(f"\n✓ Kolloquium-Pipeline abgeschlossen:")
    if tex:
        print(f"  • LaTeX: {tex}")
    if pdf:
        print(f"  • PDF: {pdf}")
    if email:
        print(f"  • E-Mail: {email}")


def run_project_direct(args) -> None:
    """Führt Project-Task mit direkten CLI-Argumenten aus.

    Args:
        args: Parsed command-line arguments.
    """
    try:
        llm_client = LLMClient(api_choice=args.api, llm=args.model)
        print(f"✓ LLM: {llm_client.api_choice} / {llm_client.llm}")
    except Exception as e:
        print(f"❌ Fehler beim Initialisieren des LLM-Clients: {e}")
        print("Stelle sicher, dass die API-Keys in secrets.env oder als Umgebungsvariablen gesetzt sind.")
        sys.exit(1)

    tex, pdf = run_project_pipeline(
        pdf_path=args.pdf,
        llm_client=llm_client,
        output_folder=args.out,
        compile_pdf=not args.no_compile,
        signature_file=args.signature
    )

    print(f"\n✓ Projektarbeits-Pipeline abgeschlossen:")
    print(f"  • LaTeX: {tex}")
    if pdf:
        print(f"  • PDF: {pdf}")


def run_review_direct(args) -> None:
    """Führt Review-Task mit direkten CLI-Argumenten aus.

    Args:
        args: Parsed command-line arguments.
    """
    try:
        llm_client = LLMClient(api_choice=args.api, llm=args.model)
        print(f"✓ LLM: {llm_client.api_choice} / {llm_client.llm}")
    except Exception as e:
        print(f"❌ Fehler beim Initialisieren des LLM-Clients: {e}")
        print("Stelle sicher, dass die API-Keys in secrets.env oder als Umgebungsvariablen gesetzt sind.")
        sys.exit(1)

    md_path = run_review_pipeline(
        pdf_path=args.pdf,
        llm_client=llm_client,
        groq_free=args.groq_free,
        output_folder=args.out
    )

    print(f"\n✓ Review-Pipeline abgeschlossen:")
    print(f"  • Markdown: {md_path}")


def create_parser() -> argparse.ArgumentParser:
    """Erstellt den ArgumentParser mit allen Subcommands.

    Returns:
        Konfigurierter ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        prog="academic-doc-generator",
        description="Unified tool for thesis colloquiums, project grading, and peer reviews"
    )

    # Global arguments
    parser.add_argument(
        "--config",
        help="Path to JSON configuration file",
        metavar="CONFIG"
    )

    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available configuration templates"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Task to execute")

    # --- Colloquium Subcommand ---
    colloquium_parser = subparsers.add_parser(
        "colloquium",
        help="Generate colloquium protocol letter"
    )
    colloquium_parser.add_argument("pdf", help="Path to the thesis PDF")
    colloquium_parser.add_argument("--date", required=True, help="Colloquium date (DD.MM.YYYY)")
    colloquium_parser.add_argument("--time", required=True, help="Colloquium time (HH:MM)")
    colloquium_parser.add_argument(
        "--location-type",
        choices=["campus", "company", "online"],
        default="campus",
        help="Location type (default: campus)"
    )
    colloquium_parser.add_argument("--room", help="Room number (for campus)")
    colloquium_parser.add_argument("--company-name", help="Company name (for company)")
    colloquium_parser.add_argument("--company-address", help="Company address (for company)")
    colloquium_parser.add_argument("--zoom-link", help="Zoom meeting link (for online)")
    colloquium_parser.add_argument("--zoom-passcode", help="Zoom passcode (for online)")
    colloquium_parser.add_argument(
        "--api",
        choices=["openai", "groq", "gemini", "ollama"],
        help="LLM API to use (auto-detected if omitted)"
    )
    colloquium_parser.add_argument("--model", help="LLM model to use")
    colloquium_parser.add_argument("--groq-free", action="store_true", help="Use free-tier pacing")
    colloquium_parser.add_argument("--out", help="Output folder")
    colloquium_parser.add_argument("--no-compile", action="store_true", help="Do not compile .tex to PDF")

    # --- Project Subcommand ---
    project_parser = subparsers.add_parser(
        "project",
        help="Generate project work grading letter"
    )
    project_parser.add_argument("pdf", help="Path to the project work PDF")
    project_parser.add_argument(
        "--api",
        choices=["openai", "groq", "gemini", "ollama"],
        help="LLM API to use (auto-detected if omitted)"
    )
    project_parser.add_argument("--model", help="LLM model to use")
    project_parser.add_argument("--out", help="Output folder")
    project_parser.add_argument("--no-compile", action="store_true", help="Do not compile .tex to PDF")
    project_parser.add_argument("--signature", default="signature.png", help="Path to signature image")

    # --- Review Subcommand ---
    review_parser = subparsers.add_parser(
        "review",
        help="Generate peer review comments"
    )
    review_parser.add_argument("pdf", help="Path to the paper PDF")
    review_parser.add_argument(
        "--api",
        choices=["openai", "groq", "gemini", "ollama"],
        help="LLM API to use (auto-detected if omitted)"
    )
    review_parser.add_argument("--model", help="LLM model to use")
    review_parser.add_argument("--groq-free", action="store_true", help="Use free-tier pacing")
    review_parser.add_argument("--out", help="Output folder")

    return parser


def main():
    """Haupt-CLI-Einstiegspunkt."""
    parser = create_parser()
    args = parser.parse_args()

    # Liste verfügbare Templates
    if args.list_templates:
        templates_dir = Path("config_templates")
        if not templates_dir.exists():
            print("❌ config_templates-Ordner nicht gefunden")
            sys.exit(1)

        templates = sorted(templates_dir.glob("*.json"))
        if not templates:
            print("❌ Keine Config-Templates gefunden")
            sys.exit(1)

        print("📋 Verfügbare Config-Templates:\n")
        for tmpl in templates:
            print(f"  • {tmpl.name}")
        print("\nVerwendung:")
        print("  academic-doc-generator --config config_templates/config_colloquium_campus.json")
        return

    # Config-Modus
    if args.config:
        run_from_config(args.config)
        return

    # Subcommand-Modus
    if args.command == "colloquium":
        run_colloquium_direct(args)
    elif args.command == "project":
        run_project_direct(args)
    elif args.command == "review":
        run_review_direct(args)
    else:
        # Kein Subcommand → Hilfe anzeigen
        parser.print_help()
        print("\n💡 Tipp:")
        print("  • Verwenden Sie --list-templates für verfügbare Config-Templates")
        print("  • Verwenden Sie ein Subcommand (colloquium, project, review) für direkte Ausführung")
        print("\nBeispiele:")
        print("  academic-doc-generator --config config.json")
        print("  academic-doc-generator colloquium thesis.pdf --date 20.01.2026 --time 14:00 --room 3.217")
        print("  academic-doc-generator project project.pdf")
        print("  academic-doc-generator review paper.pdf")


def colloquium_main():
    """Entry point für colloquium-protocol-creator command.

    Dieser Entry Point ermöglicht die Verwendung des alten Command-Namens
    mit der neuen konsolidierten CLI-Struktur.
    """
    sys.argv = ["academic-doc-generator", "colloquium"] + sys.argv[1:]
    main()


def project_main():
    """Entry point für project-grading-letter command.

    Dieser Entry Point ermöglicht die Verwendung des alten Command-Namens
    mit der neuen konsolidierten CLI-Struktur.
    """
    sys.argv = ["academic-doc-generator", "project"] + sys.argv[1:]
    main()


if __name__ == "__main__":
    main()
