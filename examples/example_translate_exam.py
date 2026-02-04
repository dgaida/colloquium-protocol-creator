#!/usr/bin/env python3
# example_translate_exam.py
"""Beispiel-Skript zur Übersetzung einer LaTeX-Klausur."""

from llm_client import LLMClient
from academic_doc_generator.exam_translator import translate_latex_exam


def main():
    """Übersetzt eine LaTeX-Klausur von Deutsch nach Englisch."""

    # Pfad zur deutschen Klausur
    input_path = (
        "../../Mensch-Zentrierte KI/Klausur (auf Teams)/WS2526/hcai_exam_ws2526.tex"
    )

    # Erstelle LLMClient (verwendet automatisch verfügbare API)
    client = LLMClient()

    print(f"🤖 Verwende LLM: {client.api_choice} / {client.llm}")

    # Übersetze die Klausur
    output_path = translate_latex_exam(
        input_path=input_path,
        llm_client=client,
        verbose=False,  # Setze auf True für detaillierte Debug-Ausgaben
    )

    print("\n✨ Übersetzung erfolgreich!")
    print(f"📁 Ausgabedatei: {output_path}")


if __name__ == "__main__":
    main()
