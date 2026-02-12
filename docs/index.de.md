# Academic Document Generator Dokumentation

![Workflow Infografik](infografik.png)

Willkommen zur Dokumentation des Academic Document Generators!

Verwandeln Sie annotierte PDFs mithilfe von KI in professionelle LaTeX-Dokumente. Generieren Sie automatisch Protokolle für Thesis-Kolloquien, Benotungsbriefe für Praxisprojekte, Peer-Review-Kommentare und übersetzen Sie LaTeX-Klausuren.

---

## 📊 Vier Hauptanwendungsfälle

<div class="grid cards" markdown>

-   :material-school:{ .lg .middle } __🎓 Kolloquium-Protokolle__

    ---

    - Notizen → klare Fragen
    - Auto-Metadaten-Extraktion
    - Thesis-Zusammenfassung
    - Formular-Ausfüllung
    - E-Mail-Generierung

    [:octicons-arrow-right-24: Dokumentation](COLLOQUIUM.md)

-   :material-file-document:{ .lg .middle } __📊 Praxisprojekt-Benotung__

    ---

    - Metadaten-Extraktion
    - Anrede-Bestimmung (Herr/Frau)
    - Bewertungsbrief-Vorlage
    - Feedback-Zusammenfassung
    - Studierenden-E-Mail

    [:octicons-arrow-right-24: Dokumentation](PROJECT.md)

-   :material-pencil:{ .lg .middle } __✍️ Peer Review Kommentare__

    ---

    - Notizen → konstruktives Feedback
    - Auto-Zeilennummern-Erkennung
    - Markdown-Export
    - Immer auf Englisch
    - Wissenschaftlicher Ton

    [:octicons-arrow-right-24: Dokumentation](REVIEW.md)

-   :material-translate:{ .lg .middle } __🔤 LaTeX-Klausur-Übersetzer__

    ---

    - Deutsch → Englisch
    - Exam-Klasse optimiert
    - Mathe-Formeln erhalten
    - Kommentare geschützt
    - Struktur-bewusst

    [:octicons-arrow-right-24: Dokumentation](TRANSLATOR.md)

</div>

---

## 🎯 Quick Links

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __Schnellstart__

    ---

    In wenigen Minuten startklar mit unserer Installationsanleitung

    [:octicons-arrow-right-24: Installation](INSTALL.md)

-   :material-cog:{ .lg .middle } __Konfiguration__

    ---

    Konfigurieren Sie Ihre LLM-APIs und Vorlagen

    [:octicons-arrow-right-24: Konfigurations-Guide](configuration.md)

-   :material-file-find:{ .lg .middle } __Beispiele__

    ---

    Sehen Sie sich Beispiele für erzeugte Dokumente an

    [:octicons-arrow-right-24: Beispiel-Ausgaben](EXAMPLES.md)

-   :material-code-braces:{ .lg .middle } __API-Referenz__

    ---

    Vollständige API-Dokumentation für Entwickler

    [:octicons-arrow-right-24: API-Docs](api_reference/index.md)

</div>

## ✨ Hauptmerkmale

- 🚀 **Einheitliche CLI** - Ein einziger `academic-doc-generator`-Befehl für alle Aufgaben
- 🔍 **Extraktion von PDF-Annotationen** - Extrahiert Text und Annotationspositionen mit Docling + PyPDF
- 🤖 **Unterstützung mehrerer LLMs** - Funktioniert mit OpenAI, Groq, Google Gemini oder Ollama
- 🎯 **Kontextsensitive Umformulierung** - Ordnet Annotationen dem exakt markierten Text und den umgebenden Absätzen zu
- ✍️ **Intelligente Kommentar-Veredelung** - Schreibt kurze Notizen in vollständige Fragen um
- 📝 **LaTeX-Generierung** - Erzeugt professionelle Briefe mit TH Köln-Formatierung
- ✒️ **Automatische Signatur-Erkennung** - Bindet Signaturen aus `data/signature.png` automatisch ein
- 📋 **Vorausfüllen von PDF-Formularen** - Füllt offizielle Bewertungsformulare automatisch aus
- 📧 **E-Mail- & Outlook-Integration** - Erstellt Anmelde-E-Mails und Outlook-Entwürfe
- 🌐 **Unicode-Unterstützung** - Korrekte Handhabung deutscher Umlaute

## 🛠️ Anforderungen

- **Python**: 3.9 oder höher
- **LaTeX**: LuaLaTeX empfohlen (for Unicode-Unterstützung)
- **LLM API**: Mindestens eine von OpenAI, Groq, Gemini oder Ollama

## 🤝 Mitwirken

Beiträge sind willkommen! Bitte lesen Sie die [CONTRIBUTING.md](CONTRIBUTING.md) für Richtlinien.

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz veröffentlicht.

---

**Hinweis:** Dieses Tool unterstützt bei der Erstellung von Dokumentvorlagen — es trifft keine automatischen Benotungs- oder Bewertungsentscheidungen. Alle akademischen Bewertungen verbleiben in der Verantwortung des Prüfers.
