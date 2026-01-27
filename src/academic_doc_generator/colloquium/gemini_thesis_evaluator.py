# src/academic_doc_generator/colloquium/gemini_thesis_evaluator.py
"""Modul zur automatischen Bewertung von Abschlussarbeiten mit Google Gemini."""

import os
import tempfile
from typing import Optional
from llm_client import LLMClient
from pypdf import PdfReader, PdfWriter


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

    def _create_evaluation_prompt(self, thesis_title: str, degree: str) -> str:
        """Erstellt den Prompt für die Thesis-Bewertung.

        Args:
            thesis_title: Titel der Arbeit.
            degree: "Bachelor" oder "Master".

        Returns:
            Formatierter Prompt-String.
        """
        niveau = "Bachelor" if degree == "Bachelor" else "Master"

        prompt = f"""Du bist ein erfahrener Professor für Informatik an der TH Köln und bewertest eine {niveau}arbeit.

**Titel der Arbeit:** {thesis_title}

**Deine Aufgabe:**

1. **Kritische Analyse der Stärken und Schwächen:**
   - Analysiere die gesamte Arbeit gründlich
   - Identifiziere mindestens 5 konkrete Stärken der Arbeit
   - Identifiziere mindestens 5 konkrete Schwächen oder Verbesserungspotenziale
   - Beziehe dich auf spezifische Kapitel, Methoden, Argumente oder Abbildungen
   - Bewerte das Niveau angemessen für eine {niveau}arbeit

2. **Kolloquiumsfragen:**
   - Entwickle genau 10 Fragen für das Kolloquium
   - Die Fragen sollen das Verständnis der Studierenden prüfen
   - Fragen sollen sich auf kritische Stellen, Designentscheidungen und Ergebnisse beziehen
   - Niveau muss einer {niveau}arbeit angemessen sein
   - Mischung aus technischen Details und konzeptionellem Verständnis

**Wichtig:**
- Antworte ausschließlich auf Deutsch
- Formatiere deine Antwort als LaTeX-Text (verwende \\\\, \\textbf{{}}, \\begin{{itemize}}, etc.)
- Escape LaTeX-Sonderzeichen korrekt (verwende \\& statt &, \\% statt %, etc.)
- Sei konstruktiv und professionell
- Gib konkrete Beispiele aus der Arbeit

**Format der Antwort:**

\\textbf{{Stärken der Arbeit:}}

\\begin{{itemize}}
\\item Stärke 1 mit konkretem Bezug
\\item Stärke 2 mit konkretem Bezug
\\item ...
\\end{{itemize}}

\\textbf{{Schwächen und Verbesserungspotenzial:}}

\\begin{{itemize}}
\\item Schwäche 1 mit konkretem Bezug
\\item Schwäche 2 mit konkretem Bezug
\\item ...
\\end{{itemize}}

\\textbf{{Vorgeschlagene Kolloquiumsfragen:}}

\\begin{{enumerate}}
\\item Frage 1
\\item Frage 2
\\item ...
\\item Frage 10
\\end{{enumerate}}
"""
        return prompt

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
        print(f"\n🤖 Starte automatische Bewertung mit Google Gemini...")
        print(f"   Niveau: {degree}arbeit")
        print(f"   Titel: {thesis_title}")

        try:
            # Schritt 1: Erste Seite entfernen (Datenschutz)
            print("   📄 Entferne erste Seite (Datenschutz)...")
            temp_pdf = self._remove_first_page(pdf_path)

            # Schritt 2: Prompt erstellen
            prompt = self._create_evaluation_prompt(thesis_title, degree)

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

    def format_evaluation_for_latex(self, evaluation: str) -> str:
        """Formatiert die Gemini-Bewertung für LaTeX-Einfügung.

        Args:
            evaluation: Rohe Gemini-Antwort.

        Returns:
            LaTeX-ready formatierter Text.
        """
        # Die Antwort sollte bereits LaTeX-formatiert sein
        # Hier können noch zusätzliche Bereinigungen erfolgen

        # Entferne eventuell vorhandene Markdown-Codeblöcke
        evaluation = evaluation.replace("```latex", "").replace("```", "")

        # Stelle sicher, dass Zeilenumbrüche korrekt sind
        evaluation = evaluation.strip()

        # Füge Abschnittstrennungen hinzu
        formatted = f"""
\\vspace{{1cm}}
\\hrule
\\vspace{{0.5cm}}

\\section*{{Automatische Bewertung (Google Gemini)}}

\\textit{{Hinweis: Diese Bewertung wurde automatisch durch Google Gemini erstellt und dient als zusätzliche Orientierung für das Kolloquium.}}

\\vspace{{0.5cm}}

{evaluation}

\\vspace{{0.5cm}}
\\hrule
"""
        return formatted
