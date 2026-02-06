"""Unified CLI for academic-doc-generator."""

import argparse
import sys
from pathlib import Path
from typing import List
from . import handlers
from .domain.validation import validate_api_keys


def create_parser() -> argparse.ArgumentParser:
    """Create ArgumentParser with all subcommands."""
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
        "--zoom-code", dest="zcode", help="Zoom access code (for online)"
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
        "--gemini-eval",
        action="store_true",
        help="Enable automatic Gemini emark",
    )
    colloquium_parser.add_argument(
        "--gemini-model",
        default="gemini-2.0-flash-exp",
        help="Gemini model for emark",
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
    project_parser.add_argument("--mark", help="Grade for the project (e.g., 1.3)")
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
    """Main CLI entry point."""
    try:
        available_apis = validate_api_keys()
        if not available_apis:
            print(
                "❌ No LLM APIs configured. Please set API keys or install Ollama.",
                file=sys.stderr,
            )
            sys.exit(1)
    except Exception as e:
        print(f"⚠️ Warning during API validation: {e}", file=sys.stderr)

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
        handlers.run_from_config(args.config)
        return

    # Subcommand mode
    if args.command == "colloquium":
        handlers.run_colloquium_direct(args)
    elif args.command == "project":
        handlers.run_project_direct(args)
    elif args.command == "review":
        handlers.run_review_direct(args)
    else:
        # No subcommand → show help
        parser.print_help()
        print("\n💡 Tipp:")
        print("  • Verwenden Sie --list-templates für verfügbare Config-Templates")
        print(
            "  • Verwenden Sie ein Subcommand (colloquium, project, review) für direkte Ausführung"
        )


def colloquium_main() -> None:
    """Entry point for colloquium-protocol-creator command."""
    sys.argv = ["academic-doc-generator", "colloquium"] + sys.argv[1:]
    main()


def project_main() -> None:
    """Entry point for project-grading-letter command."""
    sys.argv = ["academic-doc-generator", "project"] + sys.argv[1:]
    main()


if __name__ == "__main__":
    main()
