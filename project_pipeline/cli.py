# project_pipeline/cli.py
"""Command-line interface for project work grading letter generation."""

import argparse
import os
from llm_client import LLMClient
from .orchestrator import run_project_pipeline


def main(argv=None):
    """CLI entry point for project work grading letter generator.

    Args:
        argv: Command-line arguments (defaults to sys.argv if None).
    """
    parser = argparse.ArgumentParser(
        prog="project-grading-letter",
        description="Generate grading letters for project work (Praxisprojekt) at TH Köln"
    )
    parser.add_argument("pdf", help="Path to the project work PDF")
    parser.add_argument(
        "--api",
        help="LLM API to use (openai, groq, gemini, ollama). Auto-detected if omitted.",
        default=None,
        choices=["openai", "groq", "gemini", "ollama"]
    )
    parser.add_argument(
        "--model",
        help="LLM model to use (e.g., gpt-4o, gemini-2.0-flash-exp)",
        default=None
    )
    parser.add_argument(
        "--out",
        help="Output folder (defaults to same folder as PDF)",
        default=None
    )
    parser.add_argument(
        "--no-compile",
        action="store_true",
        help="Do not compile .tex to PDF"
    )
    parser.add_argument(
        "--signature",
        help="Path to signature image file",
        default="signature.png"
    )

    args = parser.parse_args(argv)

    # Create LLMClient with specified or auto-detected API
    try:
        llm_client = LLMClient(api_choice=args.api, llm=args.model)
        print(f"Using LLM API: {llm_client.api_choice} with model: {llm_client.llm}")
    except Exception as e:
        print(f"Error initializing LLM client: {e}")
        print("Make sure you have set the appropriate API keys in secrets.env or environment variables.")
        return

    tex, pdf = run_project_pipeline(
        args.pdf,
        llm_client=llm_client,
        output_folder=args.out,
        compile_pdf=not args.no_compile,
        signature_file=args.signature
    )

    print(f"✓ LaTeX file: {tex}")
    if pdf:
        print(f"✓ PDF file: {pdf}")


if __name__ == "__main__":
    main()
