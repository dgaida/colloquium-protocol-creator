# src/academic_doc_generator/exam_translator/cli.py
"""CLI interface for the exam translator."""

import argparse
import sys
from pathlib import Path
from llm_client import LLMClient
from .translator import translate_latex_exam


def exam_translator_main() -> None:
    """CLI entry point for exam translation.
    
    This function can be called standalone or integrated into the main CLI.
    """
    parser = argparse.ArgumentParser(
        prog="exam-translator",
        description="Translate LaTeX exam documents from German to English",
    )
    
    parser.add_argument(
        "input",
        help="Path to the German LaTeX exam file (.tex)",
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output path for English exam (default: input_engl.tex)",
        default=None,
    )
    
    parser.add_argument(
        "--api",
        choices=["openai", "groq", "gemini", "ollama"],
        help="LLM API to use (auto-detected if omitted)",
    )
    
    parser.add_argument(
        "--model",
        help="LLM model to use",
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed translation progress",
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Fehler: Datei nicht gefunden: {input_path}")
        sys.exit(1)
    
    if input_path.suffix != ".tex":
        print("⚠️  Warnung: Datei hat keine .tex Endung")
    
    # Create LLM client
    try:
        llm_client = LLMClient(api_choice=args.api, llm=args.model)
        print(f"✓ LLM: {llm_client.api_choice} / {llm_client.llm}")
    except Exception as e:
        print(f"❌ Fehler beim Initialisieren des LLM-Clients: {e}")
        print("Stelle sicher, dass die API-Keys in secrets.env oder als Umgebungsvariablen gesetzt sind.")
        sys.exit(1)
    
    # Translate exam
    try:
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
        print(f"❌ Fehler in der LaTeX-Struktur: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    exam_translator_main()
