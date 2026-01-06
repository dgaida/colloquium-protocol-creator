"""Unified CLI for colloquium-protocol-creator.

This CLI supports both direct arguments and JSON configuration files
for running colloquium, project, and review tasks.
"""

import argparse
import os.path
import sys
from pathlib import Path
from llm_client import LLMClient
from .config_loader import load_config


def run_from_config(pdf_path: str) -> None:
    """Führt einen Task basierend auf einer Config-Datei aus.

    Args:
        pdf_path: Pfad zur JSON-Konfigurationsdatei.
    """
    # Lade und validiere Konfiguration
    try:
        config = load_config(pdf_path)
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

    path2pdf = config.get_pdf_path()

    if task == "colloquium":
        from .colloquium.orchestrator import run_pipeline

        coll_config = config.get_colloquium_config()

        tex, pdf, email = run_pipeline(
            pdf_path=path2pdf,
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
        from .project.orchestrator import run_project_pipeline

        tex, pdf = run_project_pipeline(
            pdf_path=path2pdf,
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
        from .review.orchestrator import run_review_pipeline

        md_path = run_review_pipeline(
            pdf_path=path2pdf,
            llm_client=llm_client,
            groq_free=llm_config.get("groq_free", False),
            output_folder=output_config.get("folder")
        )

        print(f"\n✓ Review-Pipeline abgeschlossen:")
        print(f"  • Markdown: {md_path}")


def main():
    """Haupt-CLI-Einstiegspunkt."""
    parser = argparse.ArgumentParser(
        prog="colloquium-protocol-creator",
        description="Unified tool for thesis colloquiums, project grading, and peer reviews"
    )

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
        print("  colloquium-protocol-creator --config config_templates/config_colloquium_campus.json")
        return

    # Config-Modus
    if args.config:
        run_from_config(args.config)
        return

    # Kein Config-Argument → Hilfe anzeigen
    parser.print_help()
    print("\n💡 Tipp: Verwenden Sie --list-templates um verfügbare Config-Templates zu sehen")


if __name__ == "__main__":
    main()
