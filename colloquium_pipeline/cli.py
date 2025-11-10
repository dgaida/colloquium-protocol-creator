# colloquium_pipeline/cli.py
"""Simple CLI for the pipeline."""

import argparse
import os
from llm_client import LLMClient
from .orchestrator import run_pipeline


def main(argv=None):
    parser = argparse.ArgumentParser(prog="colloquium-protocol-creator")
    parser.add_argument("pdf", help="Path to the thesis PDF")
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
        "--groq-free",
        action="store_true",
        help="Use free-tier pacing (applies rate limiting)"
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
    args = parser.parse_args(argv)

    # Create LLMClient with specified or auto-detected API
    try:
        llm_client = LLMClient(api_choice=args.api, llm=args.model)
        print(f"Using LLM API: {llm_client.api_choice} with model: {llm_client.llm}")
    except Exception as e:
        print(f"Error initializing LLM client: {e}")
        print("Make sure you have set the appropriate API keys in secrets.env or environment variables.")
        return

    tex, pdf = run_pipeline(
        args.pdf,
        llm_client=llm_client,
        groq_free=args.groq_free,
        output_folder=args.out,
        compile_pdf=not args.no_compile
    )

    print("Tex path:", tex)
    if pdf:
        print("PDF path:", pdf)
