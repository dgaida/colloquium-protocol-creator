# Installationsanleitung

## Systemvoraussetzungen

- **Python**: 3.9 oder höher
- **Betriebssystem**: Linux, macOS oder Windows
- **LaTeX**: LuaLaTeX empfohlen für vollständige Unicode-Unterstützung
- **API-Zugang**: Mindestens eine von OpenAI, Groq, Google Gemini oder Ollama

## Quick Start

```bash
# Repository klonen
git clone https://github.com/dgaida/colloquium-protocol-creator.git
cd colloquium-protocol-creator

# Im editierbaren Modus installieren
pip install -e .

# Überprüfung
academic-doc-generator --help
```

## Installationsmethoden

### Methode 1: Für Entwickler (empfohlen)

```bash
git clone https://github.com/dgaida/colloquium-protocol-creator.git
cd colloquium-protocol-creator
pip install -e .
```

Dies macht den einheitlichen Befehl `academic-doc-generator` global verfügbar.

### Methode 2: Mit Anaconda/Miniconda

```bash
git clone https://github.com/dgaida/colloquium-protocol-creator.git
cd colloquium-protocol-creator
conda env create -f environment.yml
conda activate colloquium-protocol-creator
pip install -e .
```

## LaTeX-Installation

Das Tool benötigt LaTeX zum Kompilieren von Protokollbriefen und Bewertungsformularen.

### Linux (Ubuntu/Debian)
`sudo apt-get install texlive-full`

### macOS
`brew install --cask mactex`

### Windows
Laden Sie [MiKTeX](https://miktex.org/download) herunter und führen Sie das Installationsprogramm aus.

## API-Einrichtung

Erstellen Sie eine `secrets.env`-Datei im Projektstammverzeichnis:

```bash
# OpenAI (kostenpflichtig, sehr zuverlässig)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Groq (sehr schnell, kostenlose Stufe verfügbar)
GROQ_API_KEY=gsk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google Gemini (schnell, kostenlose Stufe verfügbar)
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Ollama - kein API-Key erforderlich
```

## Installation überprüfen

### Kommandozeilen-Tool testen

```bash
academic-doc-generator --help
```

### Python-Implementierung testen

```python
from llm_client import LLMClient
client = LLMClient()
print(f"Verwendet: {client.api_choice}")
```

## Fehlerbehebung

### Import-Fehler
Falls Sie `ModuleNotFoundError: No module named 'llm_client'` sehen, stellen Sie sicher, dass Sie im editierbaren Modus installiert haben oder installieren Sie es manuell:
`pip install git+https://github.com/dgaida/llm_client.git`

### Befehl nicht gefunden
Falls `academic-doc-generator` nicht gefunden wird, stellen Sie sicher, dass sich das Verzeichnis für Python-Skripte in Ihrem PATH befindet.

## Entwicklungsumgebung

```bash
# Mit Entwickler-Extras installieren
pip install -e ".[dev]"

# Tests ausführen
pytest
```

## Nächste Schritte

1. [Kolloquium-Protokolle](COLLOQUIUM.md)
2. [Praxisprojekt-Benotung](PROJECT.md)
3. [Peer-Review-Kommentare](REVIEW.md)
4. [Klausur-Übersetzung](TRANSLATOR.md)
