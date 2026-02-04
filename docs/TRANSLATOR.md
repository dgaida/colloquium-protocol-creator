# LaTeX Exam Translator

**Automatische Übersetzung von LaTeX-Klausuren (exam-Klasse) von Deutsch nach Englisch**

## Überblick

Dieses Modul übersetzt LaTeX-Klausurdokumente, die die `exam`-Klasse verwenden, automatisch von Deutsch nach Englisch. Es nutzt LLM-APIs (OpenAI, Groq, Gemini, oder Ollama), um hochqualitative Übersetzungen zu erstellen, während die gesamte LaTeX-Struktur, Formatierung und mathematische Notation erhalten bleibt.

## Features

✅ **Strukturierte Übersetzung**: Teilt Dokument in Präambel und einzelne Fragen auf  
✅ **LaTeX-Preservation**: Behält alle LaTeX-Befehle, Umgebungen und Formatierungen bei  
✅ **Mathematik-Schutz**: Mathematische Formeln bleiben unverändert  
✅ **Mehrere LLM-Provider**: Unterstützt OpenAI, Groq, Gemini, Ollama  
✅ **Automatische Benennung**: Ausgabedatei erhält automatisch Suffix `_engl`  

## Verwendung

### Grundlegende Verwendung

```python
from llm_client import LLMClient
from latex_exam_translator import translate_latex_exam

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
# Direkt ausführen
python latex_exam_translator.py KIKlausurSoSe25_1.tex

# Oder mit Beispiel-Skript
python example_translate_exam.py
```

### Erweiterte Optionen

```python
# Mit spezifischem Output-Pfad
output_path = translate_latex_exam(
    input_path="klausur_de.tex",
    llm_client=client,
    output_path="exam_english.tex",
    verbose=True  # Zeigt Debug-Informationen
)

# Mit spezifischem LLM-Provider
from llm_client import LLMClient

# OpenAI verwenden
client = LLMClient(api_choice="openai", llm="gpt-4o-mini")

# Groq verwenden (kostenlos)
client = LLMClient(api_choice="groq", llm="moonshotai/kimi-k2-instruct-0905")

# Gemini verwenden (kostenlos)
client = LLMClient(api_choice="gemini", llm="gemini-2.0-flash-exp")

# Ollama lokal verwenden (komplett kostenlos)
client = LLMClient(api_choice="ollama", llm="llama3.2:1b")
```

## Funktionsweise

### 1. Dokumentstruktur-Analyse

```python
from latex_exam_translator import split_latex_exam_into_sections

# Teilt Dokument in:
# - Präambel (bis \begin{questions})
# - Einzelne Fragen (beginnend mit \question)
# - Postamble (\end{questions} und danach)
preamble, questions, postamble = split_latex_exam_into_sections(latex_text)
```

### 2. Übersetzungsprozess

Für jeden Abschnitt:

1. **Präambel**: Übersetzt Header, Anweisungen, Labels
2. **Jede Frage**: Übersetzt Text, behält LaTeX-Struktur bei
3. **Zusammenfügen**: Konkateniert alle Teile wieder

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
- Referenzen: `\ref{tab:...}`, `\label{...}`
- Pakete: `\usepackage{...}`

## Beispiel

### Input (Deutsch)

```latex
\question[7] Definieren Sie ein geeignetes, möglichst \textbf{spezifisches}, 
Leistungsma{\ss} für die autonom fahrende Rikscha in 1-2 Sätzen.

\begin{solutionordottedlines}[3.25in]
Die Rikscha soll seine Kunden zeitnah (keine Staus und Umwege), 
sicher und komfortabel (keine zu hohen Beschleunigungen) an die 
angegebenen Ziele bringen...
\end{solutionordottedlines}
```

### Output (Englisch)

```latex
\question[7] Define an appropriate, as \textbf{specific} as possible, 
performance measure for the autonomously driving rickshaw in 1-2 sentences.

\begin{solutionordottedlines}[3.25in]
The rickshaw should bring its customers promptly (no traffic jams and detours), 
safely and comfortably (no excessive accelerations) to the specified destinations...
\end{solutionordottedlines}
```

## API-Auswahl

| Provider | Default Model | API-Key | Kosten | Geschwindigkeit |
|----------|--------------|---------|--------|-----------------|
| OpenAI | `gpt-4o-mini` | Ja | ~$0.01-0.05/Klausur | Mittel |
| Groq | `kimi-k2-instruct` | Ja | Kostenlos | Sehr schnell |
| Gemini | `gemini-2.0-flash-exp` | Ja | Kostenlos | Schnell |
| Ollama | `llama3.2:1b` | Nein | Kostenlos | Langsam (lokal) |

## Fortgeschrittene Verwendung

### Integration in bestehende Projekte

```python
from latex_exam_translator import (
    split_latex_exam_into_sections,
    translate_question_to_english,
    translate_preamble_to_english
)

# Eigene Verarbeitung
with open("klausur.tex", "r") as f:
    content = f.read()

preamble, questions, postamble = split_latex_exam_into_sections(content)

# Nur bestimmte Fragen übersetzen
translated_q1 = translate_question_to_english(questions[0], client)
```

### Batch-Verarbeitung

```python
from pathlib import Path

# Übersetze alle Klausuren in einem Ordner
klausur_dir = Path("klausuren")

for tex_file in klausur_dir.glob("*.tex"):
    if "_engl" not in tex_file.stem:  # Überspringe bereits übersetzte
        print(f"Übersetze: {tex_file}")
        translate_latex_exam(tex_file, client)
```

## Fehlerbehandlung

```python
try:
    output = translate_latex_exam("klausur.tex", client)
except FileNotFoundError:
    print("Datei nicht gefunden!")
except ValueError as e:
    print(f"LaTeX-Strukturfehler: {e}")
except Exception as e:
    print(f"Unerwarteter Fehler: {e}")
```

## Bekannte Einschränkungen

1. **Exam-Klasse erforderlich**: Funktioniert nur mit LaTeX-Dokumenten, die `\documentclass{exam}` verwenden
2. **Fragen-Struktur**: Erwartet `\begin{questions}` ... `\end{questions}` Umgebung
3. **Komplexe Makros**: Sehr komplexe benutzerdefinierte Makros könnten Probleme verursachen
4. **Kontext-Grenzen**: Sehr lange Fragen (>4000 Tokens) können LLM-Limits überschreiten

## Tipps für beste Ergebnisse

✅ **Empfohlen:**
- Nutze Groq oder Gemini für schnelle kostenlose Übersetzungen
- Aktiviere `verbose=True` für erste Tests
- Prüfe die Ausgabe manuell bei kritischen Klausuren
- Nutze OpenAI für höchste Qualität bei wichtigen Dokumenten

❌ **Zu vermeiden:**
- Sehr verschachtelte LaTeX-Strukturen
- Custom-Makros mit Textargumenten
- Gemischte Sprachen im Original

## Lizenz

MIT License - siehe Hauptprojekt

## Support

Bei Problemen:
1. Prüfe die [Hauptdokumentation](../README.md)
2. Öffne ein [Issue](https://github.com/dgaida/colloquium-protocol-creator/issues)
3. Stelle sicher, dass API-Keys korrekt konfiguriert sind

## Verwandte Projekte

- [llm_client](https://github.com/dgaida/llm_client) - Universal Python LLM Client
