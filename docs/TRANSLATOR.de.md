# LaTeX-Klausur-Übersetzer

## Übersicht

Dieses Modul übersetzt LaTeX-Klausurdokumente, die die `exam`-Klasse verwenden, automatisch von Deutsch nach Englisch. Es nutzt LLM-APIs (OpenAI, Groq, Gemini oder Ollama), um hochqualitative Übersetzungen zu erstellen, während die gesamte LaTeX-Struktur, Formatierung und mathematische Notation exakt erhalten bleibt.

## Erzeugte Dateien (Ergebnisse)

### 1. Übersetzte LaTeX-Datei
**Dateiname:** `<originalname>_engl.tex`
Die fertig übersetzte LaTeX-Datei, in der alle fachlichen Inhalte ins Englische übertragen wurden, während Formeln und Befehle unverändert blieben.

---

## Benutzung

### Kommandozeile (CLI)

```bash
# Basis-Nutzung
academic-doc-generator translator KIKlausur.tex
```

### Python API

```python
from llm_client import LLMClient
from academic_doc_generator.exam_translator import translate_latex_exam

# Erstelle LLM-Client
client = LLMClient()

# Übersetze Klausur
output_path = translate_latex_exam("KIKlausur.tex", client)
```

## Hauptmerkmale

- ✅ **Strukturierte Übersetzung**: Teilt das Dokument intelligent in Präambel und einzelne Fragen auf.  
- ✅ **LaTeX-Erhalt**: Behält alle LaTeX-Befehle und Umgebungen bei.  
- ✅ **Mathematik-Schutz**: Mathematische Formeln werden nicht verändert.  
- ✅ **Kommentar-Schutz**: Maskiert LaTeX-Kommentare (`%`), um deren Position und Inhalt exakt zu bewahren.  

---

## Funktionsweise (Details)

### 1. Dokumentstruktur-Analyse
Das Dokument wird in drei Teile zerlegt:  
- **Präambel**: Alles bis zum ersten `\begin{questions}`.  
- **Fragen**: Jeder Block, der mit `\question` beginnt.  
- **Postamble**: Alles ab `\end{questions}`.  

### 2. Maskierung von Kommentaren
Um zu verhindern, dass die KI LaTeX-Kommentare übersetzt oder löscht, werden diese vor der Verarbeitung durch Platzhalter ersetzt und nach der Übersetzung wieder an der exakten Stelle eingefügt.

### 3. Was wird übersetzt?  
- **Übersetzt**: Fließtext, Aufgabenstellungen, Multiple-Choice-Optionen, Lösungstexte, Header/Footer.  
- **Unverändert**: Mathematische Formeln (`$...$`, `\[...\]`), LaTeX-Befehle (`\question[5]`), Umgebungen, Kommentare.  

---

## Einschränkungen & Tipps

1. **Exam-Klasse erforderlich**: Das Tool ist speziell für die LaTeX `exam`-Klasse optimiert.  
2. **KI-Wahl**: Nutzen Sie **OpenAI (GPT-4o)** für die höchste Qualität bei komplexen fachlichen Formulierungen.  
3. **Schnelligkeit**: Nutzen Sie **Groq** oder **Gemini** für sehr schnelle und oft kostenlose Übersetzungen.  

## Weitere Dokumentation

- [Haupt-Dokumentation](index.de.md)  
- [Konfigurations-Handbuch](configuration.de.md)  
