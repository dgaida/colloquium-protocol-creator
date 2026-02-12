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
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", mode="wb") as temp_file:
            writer.write(temp_file)
            temp_name = temp_file.name

        return temp_name

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrahiert den Text aus dem PDF mit docling.

        Args:
            pdf_path: Pfad zum PDF.

        Returns:
            Extrahierter Text.
        """
        from ..core.pdf import extract_text_per_page

        pages_text = extract_text_per_page(pdf_path, max_pages=None)
        return "\n\n".join(pages_text.values())

    def _create_emark_prompt(self, thesis_title: str, degree: str, document_text: str = "") -> str:
        """Erstellt den Prompt für die Thesis-Bewertung.

        Args:
            thesis_title: Titel der Arbeit.
            degree: "Bachelor" oder "Master".
            document_text: Extrahierter Text der Arbeit (optional).

        Returns:
            Formatierter Prompt-String.
        """
        niveau = "Bachelor" if degree == "Bachelor" else "Master"

        return build_prompt(
            PromptTemplate.THESIS_EVALUATION,
            niveau=niveau,
            title=thesis_title,
            document_text=(f"\n\n**Dokumententext:**\n\n{document_text}" if document_text else ""),
        )

    def evaluate_thesis(
        self,
        pdf_path: str,
        thesis_title: str,
        degree: str,
        use_text_extraction: bool = True,
        verbose: bool = False,
    ) -> Optional[str]:
        """Bewertet eine Thesis mit Google Gemini.

        Args:
            pdf_path: Pfad zur Thesis-PDF.
            thesis_title: Titel der Arbeit (aus Metadaten extrahiert).
            degree: "Bachelor" oder "Master".
            use_text_extraction: Text-Extraktion statt PDF-Upload verwenden.
            verbose: Debug-Ausgaben aktivieren.

        Returns:
            LaTeX-formatierte Bewertung oder None bei Fehler.
        """
        print("\n🤖 Starte automatische Bewertung mit Google Gemini...")
        print(f"   Niveau: {degree}arbeit")
        print(f"   Titel: {thesis_title}")
        print(f"   Modus: {'Text-Extraktion' if use_text_extraction else 'PDF-Upload'}")

        try:
            # Schritt 1: Erste Seite entfernen (Datenschutz)
            print("   📄 Entferne erste Seite (Datenschutz)...")
            temp_pdf = self._remove_first_page(pdf_path)

            if use_text_extraction:
                # Schritt 2: Text extrahieren
                print("   🔍 Extrahiere Text aus PDF mit docling...")
                text = self._extract_text_from_pdf(temp_pdf)

                # Schritt 3: Prompt erstellen
                prompt = self._create_emark_prompt(thesis_title, degree, document_text=text)

                # Schritt 4: API-Aufruf mit extrahiertem Text
                print("   🚀 Sende Text an Google Gemini...")
                messages = [{"role": "user", "content": prompt}]
                response = self.llm_client.chat_completion(messages=messages)
            else:
                # Schritt 2: Prompt erstellen (ohne Text)
                prompt = self._create_emark_prompt(thesis_title, degree)

                # Schritt 3: API-Aufruf mit PDF-Dokument (File-Upload)
                print("   🚀 Sende PDF-Datei an Google Gemini (dies kann 1-2 Minuten dauern)...")
                messages = [{"role": "user", "content": prompt}]
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
