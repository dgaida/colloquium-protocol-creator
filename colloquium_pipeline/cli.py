# colloquium_pipeline/cli.py
"""Simple CLI for the pipeline."""

import argparse
import os
from .orchestrator import run_pipeline


def main(argv=None):
    parser = argparse.ArgumentParser(prog="colloquium-protocol-creator")
    parser.add_argument("pdf", help="Path to the thesis PDF")
    parser.add_argument("--groq-key", help="Groq API key (env GROQ_API_KEY used if omitted)",
                        default=os.getenv("GROQ_API_KEY"))
    parser.add_argument("--groq-free", action="store_true", help="Use free-tier pacing for Groq")
    parser.add_argument("--out", help="Output folder (defaults to same folder as PDF)", default=None)
    parser.add_argument("--no-compile", action="store_true", help="Do not compile .tex to PDF")
    args = parser.parse_args(argv)

    if args.groq_key is None:
        raise RuntimeError("Groq API key is required (set via --groq-key or env GROQ_API_KEY)")

    tex, pdf = run_pipeline(args.pdf, args.groq_key, groq_free=args.groq_free, output_folder=args.out,
                            compile_pdf=not args.no_compile)
    print("Tex path:", tex)
    if pdf:
        print("PDF path:", pdf)
