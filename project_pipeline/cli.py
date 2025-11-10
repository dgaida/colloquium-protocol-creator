# project_pipeline/cli.py
"""Command-line interface for project work grading letter generation."""

import argparse
import os
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
        "--groq-key",
        help="Groq API key (env GROQ_API_KEY used if omitted)",
        default=os.getenv("GROQ_API_KEY")
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
    
    if args.groq_key is None:
        raise RuntimeError(
            "Groq API key is required (set via --groq-key or env GROQ_API_KEY)"
        )
    
    tex, pdf = run_project_pipeline(
        args.pdf,
        args.groq_key,
        output_folder=args.out,
        compile_pdf=not args.no_compile,
        signature_file=args.signature
    )
    
    print(f"✓ LaTeX file: {tex}")
    if pdf:
        print(f"✓ PDF file: {pdf}")


if __name__ == "__main__":
    main()
