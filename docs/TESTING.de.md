# Test-Anleitung

Dieses Dokument beschreibt, wie Sie die Tests für das Projekt Academic Document Generator ausführen.

## Installation

Installieren Sie zunächst die Entwicklungs-Abhängigkeiten:

```bash
pip install -e ".[dev]"
```

## Tests ausführen

### Alle Tests ausführen

```bash
pytest
```

### Mit Coverage-Bericht ausführen

```bash
pytest --cov=academic_doc_generator
```

### Spezifische Testdatei ausführen

```bash
pytest tests/test_colloquium_creator.py
```

### Mit ausführlicher Ausgabe ausführen

```bash
pytest -v
```

## Test-Struktur

Die Testsuite ist im Verzeichnis `tests/` organisiert:

- `test_colloquium_creator.py`: Tests für PDF-Parsing, Annotations-Extraktion und LaTeX-Generierung für Kolloquien.  
- `test_project_creator.py`: Tests für Metadaten-Extraktion und Geschlechtserkennung bei Projektarbeiten.  
- `test_review_creator.py`: Tests für Zeilennummer-Erkennung und Markdown-Generierung für Peer-Reviews.  
- `test_pipelines.py`: Integrationstests für die Orchestratoren.  
- `test_outlook_mail_generator.py`: Plattformunabhängige Tests für die E-Mail-Generierung.  
- `test_utils.py`: Unit-Tests für Hilfsfunktionen.  

## Mocking externer Abhängigkeiten

### LLM-APIs
Wir verwenden Mocks für den `llm_client`, um tatsächliche API-Aufrufe und Kosten während der Tests zu vermeiden.

### Plattformspezifische Module
Für `win32com` (Outlook unter Windows) verwenden wir Patches, damit die Testsuite auch in Linux-CI-Umgebungen (wie GitHub Actions) fehlerfrei durchläuft.

## Fehlerbehebung

### Tests schlagen mit `ModuleNotFoundError` fehl
Stellen Sie sicher, dass das Paket im editierbaren Modus installiert ist: `pip install -e .`
