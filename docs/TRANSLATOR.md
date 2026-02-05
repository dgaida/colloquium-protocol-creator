# LaTeX Exam Translator

**Automatische Übersetzung von LaTeX-Klausuren (exam-Klasse) von Deutsch nach Englisch**

## Überblick

Dieses Modul übersetzt LaTeX-Klausurdokumente, die die `exam`-Klasse verwenden, automatisch von Deutsch nach Englisch. Es nutzt LLM-APIs (OpenAI, Groq, Gemini, oder Ollama), um hochqualitative Übersetzungen zu erstellen, während die gesamte LaTeX-Struktur, Formatierung und mathematische Notation erhalten bleibt.

## Features

✅ **Strukturierte Übersetzung**: Teilt Dokument in Präambel und einzelne Fragen auf  
✅ **LaTeX-Preservation**: Behält alle LaTeX-Befehle, Umgebungen und Formatierungen bei  
✅ **Mathematik-Schutz**: Mathematische Formeln bleiben unverändert  
✅ **Kommentar-Schutz**: Maskiert LaTeX-Kommentare (`%`) während der Übersetzung, um deren Position und Inhalt exakt zu erhalten
✅ **Mehrere LLM-Provider**: Unterstützt OpenAI, Groq, Gemini, Ollama  
✅ **Automatische Benennung**: Ausgabedatei erhält automatisch Suffix `_engl`  

## Verwendung

### Python API

```python
from llm_client import LLMClient
from academic_doc_generator.exam_translator import translate_latex_exam

# Erstelle LLM-Client (automatische API-Auswahl)
client = LLMClient()

# Übersetze Klausur
output_path = translate_latex_exam(
    input_path="KIKlausurSoSe25_1.tex",
    llm_client=client
)

print(f"Übersetzt: {output_path}")
# Output: KIKlausurSoSe25_1_engl.tex
```

### Kommandozeilen-Verwendung

```bash
# Direkt ausführen (wenn im Pfad)
python -m academic_doc_generator.exam_translator.translator KIKlausurSoSe25_1.tex
```

## Funktionsweise

### 1. Dokumentstruktur-Analyse

Das Dokument wird robust in drei Teile zerlegt:
- **Präambel**: Alles bis zum ersten `\begin{questions}`.
- **Fragen**: Jeder Block, der mit `\question` beginnt.
- **Postamble**: Alles ab `\end{questions}`.

Dabei werden auch Indentationen berücksichtigt und kommentierte Umgebungsmarker ignoriert.

### 2. Maskierung von Kommentaren

Um zu verhindern, dass das LLM LaTeX-Kommentare (Zeilen, die mit `%` beginnen) übersetzt, löscht oder verschiebt, nutzt der Translator einen Maskierungsmechanismus:
1. Alle Kommentare werden vor der Übersetzung durch Platzhalter ersetzt.
2. Der verbleibende Text wird übersetzt.
3. Die Platzhalter werden wieder durch die originalen Kommentare ersetzt.

### 3. Was wird übersetzt?

✅ **Wird übersetzt:**
- Deutscher Fließtext in Aufgabenstellungen
- Anweisungen für Studierende
- Multiple-Choice-Optionen (Textinhalt)
- Lösungstexte in `solutionordottedlines`, `solutionorgrid`
- Header/Footer (Kursnamen, Datum, etc.)
- Tabellen-Beschriftungen und Labels

❌ **Bleibt unverändert:**
- Mathematische Formeln: `$s_1$`, `\gamma = 0.9`, `\[...\]`
- LaTeX-Befehle: `\question[7]`, `\part[\half]`
- Umgebungen: `\begin{parts}`, `\begin{oneparchoices}`
- LaTeX-Kommentare: `% TODO: Punkte anpassen`

## Bekannte Einschränkungen

1. **Exam-Klasse erforderlich**: Funktioniert nur mit LaTeX-Dokumenten, die `\documentclass{exam}` verwenden.
2. **Struktur**: Erwartet eine `questions`-Umgebung.
3. **Regex-Basiert**: Die Aufteilung der Fragen basiert auf Regex-Pattern, die Standard-Indentationen unterstützen.

## Tipps für beste Ergebnisse

✅ **Empfohlen:**
- Nutzen Sie **OpenAI (GPT-4o)** für die höchste Übersetzungsqualität bei komplexen Formulierungen.
- Prüfen Sie die generierte Datei insbesondere bei Tabellen und sehr speziellen LaTeX-Makros.
- Nutzen Sie **Groq** oder **Gemini** für sehr schnelle und kostenlose Übersetzungen.

## Verwandte Dokumentation

- [Haupt-Dokumentation](index.md)
- [Konfigurations-Guide](configuration.md)
