# Klausur-Übersetzer (LaTeX & XML)

## Übersicht

Dieses Modul übersetzt Klausurdokumente (LaTeX oder XML/ILIAS) automatisch von Deutsch nach Englisch. Es nutzt LLM-APIs (OpenAI, Groq, Gemini oder Ollama), um hochqualitative Übersetzungen zu erstellen, während die Struktur, Formatierung und technische Inhalte exakt erhalten bleiben.

## Erzeugte Dateien (Ergebnisse)

### 1. Übersetzte Datei
**Dateiname:** `<originalname>_engl.tex` oder `<originalname>_engl.xml`
Die fertig übersetzte Datei, in der alle fachlichen Inhalte ins Englische übertragen wurden.

---

## Benutzung

### Kommandozeile (CLI)

Das Tool erkennt das Format automatisch anhand der Dateiendung (`.tex` oder `.xml`).

```bash
# LaTeX-Übersetzung
academic-doc-generator translator KIKlausur.tex

# XML-Übersetzung (z.B. ILIAS-Export)
academic-doc-generator translator KIKlausur.xml
```

### Python API

```python
from llm_client import LLMClient
from academic_doc_generator.exam_translator import translate_latex_exam, translate_xml_exam

# Erstelle LLM-Client
client = LLMClient()

# LaTeX übersetzen
translate_latex_exam("KIKlausur.tex", client)

# XML übersetzen
translate_xml_exam("KIKlausur.xml", client)
```

## Hauptmerkmale

- ✅ **Format-Erhalt**: Behält die gesamte Struktur und alle technischen Tags bei.  
- ✅ **LaTeX-Spezialisierung**: Intelligente Aufteilung von LaTeX-Dokumenten (`exam`-Klasse) in Fragen.  
- ✅ **XML/ILIAS-Unterstützung**: Übersetzt gezielt Inhalte in `<mattext>`-Tags und schützt HTML-Entities.  
- ✅ **Mathematik-Schutz**: Mathematische Formeln werden nicht verändert.  
- ✅ **Kommentar-Schutz**: Maskiert LaTeX-Kommentare, um deren Position zu bewahren.  

---

## Funktionsweise (Details)

### LaTeX-Übersetzung  
1. **Struktur-Analyse**: Das Dokument wird in Präambel, Fragen und Postamble zerlegt.  
2. **Maskierung**: Kommentare werden vorübergehend maskiert.  
3. **Übersetzung**: Fließtext und Aufgabenstellungen werden übersetzt, Befehle bleiben erhalten.  

### XML-Übersetzung (z.B. ILIAS)
Das Tool sucht nach `<mattext texttype="text/xhtml">...</mattext>` Tags. Der darin enthaltene Text wird übersetzt, wobei interne HTML-Tags und XML-Entities (z.B. `&lt;`, `&#13;`) erhalten bleiben.

---

## Einschränkungen & Tipps

1. **Dateiendungen**: Nutzen Sie `.tex` für LaTeX und `.xml` für ILIAS-Exporte.  
2. **KI-Wahl**: Nutzen Sie **OpenAI (GPT-4o)** für die höchste Qualität bei komplexen fachlichen Formulierungen.  
3. **Schnelligkeit**: Nutzen Sie **Groq** oder **Gemini** für sehr schnelle und oft kostenlose Übersetzungen.  

## Weitere Dokumentation

- [Haupt-Dokumentation](index.de.md)  
- [Konfigurations-Handbuch](configuration.de.md)  
