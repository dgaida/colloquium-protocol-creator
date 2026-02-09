# src/academic_doc_generator/colloquium/gemini_thesis_evaluator.py
"""Modul zur automatischen Bewertung von Abschlussarbeiten mit Google Gemini."""

import os
import tempfile
from typing import Optional

from llm_client import LLMClient
from pypdf import PdfReader, PdfWriter

from ..core.prompts import PromptTemplate, build_prompt


class GeminiThesisEvaluator:
    """Bewertet Bachelor- und Masterarbeiten mit Google Gemini Vision API."""

    def __init__(self, llm_client: LLMClient):
        """Initialisiert den Evaluator.

        Args:
            llm_client: LLMClient-Instanz (muss auf Gemini konfiguriert sein).
        """
        self.llm_client = llm_client

        # Stelle sicher, dass Gemini verwendet wird
        if self.llm_client.api_choice != "gemini":
            raise ValueError(
                "GeminiThesisEvaluator benötigt einen LLMClient mit api_choice='gemini'"
            )

    def _remove_first_page(self, pdf_path: str) -> str:
        """Entfernt die erste Seite aus dem PDF (Datenschutz).

        Args:
            pdf_path: Pfad zum Original-PDF.

        Returns:
            Pfad zur temporären PDF-Datei ohne erste Seite.
        """
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        # Kopiere alle Seiten außer der ersten und letzten (letzte: Eigenständigkeitserklärung)
        for page_num in range(1, len(reader.pages) - 1):
            writer.add_page(reader.pages[page_num])

        # Speichere in temporärer Datei
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", mode="wb")
        writer.write(temp_file)
        temp_file.close()

        return temp_file.name

    def _create_emark_prompt(self, thesis_title: str, degree: str) -> str:
        """Erstellt den Prompt für die Thesis-Bewertung.

        Args:
            thesis_title: Titel der Arbeit.
            degree: "Bachelor" oder "Master".

        Returns:
            Formatierter Prompt-String.
        """
        niveau = "Bachelor" if degree == "Bachelor" else "Master"

        return build_prompt(
            PromptTemplate.THESIS_EVALUATION, niveau=niveau, title=thesis_title
        )

    def evaluate_thesis(
        self,
        pdf_path: str,
        thesis_title: str,
        degree: str,
        verbose: bool = False,
    ) -> Optional[str]:
        """Bewertet eine Thesis mit Google Gemini.

        Args:
            pdf_path: Pfad zur Thesis-PDF.
            thesis_title: Titel der Arbeit (aus Metadaten extrahiert).
            degree: "Bachelor" oder "Master".
            verbose: Debug-Ausgaben aktivieren.

        Returns:
            LaTeX-formatierte Bewertung oder None bei Fehler.
        """
        print("\n🤖 Starte automatische Bewertung mit Google Gemini...")
        print(f"   Niveau: {degree}arbeit")
        print(f"   Titel: {thesis_title}")

        try:
            # Schritt 1: Erste Seite entfernen (Datenschutz)
            print("   📄 Entferne erste Seite (Datenschutz)...")
            temp_pdf = self._remove_first_page(pdf_path)

            # Schritt 2: Prompt erstellen
            prompt = self._create_emark_prompt(thesis_title, degree)

            # Schritt 3: API-Aufruf mit PDF-Dokument (neues File-Upload-Feature)
            print(
                "   🚀 Sende Arbeit an Google Gemini (dies kann 1-2 Minuten dauern)..."
            )

            messages = [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]

            # Nutze das neue chat_completion_with_files Feature
            response = self.llm_client.chat_completion_with_files(
                messages=messages,
                files=[temp_pdf],
            )

            # Schritt 4: Temporäre Datei löschen
            os.unlink(temp_pdf)

            if verbose:
                print(f"\n📝 Gemini-Antwort:\n{response}\n")

            print("   ✅ Bewertung erfolgreich erhalten")
            return response

        except Exception as e:
            print(f"   ❌ Fehler bei der Gemini-Bewertung: {e}")
            import traceback

            traceback.print_exc()
            # Stelle sicher, dass temporäre Datei gelöscht wird
            if "temp_pdf" in locals() and os.path.exists(temp_pdf):
                os.unlink(temp_pdf)
            return None

    def format_emark_for_latex(self, emark: str) -> str:
        """Formatiert die Gemini-Bewertung für LaTeX-Einfügung.

        Args:
            emark: Rohe Gemini-Antwort.

        Returns:
            LaTeX-ready formatierter Text.
        """
        # Die Antwort sollte bereits LaTeX-formatiert sein
        # Hier können noch zusätzliche Bereinigungen erfolgen

        # Entferne eventuell vorhandene Markdown-Codeblöcke
        emark = emark.replace("```latex", "").replace("```", "")

        # Stelle sicher, dass Zeilenumbrüche korrekt sind
        emark = emark.strip()

        # Füge Abschnittstrennungen hinzu
        formatted = f"""
\\vspace{{1cm}}
\\hrule
\\vspace{{0.5cm}}

\\section*{{Automatische Bewertung (Google Gemini)}}

\\textit{{Hinweis: Diese Bewertung wurde automatisch durch Google Gemini erstellt und dient als zusätzliche Orientierung für das Kolloquium.}}

\\vspace{{0.5cm}}

{emark}

\\vspace{{0.5cm}}
\\hrule
"""
        return formatted
